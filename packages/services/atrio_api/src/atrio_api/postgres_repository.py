from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from dataclasses import replace
from enum import Enum
from types import MappingProxyType
from typing import Any, ContextManager
from uuid import uuid4

from atrio_api.cerne.persistence import CernePersistResult
from atrio_api.lux.persistence import LuxPersistResult
from atrio_api.database import (
    DATABASE_MIGRATIONS,
    DATABASE_SCHEMA_VERSION,
)
from atrio_api.corpus_intake import (
    CorpusIntakeConflict,
    CorpusIntakeRecordResult,
    CorpusIntakeRef,
)
from atrio_api.corpus_processing import (
    CorpusInventoryRecord,
    ExtractionMethod,
    ProcessingStatus,
    ReviewType,
)
from atrio_api.corpus_service import (
    CorpusDocumentRecord,
    CorpusProcessingIncomplete,
    CorpusProcessingRecordResult,
    CorpusReviewDecision,
    CorpusReviewNotFound,
    CorpusReviewResult,
)
from atrio_api.domain import (
    ArtifactRef,
    CerneGate,
    Command,
    CommandKind,
    ComponentName,
    Destination,
    ExecutionStage,
    ExecutionState,
    ExecutionStatus,
    RatioModule,
    ReleaseEnvelope,
)
from atrio_api.ratio.contract import (
    RatioPhase,
    RatioPhaseStatus,
    TroiaMode,
    TroiaStatus,
    TroiaTrigger,
    phases_for,
    troia_policy_for,
)
from atrio_api.ratio.persistence import (
    RatioArtifactRecord,
    RatioPersistResult,
    RatioPersistenceIntegrityError,
    RatioRevisionConflict,
    RatioRuntimeAlreadyStarted,
    RatioRuntimeNotFound,
    RatioRuntimeStartResult,
)
from atrio_api.ratio.state import (
    RatioPhaseSnapshot,
    RatioRunState,
    TroiaState,
    create_ratio_run,
)
from atrio_api.repository import (
    CreateResult,
    ExecutionNotFound,
    IdempotencyConflict,
    RepositoryError,
)
from atrio_api.state_machine import (
    TransitionEvent,
    TransitionResult,
    VersionConflict,
    transition,
)


ConnectionFactory = Callable[[], ContextManager[Any]]


class PostgresDriverUnavailable(RepositoryError):
    pass


class DatabaseSchemaMismatch(RepositoryError):
    pass


class PostgresExecutionRepository:
    """Persistência transacional do núcleo, sem conteúdo jurídico em logs."""

    def __init__(self, connection_factory: ConnectionFactory):
        self._connection_factory = connection_factory

    @classmethod
    def from_conninfo(cls, conninfo: str) -> PostgresExecutionRepository:
        if not conninfo.strip():
            raise ValueError("conninfo é obrigatório.")
        psycopg, dict_row = _load_psycopg()

        def connect() -> ContextManager[Any]:
            return psycopg.connect(conninfo, row_factory=dict_row)

        return cls(connect)

    @classmethod
    def from_parameters(
        cls,
        **parameters: Any,
    ) -> PostgresExecutionRepository:
        psycopg, dict_row = _load_psycopg()

        def connect() -> ContextManager[Any]:
            return psycopg.connect(**parameters, row_factory=dict_row)

        return cls(connect)

    def verify_schema(self) -> None:
        with self._connection_factory() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT version, checksum
                      FROM atrio.schema_migrations
                     WHERE version = ANY(%s)
                    """,
                    (list(DATABASE_MIGRATIONS),),
                )
                rows = cursor.fetchall()

        persisted = {
            row["version"]: row["checksum"].strip()
            for row in rows
        }
        missing = sorted(set(DATABASE_MIGRATIONS) - set(persisted))
        if missing:
            raise DatabaseSchemaMismatch(
                "Migrações PostgreSQL ausentes: " + ", ".join(missing) + "."
            )
        for version, expected_checksum in DATABASE_MIGRATIONS.items():
            if persisted[version] != expected_checksum:
                raise DatabaseSchemaMismatch(
                    f"Checksum do schema PostgreSQL {version} diverge."
                )

    def create(
        self,
        state: ExecutionState,
        *,
        idempotency_key: str,
        request_fingerprint: str,
    ) -> CreateResult:
        with self._connection_factory() as connection:
            with connection.cursor() as cursor:
                _ensure_release(cursor, state.release)
                cursor.execute(
                    """
                    SELECT pg_catalog.pg_advisory_xact_lock(
                        pg_catalog.hashtextextended(%s, 0)
                    )
                    """,
                    (f"{state.tenant_id}\x1f{idempotency_key}",),
                )
                cursor.execute(
                    """
                    SELECT execution_id::text, request_fingerprint
                      FROM atrio.idempotency_keys
                     WHERE tenant_id = %s
                       AND idempotency_key = %s
                    """,
                    (state.tenant_id, idempotency_key),
                )
                previous = cursor.fetchone()
                if previous is not None:
                    if previous["request_fingerprint"].strip() != request_fingerprint:
                        raise IdempotencyConflict(idempotency_key)
                    persisted = _load_state(
                        cursor,
                        previous["execution_id"],
                    )
                    return CreateResult(state=persisted, created=False)

                cursor.execute(
                    """
                    INSERT INTO atrio.executions (
                        execution_id,
                        tenant_id,
                        created_by,
                        ratio_module,
                        destination,
                        release_id,
                        stage,
                        status,
                        state_version
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        state.execution_id,
                        state.tenant_id,
                        state.created_by,
                        state.ratio_module.value,
                        state.destination.value,
                        state.release.release_id,
                        state.stage.value,
                        state.status.value,
                        state.state_version,
                    ),
                )
                cursor.execute(
                    """
                    INSERT INTO atrio.idempotency_keys (
                        tenant_id,
                        idempotency_key,
                        request_fingerprint,
                        execution_id
                    ) VALUES (%s, %s, %s, %s)
                    """,
                    (
                        state.tenant_id,
                        idempotency_key,
                        request_fingerprint,
                        state.execution_id,
                    ),
                )
        return CreateResult(state=state, created=True)

    def get(self, execution_id: str) -> ExecutionState:
        with self._connection_factory() as connection:
            with connection.cursor() as cursor:
                return _load_state(cursor, execution_id)

    def apply(
        self,
        execution_id: str,
        command: Command,
    ) -> TransitionResult:
        with self._connection_factory() as connection:
            with connection.cursor() as cursor:
                current = _load_state(
                    cursor,
                    execution_id,
                    for_update=True,
                )
                result = transition(current, command)
                _persist_transition(cursor, current, command, result)
        return result

    def record_corpus_intake(
        self,
        intake: CorpusIntakeRef,
        *,
        expected_version: int,
    ) -> CorpusIntakeRecordResult:
        with self._connection_factory() as connection:
            with connection.cursor() as cursor:
                current = _load_state(
                    cursor,
                    intake.execution_id,
                    for_update=True,
                )
                cursor.execute(
                    """
                    SELECT
                        document_id::text,
                        execution_id::text,
                        idempotency_key,
                        created_by,
                        sha256,
                        byte_length,
                        media_type,
                        storage_key,
                        encryption_algorithm,
                        envelope_version,
                        intake_version
                      FROM atrio.corpus_intakes
                     WHERE execution_id = %s
                       AND idempotency_key = %s
                    """,
                    (
                        intake.execution_id,
                        intake.idempotency_key,
                    ),
                )
                previous = cursor.fetchone()
                if previous is not None:
                    persisted = _intake_from_row(previous)
                    if persisted != intake:
                        raise CorpusIntakeConflict(
                            "A chave idempotente já possui outros parâmetros."
                        )
                    return CorpusIntakeRecordResult(
                        state=current,
                        intake=persisted,
                        created=False,
                    )

                cursor.execute(
                    """
                    SELECT document_id::text
                      FROM atrio.corpus_intakes
                     WHERE execution_id = %s
                       AND sha256 = %s
                    """,
                    (intake.execution_id, intake.sha256),
                )
                duplicate = cursor.fetchone()
                if duplicate is not None:
                    raise CorpusIntakeConflict(
                        "O documento já foi registrado com outra chave idempotente."
                    )

                command_kind = (
                    CommandKind.START_INGESTION
                    if current.stage is ExecutionStage.CREATED
                    else CommandKind.REGISTER_CORPUS_DOCUMENT
                )
                command = Command(
                    kind=command_kind,
                    expected_version=expected_version,
                    actor_id=intake.created_by,
                    payload={
                        "document_id": intake.document_id,
                        "document_sha256": intake.sha256,
                    },
                )
                result = transition(current, command)
                cursor.execute(
                    """
                    INSERT INTO atrio.corpus_intakes (
                        document_id,
                        execution_id,
                        idempotency_key,
                        created_by,
                        sha256,
                        byte_length,
                        media_type,
                        storage_key,
                        encryption_algorithm,
                        envelope_version,
                        intake_version
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        intake.document_id,
                        intake.execution_id,
                        intake.idempotency_key,
                        intake.created_by,
                        intake.sha256,
                        intake.byte_length,
                        intake.media_type,
                        intake.storage_key,
                        intake.encryption_algorithm,
                        intake.envelope_version,
                        intake.intake_version,
                    ),
                )
                _persist_transition(cursor, current, command, result)
        return CorpusIntakeRecordResult(
            state=result.state,
            intake=intake,
            created=True,
        )

    def list_corpus_documents(
        self,
        execution_id: str,
    ) -> tuple[CorpusDocumentRecord, ...]:
        with self._connection_factory() as connection:
            with connection.cursor() as cursor:
                _load_state(cursor, execution_id)
                rows = _select_corpus_documents(cursor, execution_id)
        return tuple(_corpus_document_from_row(row) for row in rows)

    def record_corpus_processing(
        self,
        document: CorpusDocumentRecord,
        *,
        processed_storage_key: str,
        actor_id: str,
        expected_version: int,
    ) -> CorpusProcessingRecordResult:
        inventory = document.inventory
        if inventory is None or document.processing_id is None:
            raise ValueError("Resultado de processamento incompleto.")
        with self._connection_factory() as connection:
            with connection.cursor() as cursor:
                current = _load_state(
                    cursor,
                    document.intake.execution_id,
                    for_update=True,
                )
                cursor.execute(
                    """
                    SELECT 1
                      FROM atrio.corpus_processing_results
                     WHERE document_id = %s
                    """,
                    (document.intake.document_id,),
                )
                if cursor.fetchone() is not None:
                    persisted = _load_corpus_document(
                        cursor,
                        document.intake.execution_id,
                        document.intake.document_id,
                    )
                    if (
                        persisted.inventory != inventory
                        or persisted.processing_id
                        != document.processing_id
                    ):
                        # processing_id é descartável em uma repetição após
                        # perda da resposta; o contrato seguro é o inventário.
                        if persisted.inventory != inventory:
                            raise CorpusIntakeConflict(
                                "Documento já possui outro processamento."
                            )
                    return CorpusProcessingRecordResult(
                        state=current,
                        document=persisted,
                        created=False,
                    )

                if current.state_version != expected_version:
                    raise VersionConflict(
                        expected_version,
                        current.state_version,
                    )
                if inventory.execution_id != current.execution_id:
                    raise CorpusIntakeConflict(
                        "Inventário pertence a outra execução."
                    )
                if inventory.document_id != document.intake.document_id:
                    raise CorpusIntakeConflict(
                        "Inventário pertence a outro documento."
                    )
                if inventory.input_sha256 != document.intake.sha256:
                    raise CorpusIntakeConflict(
                        "Inventário diverge do hash de intake."
                    )
                if (
                    inventory.corpus_pipeline_version
                    != current.release.corpus_version
                    or inventory.atrio_pii_version
                    != current.release.atrio_pii_version
                ):
                    raise CorpusIntakeConflict(
                        "Versão do processamento diverge da release."
                    )

                cursor.execute(
                    """
                    INSERT INTO atrio.corpus_processing_results (
                        processing_id,
                        document_id,
                        execution_id,
                        input_sha256,
                        byte_length,
                        media_type,
                        extraction_method,
                        page_count,
                        extracted_char_count,
                        ocr_mean_confidence,
                        cnj,
                        procedural_class,
                        secrecy_level,
                        pii_counts,
                        pseudonym_count,
                        pseudonymized_sha256,
                        processing_status,
                        review_type,
                        processed_storage_key,
                        corpus_pipeline_version,
                        atrio_pii_version,
                        processed_by
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        document.processing_id,
                        inventory.document_id,
                        inventory.execution_id,
                        inventory.input_sha256,
                        inventory.byte_length,
                        inventory.media_type,
                        inventory.extraction_method.value,
                        inventory.page_count,
                        inventory.extracted_char_count,
                        inventory.ocr_mean_confidence,
                        inventory.cnj,
                        inventory.procedural_class,
                        inventory.secrecy_level,
                        json.dumps(
                            dict(inventory.pii_counts),
                            ensure_ascii=True,
                            separators=(",", ":"),
                            sort_keys=True,
                        ),
                        inventory.pseudonym_count,
                        inventory.pseudonymized_sha256,
                        inventory.status.value,
                        (
                            inventory.review_type.value
                            if inventory.review_type is not None
                            else None
                        ),
                        processed_storage_key,
                        inventory.corpus_pipeline_version,
                        inventory.atrio_pii_version,
                        actor_id,
                    ),
                )
                if inventory.status is ProcessingStatus.REVIEW_REQUIRED:
                    command = Command(
                        kind=CommandKind.REQUEST_CORPUS_REVIEW,
                        expected_version=expected_version,
                        actor_id=actor_id,
                        payload={
                            "review_type": inventory.review_type.value,
                        },
                    )
                    result = transition(current, command)
                    _persist_transition(cursor, current, command, result)
                    current = result.state

        return CorpusProcessingRecordResult(
            state=current,
            document=document,
            created=True,
        )

    def record_corpus_review(
        self,
        *,
        execution_id: str,
        document_id: str,
        decision: CorpusReviewDecision,
        actor_id: str,
        expected_version: int,
    ) -> CorpusReviewResult:
        with self._connection_factory() as connection:
            with connection.cursor() as cursor:
                current = _load_state(
                    cursor,
                    execution_id,
                    for_update=True,
                )
                document = _load_corpus_document(
                    cursor,
                    execution_id,
                    document_id,
                )
                if (
                    document.inventory is None
                    or document.processing_id is None
                    or document.inventory.status
                    is not ProcessingStatus.REVIEW_REQUIRED
                ):
                    raise CorpusReviewNotFound(
                        "Documento não possui revisão pendente."
                    )
                if document.review_decision is not None:
                    raise CorpusReviewNotFound(
                        "A revisão deste documento já foi decidida."
                    )
                command = Command(
                    kind=CommandKind.RESUME_CORPUS,
                    expected_version=expected_version,
                    actor_id=actor_id,
                    payload={"decision_code": decision.value},
                )
                result = transition(current, command)
                if current.waiting_reason != (
                    document.inventory.review_type.value
                ):
                    raise CorpusReviewNotFound(
                        "A revisão não corresponde à espera da execução."
                    )
                cursor.execute(
                    """
                    INSERT INTO atrio.corpus_review_decisions (
                        review_id,
                        processing_id,
                        decision_code,
                        actor_id
                    ) VALUES (%s, %s, %s, %s)
                    """,
                    (
                        str(uuid4()),
                        document.processing_id,
                        decision.value,
                        actor_id,
                    ),
                )
                _persist_transition(cursor, current, command, result)
                reviewed = replace(
                    document,
                    review_decision=decision,
                    reviewed_by=actor_id,
                )
        return CorpusReviewResult(
            state=result.state,
            document=reviewed,
        )

    def finalize_corpus(
        self,
        *,
        execution_id: str,
        artifact: ArtifactRef,
        storage_key: str,
        document_count: int,
        pipeline_version: str,
        actor_id: str,
        expected_version: int,
    ) -> ExecutionState:
        with self._connection_factory() as connection:
            with connection.cursor() as cursor:
                current = _load_state(
                    cursor,
                    execution_id,
                    for_update=True,
                )
                command = Command(
                    kind=CommandKind.COMPLETE_CORPUS,
                    expected_version=expected_version,
                    actor_id=actor_id,
                    payload={"artifact": artifact},
                )
                result = transition(current, command)
                cursor.execute(
                    """
                    SELECT
                        count(*)::integer AS total,
                        count(p.processing_id)::integer AS processed,
                        count(*) FILTER (
                            WHERE p.processing_status = 'REVIEW_REQUIRED'
                              AND r.review_id IS NULL
                        )::integer AS unresolved,
                        count(*) FILTER (
                            WHERE r.decision_code = 'EXCLUDE'
                        )::integer AS excluded
                      FROM atrio.corpus_intakes AS i
                      LEFT JOIN atrio.corpus_processing_results AS p
                        ON p.document_id = i.document_id
                      LEFT JOIN atrio.corpus_review_decisions AS r
                        ON r.processing_id = p.processing_id
                     WHERE i.execution_id = %s
                    """,
                    (execution_id,),
                )
                counts = cursor.fetchone()
                included = counts["total"] - counts["excluded"]
                if (
                    counts["total"] == 0
                    or counts["processed"] != counts["total"]
                    or counts["unresolved"] != 0
                    or included != document_count
                    or included <= 0
                ):
                    raise CorpusProcessingIncomplete(
                        "Lote CORPUS não está pronto para handoff."
                    )
                _persist_transition(cursor, current, command, result)
                cursor.execute(
                    """
                    INSERT INTO atrio.corpus_outputs (
                        artifact_id,
                        execution_id,
                        storage_key,
                        document_count,
                        bundle_sha256,
                        corpus_pipeline_version,
                        created_by
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        artifact.artifact_id,
                        execution_id,
                        storage_key,
                        document_count,
                        artifact.sha256,
                        pipeline_version,
                        actor_id,
                    ),
                )
        return result.state

    def start_ratio_runtime(
        self,
        execution_id: str,
        *,
        actor_id: str,
        expected_version: int,
        idempotency_key: str,
    ) -> RatioRuntimeStartResult:
        """Persiste START_RATIO e snapshot inicial RATIO na mesma transação."""

        if not actor_id.strip():
            raise ValueError("actor_id é obrigatório.")
        if not idempotency_key.strip():
            raise ValueError("idempotency_key é obrigatória.")

        fingerprint = _payload_fingerprint(
            {
                "operation": "START_RATIO_RUNTIME",
                "execution_id": execution_id,
                "actor_id": actor_id,
                "expected_version": expected_version,
            }
        )

        with self._connection_factory() as connection:
            with connection.cursor() as cursor:
                current = _load_state(
                    cursor,
                    execution_id,
                    for_update=True,
                )

                previous_idempotency = _load_ratio_idempotency(
                    cursor,
                    execution_id,
                    idempotency_key,
                )
                if previous_idempotency is not None:
                    if (
                        previous_idempotency["request_fingerprint"].strip()
                        != fingerprint
                    ):
                        raise IdempotencyConflict(idempotency_key)
                    ratio_state = _load_ratio_state(
                        cursor,
                        execution_id,
                        revision=int(
                            previous_idempotency["resulting_revision"]
                        ),
                    )
                    return RatioRuntimeStartResult(
                        execution_state=current,
                        ratio_state=ratio_state,
                        created=False,
                    )

                cursor.execute(
                    """
                    SELECT head_revision
                      FROM atrio.ratio_runs
                     WHERE execution_id = %s
                    """,
                    (execution_id,),
                )
                if cursor.fetchone() is not None:
                    raise RatioRuntimeAlreadyStarted(execution_id)

                command = Command(
                    kind=CommandKind.START_RATIO,
                    expected_version=expected_version,
                    actor_id=actor_id,
                )
                transition_result = transition(current, command)
                ratio_state = create_ratio_run(current.ratio_module)

                _persist_transition(
                    cursor,
                    current,
                    command,
                    transition_result,
                )
                cursor.execute(
                    """
                    INSERT INTO atrio.ratio_runs (
                        execution_id,
                        module,
                        head_revision,
                        started_command_sequence
                    ) VALUES (%s, %s, %s, %s)
                    """,
                    (
                        execution_id,
                        ratio_state.module.value,
                        ratio_state.revision,
                        transition_result.event.sequence,
                    ),
                )
                _insert_ratio_snapshot(
                    cursor,
                    execution_id,
                    ratio_state,
                )
                _insert_ratio_idempotency(
                    cursor,
                    execution_id,
                    idempotency_key,
                    fingerprint,
                    ratio_state.revision,
                )

        return RatioRuntimeStartResult(
            execution_state=transition_result.state,
            ratio_state=ratio_state,
            created=True,
        )

    def get_ratio_runtime(
        self,
        execution_id: str,
        *,
        revision: int | None = None,
    ) -> RatioRunState:
        """Reconstrói head ou snapshot histórico exclusivamente do PostgreSQL."""

        with self._connection_factory() as connection:
            with connection.cursor() as cursor:
                run = _load_ratio_run_head(cursor, execution_id)
                actual_revision = int(run["head_revision"])
                if revision is not None and revision > actual_revision:
                    raise RatioRevisionConflict(revision, actual_revision)
                return _load_ratio_state(
                    cursor,
                    execution_id,
                    revision=revision,
                )

    def persist_ratio_transition(
        self,
        execution_id: str,
        *,
        previous: RatioRunState,
        updated: RatioRunState,
        action: str,
        actor_id: str,
        idempotency_key: str,
        external_command: Command | None = None,
        artifact_refs: tuple[tuple[str, ArtifactRef], ...] = (),
        operator_decision_code: str | None = None,
    ) -> RatioPersistResult:
        """Persiste uma revisão interna RATIO de modo otimista e idempotente.

        `updated` deve ter sido produzido pelo motor puro. Este método verifica
        forma, revisão, integridade do snapshot anterior e serialização no banco.
        Quando há `external_command`, a transição macro ATRIO é persistida na
        mesma transação da revisão interna.
        """

        _validate_ratio_transition_pair(previous, updated, action)

        if not actor_id.strip():
            raise ValueError("actor_id é obrigatório.")
        if not idempotency_key.strip():
            raise ValueError("idempotency_key é obrigatória.")
        roles = [role for role, _artifact in artifact_refs]
        if any(not role.strip() for role in roles) or len(set(roles)) != len(roles):
            raise ValueError("Papéis de artefato RATIO devem ser únicos e não vazios.")
        if operator_decision_code is not None and not operator_decision_code.strip():
            raise ValueError("operator_decision_code não pode ser vazio.")
        if external_command is not None and external_command.actor_id != actor_id:
            raise ValueError(
                "actor_id da transição RATIO diverge do comando externo."
            )

        external_descriptor = None
        if external_command is not None:
            external_descriptor = {
                "kind": external_command.kind.value,
                "expected_version": external_command.expected_version,
                "actor_id": external_command.actor_id,
                "payload": external_command.payload,
            }

        updated_sha256 = _ratio_state_sha256(updated)
        fingerprint = _payload_fingerprint(
            {
                "operation": "RATIO_TRANSITION",
                "execution_id": execution_id,
                "expected_revision": previous.revision,
                "resulting_revision": updated.revision,
                "action": action,
                "actor_id": actor_id,
                "updated_state_sha256": updated_sha256,
                "external_command": external_descriptor,
                "artifact_refs": [
                    {
                        "role": role,
                        "artifact": artifact,
                    }
                    for role, artifact in artifact_refs
                ],
                "operator_decision_code": operator_decision_code,
            }
        )

        with self._connection_factory() as connection:
            with connection.cursor() as cursor:
                execution_state = _load_state(
                    cursor,
                    execution_id,
                    for_update=True,
                )

                previous_idempotency = _load_ratio_idempotency(
                    cursor,
                    execution_id,
                    idempotency_key,
                )
                if previous_idempotency is not None:
                    if (
                        previous_idempotency["request_fingerprint"].strip()
                        != fingerprint
                    ):
                        raise IdempotencyConflict(idempotency_key)
                    persisted = _load_ratio_state(
                        cursor,
                        execution_id,
                        revision=int(
                            previous_idempotency["resulting_revision"]
                        ),
                    )
                    return RatioPersistResult(
                        execution_state=execution_state,
                        ratio_state=persisted,
                        created=False,
                    )

                run = _load_ratio_run_head(
                    cursor,
                    execution_id,
                    for_update=True,
                )
                if run["module"] != previous.module.value:
                    raise RatioPersistenceIntegrityError(
                        "Módulo do head RATIO diverge do estado anterior."
                    )

                actual_revision = int(run["head_revision"])
                if actual_revision != previous.revision:
                    raise RatioRevisionConflict(
                        previous.revision,
                        actual_revision,
                    )

                persisted_previous = _load_ratio_state(
                    cursor,
                    execution_id,
                    revision=previous.revision,
                )
                if persisted_previous != previous:
                    raise RatioPersistenceIntegrityError(
                        "Snapshot RATIO anterior diverge do estado fornecido."
                    )

                external_sequence = None
                if external_command is not None:
                    external_result = transition(
                        execution_state,
                        external_command,
                    )
                    _persist_transition(
                        cursor,
                        execution_state,
                        external_command,
                        external_result,
                    )
                    execution_state = external_result.state
                    external_sequence = external_result.event.sequence

                _insert_ratio_snapshot(
                    cursor,
                    execution_id,
                    updated,
                )
                for artifact_role, artifact in artifact_refs:
                    _ensure_artifact(cursor, execution_id, artifact)
                    cursor.execute(
                        """
                        INSERT INTO atrio.ratio_artifact_refs (
                            execution_id,
                            ratio_revision,
                            artifact_role,
                            artifact_id
                        ) VALUES (%s, %s, %s, %s)
                        """,
                        (
                            execution_id,
                            updated.revision,
                            artifact_role,
                            artifact.artifact_id,
                        ),
                    )
                cursor.execute(
                    """
                    INSERT INTO atrio.ratio_transitions (
                        execution_id,
                        expected_revision,
                        resulting_revision,
                        action,
                        actor_id,
                        payload_fingerprint,
                        external_command_sequence
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        execution_id,
                        previous.revision,
                        updated.revision,
                        action,
                        actor_id,
                        fingerprint,
                        external_sequence,
                    ),
                )
                if operator_decision_code is not None:
                    cursor.execute(
                        """
                        INSERT INTO atrio.ratio_operator_decisions (
                            decision_id,
                            execution_id,
                            ratio_revision,
                            phase,
                            decision_code,
                            actor_id,
                            payload_fingerprint
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            str(uuid4()),
                            execution_id,
                            updated.revision,
                            previous.current_phase.value,
                            operator_decision_code,
                            actor_id,
                            fingerprint,
                        ),
                    )
                cursor.execute(
                    """
                    UPDATE atrio.ratio_runs
                       SET head_revision = %s,
                           updated_at = clock_timestamp()
                     WHERE execution_id = %s
                       AND head_revision = %s
                    """,
                    (
                        updated.revision,
                        execution_id,
                        previous.revision,
                    ),
                )
                if cursor.rowcount != 1:
                    raise RatioRevisionConflict(
                        previous.revision,
                        actual_revision,
                    )

                _insert_ratio_idempotency(
                    cursor,
                    execution_id,
                    idempotency_key,
                    fingerprint,
                    updated.revision,
                )

        return RatioPersistResult(
            execution_state=execution_state,
            ratio_state=updated,
            created=True,
        )

    def list_ratio_artifacts(
        self,
        execution_id: str,
    ) -> tuple[RatioArtifactRecord, ...]:
        with self._connection_factory() as connection:
            with connection.cursor() as cursor:
                _load_ratio_run_head(cursor, execution_id)
                cursor.execute(
                    """
                    SELECT
                        ratio_revision,
                        artifact_role,
                        artifact_id
                      FROM atrio.ratio_artifact_refs
                     WHERE execution_id = %s
                     ORDER BY ratio_revision, artifact_role, artifact_id
                    """,
                    (execution_id,),
                )
                rows = cursor.fetchall()
                return tuple(
                    RatioArtifactRecord(
                        revision=int(row["ratio_revision"]),
                        role=row["artifact_role"],
                        artifact=_load_artifact(cursor, row["artifact_id"]),
                    )
                    for row in rows
                )

    def latest_ratio_execution_barrier(self, execution_id: str) -> int:
        with self._connection_factory() as connection:
            with connection.cursor() as cursor:
                _load_ratio_run_head(cursor, execution_id)
                cursor.execute(
                    """
                    SELECT COALESCE(max(resulting_revision), 0)::bigint AS revision
                      FROM atrio.ratio_transitions
                     WHERE execution_id = %s
                       AND action IN (
                           'ADVANCE',
                           'RETURN_AFTER_CHANGE',
                           'RESUME_TROIA',
                           'CONFIGURE_TROIA'
                       )
                    """,
                    (execution_id,),
                )
                row = cursor.fetchone()
                return int(row["revision"])

    def apply_cerne_audit(
        self,
        execution_id: str,
        *,
        expected_version: int,
        actor_id: str,
        artifact: ArtifactRef,
        gate: CerneGate,
        reason_code: str | None,
    ) -> CernePersistResult:
        """Persiste START_CERNE + gate final na mesma transação PostgreSQL."""

        if not actor_id.strip():
            raise ValueError("actor_id é obrigatório.")
        if gate is not CerneGate.AVANCA and not (reason_code or "").strip():
            raise ValueError("Gate CERNE não-AVANCA exige reason_code.")

        with self._connection_factory() as connection:
            with connection.cursor() as cursor:
                current = _load_state(
                    cursor,
                    execution_id,
                    for_update=True,
                )
                if (
                    current.cerne_artifact == artifact
                    and current.cerne_gate is gate
                ):
                    return CernePersistResult(
                        execution_state=current,
                        created=False,
                    )

                start_command = Command(
                    kind=CommandKind.START_CERNE,
                    expected_version=expected_version,
                    actor_id=actor_id,
                )
                started = transition(current, start_command)
                _persist_transition(
                    cursor,
                    current,
                    start_command,
                    started,
                )

                payload: dict[str, Any] = {
                    "artifact": artifact,
                    "gate": gate.value,
                }
                if gate is not CerneGate.AVANCA:
                    payload["reason_code"] = reason_code
                gate_command = Command(
                    kind=CommandKind.APPLY_CERNE_GATE,
                    expected_version=started.state.state_version,
                    actor_id=actor_id,
                    payload=payload,
                )
                gated = transition(started.state, gate_command)
                _persist_transition(
                    cursor,
                    started.state,
                    gate_command,
                    gated,
                )

        return CernePersistResult(
            execution_state=gated.state,
            created=True,
        )

    def apply_lux_refinement(
        self,
        execution_id: str,
        *,
        expected_version: int,
        actor_id: str,
        artifact: ArtifactRef,
    ) -> LuxPersistResult:
        """Persiste START_LUX + COMPLETE_LUX atomicamente no PostgreSQL."""

        if not actor_id.strip():
            raise ValueError("actor_id é obrigatório.")

        with self._connection_factory() as connection:
            with connection.cursor() as cursor:
                current = _load_state(
                    cursor,
                    execution_id,
                    for_update=True,
                )
                if current.lux_artifact == artifact:
                    return LuxPersistResult(
                        execution_state=current,
                        created=False,
                    )

                active = current
                if current.stage is ExecutionStage.CERNE_APPROVED:
                    start_command = Command(
                        kind=CommandKind.START_LUX,
                        expected_version=expected_version,
                        actor_id=actor_id,
                    )
                    started = transition(current, start_command)
                    _persist_transition(
                        cursor,
                        current,
                        start_command,
                        started,
                    )
                    active = started.state
                elif current.stage is not ExecutionStage.LUX_REFINING:
                    start_command = Command(
                        kind=CommandKind.START_LUX,
                        expected_version=expected_version,
                        actor_id=actor_id,
                    )
                    transition(current, start_command)
                elif current.state_version != expected_version:
                    raise VersionConflict(
                        expected_version,
                        current.state_version,
                    )

                complete_command = Command(
                    kind=CommandKind.COMPLETE_LUX,
                    expected_version=active.state_version,
                    actor_id=actor_id,
                    payload={"artifact": artifact},
                )
                completed = transition(active, complete_command)
                _persist_transition(
                    cursor,
                    active,
                    complete_command,
                    completed,
                )

        return LuxPersistResult(
            execution_state=completed.state,
            created=True,
        )


    def events(self, execution_id: str) -> tuple[TransitionEvent, ...]:
        with self._connection_factory() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        execution_id::text,
                        sequence,
                        command_kind,
                        from_stage,
                        to_stage,
                        component,
                        component_version,
                        release_id,
                        actor_id,
                        occurred_at,
                        metadata
                      FROM atrio.execution_events
                     WHERE execution_id = %s
                     ORDER BY sequence
                    """,
                    (execution_id,),
                )
                rows = cursor.fetchall()
                if not rows:
                    cursor.execute(
                        """
                        SELECT 1
                          FROM atrio.executions
                         WHERE execution_id = %s
                        """,
                        (execution_id,),
                    )
                    if cursor.fetchone() is None:
                        raise ExecutionNotFound(execution_id)

        return tuple(_event_from_row(row) for row in rows)


def _load_ratio_idempotency(
    cursor: Any,
    execution_id: str,
    idempotency_key: str,
) -> Mapping[str, Any] | None:
    cursor.execute(
        """
        SELECT request_fingerprint, resulting_revision
          FROM atrio.ratio_idempotency_keys
         WHERE execution_id = %s
           AND idempotency_key = %s
        """,
        (execution_id, idempotency_key),
    )
    return cursor.fetchone()


def _insert_ratio_idempotency(
    cursor: Any,
    execution_id: str,
    idempotency_key: str,
    request_fingerprint: str,
    resulting_revision: int,
) -> None:
    cursor.execute(
        """
        INSERT INTO atrio.ratio_idempotency_keys (
            execution_id,
            idempotency_key,
            request_fingerprint,
            resulting_revision
        ) VALUES (%s, %s, %s, %s)
        """,
        (
            execution_id,
            idempotency_key,
            request_fingerprint,
            resulting_revision,
        ),
    )


def _load_ratio_run_head(
    cursor: Any,
    execution_id: str,
    *,
    for_update: bool = False,
) -> Mapping[str, Any]:
    lock_clause = " FOR UPDATE" if for_update else ""
    cursor.execute(
        """
        SELECT module, head_revision
          FROM atrio.ratio_runs
         WHERE execution_id = %s
        """
        + lock_clause,
        (execution_id,),
    )
    row = cursor.fetchone()
    if row is None:
        raise RatioRuntimeNotFound(execution_id)
    return row


def _load_ratio_state(
    cursor: Any,
    execution_id: str,
    *,
    revision: int | None = None,
) -> RatioRunState:
    run = _load_ratio_run_head(cursor, execution_id)
    selected_revision = (
        int(run["head_revision"])
        if revision is None
        else revision
    )

    cursor.execute(
        """
        SELECT
            revision,
            module,
            current_phase,
            last_operator_action,
            troia_mode,
            troia_phase,
            troia_status,
            troia_triggers,
            troia_blocking_code,
            state_sha256
          FROM atrio.ratio_snapshots
         WHERE execution_id = %s
           AND revision = %s
        """,
        (execution_id, selected_revision),
    )
    row = cursor.fetchone()
    if row is None:
        raise RatioPersistenceIntegrityError(
            f"Snapshot RATIO ausente na revisão {selected_revision}."
        )

    module = RatioModule(row["module"])
    if module.value != run["module"]:
        raise RatioPersistenceIntegrityError(
            "Módulo do snapshot RATIO diverge do head."
        )

    cursor.execute(
        """
        SELECT phase, status
          FROM atrio.ratio_snapshot_phases
         WHERE execution_id = %s
           AND revision = %s
        """,
        (execution_id, selected_revision),
    )
    phase_rows = cursor.fetchall()
    status_by_phase = {
        RatioPhase(item["phase"]): RatioPhaseStatus(item["status"])
        for item in phase_rows
    }

    expected_phases = phases_for(module)
    if set(status_by_phase) != set(expected_phases):
        raise RatioPersistenceIntegrityError(
            "Conjunto de fases persistidas diverge do contrato RATIO."
        )

    state = RatioRunState(
        module=module,
        current_phase=RatioPhase(row["current_phase"]),
        phases=tuple(
            RatioPhaseSnapshot(
                phase=phase,
                status=status_by_phase[phase],
            )
            for phase in expected_phases
        ),
        troia=TroiaState(
            mode=TroiaMode(row["troia_mode"]),
            phase=(
                RatioPhase(row["troia_phase"])
                if row["troia_phase"] is not None
                else None
            ),
            status=TroiaStatus(row["troia_status"]),
            triggers=frozenset(
                TroiaTrigger(value)
                for value in row["troia_triggers"]
            ),
            blocking_code=row["troia_blocking_code"],
        ),
        revision=int(row["revision"]),
        last_operator_action=row["last_operator_action"],
    )
    _validate_ratio_state_shape(state)

    persisted_hash = row["state_sha256"].strip()
    calculated_hash = _ratio_state_sha256(state)
    if persisted_hash != calculated_hash:
        raise RatioPersistenceIntegrityError(
            "Hash do snapshot RATIO diverge do estado reconstruído."
        )

    return state


def _insert_ratio_snapshot(
    cursor: Any,
    execution_id: str,
    state: RatioRunState,
) -> None:
    _validate_ratio_state_shape(state)

    cursor.execute(
        """
        INSERT INTO atrio.ratio_snapshots (
            execution_id,
            revision,
            module,
            current_phase,
            last_operator_action,
            troia_mode,
            troia_phase,
            troia_status,
            troia_triggers,
            troia_blocking_code,
            state_sha256
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """,
        (
            execution_id,
            state.revision,
            state.module.value,
            state.current_phase.value,
            state.last_operator_action,
            state.troia.mode.value,
            state.troia.phase.value if state.troia.phase else None,
            state.troia.status.value,
            sorted(trigger.value for trigger in state.troia.triggers),
            state.troia.blocking_code,
            _ratio_state_sha256(state),
        ),
    )

    for item in state.phases:
        cursor.execute(
            """
            INSERT INTO atrio.ratio_snapshot_phases (
                execution_id,
                revision,
                module,
                phase,
                status
            ) VALUES (%s, %s, %s, %s, %s)
            """,
            (
                execution_id,
                state.revision,
                state.module.value,
                item.phase.value,
                item.status.value,
            ),
        )


def _validate_ratio_transition_pair(
    previous: RatioRunState,
    updated: RatioRunState,
    action: str,
) -> None:
    if not action.strip():
        raise ValueError("action é obrigatória.")

    _validate_ratio_state_shape(previous)
    _validate_ratio_state_shape(updated)

    if previous.module is not updated.module:
        raise RatioPersistenceIntegrityError(
            "Transição RATIO não pode trocar de módulo."
        )
    if updated.revision != previous.revision + 1:
        raise RatioRevisionConflict(
            previous.revision + 1,
            updated.revision,
        )


def _validate_ratio_state_shape(state: RatioRunState) -> None:
    if state.revision < 0:
        raise RatioPersistenceIntegrityError(
            "Revisão RATIO não pode ser negativa."
        )

    expected_phases = phases_for(state.module)
    actual_phases = tuple(item.phase for item in state.phases)
    if actual_phases != expected_phases:
        raise RatioPersistenceIntegrityError(
            "Ordem/conjunto de fases diverge do contrato RATIO."
        )
    if state.current_phase not in expected_phases:
        raise RatioPersistenceIntegrityError(
            "Fase atual não pertence ao módulo RATIO."
        )

    policy = troia_policy_for(state.module)
    if (
        state.troia.mode is not policy.mode
        or state.troia.phase is not policy.phase
    ):
        raise RatioPersistenceIntegrityError(
            "Posição de TROIA diverge da política do módulo."
        )

    if state.troia.mode is TroiaMode.NOT_DEFINED:
        if (
            state.troia.status is not TroiaStatus.NOT_DEFINED
            or state.troia.triggers
            or state.troia.blocking_code is not None
        ):
            raise RatioPersistenceIntegrityError(
                "Módulo sem TROIA contém estado contrafactual indevido."
            )
    elif state.troia.mode is TroiaMode.AUTONOMOUS_REQUIRED:
        if state.troia.triggers:
            raise RatioPersistenceIntegrityError(
                "TROIA autônomo não usa gatilhos ED."
            )
    elif not state.troia.triggers.issubset(policy.triggers):
        raise RatioPersistenceIntegrityError(
            "TROIA ED contém gatilho fora do contrato."
        )

    if (
        state.troia.status is TroiaStatus.BLOCKED
    ) != (state.troia.blocking_code is not None):
        raise RatioPersistenceIntegrityError(
            "Código de bloqueio TROIA diverge do status."
        )


def _ratio_state_sha256(state: RatioRunState) -> str:
    payload = {
        "module": state.module.value,
        "current_phase": state.current_phase.value,
        "phases": [
            {
                "phase": item.phase.value,
                "status": item.status.value,
            }
            for item in state.phases
        ],
        "troia": {
            "mode": state.troia.mode.value,
            "phase": (
                state.troia.phase.value
                if state.troia.phase is not None
                else None
            ),
            "status": state.troia.status.value,
            "triggers": sorted(
                trigger.value
                for trigger in state.troia.triggers
            ),
            "blocking_code": state.troia.blocking_code,
        },
        "revision": state.revision,
        "last_operator_action": state.last_operator_action,
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _select_corpus_documents(
    cursor: Any,
    execution_id: str,
) -> list[Mapping[str, Any]]:
    cursor.execute(
        """
        SELECT
            i.document_id::text AS intake_document_id,
            i.execution_id::text AS intake_execution_id,
            i.idempotency_key AS intake_idempotency_key,
            i.created_by AS intake_created_by,
            i.sha256 AS intake_sha256,
            i.byte_length AS intake_byte_length,
            i.media_type AS intake_media_type,
            i.storage_key AS intake_storage_key,
            i.encryption_algorithm AS intake_encryption_algorithm,
            i.envelope_version AS intake_envelope_version,
            i.intake_version AS intake_version,
            p.processing_id::text,
            p.input_sha256 AS processing_input_sha256,
            p.byte_length AS processing_byte_length,
            p.media_type AS processing_media_type,
            p.extraction_method,
            p.page_count,
            p.extracted_char_count,
            p.ocr_mean_confidence,
            p.cnj,
            p.procedural_class,
            p.secrecy_level,
            p.pii_counts,
            p.pseudonym_count,
            p.pseudonymized_sha256,
            p.processing_status,
            p.review_type,
            p.corpus_pipeline_version,
            p.atrio_pii_version,
            r.decision_code AS review_decision,
            r.actor_id AS reviewed_by
          FROM atrio.corpus_intakes AS i
          LEFT JOIN atrio.corpus_processing_results AS p
            ON p.document_id = i.document_id
          LEFT JOIN atrio.corpus_review_decisions AS r
            ON r.processing_id = p.processing_id
         WHERE i.execution_id = %s
         ORDER BY i.created_at, i.document_id
        """,
        (execution_id,),
    )
    return cursor.fetchall()


def _load_corpus_document(
    cursor: Any,
    execution_id: str,
    document_id: str,
) -> CorpusDocumentRecord:
    rows = _select_corpus_documents(cursor, execution_id)
    for row in rows:
        if row["intake_document_id"] == document_id:
            return _corpus_document_from_row(row)
    raise CorpusReviewNotFound("Documento CORPUS não encontrado.")


def _corpus_document_from_row(
    row: Mapping[str, Any],
) -> CorpusDocumentRecord:
    intake = CorpusIntakeRef(
        document_id=row["intake_document_id"],
        execution_id=row["intake_execution_id"],
        idempotency_key=row["intake_idempotency_key"],
        created_by=row["intake_created_by"],
        sha256=row["intake_sha256"].strip(),
        byte_length=int(row["intake_byte_length"]),
        media_type=row["intake_media_type"],
        storage_key=row["intake_storage_key"],
        encryption_algorithm=row["intake_encryption_algorithm"],
        envelope_version=row["intake_envelope_version"],
        intake_version=row["intake_version"],
    )
    processing_id = row["processing_id"]
    inventory = None
    if processing_id is not None:
        inventory = CorpusInventoryRecord(
            document_id=intake.document_id,
            execution_id=intake.execution_id,
            input_sha256=row["processing_input_sha256"].strip(),
            byte_length=int(row["processing_byte_length"]),
            media_type=row["processing_media_type"],
            extraction_method=ExtractionMethod(row["extraction_method"]),
            page_count=int(row["page_count"]),
            extracted_char_count=int(row["extracted_char_count"]),
            ocr_mean_confidence=(
                float(row["ocr_mean_confidence"])
                if row["ocr_mean_confidence"] is not None
                else None
            ),
            cnj=row["cnj"],
            procedural_class=row["procedural_class"],
            secrecy_level=row["secrecy_level"],
            pii_counts=tuple(
                sorted(
                    (
                        str(key),
                        int(value),
                    )
                    for key, value in row["pii_counts"].items()
                )
            ),
            pseudonym_count=int(row["pseudonym_count"]),
            pseudonymized_sha256=row["pseudonymized_sha256"].strip(),
            status=ProcessingStatus(row["processing_status"]),
            review_type=(
                ReviewType(row["review_type"])
                if row["review_type"] is not None
                else None
            ),
            corpus_pipeline_version=row["corpus_pipeline_version"],
            atrio_pii_version=row["atrio_pii_version"],
        )
    return CorpusDocumentRecord(
        intake=intake,
        processing_id=processing_id,
        inventory=inventory,
        review_decision=(
            CorpusReviewDecision(row["review_decision"])
            if row["review_decision"] is not None
            else None
        ),
        reviewed_by=row["reviewed_by"],
    )


def _load_psycopg() -> tuple[Any, Any]:
    try:
        import psycopg
        from psycopg.rows import dict_row
    except ImportError as exc:
        raise PostgresDriverUnavailable(
            "Driver PostgreSQL ausente; instale o projeto atrio-api."
        ) from exc
    return psycopg, dict_row


def _ensure_release(cursor: Any, release: ReleaseEnvelope) -> None:
    values = (
        release.release_id,
        release.atrio_api_version,
        release.corpus_version,
        release.ratio_version,
        release.cerne_module_version,
        release.cerne_service_build,
        release.lux_version,
        release.atrio_pii_version,
        release.prompt_bundle_hash,
        release.schema_version,
    )
    cursor.execute(
        """
        INSERT INTO atrio.releases (
            release_id,
            atrio_api_version,
            corpus_version,
            ratio_version,
            cerne_module_version,
            cerne_service_build,
            lux_version,
            atrio_pii_version,
            prompt_bundle_hash,
            artifact_schema_version
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (release_id) DO NOTHING
        """,
        values,
    )
    cursor.execute(
        """
        SELECT
            release_id,
            atrio_api_version,
            corpus_version,
            ratio_version,
            cerne_module_version,
            cerne_service_build,
            lux_version,
            atrio_pii_version,
            prompt_bundle_hash,
            artifact_schema_version
          FROM atrio.releases
         WHERE release_id = %s
        """,
        (release.release_id,),
    )
    row = cursor.fetchone()
    persisted = tuple(
        row[name]
        for name in (
            "release_id",
            "atrio_api_version",
            "corpus_version",
            "ratio_version",
            "cerne_module_version",
            "cerne_service_build",
            "lux_version",
            "atrio_pii_version",
            "prompt_bundle_hash",
            "artifact_schema_version",
        )
    )
    if persisted != values:
        raise RepositoryError(
            f"Release imutável diverge do envelope: {release.release_id}."
        )


def _load_state(
    cursor: Any,
    execution_id: str,
    *,
    for_update: bool = False,
) -> ExecutionState:
    lock_clause = " FOR UPDATE OF e" if for_update else ""
    cursor.execute(
        """
        SELECT
            e.*,
            r.atrio_api_version,
            r.corpus_version,
            r.ratio_version,
            r.cerne_module_version,
            r.cerne_service_build,
            r.lux_version,
            r.atrio_pii_version,
            r.prompt_bundle_hash,
            r.artifact_schema_version
          FROM atrio.executions AS e
          JOIN atrio.releases AS r USING (release_id)
         WHERE e.execution_id = %s
        """
        + lock_clause,
        (execution_id,),
    )
    row = cursor.fetchone()
    if row is None:
        raise ExecutionNotFound(execution_id)

    release = ReleaseEnvelope(
        release_id=row["release_id"],
        atrio_api_version=row["atrio_api_version"],
        corpus_version=row["corpus_version"],
        ratio_version=row["ratio_version"],
        cerne_module_version=row["cerne_module_version"],
        cerne_service_build=row["cerne_service_build"],
        lux_version=row["lux_version"],
        atrio_pii_version=row["atrio_pii_version"],
        prompt_bundle_hash=row["prompt_bundle_hash"],
        schema_version=row["artifact_schema_version"],
    )
    artifacts = {
        name: _load_artifact(cursor, row[f"{name}_artifact_id"])
        for name in ("corpus", "ratio", "cerne", "lux", "released")
    }
    return ExecutionState(
        execution_id=str(row["execution_id"]),
        tenant_id=row["tenant_id"],
        created_by=row["created_by"],
        ratio_module=RatioModule(row["ratio_module"]),
        destination=Destination(row["destination"]),
        release=release,
        stage=ExecutionStage(row["stage"]),
        status=ExecutionStatus(row["status"]),
        state_version=int(row["state_version"]),
        corpus_artifact=artifacts["corpus"],
        ratio_artifact=artifacts["ratio"],
        cerne_artifact=artifacts["cerne"],
        lux_artifact=artifacts["lux"],
        released_artifact=artifacts["released"],
        current_ratio_phase=row["current_ratio_phase"],
        waiting_reason=row["waiting_reason"],
        last_operator_actor=row["last_operator_actor"],
        last_operator_decision=row["last_operator_decision"],
        cerne_gate=CerneGate(row["cerne_gate"]) if row["cerne_gate"] else None,
        last_error_code=row["last_error_code"],
        retry_stage=(
            ExecutionStage(row["retry_stage"])
            if row["retry_stage"]
            else None
        ),
    )


def _load_artifact(cursor: Any, artifact_id: str | None) -> ArtifactRef | None:
    if artifact_id is None:
        return None
    cursor.execute(
        """
        SELECT
            artifact_id,
            sha256,
            media_type,
            classification,
            producer,
            producer_version,
            release_id,
            artifact_schema_version
          FROM atrio.artifacts
         WHERE artifact_id = %s
        """,
        (artifact_id,),
    )
    row = cursor.fetchone()
    if row is None:
        raise RepositoryError(f"Referência de artefato órfã: {artifact_id}.")
    return ArtifactRef(
        artifact_id=row["artifact_id"],
        sha256=row["sha256"].strip(),
        media_type=row["media_type"],
        classification=row["classification"],
        producer=ComponentName(row["producer"]),
        producer_version=row["producer_version"],
        release_id=row["release_id"],
        schema_version=row["artifact_schema_version"],
    )


def _persist_new_artifacts(
    cursor: Any,
    execution_id: str,
    previous: ExecutionState,
    updated: ExecutionState,
) -> None:
    for field_name in (
        "corpus_artifact",
        "ratio_artifact",
        "cerne_artifact",
        "lux_artifact",
        "released_artifact",
    ):
        before = getattr(previous, field_name)
        after = getattr(updated, field_name)
        if after is not None and after != before:
            _ensure_artifact(cursor, execution_id, after)


def _persist_transition(
    cursor: Any,
    previous: ExecutionState,
    command: Command,
    result: TransitionResult,
) -> None:
    _persist_new_artifacts(
        cursor,
        previous.execution_id,
        previous,
        result.state,
    )
    _update_execution(cursor, result.state)
    cursor.execute(
        """
        INSERT INTO atrio.command_log (
            execution_id,
            sequence,
            command_kind,
            expected_version,
            resulting_version,
            actor_id,
            payload_fingerprint
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            previous.execution_id,
            result.event.sequence,
            command.kind.value,
            command.expected_version,
            result.state.state_version,
            command.actor_id,
            _payload_fingerprint(command.payload),
        ),
    )
    cursor.execute(
        """
        INSERT INTO atrio.execution_events (
            execution_id,
            sequence,
            command_kind,
            from_stage,
            to_stage,
            component,
            component_version,
            release_id,
            actor_id,
            occurred_at,
            metadata
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s::jsonb
        )
        """,
        (
            result.event.execution_id,
            result.event.sequence,
            result.event.command.value,
            result.event.from_stage.value,
            result.event.to_stage.value,
            result.event.component.value,
            result.event.component_version,
            result.event.release_id,
            result.event.actor_id,
            result.event.occurred_at,
            json.dumps(
                dict(result.event.metadata),
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            ),
        ),
    )


def _intake_from_row(row: Mapping[str, Any]) -> CorpusIntakeRef:
    return CorpusIntakeRef(
        document_id=row["document_id"],
        execution_id=row["execution_id"],
        idempotency_key=row["idempotency_key"],
        created_by=row["created_by"],
        sha256=row["sha256"].strip(),
        byte_length=int(row["byte_length"]),
        media_type=row["media_type"],
        storage_key=row["storage_key"],
        encryption_algorithm=row["encryption_algorithm"],
        envelope_version=row["envelope_version"],
        intake_version=row["intake_version"],
    )


def _ensure_artifact(
    cursor: Any,
    execution_id: str,
    artifact: ArtifactRef,
) -> None:
    values = (
        artifact.artifact_id,
        execution_id,
        artifact.release_id,
        artifact.sha256,
        artifact.media_type,
        artifact.classification,
        artifact.producer.value,
        artifact.producer_version,
        artifact.schema_version,
    )
    cursor.execute(
        """
        INSERT INTO atrio.artifacts (
            artifact_id,
            owner_execution_id,
            release_id,
            sha256,
            media_type,
            classification,
            producer,
            producer_version,
            artifact_schema_version
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (artifact_id) DO NOTHING
        """,
        values,
    )
    cursor.execute(
        """
        SELECT
            artifact_id,
            owner_execution_id::text,
            release_id,
            sha256,
            media_type,
            classification,
            producer,
            producer_version,
            artifact_schema_version
          FROM atrio.artifacts
         WHERE artifact_id = %s
        """,
        (artifact.artifact_id,),
    )
    row = cursor.fetchone()
    persisted = (
        row["artifact_id"],
        row["owner_execution_id"],
        row["release_id"],
        row["sha256"].strip(),
        row["media_type"],
        row["classification"],
        row["producer"],
        row["producer_version"],
        row["artifact_schema_version"],
    )
    if persisted != values:
        raise RepositoryError(
            f"Artefato imutável diverge da referência: {artifact.artifact_id}."
        )


def _update_execution(cursor: Any, state: ExecutionState) -> None:
    cursor.execute(
        """
        UPDATE atrio.executions
           SET stage = %s,
               status = %s,
               state_version = %s,
               corpus_artifact_id = %s,
               ratio_artifact_id = %s,
               cerne_artifact_id = %s,
               lux_artifact_id = %s,
               released_artifact_id = %s,
               current_ratio_phase = %s,
               waiting_reason = %s,
               last_operator_actor = %s,
               last_operator_decision = %s,
               cerne_gate = %s,
               last_error_code = %s,
               retry_stage = %s
         WHERE execution_id = %s
           AND state_version = %s
        """,
        (
            state.stage.value,
            state.status.value,
            state.state_version,
            state.corpus_artifact_id,
            state.ratio_artifact_id,
            state.cerne_artifact_id,
            state.lux_artifact_id,
            state.released_artifact_id,
            state.current_ratio_phase,
            state.waiting_reason,
            state.last_operator_actor,
            state.last_operator_decision,
            state.cerne_gate.value if state.cerne_gate else None,
            state.last_error_code,
            state.retry_stage.value if state.retry_stage else None,
            state.execution_id,
            state.state_version - 1,
        ),
    )
    if cursor.rowcount != 1:
        raise RepositoryError(
            f"Atualização concorrente inesperada: {state.execution_id}."
        )


def _event_from_row(row: Mapping[str, Any]) -> TransitionEvent:
    return TransitionEvent(
        execution_id=row["execution_id"],
        sequence=int(row["sequence"]),
        command=CommandKind(row["command_kind"]),
        from_stage=ExecutionStage(row["from_stage"]),
        to_stage=ExecutionStage(row["to_stage"]),
        component=ComponentName(row["component"]),
        component_version=row["component_version"],
        release_id=row["release_id"],
        actor_id=row["actor_id"],
        occurred_at=row["occurred_at"],
        metadata=MappingProxyType(dict(row["metadata"])),
    )


def _payload_fingerprint(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(
        _canonical_value(payload),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _canonical_value(value: Any) -> Any:
    if isinstance(value, ArtifactRef):
        return {
            "artifact_id": value.artifact_id,
            "sha256": value.sha256,
            "media_type": value.media_type,
            "classification": value.classification,
            "producer": value.producer.value,
            "producer_version": value.producer_version,
            "release_id": value.release_id,
            "schema_version": value.schema_version,
        }
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {
            str(key): _canonical_value(item)
            for key, item in sorted(
                value.items(),
                key=lambda pair: str(pair[0]),
            )
        }
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(
        f"Tipo não suportado no payload do comando: {type(value).__name__}."
    )
