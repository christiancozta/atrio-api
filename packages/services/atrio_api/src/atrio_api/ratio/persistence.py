"""Contratos de persistência do runtime interno do RATIO."""

from __future__ import annotations

from dataclasses import dataclass

from atrio_api.domain import ArtifactRef, ExecutionState
from atrio_api.ratio.state import RatioRunState
from atrio_api.repository import RepositoryError


class RatioRuntimeNotFound(RepositoryError):
    def __init__(self, execution_id: str):
        super().__init__(f"Runtime RATIO não encontrado: {execution_id}.")
        self.execution_id = execution_id


class RatioRuntimeAlreadyStarted(RepositoryError):
    def __init__(self, execution_id: str):
        super().__init__(f"Runtime RATIO já iniciado: {execution_id}.")
        self.execution_id = execution_id


class RatioRevisionConflict(RepositoryError):
    def __init__(self, expected: int, actual: int):
        super().__init__(
            f"Conflito de revisão RATIO: esperada {expected}, atual {actual}."
        )
        self.expected = expected
        self.actual = actual


class RatioPersistenceIntegrityError(RepositoryError):
    pass


@dataclass(frozen=True, slots=True)
class RatioRuntimeStartResult:
    execution_state: ExecutionState
    ratio_state: RatioRunState
    created: bool


@dataclass(frozen=True, slots=True)
class RatioPersistResult:
    execution_state: ExecutionState
    ratio_state: RatioRunState
    created: bool


@dataclass(frozen=True, slots=True)
class RatioArtifactRecord:
    revision: int
    role: str
    artifact: ArtifactRef
