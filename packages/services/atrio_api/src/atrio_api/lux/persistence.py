from __future__ import annotations

from dataclasses import dataclass

from atrio_api.domain import ExecutionState


@dataclass(frozen=True, slots=True)
class LuxPersistResult:
    execution_state: ExecutionState
    created: bool
