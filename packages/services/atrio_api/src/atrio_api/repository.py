from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Protocol

from atrio_api.domain import Command, ExecutionState
from atrio_api.state_machine import TransitionEvent, TransitionResult, transition


class RepositoryError(RuntimeError):
    pass


class ExecutionNotFound(RepositoryError):
    def __init__(self, execution_id: str):
        super().__init__(f"Execução não encontrada: {execution_id}.")
        self.execution_id = execution_id


class IdempotencyConflict(RepositoryError):
    def __init__(self, idempotency_key: str):
        super().__init__(
            "A chave de idempotência já foi usada com parâmetros diferentes: "
            f"{idempotency_key}."
        )
        self.idempotency_key = idempotency_key


@dataclass(frozen=True, slots=True)
class CreateResult:
    state: ExecutionState
    created: bool


class ExecutionRepository(Protocol):
    def create(
        self,
        state: ExecutionState,
        *,
        idempotency_key: str,
        request_fingerprint: str,
    ) -> CreateResult: ...

    def get(self, execution_id: str) -> ExecutionState: ...

    def apply(self, execution_id: str, command: Command) -> TransitionResult: ...

    def events(self, execution_id: str) -> tuple[TransitionEvent, ...]: ...


class InMemoryExecutionRepository:
    """Referência transacional para testes; o adapter PostgreSQL manterá o contrato."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._states: dict[str, ExecutionState] = {}
        self._events: dict[str, list[TransitionEvent]] = {}
        self._idempotency: dict[tuple[str, str], tuple[str, str]] = {}

    def create(
        self,
        state: ExecutionState,
        *,
        idempotency_key: str,
        request_fingerprint: str,
    ) -> CreateResult:
        with self._lock:
            scoped_key = (state.tenant_id, idempotency_key)
            previous = self._idempotency.get(scoped_key)
            if previous is not None:
                execution_id, fingerprint = previous
                if fingerprint != request_fingerprint:
                    raise IdempotencyConflict(idempotency_key)
                return CreateResult(state=self._states[execution_id], created=False)

            if state.execution_id in self._states:
                raise RepositoryError(
                    f"execution_id já existe: {state.execution_id}."
                )
            self._states[state.execution_id] = state
            self._events[state.execution_id] = []
            self._idempotency[scoped_key] = (
                state.execution_id,
                request_fingerprint,
            )
            return CreateResult(state=state, created=True)

    def get(self, execution_id: str) -> ExecutionState:
        with self._lock:
            try:
                return self._states[execution_id]
            except KeyError as exc:
                raise ExecutionNotFound(execution_id) from exc

    def apply(self, execution_id: str, command: Command) -> TransitionResult:
        with self._lock:
            state = self.get(execution_id)
            result = transition(state, command)
            self._states[execution_id] = result.state
            self._events[execution_id].append(result.event)
            return result

    def events(self, execution_id: str) -> tuple[TransitionEvent, ...]:
        with self._lock:
            if execution_id not in self._events:
                raise ExecutionNotFound(execution_id)
            return tuple(self._events[execution_id])
