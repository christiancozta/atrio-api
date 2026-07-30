#!/usr/bin/env python3
"""Executa o braço ATRIO completo para smoke técnico sob custódia local.

Este runner é deliberadamente recusado fora do pool ``smoke``. As validações
automáticas de fase simulam o operador apenas para provar a integração técnica;
não substituem avaliação humana em calibração ou teste.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from atrio_api.corpus_intake import EncryptedCorpusStore


RUNNER_VERSION = "0.1.0"
OUTPUT_SCHEMA_VERSION = "1.0.0"
DEFAULT_API_URL = "http://127.0.0.1:8080"
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"


class SmokeError(RuntimeError):
    pass


class HttpFailure(SmokeError):
    def __init__(self, status: int, method: str, path: str, body: str):
        super().__init__(f"{method} {path} retornou HTTP {status}: {body[:500]}")
        self.status = status


class ApiClient:
    def __init__(self, base_url: str, *, timeout: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get(self, path: str, *, timeout: float | None = None) -> dict[str, Any]:
        return self._request("GET", path, timeout=timeout)

    def post(
        self,
        path: str,
        payload: dict[str, Any],
        *,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            path,
            payload=payload,
            headers=headers,
            timeout=timeout,
        )

    def upload(
        self,
        path: str,
        content: bytes,
        *,
        headers: dict[str, str],
    ) -> dict[str, Any]:
        resolved = {
            "Content-Type": "text/plain; charset=utf-8",
            "Content-Length": str(len(content)),
            **headers,
        }
        return self._request(
            "POST",
            path,
            raw=content,
            headers=resolved,
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
        raw: bytes | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        if payload is not None and raw is not None:
            raise ValueError("payload e raw são mutuamente exclusivos.")
        body = raw
        resolved_headers = dict(headers or {})
        if payload is not None:
            body = json.dumps(
                payload,
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
            resolved_headers["Content-Type"] = "application/json"
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            headers=resolved_headers,
            method=method,
        )
        try:
            with urlopen(
                request,
                timeout=self.timeout if timeout is None else timeout,
            ) as response:
                data = response.read()
        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise HttpFailure(exc.code, method, path, error_body) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise SmokeError(f"{method} {path} indisponível.") from exc
        try:
            decoded = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SmokeError(f"{method} {path} devolveu JSON inválido.") from exc
        if not isinstance(decoded, dict):
            raise SmokeError(f"{method} {path} não devolveu objeto JSON.")
        return decoded


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Executa o braço ATRIO no pool smoke."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--api-url",
        default=os.environ.get("ATRIO_EVAL_API_URL", DEFAULT_API_URL),
    )
    parser.add_argument(
        "--ollama-url",
        default=os.environ.get("ATRIO_EVAL_OLLAMA_URL", DEFAULT_OLLAMA_URL),
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("ATRIO_EVAL_MODEL", "qwen3:8b"),
    )
    parser.add_argument(
        "--model-digest",
        default=os.environ.get("ATRIO_EVAL_MODEL_DIGEST", ""),
    )
    parser.add_argument(
        "--vault-root",
        type=Path,
        default=Path(
            os.environ.get(
                "ATRIO_EVAL_VAULT_ROOT",
                "var/vault",
            )
        ),
    )
    parser.add_argument(
        "--vault-passphrase-file",
        type=Path,
        default=Path(
            os.environ.get(
                "ATRIO_EVAL_VAULT_PASSPHRASE_FILE",
                "evaluation/_custody/vault_passphrase.txt",
            )
        ),
    )
    parser.add_argument(
        "--candidate-commit",
        default=os.environ.get("ATRIO_EVAL_CANDIDATE_COMMIT", ""),
    )
    parser.add_argument(
        "--num-ctx",
        type=int,
        default=int(os.environ.get("ATRIO_EVAL_NUM_CTX", "40960")),
    )
    parser.add_argument(
        "--num-predict",
        type=int,
        default=int(os.environ.get("ATRIO_EVAL_NUM_PREDICT", "4096")),
    )
    parser.add_argument("--timeout", type=float, default=1800.0)
    args = parser.parse_args()

    pool = os.environ.get("ATRIO_EVAL_POOL", "")
    if pool != "smoke":
        raise SmokeError(
            "Este runner automatiza decisões e só pode operar no pool smoke."
        )
    if not args.candidate_commit or len(args.candidate_commit) != 40:
        raise SmokeError("Commit candidato de 40 caracteres é obrigatório.")
    if args.num_ctx < 1 or not 0 < args.num_predict < args.num_ctx:
        raise SmokeError("Contrato num_ctx/num_predict inválido.")
    input_path = args.input.resolve()
    output_path = args.output.resolve()
    content = input_path.read_bytes()
    try:
        content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SmokeError("O caso smoke deve ser TXT UTF-8.") from exc
    if not content.strip():
        raise SmokeError("O caso smoke está vazio.")

    _verify_model(
        args.ollama_url,
        args.model,
        args.model_digest,
        num_ctx=args.num_ctx,
    )
    client = ApiClient(args.api_url, timeout=args.timeout)
    ready = client.get("/v1/health/ready", timeout=30)
    if ready.get("status") != "ready":
        raise SmokeError("A API não declarou readiness.")

    case_id = _required_environment("ATRIO_EVAL_CASE_ID")
    run_id = _required_environment("ATRIO_EVAL_RUN_ID")
    token = hashlib.sha256(
        f"{case_id}\0{run_id}\0ATRIO".encode("utf-8")
    ).hexdigest()[:24]
    actor = "eval-smoke-operator"

    created = client.post(
        "/v1/executions",
        {
            "tenant_id": "eval-smoke",
            "actor_id": actor,
            "ratio_module": "RI",
            "destination": "PUBLICO",
        },
        headers={"Idempotency-Key": f"create-{token}"},
    )
    execution = _required_object(created, "execution")
    execution_id = _required_text(execution, "execution_id")

    uploaded = client.upload(
        f"/v1/executions/{execution_id}/corpus/documents",
        content,
        headers={
            "Idempotency-Key": f"upload-{token}",
            "X-ATRIO-Expected-Version": str(
                _required_int(execution, "state_version")
            ),
            "X-ATRIO-Actor": actor,
        },
    )
    execution = _required_object(uploaded, "execution")

    processed = client.post(
        f"/v1/executions/{execution_id}/corpus/process",
        {
            "expected_version": _required_int(execution, "state_version"),
            "actor_id": actor,
        },
    )
    execution = _required_object(processed, "execution")
    if processed.get("halted_for_review") is True:
        _write_rater_output(output_path, status="blocked", text=None)
        print(f"execution_id={execution_id}")
        print("blocked=CORPUS_REVIEW")
        return 0

    corpus_final = client.post(
        f"/v1/executions/{execution_id}/corpus/finalize",
        {
            "expected_version": _required_int(execution, "state_version"),
            "actor_id": actor,
        },
    )
    execution = _required_object(corpus_final, "execution")

    ratio_started = client.post(
        f"/v1/executions/{execution_id}/ratio/start",
        {
            "expected_version": _required_int(execution, "state_version"),
            "actor_id": actor,
        },
        headers={"Idempotency-Key": f"ratio-start-{token}"},
    )
    execution = _required_object(ratio_started, "execution")
    macro_version = _required_int(execution, "state_version")
    ratio = _required_object(ratio_started, "ratio")

    while True:
        phase = _required_text(ratio, "current_phase")
        executed = client.post(
            f"/v1/executions/{execution_id}/ratio/execute",
            {
                "expected_revision": _required_int(ratio, "revision"),
                "actor_id": actor,
            },
            headers={"Idempotency-Key": f"execute-{phase}-{token}"},
        )
        ratio = _required_object(executed, "ratio")

        if phase == "RI_03":
            troia = client.post(
                f"/v1/executions/{execution_id}/ratio/actions",
                {
                    "action": "VALIDATE_TROIA",
                    "expected_revision": _required_int(ratio, "revision"),
                    "actor_id": actor,
                },
                headers={"Idempotency-Key": f"troia-{token}"},
            )
            ratio = _required_object(troia, "ratio")

        validated = client.post(
            f"/v1/executions/{execution_id}/ratio/actions",
            {
                "action": "VALIDATE",
                "expected_revision": _required_int(ratio, "revision"),
                "actor_id": actor,
            },
            headers={"Idempotency-Key": f"validate-{phase}-{token}"},
        )
        ratio = _required_object(validated, "ratio")
        phases = ratio.get("phases")
        if not isinstance(phases, list) or not phases:
            raise SmokeError("RATIO não devolveu a sequência de fases.")
        last_phase = _required_text(_as_object(phases[-1]), "phase")
        if phase == last_phase:
            break

        advanced = client.post(
            f"/v1/executions/{execution_id}/ratio/actions",
            {
                "action": "ADVANCE",
                "expected_revision": _required_int(ratio, "revision"),
                "actor_id": actor,
            },
            headers={"Idempotency-Key": f"advance-{phase}-{token}"},
        )
        ratio = _required_object(advanced, "ratio")

    ratio_final = client.post(
        f"/v1/executions/{execution_id}/ratio/finalize",
        {
            "expected_revision": _required_int(ratio, "revision"),
            "expected_version": macro_version,
            "actor_id": actor,
        },
        headers={"Idempotency-Key": f"ratio-final-{token}"},
    )
    execution = _required_object(ratio_final, "execution")

    cerne = client.post(
        f"/v1/executions/{execution_id}/cerne/audit",
        {
            "expected_version": _required_int(execution, "state_version"),
            "actor_id": actor,
        },
        headers={"Idempotency-Key": f"cerne-{token}"},
        timeout=args.timeout,
    )
    execution = _required_object(cerne, "execution")
    gate = _required_text(cerne, "gate")
    if gate != "AVANCA":
        _write_rater_output(output_path, status="blocked", text=None)
        print(f"execution_id={execution_id}")
        print(f"blocked_gate={gate}")
        return 0

    lux = client.post(
        f"/v1/executions/{execution_id}/lux/refine",
        {
            "expected_version": _required_int(execution, "state_version"),
            "actor_id": actor,
            "mode": "PADRAO",
            "data_mode": "PUBLICO",
        },
        headers={"Idempotency-Key": f"lux-{token}"},
        timeout=args.timeout,
    )
    execution = _required_object(lux, "execution")
    artifact = _required_object(lux, "artifact")
    final_text = _export_lux_text(
        execution_id=execution_id,
        artifact=artifact,
        vault_root=args.vault_root.resolve(),
        passphrase_file=args.vault_passphrase_file.resolve(),
    )
    _write_rater_output(output_path, status="completed", text=final_text)

    print(f"runner_version={RUNNER_VERSION}")
    print(f"candidate_commit={args.candidate_commit}")
    print(f"num_ctx={args.num_ctx}")
    print(f"num_predict={args.num_predict}")
    print(f"execution_id={execution_id}")
    print(f"release_id={_required_text(execution, 'release_id', nested='release')}")
    print(f"final_stage={_required_text(execution, 'stage')}")
    print(f"output_sha256={hashlib.sha256(final_text.encode('utf-8')).hexdigest()}")
    return 0


def _verify_model(
    base_url: str,
    model: str,
    expected_digest: str,
    *,
    num_ctx: int,
) -> None:
    client = ApiClient(base_url, timeout=30)
    tags = client.get("/api/tags")
    models = tags.get("models")
    if not isinstance(models, list):
        raise SmokeError("Ollama não devolveu models.")
    for item in models:
        if not isinstance(item, dict):
            continue
        name = item.get("model") or item.get("name")
        if name != model:
            continue
        digest = item.get("digest")
        if not isinstance(digest, str):
            raise SmokeError("Modelo Ollama sem digest.")
        if expected_digest and digest.removeprefix("sha256:") != (
            expected_digest.removeprefix("sha256:")
        ):
            raise SmokeError("Digest do modelo diverge do pré-registro.")
        break
    else:
        raise SmokeError(f"Modelo Ollama ausente: {model}.")

    preflight = client.post(
        "/api/generate",
        {
            "model": model,
            "prompt": "ATRIO_CONTEXT_PREFLIGHT",
            "stream": False,
            "options": {
                "temperature": 0,
                "seed": 0,
                "num_ctx": num_ctx,
                "num_predict": 1,
            },
        },
        timeout=120,
    )
    if not isinstance(preflight.get("prompt_eval_count"), int):
        raise SmokeError("Ollama não devolveu prompt_eval_count no preflight.")
    if not isinstance(preflight.get("eval_count"), int):
        raise SmokeError("Ollama não devolveu eval_count no preflight.")

    running = client.get("/api/ps")
    models = running.get("models")
    if not isinstance(models, list):
        raise SmokeError("Ollama não devolveu modelos carregados em /api/ps.")
    for item in models:
        if not isinstance(item, dict):
            continue
        name = item.get("model") or item.get("name")
        if name not in {model, model.removesuffix(":latest")}:
            continue
        context_length = item.get("context_length")
        if not isinstance(context_length, int) or context_length < num_ctx:
            raise SmokeError(
                "Contexto efetivamente alocado pelo Ollama é menor que num_ctx."
            )
        return
    raise SmokeError("Modelo não apareceu carregado em /api/ps após preflight.")


def _export_lux_text(
    *,
    execution_id: str,
    artifact: dict[str, Any],
    vault_root: Path,
    passphrase_file: Path,
) -> str:
    passphrase = _read_secret(passphrase_file)
    store = EncryptedCorpusStore.from_passphrase(vault_root, passphrase)
    passphrase = ""
    artifact_id = _required_text(artifact, "artifact_id")
    plaintext = store.read_private_record(
        f"artifacts/{execution_id}/{artifact_id}.atrio"
    )
    expected_sha256 = _required_text(artifact, "sha256")
    if hashlib.sha256(plaintext).hexdigest() != expected_sha256:
        raise SmokeError("Hash do artefato LUX diverge do cofre.")
    try:
        bundle = json.loads(plaintext.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SmokeError("Bundle LUX cifrado possui JSON inválido.") from exc
    output = _required_object(_as_object(bundle), "output")
    final_text = _required_text(output, "versao_final_limpa")
    return final_text


def _read_secret(path: Path) -> str:
    try:
        value = path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise SmokeError(f"Arquivo de custódia indisponível: {path}.") from exc
    if not value or "\x00" in value or "\n" in value or "\r" in value:
        raise SmokeError("Arquivo de custódia possui formato inválido.")
    return value


def _write_rater_output(path: Path, *, status: str, text: str | None) -> None:
    payload = {
        "schema_version": OUTPUT_SCHEMA_VERSION,
        "status": status,
        "text": text,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _required_environment(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SmokeError(f"Variável obrigatória ausente: {name}.")
    return value


def _as_object(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SmokeError("Objeto JSON obrigatório ausente.")
    return value


def _required_object(value: dict[str, Any], key: str) -> dict[str, Any]:
    return _as_object(value.get(key))


def _required_text(
    value: dict[str, Any],
    key: str,
    *,
    nested: str | None = None,
) -> str:
    source = _required_object(value, nested) if nested else value
    item = source.get(key)
    if not isinstance(item, str) or not item.strip():
        raise SmokeError(f"Campo textual obrigatório ausente: {key}.")
    return item.strip()


def _required_int(value: dict[str, Any], key: str) -> int:
    item = value.get(key)
    if not isinstance(item, int) or isinstance(item, bool) or item < 0:
        raise SmokeError(f"Campo inteiro obrigatório ausente: {key}.")
    return item


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SmokeError as exc:
        print(f"ERRO_SMOKE: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
