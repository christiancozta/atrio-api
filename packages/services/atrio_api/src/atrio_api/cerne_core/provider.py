from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class ProviderError(RuntimeError):
    pass


class ProviderNotConfiguredError(ProviderError):
    pass


class ProviderRateLimitError(ProviderError):
    pass


@dataclass(frozen=True, slots=True)
class StageCallResult(Generic[T]):
    parsed: T
    response_id: str
    model: str


class ModelProvider(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def configured(self) -> bool: ...

    @property
    def model(self) -> str: ...

    async def run(
        self,
        *,
        stage: str,
        instructions: str,
        payload: dict,
        response_model: type[T],
    ) -> StageCallResult[T]: ...


class UnavailableProvider:
    def __init__(self, model: str, *, credential_name: str = "ATRIO_OLLAMA_MODEL"):
        self._model = model
        self._credential_name = credential_name

    @property
    def name(self) -> str:
        return "atrio-unavailable"

    @property
    def configured(self) -> bool:
        return False

    @property
    def model(self) -> str:
        return self._model

    async def run(
        self,
        *,
        stage: str,
        instructions: str,
        payload: dict,
        response_model: type[T],
    ) -> StageCallResult[T]:
        del stage, instructions, payload, response_model
        raise ProviderNotConfiguredError(
            f"{self._credential_name} não configurado; a auditoria não pode ser executada."
        )
