"""Camada de aplicação governada do runtime interno do RATIO."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Protocol

from atrio_api.domain import (
    ArtifactRef,
    Command,
    CommandKind,
    ExecutionStage,
    ExecutionState,
)
from atrio_api.ratio.catalog import HardStopCatalog, load_hard_stop_catalog
from atrio_api.ratio.contract import RatioPhase, TroiaTrigger
from atrio_api.ratio.engine import (
    RatioTransitionError,
    advance_phase,
    block_troia,
    configure_ed_troia,
    finalize_ratio_state,
    record_phase_execution,
    resume_troia,
    return_after_substantial_change,
    validate_current_phase,
    validate_troia,
)
from atrio_api.ratio.execution import (
    RatioArtifactMissing,
    RatioExecutionUnavailable,
    RatioFinalizeResult,
    RatioPhaseExecutionResult,
    RatioPhaseExecutor,
)
from atrio_api.ratio.persistence import (
    RatioArtifactRecord,
    RatioPersistResult,
    RatioRevisionConflict,
    RatioRuntimeStartResult,
)
from atrio_api.ratio.state import RatioRunState


class RatioActionPayloadError(ValueError):
    pass


class RatioActionKind(StrEnum):
    VALIDATE = "VALIDATE"
    VALIDATE_WITH_CAVEAT = "VALIDATE_WITH_CAVEAT"
    ADVANCE = "ADVANCE"
    CONFIGURE_TROIA = "CONFIGURE_TROIA"
    VALIDATE_TROIA = "VALIDATE_TROIA"
    BLOCK_TROIA = "BLOCK_TROIA"
    RESUME_TROIA = "RESUME_TROIA"
    RETURN_AFTER_CHANGE = "RETURN_AFTER_CHANGE"


class RatioRuntimeRepository(Protocol):
    def get(self, execution_id: str) -> ExecutionState: ...

    def start_ratio_runtime(
        self,
        execution_id: str,
        *,
        actor_id: str,
        expected_version: int,
        idempotency_key: str,
    ) -> RatioRuntimeStartResult: ...

    def get_ratio_runtime(
        self,
        execution_id: str,
        *,
        revision: int | None = None,
    ) -> RatioRunState: ...

    def list_ratio_artifacts(
        self,
        execution_id: str,
    ) -> tuple[RatioArtifactRecord, ...]: ...

    def latest_ratio_execution_barrier(self, execution_id: str) -> int: ...

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
    ) -> RatioPersistResult: ...


class RatioWorkflowService:
    def __init__(
        self,
        repository: RatioRuntimeRepository,
        hard_stop_catalog: HardStopCatalog,
        *,
        executor: RatioPhaseExecutor | None = None,
        enforce_execution: bool = True,
    ) -> None:
        self._repository = repository
        self._hard_stop_catalog = hard_stop_catalog
        self._executor = executor
        self._enforce_execution = enforce_execution

    def start(
        self,
        execution_id: str,
        *,
        actor_id: str,
        expected_version: int,
        idempotency_key: str,
    ) -> RatioRuntimeStartResult:
        return self._repository.start_ratio_runtime(
            execution_id,
            actor_id=actor_id,
            expected_version=expected_version,
            idempotency_key=idempotency_key,
        )

    def get(self, execution_id: str) -> RatioRunState:
        return self._repository.get_ratio_runtime(execution_id)

    def execute_phase(
        self,
        execution_id: str,
        *,
        expected_revision: int,
        actor_id: str,
        idempotency_key: str,
    ) -> RatioPhaseExecutionResult:
        executor = self._require_executor()
        execution = self._repository.get(execution_id)
        if execution.stage not in {
            ExecutionStage.RATIO_RUNNING,
            ExecutionStage.RATIO_REWORK,
        }:
            from atrio_api.ratio.engine import RatioTransitionError

            raise RatioTransitionError(
                f"Execução de fase RATIO não é permitida em {execution.stage.value}."
            )

        head = self._repository.get_ratio_runtime(execution_id)
        if head.revision != expected_revision and not executor.has_prepared(
            execution_id,
            operation="EXECUTE_PHASE",
            idempotency_key=idempotency_key,
        ):
            raise RatioRevisionConflict(expected_revision, head.revision)

        previous = self._repository.get_ratio_runtime(
            execution_id,
            revision=expected_revision,
        )
        records = self._repository.list_ratio_artifacts(execution_id)
        draft = executor.prepare_phase(
            execution,
            previous,
            records,
            actor_id=actor_id,
            idempotency_key=idempotency_key,
        )
        updated = record_phase_execution(previous)
        persisted = self._repository.persist_ratio_transition(
            execution_id,
            previous=previous,
            updated=updated,
            action="EXECUTE_PHASE",
            actor_id=actor_id,
            idempotency_key=idempotency_key,
            artifact_refs=tuple(
                (role, draft.artifact)
                for role in draft.artifact_roles
            ),
        )
        return RatioPhaseExecutionResult(
            execution_state=persisted.execution_state,
            ratio_state=persisted.ratio_state,
            artifact=draft.artifact,
            artifact_roles=draft.artifact_roles,
            created=persisted.created,
        )

    def act(
        self,
        execution_id: str,
        *,
        action: RatioActionKind,
        expected_revision: int,
        actor_id: str,
        idempotency_key: str,
        troia_triggers: frozenset[TroiaTrigger] = frozenset(),
        blocking_code: str | None = None,
        target_phase: RatioPhase | None = None,
    ) -> RatioPersistResult:
        if expected_revision < 0:
            raise RatioActionPayloadError(
                "expected_revision não pode ser negativa."
            )

        previous = self._repository.get_ratio_runtime(
            execution_id,
            revision=expected_revision,
        )

        if action in {
            RatioActionKind.VALIDATE,
            RatioActionKind.VALIDATE_WITH_CAVEAT,
        }:
            self._require_phase_artifact(execution_id, previous)
        elif action in {
            RatioActionKind.VALIDATE_TROIA,
            RatioActionKind.BLOCK_TROIA,
        }:
            self._require_troia_artifact(execution_id, previous)

        if action is RatioActionKind.VALIDATE:
            _reject_extra(action, troia_triggers, blocking_code, target_phase)
            updated = validate_current_phase(previous)
        elif action is RatioActionKind.VALIDATE_WITH_CAVEAT:
            _reject_extra(action, troia_triggers, blocking_code, target_phase)
            updated = validate_current_phase(previous, with_caveat=True)
        elif action is RatioActionKind.ADVANCE:
            _reject_extra(action, troia_triggers, blocking_code, target_phase)
            updated = advance_phase(previous)
        elif action is RatioActionKind.CONFIGURE_TROIA:
            if blocking_code is not None or target_phase is not None:
                raise RatioActionPayloadError(
                    "CONFIGURE_TROIA aceita somente troia_triggers."
                )
            updated = configure_ed_troia(previous, troia_triggers)
        elif action is RatioActionKind.VALIDATE_TROIA:
            _reject_extra(action, troia_triggers, blocking_code, target_phase)
            updated = validate_troia(previous)
        elif action is RatioActionKind.BLOCK_TROIA:
            if troia_triggers or target_phase is not None or not blocking_code:
                raise RatioActionPayloadError(
                    "BLOCK_TROIA exige apenas blocking_code."
                )
            updated = block_troia(
                previous,
                blocking_code=blocking_code,
                catalog=self._hard_stop_catalog,
            )
        elif action is RatioActionKind.RESUME_TROIA:
            _reject_extra(action, troia_triggers, blocking_code, target_phase)
            updated = resume_troia(previous)
        elif action is RatioActionKind.RETURN_AFTER_CHANGE:
            if troia_triggers or blocking_code is not None or target_phase is None:
                raise RatioActionPayloadError(
                    "RETURN_AFTER_CHANGE exige apenas target_phase."
                )
            updated = return_after_substantial_change(
                previous,
                target_phase=target_phase,
            )
        else:  # pragma: no cover
            raise RatioActionPayloadError("Ação RATIO desconhecida.")

        return self._repository.persist_ratio_transition(
            execution_id,
            previous=previous,
            updated=updated,
            action=action.value,
            actor_id=actor_id,
            idempotency_key=idempotency_key,
            operator_decision_code=action.value,
        )

    def finalize(
        self,
        execution_id: str,
        *,
        expected_revision: int,
        expected_version: int,
        actor_id: str,
        idempotency_key: str,
    ) -> RatioFinalizeResult:
        executor = self._require_executor()
        execution = self._repository.get(execution_id)
        head = self._repository.get_ratio_runtime(execution_id)
        if head.revision != expected_revision and not executor.has_prepared(
            execution_id,
            operation="FINALIZE_RATIO",
            idempotency_key=idempotency_key,
        ):
            raise RatioRevisionConflict(expected_revision, head.revision)

        previous = self._repository.get_ratio_runtime(
            execution_id,
            revision=expected_revision,
        )
        updated = finalize_ratio_state(previous)
        records = self._repository.list_ratio_artifacts(execution_id)
        draft = executor.prepare_handoff(
            execution,
            previous,
            records,
            actor_id=actor_id,
            idempotency_key=idempotency_key,
        )
        if execution.stage is ExecutionStage.RATIO_REWORK:
            completion_kind = CommandKind.COMPLETE_RATIO_REWORK
        elif execution.stage is ExecutionStage.RATIO_RUNNING:
            completion_kind = CommandKind.COMPLETE_RATIO
        elif execution.stage is ExecutionStage.RATIO_READY:
            completion_kind = (
                CommandKind.COMPLETE_RATIO_REWORK
                if execution.cerne_artifact is not None
                else CommandKind.COMPLETE_RATIO
            )
        else:
            raise RatioTransitionError(
                f"Finalização RATIO não é permitida em {execution.stage.value}."
            )
        command = Command(
            kind=completion_kind,
            expected_version=expected_version,
            actor_id=actor_id,
            payload={"artifact": draft.artifact},
        )
        persisted = self._repository.persist_ratio_transition(
            execution_id,
            previous=previous,
            updated=updated,
            action="FINALIZE",
            actor_id=actor_id,
            idempotency_key=idempotency_key,
            external_command=command,
            artifact_refs=(("FINAL_HANDOFF", draft.artifact),),
            operator_decision_code="FINALIZE",
        )
        return RatioFinalizeResult(
            execution_state=persisted.execution_state,
            ratio_state=persisted.ratio_state,
            artifact=draft.artifact,
            created=persisted.created,
        )

    def _require_executor(self) -> RatioPhaseExecutor:
        if self._executor is None:
            raise RatioExecutionUnavailable(
                "Executor RATIO não está configurado."
            )
        return self._executor

    def _require_phase_artifact(
        self,
        execution_id: str,
        state: RatioRunState,
    ) -> None:
        if not self._enforce_execution:
            return
        self._require_fresh_role(
            execution_id,
            f"PHASE:{state.current_phase.value}",
        )

    def _require_troia_artifact(
        self,
        execution_id: str,
        state: RatioRunState,
    ) -> None:
        if not self._enforce_execution:
            return
        self._require_fresh_role(
            execution_id,
            f"TROIA:{state.current_phase.value}",
        )

    def _require_fresh_role(
        self,
        execution_id: str,
        role: str,
    ) -> None:
        barrier = self._repository.latest_ratio_execution_barrier(
            execution_id
        )
        revisions = [
            item.revision
            for item in self._repository.list_ratio_artifacts(execution_id)
            if item.role == role
        ]
        if not revisions or max(revisions) <= barrier:
            raise RatioArtifactMissing(
                f"Artefato executado e atual exigido: {role}."
            )


def _reject_extra(
    action: RatioActionKind,
    troia_triggers: frozenset[TroiaTrigger],
    blocking_code: str | None,
    target_phase: RatioPhase | None,
) -> None:
    if troia_triggers or blocking_code is not None or target_phase is not None:
        raise RatioActionPayloadError(
            f"{action.value} não aceita parâmetros adicionais."
        )


def default_ratio_workflow(
    repository: RatioRuntimeRepository,
    *,
    ratio_root: Path,
    executor: RatioPhaseExecutor | None = None,
    enforce_execution: bool = True,
) -> RatioWorkflowService:
    return RatioWorkflowService(
        repository,
        load_hard_stop_catalog(ratio_root),
        executor=executor,
        enforce_execution=enforce_execution,
    )
