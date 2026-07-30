from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from threading import RLock
from typing import Protocol
from uuid import UUID, uuid4, uuid5

from atrio_api.corpus_intake import (
    CorpusIntakeRef,
    EncryptedCorpusStore,
)
from atrio_api.corpus_processing import (
    CORPUS_PIPELINE_VERSION,
    CorpusInventoryRecord,
    CorpusProcessor,
    LocalCorpusExtractor,
    PseudonymMap,
    ProcessingStatus,
)
from atrio_api.domain import (
    ArtifactRef,
    ComponentName,
    ExecutionStage,
    ExecutionState,
)
from atrio_api.state_machine import InvalidTransition, VersionConflict


CORPUS_ARTIFACT_MEDIA_TYPE = "application/vnd.atrio.corpus+json"
CORPUS_ARTIFACT_CLASSIFICATION = "INTERNAL_PSEUDONYMIZED"
_CORPUS_ARTIFACT_NAMESPACE = UUID(
    "7de8c64c-a831-466c-b862-3a43fe76b403"
)


class CorpusWorkflowError(RuntimeError):
    pass


class CorpusNoDocuments(CorpusWorkflowError):
    pass


class CorpusProcessingIncomplete(CorpusWorkflowError):
    pass


class CorpusReviewNotFound(CorpusWorkflowError):
    pass


class CorpusReviewDecision(StrEnum):
    APPROVE = "APPROVE"
    EXCLUDE = "EXCLUDE"


@dataclass(frozen=True, slots=True)
class CorpusDocumentRecord:
    intake: CorpusIntakeRef
    processing_id: str | None = None
    inventory: CorpusInventoryRecord | None = None
    review_decision: CorpusReviewDecision | None = None
    reviewed_by: str | None = None

    @property
    def effective_status(self) -> str:
        if self.inventory is None:
            return "PENDING"
        if self.review_decision is CorpusReviewDecision.EXCLUDE:
            return "EXCLUDED"
        if self.review_decision is CorpusReviewDecision.APPROVE:
            return "APPROVED"
        return self.inventory.status.value

    def safe_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "byte_length": self.intake.byte_length,
            "document_id": self.intake.document_id,
            "effective_status": self.effective_status,
            "execution_id": self.intake.execution_id,
            "input_sha256": self.intake.sha256,
            "intake_version": self.intake.intake_version,
            "media_type": self.intake.media_type,
            "processing_id": self.processing_id,
            "review_decision": (
                self.review_decision.value
                if self.review_decision is not None
                else None
            ),
        }
        if self.inventory is not None:
            result["inventory"] = self.inventory.safe_dict()
        else:
            result["inventory"] = None
        return result


@dataclass(frozen=True, slots=True)
class CorpusProcessingRecordResult:
    state: ExecutionState
    document: CorpusDocumentRecord
    created: bool


@dataclass(frozen=True, slots=True)
class CorpusBatchResult:
    state: ExecutionState
    documents: tuple[CorpusDocumentRecord, ...]
    processed_count: int
    halted_for_review: bool


@dataclass(frozen=True, slots=True)
class CorpusReviewResult:
    state: ExecutionState
    document: CorpusDocumentRecord


@dataclass(frozen=True, slots=True)
class CorpusFinalizeResult:
    state: ExecutionState
    artifact: ArtifactRef
    document_count: int


class CorpusProcessingRepository(Protocol):
    def get(self, execution_id: str) -> ExecutionState: ...

    def list_corpus_documents(
        self,
        execution_id: str,
    ) -> tuple[CorpusDocumentRecord, ...]: ...

    def record_corpus_processing(
        self,
        document: CorpusDocumentRecord,
        *,
        processed_storage_key: str,
        actor_id: str,
        expected_version: int,
    ) -> CorpusProcessingRecordResult: ...

    def record_corpus_review(
        self,
        *,
        execution_id: str,
        document_id: str,
        decision: CorpusReviewDecision,
        actor_id: str,
        expected_version: int,
    ) -> CorpusReviewResult: ...

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
    ) -> ExecutionState: ...


class CorpusWorkflowService:
    def __init__(
        self,
        repository: CorpusProcessingRepository,
        store: EncryptedCorpusStore,
        processor: CorpusProcessor,
        extractor: LocalCorpusExtractor,
    ):
        self._repository = repository
        self._store = store
        self._processor = processor
        self._extractor = extractor
        self._lock = RLock()

    def verify_tools(self) -> dict[str, str]:
        return self._extractor.verify()

    def list_documents(
        self,
        execution_id: str,
    ) -> tuple[CorpusDocumentRecord, ...]:
        return self._repository.list_corpus_documents(execution_id)

    def process_pending(
        self,
        *,
        execution_id: str,
        actor_id: str,
        expected_version: int,
    ) -> CorpusBatchResult:
        with self._lock:
            state = self._expected_ingesting_state(
                execution_id,
                expected_version,
            )
            documents = self._repository.list_corpus_documents(execution_id)
            if not documents:
                raise CorpusNoDocuments(
                    "A execução não possui documentos no CORPUS."
                )

            pseudonym_map = self._load_map(execution_id)
            processed_count = 0
            halted_for_review = False
            for document in documents:
                if document.inventory is not None:
                    continue
                content = self._store.decrypt_bytes(document.intake)
                processed = self._processor.process(
                    execution_id=execution_id,
                    document_id=document.intake.document_id,
                    input_sha256=document.intake.sha256,
                    media_type=document.intake.media_type,
                    content=content,
                    pseudonym_map=pseudonym_map,
                )
                storage_key = (
                    f"processed/{execution_id}/"
                    f"{document.intake.document_id}.atrio"
                )
                self._store.write_private_record(
                    storage_key,
                    processed.pseudonymized_text.encode("utf-8"),
                )
                self._save_map(execution_id, pseudonym_map)
                persisted = self._repository.record_corpus_processing(
                    CorpusDocumentRecord(
                        intake=document.intake,
                        processing_id=str(uuid4()),
                        inventory=processed.inventory,
                    ),
                    processed_storage_key=storage_key,
                    actor_id=actor_id,
                    expected_version=state.state_version,
                )
                state = persisted.state
                if persisted.created:
                    processed_count += 1
                if (
                    persisted.document.inventory is not None
                    and persisted.document.inventory.status
                    is ProcessingStatus.REVIEW_REQUIRED
                    and persisted.document.review_decision is None
                ):
                    halted_for_review = True
                    break

            current_documents = self._repository.list_corpus_documents(
                execution_id
            )
            return CorpusBatchResult(
                state=state,
                documents=current_documents,
                processed_count=processed_count,
                halted_for_review=halted_for_review,
            )

    def review(
        self,
        *,
        execution_id: str,
        document_id: str,
        decision: CorpusReviewDecision,
        actor_id: str,
        expected_version: int,
    ) -> CorpusReviewResult:
        return self._repository.record_corpus_review(
            execution_id=execution_id,
            document_id=document_id,
            decision=decision,
            actor_id=actor_id,
            expected_version=expected_version,
        )

    def finalize(
        self,
        *,
        execution_id: str,
        actor_id: str,
        expected_version: int,
    ) -> CorpusFinalizeResult:
        with self._lock:
            state = self._expected_ingesting_state(
                execution_id,
                expected_version,
            )
            documents = self._repository.list_corpus_documents(execution_id)
            included = self._included_documents(documents)
            self._require_valid_map(execution_id)
            bundle = _build_bundle(state, included, self._store)
            digest = hashlib.sha256(bundle).hexdigest()
            artifact_id = str(
                uuid5(
                    _CORPUS_ARTIFACT_NAMESPACE,
                    f"{execution_id}\x1f{digest}",
                )
            )
            storage_key = (
                f"artifacts/{execution_id}/{artifact_id}.atrio"
            )
            self._store.write_private_record(storage_key, bundle)
            artifact = ArtifactRef(
                artifact_id=artifact_id,
                sha256=digest,
                media_type=CORPUS_ARTIFACT_MEDIA_TYPE,
                classification=CORPUS_ARTIFACT_CLASSIFICATION,
                producer=ComponentName.CORPUS,
                producer_version=state.release.corpus_version,
                release_id=state.release.release_id,
                schema_version=state.release.schema_version,
            )
            updated = self._repository.finalize_corpus(
                execution_id=execution_id,
                artifact=artifact,
                storage_key=storage_key,
                document_count=len(included),
                pipeline_version=CORPUS_PIPELINE_VERSION,
                actor_id=actor_id,
                expected_version=expected_version,
            )
            return CorpusFinalizeResult(
                state=updated,
                artifact=artifact,
                document_count=len(included),
            )

    def _expected_ingesting_state(
        self,
        execution_id: str,
        expected_version: int,
    ) -> ExecutionState:
        state = self._repository.get(execution_id)
        if state.state_version != expected_version:
            raise VersionConflict(expected_version, state.state_version)
        if state.stage is not ExecutionStage.CORPUS_INGESTING:
            raise InvalidTransition(
                state.stage,
                # O erro permanece compatível com o comando governado.
                _processing_command(),
            )
        return state

    def _load_map(self, execution_id: str) -> PseudonymMap:
        storage_key = f"maps/{execution_id}/pseudonym-map.atrio"
        try:
            serialized = self._store.read_private_record(storage_key)
        except FileNotFoundError:
            return PseudonymMap.empty()
        return PseudonymMap.from_bytes(serialized)

    def _save_map(
        self,
        execution_id: str,
        pseudonym_map: PseudonymMap,
    ) -> None:
        self._store.write_private_record(
            f"maps/{execution_id}/pseudonym-map.atrio",
            pseudonym_map.to_bytes(),
            replace=True,
        )

    def _require_valid_map(self, execution_id: str) -> None:
        try:
            serialized = self._store.read_private_record(
                f"maps/{execution_id}/pseudonym-map.atrio"
            )
        except FileNotFoundError as exc:
            raise CorpusProcessingIncomplete(
                "Mapa reversível da execução está ausente."
            ) from exc
        PseudonymMap.from_bytes(serialized)

    @staticmethod
    def _included_documents(
        documents: tuple[CorpusDocumentRecord, ...],
    ) -> tuple[CorpusDocumentRecord, ...]:
        if not documents:
            raise CorpusNoDocuments(
                "A execução não possui documentos no CORPUS."
            )
        if any(document.inventory is None for document in documents):
            raise CorpusProcessingIncomplete(
                "Ainda existem documentos pendentes de processamento."
            )
        if any(
            document.inventory is not None
            and document.inventory.status is ProcessingStatus.REVIEW_REQUIRED
            and document.review_decision is None
            for document in documents
        ):
            raise CorpusProcessingIncomplete(
                "Ainda existem revisões humanas pendentes."
            )
        included = tuple(
            document
            for document in documents
            if document.review_decision is not CorpusReviewDecision.EXCLUDE
        )
        if not included:
            raise CorpusNoDocuments(
                "Todos os documentos foram excluídos pela revisão."
            )
        return included


def _build_bundle(
    state: ExecutionState,
    documents: tuple[CorpusDocumentRecord, ...],
    store: EncryptedCorpusStore,
) -> bytes:
    serialized_documents: list[dict[str, object]] = []
    for document in sorted(
        documents,
        key=lambda item: item.intake.document_id,
    ):
        if document.inventory is None:
            raise CorpusProcessingIncomplete
        storage_key = (
            f"processed/{state.execution_id}/"
            f"{document.intake.document_id}.atrio"
        )
        pseudonymized = store.read_private_record(storage_key)
        if hashlib.sha256(pseudonymized).hexdigest() != (
            document.inventory.pseudonymized_sha256
        ):
            raise CorpusProcessingIncomplete(
                "Hash do texto pseudonimizado diverge do inventário."
            )
        serialized_documents.append(
            {
                "inventory": document.inventory.safe_dict(),
                "pseudonymized_text": pseudonymized.decode("utf-8"),
            }
        )
    return json.dumps(
        {
            "corpus_pipeline_version": CORPUS_PIPELINE_VERSION,
            "corpus_version": state.release.corpus_version,
            "documents": serialized_documents,
            "execution_id": state.execution_id,
            "release_id": state.release.release_id,
            "schema_version": state.release.schema_version,
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _processing_command():
    # Import tardio evita acoplamento do contrato público do serviço.
    from atrio_api.domain import CommandKind

    return CommandKind.REGISTER_CORPUS_DOCUMENT


def default_corpus_workflow(
    repository: CorpusProcessingRepository,
    store: EncryptedCorpusStore,
    *,
    packages_root: Path,
    scratch_root: Path,
    expected_pii_version: str,
) -> CorpusWorkflowService:
    extractor = LocalCorpusExtractor.discover(scratch_root=scratch_root)
    from atrio_api.corpus_processing import load_pii_engine

    pii = load_pii_engine(
        packages_root / "atrio_pii" / "atrio_pii.py",
        expected_version=expected_pii_version,
    )
    return CorpusWorkflowService(
        repository,
        store,
        CorpusProcessor(extractor, pii),
        extractor,
    )
