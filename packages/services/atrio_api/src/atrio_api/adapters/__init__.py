"""Adaptadores locais e substituíveis da API ATRIO."""

from atrio_api.adapters.ollama import (
    OLLAMA_ADAPTER_VERSION,
    InferenceMetadata,
    InferenceResult,
    ModelIdentity,
    OllamaAdapter,
    OllamaAdapterError,
    OllamaModelUnavailable,
    OllamaProtocolError,
)

__all__ = [
    "OLLAMA_ADAPTER_VERSION",
    "InferenceMetadata",
    "InferenceResult",
    "ModelIdentity",
    "OllamaAdapter",
    "OllamaAdapterError",
    "OllamaModelUnavailable",
    "OllamaProtocolError",
]
