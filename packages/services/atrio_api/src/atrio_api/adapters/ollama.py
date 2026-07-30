"""Adapter governado para inferência local via Ollama.

O adapter transporta conteúdo sigiloso somente entre o processo da API e o
servidor configurado. O resultado separa o texto de metadados seguros; a
resposta HTTP bruta nunca integra o contrato público.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import hashlib
import json
import re
import time
from typing import Any
from urllib.parse import urlsplit

import httpx


OLLAMA_ADAPTER_VERSION = "0.2.0"
DEFAULT_NUM_CTX = 40_960
DEFAULT_NUM_PREDICT = 4_096
_TOKENIZATION_OVERHEAD_RESERVE = 256
_MODEL_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/+:@-]{0,199}")
_RETRYABLE_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})
_ALLOWED_OPTIONS = frozenset(
    {
        "temperature",
        "seed",
        "num_ctx",
        "num_predict",
        "top_k",
        "top_p",
        "min_p",
        "repeat_last_n",
        "repeat_penalty",
        "stop",
    }
)
_DEFAULT_OPTIONS: dict[str, Any] = {
    "temperature": 0.0,
    "seed": 0,
    "num_ctx": DEFAULT_NUM_CTX,
    "num_predict": DEFAULT_NUM_PREDICT,
}


class OllamaAdapterError(RuntimeError):
    """Falha controlada do provedor local."""


class OllamaModelUnavailable(OllamaAdapterError):
    """O servidor está ativo, mas o modelo solicitado não está instalado."""


class OllamaProtocolError(OllamaAdapterError):
    """O servidor respondeu fora do contrato esperado."""


@dataclass(frozen=True, slots=True)
class ModelIdentity:
    """Identidade imutável do modelo instalado."""

    name: str
    digest: str


@dataclass(frozen=True, slots=True)
class InferenceMetadata:
    """Metadados que podem integrar a trilha segura do ATRIO."""

    adapter_version: str
    model: str
    model_digest: str
    prompt_sha256: str
    response_sha256: str
    options_sha256: str
    prompt_chars: int
    response_chars: int
    total_duration_ns: int | None = None
    load_duration_ns: int | None = None
    prompt_eval_count: int | None = None
    eval_count: int | None = None
    prompt_token_upper_bound: int | None = None
    context_headroom_tokens: int | None = None
    generation_attempts: int = 1


@dataclass(frozen=True, slots=True)
class InferenceResult:
    """Texto confidencial e metadados seguros em campos separados."""

    content: str
    metadata: InferenceMetadata


class OllamaAdapter:
    """Cliente síncrono, determinístico e sem telemetria para Ollama."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        *,
        connect_timeout_seconds: float = 5.0,
        read_timeout_seconds: float = 300.0,
        max_prompt_chars: int = 1_000_000,
        max_retries: int = 2,
        default_options: Mapping[str, Any] | None = None,
        client: httpx.Client | None = None,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self._base_url = _validate_base_url(base_url)
        if connect_timeout_seconds <= 0 or read_timeout_seconds <= 0:
            raise ValueError("Timeouts do Ollama devem ser positivos.")
        if max_prompt_chars < 1:
            raise ValueError("Limite de prompt deve ser positivo.")
        if not 0 <= max_retries <= 5:
            raise ValueError("Tentativas adicionais devem ficar entre 0 e 5.")
        self._max_prompt_chars = max_prompt_chars
        self._max_retries = max_retries
        self._default_options = _validated_options(default_options)
        self._sleeper = sleeper
        self._owns_client = client is None
        self._client = client or httpx.Client(
            base_url=self._base_url,
            timeout=httpx.Timeout(
                read_timeout_seconds,
                connect=connect_timeout_seconds,
            ),
            follow_redirects=False,
            trust_env=False,
            headers={
                "Accept": "application/json",
                "User-Agent": f"atrio-ollama-adapter/{OLLAMA_ADAPTER_VERSION}",
            },
        )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> OllamaAdapter:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def healthcheck(self) -> bool:
        data = self._request_json("GET", "/api/tags")
        _parse_models(data)
        return True

    def model_identity(self, model: str) -> ModelIdentity:
        requested = _validate_model(model)
        models = _parse_models(self._request_json("GET", "/api/tags"))
        for identity in models:
            if identity.name == requested:
                return identity
            if ":" not in requested and identity.name == f"{requested}:latest":
                return identity
        raise OllamaModelUnavailable(
            f"Modelo Ollama não instalado: {requested}."
        )

    def generate(
        self,
        prompt: str,
        *,
        model: str,
        system: str | None = None,
        options: Mapping[str, Any] | None = None,
        format_schema: Mapping[str, Any] | None = None,
    ) -> InferenceResult:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt não pode ser vazio.")
        if len(prompt) > self._max_prompt_chars:
            raise ValueError("Prompt excede o limite configurado.")
        if system is not None and (
            not isinstance(system, str) or not system.strip()
        ):
            raise ValueError("Instrução de sistema deve ser texto não vazio.")

        requested_model = _validate_model(model)
        governed_options = _validated_options(
            options,
            defaults=self._default_options,
        )
        prompt_token_upper_bound = _prompt_token_upper_bound(
            prompt,
            system=system,
            format_schema=format_schema,
        )
        num_ctx = governed_options["num_ctx"]
        num_predict = governed_options["num_predict"]
        if (
            prompt_token_upper_bound
            + num_predict
            + _TOKENIZATION_OVERHEAD_RESERVE
            > num_ctx
        ):
            raise ValueError(
                "Prompt excede o orçamento de contexto sob o limite "
                "conservador pré-inferência."
            )
        identity = self.model_identity(requested_model)
        payload: dict[str, Any] = {
            "model": identity.name,
            "prompt": prompt,
            "stream": False,
            "options": governed_options,
        }
        if system is not None:
            payload["system"] = system
        if format_schema is not None:
            payload["format"] = _json_object(format_schema, "schema de saída")

        data, generation_attempts = self._request_json_with_attempts(
            "POST",
            "/api/generate",
            json=payload,
        )
        content = data.get("response")
        response_model = data.get("model")
        if not isinstance(content, str) or not content:
            raise OllamaProtocolError(
                "Ollama respondeu sem texto no campo 'response'."
            )
        if not isinstance(response_model, str) or not response_model:
            raise OllamaProtocolError(
                "Ollama respondeu sem identidade de modelo."
            )
        if response_model not in {identity.name, _without_latest(identity.name)}:
            raise OllamaProtocolError(
                "Modelo respondente diverge do modelo validado."
            )
        prompt_eval_count = _required_nonnegative_int(
            data,
            "prompt_eval_count",
        )
        eval_count = _required_nonnegative_int(data, "eval_count")
        context_headroom_tokens = num_ctx - prompt_eval_count - num_predict
        if context_headroom_tokens < 0:
            raise OllamaProtocolError(
                "Ollama processou entrada incompatível com o orçamento "
                "num_ctx/num_predict congelado."
            )
        if eval_count > num_predict:
            raise OllamaProtocolError(
                "Ollama excedeu o teto num_predict congelado."
            )
        if data.get("done_reason") == "length":
            raise OllamaProtocolError(
                "Ollama atingiu o teto de saída; resultado truncado recusado."
            )

        metadata = InferenceMetadata(
            adapter_version=OLLAMA_ADAPTER_VERSION,
            model=identity.name,
            model_digest=identity.digest,
            prompt_sha256=_text_sha256(prompt),
            response_sha256=_text_sha256(content),
            options_sha256=_json_sha256(governed_options),
            prompt_chars=len(prompt),
            response_chars=len(content),
            total_duration_ns=_optional_nonnegative_int(
                data, "total_duration"
            ),
            load_duration_ns=_optional_nonnegative_int(
                data, "load_duration"
            ),
            prompt_eval_count=prompt_eval_count,
            eval_count=eval_count,
            prompt_token_upper_bound=prompt_token_upper_bound,
            context_headroom_tokens=context_headroom_tokens,
            generation_attempts=generation_attempts,
        )
        return InferenceResult(content=content, metadata=metadata)

    def _request_json(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        data, _ = self._request_json_with_attempts(method, path, **kwargs)
        return data

    def _request_json_with_attempts(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> tuple[dict[str, Any], int]:
        for attempt in range(self._max_retries + 1):
            try:
                response = self._client.request(method, path, **kwargs)
                if (
                    response.status_code in _RETRYABLE_STATUS_CODES
                    and attempt < self._max_retries
                ):
                    self._sleeper(0.25 * (2**attempt))
                    continue
                response.raise_for_status()
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                if attempt < self._max_retries:
                    self._sleeper(0.25 * (2**attempt))
                    continue
                raise OllamaAdapterError(
                    "Ollama local indisponível após tentativas controladas."
                ) from exc
            except httpx.HTTPStatusError as exc:
                raise OllamaAdapterError(
                    f"Ollama retornou HTTP {exc.response.status_code}."
                ) from exc

            try:
                data = response.json()
            except (ValueError, json.JSONDecodeError) as exc:
                raise OllamaProtocolError(
                    "Ollama devolveu JSON inválido."
                ) from exc
            if not isinstance(data, dict):
                raise OllamaProtocolError(
                    "Ollama devolveu envelope JSON inválido."
                )
            return data, attempt + 1
        raise AssertionError("Laço de tentativas do Ollama terminou inválido.")


def _validate_base_url(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("URL base do Ollama não pode ser vazia.")
    parsed = urlsplit(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("URL base do Ollama deve usar HTTP ou HTTPS.")
    if parsed.username or parsed.password:
        raise ValueError("Credenciais não podem integrar a URL do Ollama.")
    if parsed.query or parsed.fragment:
        raise ValueError("URL base do Ollama não aceita query ou fragmento.")
    if parsed.path not in {"", "/"}:
        raise ValueError("URL base do Ollama não aceita caminho.")
    return value.strip().rstrip("/")


def _validate_model(value: str) -> str:
    if not isinstance(value, str) or not _MODEL_PATTERN.fullmatch(value):
        raise ValueError("Identificador de modelo Ollama inválido.")
    return value


def _parse_models(data: Mapping[str, Any]) -> tuple[ModelIdentity, ...]:
    raw_models = data.get("models")
    if not isinstance(raw_models, list):
        raise OllamaProtocolError("Ollama não devolveu a lista de modelos.")
    parsed: list[ModelIdentity] = []
    for item in raw_models:
        if not isinstance(item, dict):
            raise OllamaProtocolError("Entrada inválida na lista de modelos.")
        name = item.get("model") or item.get("name")
        digest = item.get("digest")
        if (
            not isinstance(name, str)
            or not _MODEL_PATTERN.fullmatch(name)
            or not isinstance(digest, str)
            or not re.fullmatch(r"sha256:[0-9a-f]{64}|[0-9a-f]{64}", digest)
        ):
            raise OllamaProtocolError("Identidade de modelo Ollama inválida.")
        parsed.append(ModelIdentity(name=name, digest=digest))
    return tuple(parsed)


def _validated_options(
    options: Mapping[str, Any] | None,
    *,
    defaults: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    governed = dict(_DEFAULT_OPTIONS if defaults is None else defaults)
    if options is not None:
        if not isinstance(options, Mapping):
            raise ValueError("Opções do Ollama devem ser um mapa.")
        unknown = set(options) - _ALLOWED_OPTIONS
        if unknown:
            names = ", ".join(sorted(str(item) for item in unknown))
            raise ValueError(f"Opções Ollama não permitidas: {names}.")
        governed.update(options)
    governed = _json_object(governed, "opções")
    for name in ("num_ctx", "num_predict"):
        value = governed.get(name)
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ValueError(f"Opção Ollama {name} deve ser inteiro positivo.")
    if governed["num_predict"] >= governed["num_ctx"]:
        raise ValueError("num_predict deve ser menor que num_ctx.")
    return governed


def _prompt_token_upper_bound(
    prompt: str,
    *,
    system: str | None,
    format_schema: Mapping[str, Any] | None,
) -> int:
    fragments = [prompt]
    if system is not None:
        fragments.append(system)
    if format_schema is not None:
        fragments.append(
            json.dumps(
                dict(format_schema),
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
                sort_keys=True,
            )
        )
    return sum(len(fragment.encode("utf-8")) for fragment in fragments)


def _json_object(
    value: Mapping[str, Any],
    label: str,
) -> dict[str, Any]:
    try:
        canonical = json.dumps(
            dict(value),
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        decoded = json.loads(canonical)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label.capitalize()} não é JSON válido.") from exc
    if not isinstance(decoded, dict):
        raise ValueError(f"{label.capitalize()} deve ser um objeto JSON.")
    return decoded


def _json_sha256(value: Mapping[str, Any]) -> str:
    canonical = json.dumps(
        dict(value),
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _optional_nonnegative_int(
    data: Mapping[str, Any],
    key: str,
) -> int | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise OllamaProtocolError(f"Métrica Ollama inválida: {key}.")
    return value


def _required_nonnegative_int(
    data: Mapping[str, Any],
    key: str,
) -> int:
    value = _optional_nonnegative_int(data, key)
    if value is None:
        raise OllamaProtocolError(f"Métrica Ollama obrigatória ausente: {key}.")
    return value


def _without_latest(model: str) -> str:
    return model.removesuffix(":latest")
