from __future__ import annotations

import hashlib
import json
from uuid import uuid4

from atrio_api.domain import (
    Command,
    CreateExecutionRequest,
    ExecutionState,
    ReleaseEnvelope,
)
from atrio_api.repository import (
    CreateResult,
    ExecutionRepository,
)
from atrio_api.state_machine import TransitionResult
from atrio_api.state_machine import TransitionEvent


class ExecutionService:
    def __init__(self, repository: ExecutionRepository):
        self._repository = repository

    def create(
        self,
        request: CreateExecutionRequest,
        release: ReleaseEnvelope,
    ) -> CreateResult:
        state = ExecutionState(
            execution_id=str(uuid4()),
            tenant_id=request.tenant_id,
            created_by=request.actor_id,
            ratio_module=request.ratio_module,
            destination=request.destination,
            release=release,
        )
        return self._repository.create(
            state,
            idempotency_key=request.idempotency_key,
            request_fingerprint=_fingerprint(request, release),
        )

    def get(self, execution_id: str) -> ExecutionState:
        return self._repository.get(execution_id)

    def command(
        self,
        execution_id: str,
        command: Command,
    ) -> TransitionResult:
        return self._repository.apply(execution_id, command)

    def events(self, execution_id: str) -> tuple[TransitionEvent, ...]:
        return self._repository.events(execution_id)


def _fingerprint(
    request: CreateExecutionRequest,
    release: ReleaseEnvelope,
) -> str:
    canonical = json.dumps(
        {
            "tenant_id": request.tenant_id,
            "actor_id": request.actor_id,
            "ratio_module": request.ratio_module.value,
            "destination": request.destination.value,
            "input_artifact_id": request.input_artifact_id,
            "release_id": release.release_id,
        },
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
