"""Camada de aplicação governada que acopla CERNE 0.2 ao estado ATRIO."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from atrio_api.cerne.execution import CerneAuditExecutor
from atrio_api.cerne.persistence import CernePersistResult
from atrio_api.cerne_core.domain import ClientOutput
from atrio_api.cerne_core.provider import ModelProvider
from atrio_api.corpus_intake import EncryptedCorpusStore
from atrio_api.domain import (
    ArtifactRef,
    CerneGate,
    Command,
    CommandKind,
    ExecutionState,
)
from atrio_api.state_machine import TransitionResult


@dataclass(frozen=True, slots=True)
class CerneAuditResult:
    execution_state: ExecutionState
    artifact: ArtifactRef
    gate: CerneGate
    client_output: ClientOutput
    warnings: tuple[str, ...]
    created: bool


class CerneRuntimeRepository(Protocol):
    def get(self, execution_id: str) -> ExecutionState: ...

    def apply(
        self,
        execution_id: str,
        command: Command,
    ) -> TransitionResult: ...

    def apply_cerne_audit(
        self,
        execution_id: str,
        *,
        expected_version: int,
        actor_id: str,
        artifact: ArtifactRef,
        gate: CerneGate,
        reason_code: str | None,
    ) -> CernePersistResult: ...


class CerneWorkflowService:
    def __init__(
        self,
        repository: CerneRuntimeRepository,
        executor: CerneAuditExecutor,
    ) -> None:
        self._repository = repository
        self._executor = executor

    def verify(self) -> None:
        self._executor.verify()

    async def audit(
        self,
        execution_id: str,
        *,
        expected_version: int,
        actor_id: str,
        idempotency_key: str,
    ) -> CerneAuditResult:
        execution = self._repository.get(execution_id)
        draft = await self._executor.prepare(
            execution,
            actor_id=actor_id,
            idempotency_key=idempotency_key,
        )
        persisted = self._repository.apply_cerne_audit(
            execution_id,
            expected_version=expected_version,
            actor_id=actor_id,
            artifact=draft.artifact,
            gate=draft.gate,
            reason_code=(
                None
                if draft.gate is CerneGate.AVANCA
                else f"CERNE_{draft.gate.value}"
            ),
        )
        return CerneAuditResult(
            execution_state=persisted.execution_state,
            artifact=draft.artifact,
            gate=draft.gate,
            client_output=draft.client_output,
            warnings=draft.warnings,
            created=persisted.created,
        )

    def return_to_ratio(
        self,
        execution_id: str,
        *,
        expected_version: int,
        actor_id: str,
        decision_code: str,
    ) -> ExecutionState:
        return self._repository.apply(
            execution_id,
            Command(
                kind=CommandKind.RETURN_TO_RATIO,
                expected_version=expected_version,
                actor_id=actor_id,
                payload={"decision_code": decision_code},
            ),
        ).state

    def reopen_total_block(
        self,
        execution_id: str,
        *,
        expected_version: int,
        actor_id: str,
        decision_code: str,
    ) -> ExecutionState:
        return self._repository.apply(
            execution_id,
            Command(
                kind=CommandKind.REOPEN_TOTAL_BLOCK,
                expected_version=expected_version,
                actor_id=actor_id,
                payload={"decision_code": decision_code},
            ),
        ).state


def default_cerne_workflow(
    repository: CerneRuntimeRepository,
    store: EncryptedCorpusStore,
    provider: ModelProvider,
    *,
    knowledge_root: Path,
) -> CerneWorkflowService:
    return CerneWorkflowService(
        repository,
        CerneAuditExecutor(
            store,
            provider,
            knowledge_root=knowledge_root,
        ),
    )
