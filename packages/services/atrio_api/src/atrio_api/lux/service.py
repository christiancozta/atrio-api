"""Camada de aplicação governada do LUX 6.0.0."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from atrio_api.corpus_intake import EncryptedCorpusStore
from atrio_api.domain import ArtifactRef, ExecutionState
from atrio_api.lux.execution import (
    LuxDataMode,
    LuxExecutor,
    LuxMode,
    LuxOutput,
    LuxProvider,
)
from atrio_api.lux.persistence import LuxPersistResult


@dataclass(frozen=True, slots=True)
class LuxRefinementResult:
    execution_state: ExecutionState
    artifact: ArtifactRef
    output: LuxOutput
    mode: str
    data_mode: str
    profile: str | None
    privacy_applied: bool
    suppression_reinforced: bool
    created: bool


class LuxRuntimeRepository(Protocol):
    def get(self, execution_id: str) -> ExecutionState: ...

    def apply_lux_refinement(
        self,
        execution_id: str,
        *,
        expected_version: int,
        actor_id: str,
        artifact: ArtifactRef,
    ) -> LuxPersistResult: ...


class LuxWorkflowService:
    def __init__(
        self,
        repository: LuxRuntimeRepository,
        executor: LuxExecutor,
    ) -> None:
        self._repository = repository
        self._executor = executor

    def verify(self) -> None:
        self._executor.verify()

    def refine(
        self,
        execution_id: str,
        *,
        expected_version: int,
        actor_id: str,
        idempotency_key: str,
        mode: str = LuxMode.PADRAO,
        profile: str | None = None,
        data_mode: str | None = None,
    ) -> LuxRefinementResult:
        execution = self._repository.get(execution_id)
        draft = self._executor.prepare(
            execution,
            actor_id=actor_id,
            idempotency_key=idempotency_key,
            mode=mode,
            profile=profile,
            data_mode=data_mode,
        )
        persisted = self._repository.apply_lux_refinement(
            execution_id,
            expected_version=expected_version,
            actor_id=actor_id,
            artifact=draft.artifact,
        )
        return LuxRefinementResult(
            execution_state=persisted.execution_state,
            artifact=draft.artifact,
            output=draft.output,
            mode=draft.mode,
            data_mode=draft.data_mode,
            profile=draft.profile,
            privacy_applied=draft.privacy_applied,
            suppression_reinforced=draft.suppression_reinforced,
            created=persisted.created,
        )


def default_lux_workflow(
    repository: LuxRuntimeRepository,
    store: EncryptedCorpusStore,
    provider: LuxProvider,
    *,
    model: str,
    knowledge_root: Path,
    pii_source: Path,
) -> LuxWorkflowService:
    return LuxWorkflowService(
        repository,
        LuxExecutor(
            store,
            provider,
            model=model,
            knowledge_root=knowledge_root,
            pii_source=pii_source,
        ),
    )
