#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATRIO Evaluation Harness

Automatiza, sem alterar o desenho metodológico:
- inicialização do experimento;
- congelamento local verificável dos artefatos;
- captura de commit/estado do repositório;
- hashes SHA-256;
- manifesto de pré-registro;
- geração opcional de requisição RFC 3161 (.tsq) via OpenSSL;
- cadastro de casos em smoke/calibration/test;
- prevenção de reutilização de casos "queimados";
- execução dos braços automatizados A0-A9 por comandos configuráveis;
- reserva explícita de A10 para o comparador humano;
- captura de stdout/stderr, duração, exit code e hashes;
- cegamento com permutação independente por caso;
- custódia separada do mapa braço↔blind_id;
- criação de pacotes cegos para avaliadores;
- validação de JSONs contra o JSON Schema;
- log encadeado por hash;
- auditoria de integridade do experimento.

O script NÃO decide:
- hipóteses;
- desfechos;
- limiares;
- regras de severidade;
- tamanho amostral;
- conteúdo dos braços;
- plano estatístico.

Esses elementos devem vir do protocolo pré-registrado.

Python: 3.11+
Dependência obrigatória: jsonschema
Dependência opcional: OpenSSL CLI, apenas para gerar .tsq RFC 3161.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import datetime as dt
import hashlib
import hmac
import json
import os
import random
import secrets
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any

HARNESS_VERSION = "0.2.0"
PROTOCOL_ARMS = tuple(f"A{i}" for i in range(11))
AUTOMATED_ARMS = tuple(f"A{i}" for i in range(10))
HUMAN_ARM = "A10"
DEFAULT_ARMS = PROTOCOL_ARMS
POOLS = ("smoke", "calibration", "test")


class HarnessError(RuntimeError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as tmp:
        tmp.write(data)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = Path(tmp.name)
    os.replace(tmp_path, path)


def atomic_write_text(path: Path, text: str) -> None:
    atomic_write_bytes(path, text.encode("utf-8"))


def write_json(path: Path, value: Any) -> None:
    atomic_write_bytes(path, canonical_json_bytes(value) + b"\n")


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HarnessError(f"Arquivo não encontrado: {path}") from exc
    except json.JSONDecodeError as exc:
        raise HarnessError(f"JSON inválido em {path}: {exc}") from exc


def resolve_existing(path: str | Path) -> Path:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise HarnessError(f"Caminho não existe: {p}")
    return p


def run_process(
    argv: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout: float | None = None,
) -> dict[str, Any]:
    start = time.perf_counter()
    started_at = utc_now()
    try:
        proc = subprocess.run(
            argv,
            cwd=str(cwd) if cwd else None,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        timed_out = False
        return_code = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        return_code = None
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
    elapsed = time.perf_counter() - start
    return {
        "started_at": started_at,
        "finished_at": utc_now(),
        "duration_ms": round(elapsed * 1000, 3),
        "timed_out": timed_out,
        "return_code": return_code,
        "stdout": stdout,
        "stderr": stderr,
    }


def git_info(repo: Path) -> dict[str, Any]:
    def git(*args: str) -> str:
        result = run_process(["git", *args], cwd=repo)
        if result["return_code"] != 0:
            raise HarnessError(
                f"Falha no Git: git {' '.join(args)}\n{result['stderr'].strip()}"
            )
        return result["stdout"].strip()

    inside = git("rev-parse", "--is-inside-work-tree")
    if inside.lower() != "true":
        raise HarnessError(f"Não é repositório Git: {repo}")

    status = git("status", "--porcelain=v1")
    return {
        "repo": str(repo.resolve()),
        "commit": git("rev-parse", "HEAD"),
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "describe": git("describe", "--always", "--dirty", "--tags"),
        "dirty": bool(status),
        "status_porcelain": status.splitlines() if status else [],
        "captured_at": utc_now(),
    }


def load_config(root: Path) -> dict[str, Any]:
    path = root / "harness_config.json"
    config = read_json(path)
    if not isinstance(config, dict):
        raise HarnessError("harness_config.json deve conter um objeto JSON.")
    arms = config.get("arms")
    if not isinstance(arms, dict):
        raise HarnessError("harness_config.json deve declarar arms como objeto.")
    unknown = set(arms) - set(PROTOCOL_ARMS)
    if unknown:
        raise HarnessError(
            "Braços fora do protocolo A0-A10: " + ", ".join(sorted(unknown))
        )
    return config


def append_audit_event(
    root: Path, event_type: str, payload: dict[str, Any]
) -> dict[str, Any]:
    audit_dir = root / "_audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    log_path = audit_dir / "events.jsonl"
    head_path = audit_dir / "HEAD"

    prev_hash = (
        head_path.read_text(encoding="utf-8").strip()
        if head_path.exists()
        else "0" * 64
    )
    event = {
        "event_id": str(uuid.uuid4()),
        "timestamp": utc_now(),
        "event_type": event_type,
        "payload": payload,
        "prev_hash": prev_hash,
    }
    event_hash = sha256_bytes(canonical_json_bytes(event))
    event["event_hash"] = event_hash

    with log_path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())

    atomic_write_text(head_path, event_hash + "\n")
    return event


def verify_audit_chain(root: Path) -> list[str]:
    errors: list[str] = []
    log_path = root / "_audit" / "events.jsonl"
    head_path = root / "_audit" / "HEAD"

    if not log_path.exists():
        return ["Log de auditoria ausente."]

    expected_prev = "0" * 64
    last_hash = expected_prev
    with log_path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"events.jsonl:{line_no}: JSON inválido")
                continue

            event_hash = event.get("event_hash")
            stripped = dict(event)
            stripped.pop("event_hash", None)
            calculated = sha256_bytes(canonical_json_bytes(stripped))

            if event.get("prev_hash") != expected_prev:
                errors.append(f"events.jsonl:{line_no}: prev_hash inválido")
            if event_hash != calculated:
                errors.append(f"events.jsonl:{line_no}: event_hash inválido")

            expected_prev = event_hash or calculated
            last_hash = expected_prev

    if head_path.exists():
        head = head_path.read_text(encoding="utf-8").strip()
        if head != last_hash:
            errors.append("HEAD do log não coincide com o último evento.")
    else:
        errors.append("HEAD do log ausente.")

    return errors


def init_experiment(args: argparse.Namespace) -> None:
    root = Path(args.root).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    dirs = [
        "_audit",
        "_custody",
        "_freeze",
        "cases/smoke",
        "cases/calibration",
        "cases/test",
        "runs/smoke",
        "runs/calibration",
        "runs/test",
        "rater_packets",
        "validation",
    ]
    for d in dirs:
        (root / d).mkdir(parents=True, exist_ok=True)

    config_path = root / "harness_config.json"
    if not config_path.exists():
        config = {
            "harness_version": HARNESS_VERSION,
            "arms": {
                arm: {
                    "enabled": False,
                    "kind": "human" if arm == HUMAN_ARM else "automated",
                    "command": "",
                    "timeout_seconds": 1800,
                    "env": {},
                }
                for arm in DEFAULT_ARMS
            },
            "execution": {
                "working_directory": ".",
                "output_filename": "output.json",
                "stdout_filename": "stdout.txt",
                "stderr_filename": "stderr.txt",
                "metadata_filename": "execution.json",
                "output_schema": "prereg/arm_output_schema_1.0.0.json",
                "gate": {
                    "enabled": False,
                    "freeze_id": None,
                    "require_external_timestamp": True,
                },
            },
            "custody": {
                "blind_id_prefix": "OUT",
            },
            "notes": {
                "command_placeholders": [
                    "{case_dir}",
                    "{case_id}",
                    "{pool}",
                    "{arm}",
                    "{run_dir}",
                    "{input_path}",
                    "{output_path}",
                ],
                "contract": (
                    "Cada comando de braço deve produzir o output final no caminho "
                    "fornecido por {output_path}. O harness não define a lógica do braço."
                ),
            },
        }
        write_json(config_path, config)

    gitignore = root / ".gitignore"
    if not gitignore.exists():
        atomic_write_text(
            gitignore,
            "_audit/\n"
            "_custody/\n"
            "_freeze/\n"
            "cases/\n"
            "rater_packets/\n"
            "runs/\n"
            "validation/\n"
            "evidence/\n"
            "*.tsr\n"
            "__pycache__/\n",
        )

    append_audit_event(root, "INIT", {"harness_version": HARNESS_VERSION})
    print(root)


def copy_and_hash(source: Path, destination: Path) -> dict[str, Any]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return {
        "name": destination.name,
        "path": str(destination),
        "sha256": sha256_file(destination),
        "size_bytes": destination.stat().st_size,
    }


def copy_path_and_hash(
    source: Path,
    destination_root: Path,
) -> list[dict[str, Any]]:
    if source.is_symlink():
        raise HarnessError(f"Symlink não permitido no freeze: {source}")
    if source.is_file():
        return [copy_and_hash(source, destination_root / source.name)]
    if not source.is_dir():
        raise HarnessError(f"Artefato inválido para freeze: {source}")
    copied: list[dict[str, Any]] = []
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise HarnessError(f"Symlink não permitido no freeze: {path}")
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(source)
        metadata = copy_and_hash(path, destination_root / source.name / relative)
        metadata["path"] = str(
            (destination_root / source.name / relative).relative_to(
                destination_root.parent
            )
        ).replace("\\", "/")
        copied.append(metadata)
    return copied


def _jsonschema_module() -> Any:
    try:
        import jsonschema  # type: ignore
    except ImportError as exc:
        raise HarnessError(
            "jsonschema é dependência obrigatória do instrumento."
        ) from exc
    return jsonschema


def validate_json_schema_meta(schema_path: Path) -> None:
    jsonschema = _jsonschema_module()
    schema = read_json(schema_path)
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)


def validate_json_instance(schema_path: Path, instance_path: Path) -> None:
    jsonschema = _jsonschema_module()
    schema = read_json(schema_path)
    instance = read_json(instance_path)
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    errors = sorted(
        cls(schema).iter_errors(instance),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        rendered = "; ".join(
            (
                "/".join(map(str, error.absolute_path)) or "<root>"
            )
            + f": {error.message}"
            for error in errors
        )
        raise HarnessError(f"Output incompatível com o schema: {rendered}")


def create_rfc3161_query(manifest_path: Path, out_path: Path) -> dict[str, Any]:
    openssl = shutil.which("openssl")
    if not openssl:
        return {"created": False, "reason": "OpenSSL não encontrado."}

    result = run_process(
        [
            openssl,
            "ts",
            "-query",
            "-data",
            str(manifest_path),
            "-sha256",
            "-cert",
            "-out",
            str(out_path),
        ]
    )
    if result["return_code"] != 0:
        return {
            "created": False,
            "reason": result["stderr"].strip() or "Falha no OpenSSL.",
        }
    return {
        "created": True,
        "path": str(out_path),
        "sha256": sha256_file(out_path),
        "note": (
            "Este .tsq é apenas a requisição. O congelamento externo exige "
            "enviá-la a uma TSA RFC 3161 e preservar a resposta .tsr."
        ),
    }


def freeze(args: argparse.Namespace) -> None:
    root = resolve_existing(args.root)
    package = resolve_existing(args.package)
    repo = resolve_existing(args.repo)

    if not package.is_dir():
        raise HarnessError("--package deve apontar para um diretório.")
    package_manifest_path = package / "package_manifest.json"
    package_manifest = read_json(package_manifest_path)
    if package_manifest.get("status") != "READY_TO_FREEZE":
        raise HarnessError(
            "Pacote metodológico não está READY_TO_FREEZE; decisões abertas "
            "impedem o congelamento."
        )
    dataset_schema = package / "dataset_schema.json"
    example_record = package / "example_record.json"
    validate_json_schema_meta(dataset_schema)
    validate_json_instance(dataset_schema, example_record)

    git = git_info(repo)
    if git["dirty"]:
        raise HarnessError(
            "Repositório está dirty. Freeze exige commit exato e worktree limpo."
        )

    freeze_id = args.freeze_id or dt.datetime.now(
        dt.timezone.utc
    ).strftime("%Y%m%dT%H%M%SZ")
    freeze_dir = root / "_freeze" / freeze_id
    if freeze_dir.exists():
        raise HarnessError(f"Freeze já existe: {freeze_dir}")
    freeze_dir.mkdir(parents=True)

    files = copy_path_and_hash(package, freeze_dir / "methodology")
    for instrument in args.instrument:
        files.extend(
            copy_path_and_hash(
                resolve_existing(instrument),
                freeze_dir / "instrument",
            )
        )

    archive_path = freeze_dir / "candidate_source.tar"
    archive = run_process(
        [
            "git",
            "archive",
            "--format=tar",
            "-o",
            str(archive_path),
            git["commit"],
        ],
        cwd=repo,
    )
    if archive["return_code"] != 0:
        raise HarnessError(
            "Falha ao exportar candidato: " + archive["stderr"].strip()
        )
    files.append(
        {
            "name": archive_path.name,
            "path": archive_path.name,
            "sha256": sha256_file(archive_path),
            "size_bytes": archive_path.stat().st_size,
        }
    )

    manifest = {
        "freeze_id": freeze_id,
        "created_at": utc_now(),
        "harness_version": HARNESS_VERSION,
        "methodological_note": (
            "Este manifesto captura artefatos locais. A demonstração de anterioridade "
            "exige depósito/carimbo externo que o autor não controle."
        ),
        "git": git,
        "methodology_package_sha256": sha256_file(package_manifest_path),
        "artifacts": files,
    }
    manifest["content_digest"] = sha256_bytes(canonical_json_bytes(manifest))

    manifest_path = freeze_dir / "preregistration_manifest.json"
    write_json(manifest_path, manifest)

    tsq = create_rfc3161_query(
        manifest_path, freeze_dir / "preregistration_manifest.tsq"
    )
    receipt = {
        "freeze_id": freeze_id,
        "manifest_sha256": sha256_file(manifest_path),
        "rfc3161_query": tsq,
        "external_timestamp": {
            "status": "PENDING",
            "provider": None,
            "receipt_path": None,
        },
    }
    write_json(freeze_dir / "FREEZE_RECEIPT.json", receipt)

    append_audit_event(
        root,
        "FREEZE",
        {
            "freeze_id": freeze_id,
            "manifest_sha256": receipt["manifest_sha256"],
            "git_commit": git["commit"],
            "git_dirty": git["dirty"],
        },
    )
    print(manifest_path)


def case_index_path(root: Path) -> Path:
    return root / "_custody" / "case_index.json"


def load_case_index(root: Path) -> dict[str, Any]:
    path = case_index_path(root)
    if not path.exists():
        return {"cases": {}}
    data = read_json(path)
    if not isinstance(data, dict) or not isinstance(data.get("cases"), dict):
        raise HarnessError("Índice de casos inválido.")
    return data


def save_case_index(root: Path, data: dict[str, Any]) -> None:
    write_json(case_index_path(root), data)


@contextmanager
def case_index_lock(root: Path):
    lock_path = root / "_custody" / "case_index.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()
            os.fsync(handle.fileno())
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def expose_case(
    root: Path,
    *,
    case_id: str,
    pool: str,
    run_id: str,
) -> dict[str, Any]:
    with case_index_lock(root):
        index = load_case_index(root)
        metadata = index["cases"].get(case_id)
        if not isinstance(metadata, dict):
            raise HarnessError(f"Caso não cadastrado: {case_id}")
        if metadata.get("pool") != pool:
            raise HarnessError(f"Pool divergente para o caso {case_id}.")
        if metadata.get("burned") or metadata.get("status") == "exposed":
            raise HarnessError(
                f"Caso {case_id} já foi exposto e não pode ser reutilizado."
            )

        exposed_at = utc_now()
        metadata = {
            **metadata,
            "status": "exposed",
            "burned": True,
            "exposed_at": exposed_at,
            "exposure_run_id": run_id,
        }
        index["cases"][case_id] = metadata
        save_case_index(root, index)

        case_dir = root / "cases" / pool / case_id
        write_json(case_dir / "case.json", metadata)

    append_audit_event(
        root,
        "CASE_EXPOSED",
        {
            "case_id": case_id,
            "pool": pool,
            "run_id": run_id,
            "source_sha256": metadata.get("source_sha256"),
        },
    )
    return metadata


def add_case(args: argparse.Namespace) -> None:
    root = resolve_existing(args.root)
    source = resolve_existing(args.source)
    source_hash = sha256_file(source)
    index = load_case_index(root)

    for existing_id, meta in index["cases"].items():
        if meta.get("source_sha256") == source_hash:
            raise HarnessError(
                f"Mesmo conteúdo já cadastrado como {existing_id} "
                f"no pool {meta.get('pool')}."
            )

    case_id = args.case_id or f"case_{secrets.token_hex(6)}"
    if case_id in index["cases"]:
        raise HarnessError(f"case_id já existe: {case_id}")

    case_dir = root / "cases" / args.pool / case_id
    case_dir.mkdir(parents=True, exist_ok=False)
    dest = case_dir / f"source{source.suffix.lower()}"
    shutil.copy2(source, dest)

    metadata = {
        "case_id": case_id,
        "pool": args.pool,
        "source_file": dest.name,
        "source_sha256": source_hash,
        "source_size_bytes": source.stat().st_size,
        "registered_at": utc_now(),
        "status": "registered",
        "burned": False,
        "seen_outputs": False,
    }
    write_json(case_dir / "case.json", metadata)

    index["cases"][case_id] = metadata
    save_case_index(root, index)

    append_audit_event(
        root,
        "CASE_REGISTERED",
        {"case_id": case_id, "pool": args.pool, "source_sha256": source_hash},
    )
    print(case_id)


def find_case(root: Path, case_id: str) -> tuple[str, Path, dict[str, Any]]:
    index = load_case_index(root)
    meta = index["cases"].get(case_id)
    if not meta:
        raise HarnessError(f"Caso não cadastrado: {case_id}")
    pool = meta["pool"]
    return pool, root / "cases" / pool / case_id, meta


def custody_secret(root: Path) -> bytes:
    path = root / "_custody" / "secret.key"
    if not path.exists():
        raise HarnessError(
            "Chave de custódia ausente. Inicialize-a fora do fluxo de execução."
        )
    secret = path.read_bytes()
    if len(secret) != 32:
        raise HarnessError("Chave de custódia deve conter exatamente 32 bytes.")
    return secret


def blind_id(
    secret: bytes, case_id: str, arm: str, nonce: str, prefix: str
) -> str:
    digest = hmac.new(
        secret,
        f"{case_id}\0{arm}\0{nonce}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{prefix}-{digest[:12].upper()}"


def render_command(template: str, values: dict[str, str]) -> list[str]:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{" + key + "}", value)
    parsed = shlex.split(rendered, posix=os.name != "nt")
    if os.name == "nt":
        parsed = [
            (
                token[1:-1]
                if len(token) >= 2
                and token[0] == token[-1]
                and token[0] in {'"', "'"}
                else token
            )
            for token in parsed
        ]
    return parsed


def require_execution_gate(root: Path, config: dict[str, Any]) -> str:
    execution = config.get("execution", {})
    gate = execution.get("gate", {})
    if not isinstance(gate, dict) or gate.get("enabled") is not True:
        raise HarnessError(
            "Execução bloqueada: o gate do instrumento não foi habilitado."
        )
    freeze_id = str(gate.get("freeze_id") or "").strip()
    if not freeze_id:
        raise HarnessError("Execução bloqueada: freeze_id não configurado.")
    freeze_dir = root / "_freeze" / freeze_id
    manifest_path = freeze_dir / "preregistration_manifest.json"
    receipt_path = freeze_dir / "FREEZE_RECEIPT.json"
    if not manifest_path.is_file() or not receipt_path.is_file():
        raise HarnessError(
            f"Execução bloqueada: freeze {freeze_id} está incompleto."
        )
    receipt = read_json(receipt_path)
    if receipt.get("manifest_sha256") != sha256_file(manifest_path):
        raise HarnessError(
            f"Execução bloqueada: manifesto do freeze {freeze_id} divergiu."
        )
    if gate.get("require_external_timestamp", True):
        external = receipt.get("external_timestamp", {})
        if (
            not isinstance(external, dict)
            or external.get("status") != "VERIFIED"
            or not external.get("receipt_sha256")
        ):
            raise HarnessError(
                "Execução bloqueada: timestamp externo ainda não registrado."
            )
    return freeze_id


def resolve_config_path(root: Path, value: str, label: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    if not path.is_file():
        raise HarnessError(f"{label} não encontrado: {path}")
    return path


def configured_arms(
    config: dict[str, Any],
    *,
    pool: str,
) -> tuple[list[str], list[str]]:
    arm_config = config["arms"]
    if pool in {"calibration", "test"}:
        missing = set(PROTOCOL_ARMS) - set(arm_config)
        if missing:
            raise HarnessError(
                "Configuração comparativa incompleta; faltam: "
                + ", ".join(sorted(missing))
            )

    automated: list[str] = []
    human: list[str] = []
    for arm, arm_cfg in arm_config.items():
        if not isinstance(arm_cfg, dict) or arm_cfg.get("enabled") is not True:
            continue
        kind = arm_cfg.get("kind", "automated")
        if kind == "human":
            if arm != HUMAN_ARM:
                raise HarnessError(f"Somente {HUMAN_ARM} pode ser humano.")
            human.append(arm)
            continue
        if kind != "automated":
            raise HarnessError(f"Tipo de braço inválido em {arm}: {kind}")
        if arm == HUMAN_ARM:
            raise HarnessError(f"{HUMAN_ARM} não pode ser comando automatizado.")
        if not str(arm_cfg.get("command", "")).strip():
            raise HarnessError(
                f"Comando do braço {arm} está vazio em harness_config.json."
            )
        automated.append(arm)

    if not automated:
        raise HarnessError("Nenhum braço automatizado habilitado.")
    if pool in {"calibration", "test"}:
        if set(automated) != set(AUTOMATED_ARMS) or human != [HUMAN_ARM]:
            raise HarnessError(
                "Calibração/teste exigem A0-A9 automatizados e A10 humano."
            )
    return automated, human


def run_case(args: argparse.Namespace) -> None:
    root = resolve_existing(args.root)
    pool, case_dir, case_metadata = find_case(root, args.case_id)
    config = load_config(root)
    freeze_id = require_execution_gate(root, config)

    if pool == "test" and not args.confirm_test:
        raise HarnessError(
            "Execução de caso do pool TEST exige --confirm-test. "
            "Use apenas após o congelamento definitivo."
        )
    if case_metadata.get("burned") or case_metadata.get("status") == "exposed":
        raise HarnessError(
            f"Caso {args.case_id} já foi exposto e não pode ser reutilizado."
        )

    source_files = [
        p for p in case_dir.iterdir()
        if p.is_file() and p.name != "case.json"
    ]
    if len(source_files) != 1:
        raise HarnessError(
            f"Esperava exatamente um arquivo-fonte em {case_dir}; "
            f"encontrei {len(source_files)}."
        )
    input_path = source_files[0]

    run_id = args.run_id or dt.datetime.now(
        dt.timezone.utc
    ).strftime("%Y%m%dT%H%M%SZ")
    base_run_dir = root / "runs" / pool / args.case_id / run_id
    if base_run_dir.exists():
        raise HarnessError(f"run_id já existe: {base_run_dir}")
    base_run_dir.mkdir(parents=True)

    working_directory = Path(
        config.get("execution", {}).get("working_directory", ".")
    )
    if not working_directory.is_absolute():
        working_directory = (root / working_directory).resolve()

    enabled_arms, human_arms = configured_arms(config, pool=pool)
    randomization_seed = secrets.token_hex(32)
    randomized_arms = list(enabled_arms)
    random.Random(int(randomization_seed, 16)).shuffle(randomized_arms)
    output_schema = resolve_config_path(
        root,
        str(
            config.get("execution", {}).get(
                "output_schema",
                "prereg/arm_output_schema_1.0.0.json",
            )
        ),
        "Schema de output",
    )
    validate_json_schema_meta(output_schema)

    expose_case(
        root,
        case_id=args.case_id,
        pool=pool,
        run_id=run_id,
    )
    input_hash = sha256_file(input_path)

    run_manifest: dict[str, Any] = {
        "run_id": run_id,
        "case_id": args.case_id,
        "pool": pool,
        "started_at": utc_now(),
        "input_sha256": input_hash,
        "harness_version": HARNESS_VERSION,
        "freeze_id": freeze_id,
        "arm_order": randomized_arms,
        "arm_order_seed": randomization_seed,
        "human_arms": human_arms,
        "output_schema_sha256": sha256_file(output_schema),
        "arms": {},
    }

    failures: list[str] = []
    for arm in randomized_arms:
        arm_cfg = config["arms"][arm]
        template = str(arm_cfg.get("command", "")).strip()

        arm_dir = base_run_dir / arm
        arm_dir.mkdir()
        scratch_dir = arm_dir / "scratch"
        scratch_dir.mkdir()
        output_path = arm_dir / config["execution"].get(
            "output_filename", "output.json"
        )

        values = {
            "case_dir": str(case_dir),
            "case_id": args.case_id,
            "pool": pool,
            "arm": arm,
            "run_dir": str(arm_dir),
            "input_path": str(input_path),
            "output_path": str(output_path),
            "working_directory": str(working_directory),
        }
        argv = render_command(template, values)

        env = os.environ.copy()
        for k, v in arm_cfg.get("env", {}).items():
            rendered_env = str(v)
            for key, value in values.items():
                rendered_env = rendered_env.replace("{" + key + "}", value)
            env[str(k)] = rendered_env
        env.update(
            {
                "ATRIO_EVAL_CASE_ID": args.case_id,
                "ATRIO_EVAL_POOL": pool,
                "ATRIO_EVAL_ARM": arm,
                "ATRIO_EVAL_RUN_ID": run_id,
                "ATRIO_EVAL_INPUT_PATH": str(input_path),
                "ATRIO_EVAL_OUTPUT_PATH": str(output_path),
                "TMP": str(scratch_dir),
                "TEMP": str(scratch_dir),
                "TMPDIR": str(scratch_dir),
                "XDG_CACHE_HOME": str(scratch_dir / "xdg-cache"),
                "HF_HOME": str(scratch_dir / "huggingface"),
            }
        )

        timeout = float(arm_cfg.get("timeout_seconds", 1800))
        result = run_process(
            argv,
            cwd=arm_dir,
            env=env,
            timeout=timeout,
        )

        stdout_path = arm_dir / config["execution"].get(
            "stdout_filename", "stdout.txt"
        )
        stderr_path = arm_dir / config["execution"].get(
            "stderr_filename", "stderr.txt"
        )
        atomic_write_text(stdout_path, result.pop("stdout"))
        atomic_write_text(stderr_path, result.pop("stderr"))

        meta = {
            "arm": arm,
            "command_argv": argv,
            "input_sha256": input_hash,
            **result,
            "stdout_sha256": sha256_file(stdout_path),
            "stderr_sha256": sha256_file(stderr_path),
            "output_exists": output_path.exists(),
            "output_sha256": (
                sha256_file(output_path) if output_path.exists() else None
            ),
            "output_size_bytes": (
                output_path.stat().st_size if output_path.exists() else None
            ),
            "output_schema_valid": False,
        }

        if result["return_code"] != 0 or result["timed_out"]:
            meta["status"] = "failed"
            failures.append(arm)
            append_audit_event(
                root,
                "ARM_FAILED",
                {
                    "case_id": args.case_id,
                    "run_id": run_id,
                    "arm": arm,
                    "return_code": result["return_code"],
                    "timed_out": result["timed_out"],
                },
            )
        elif not output_path.exists():
            meta["status"] = "missing_output"
            failures.append(arm)
            append_audit_event(
                root,
                "ARM_OUTPUT_MISSING",
                {
                    "case_id": args.case_id,
                    "run_id": run_id,
                    "arm": arm,
                },
            )
        else:
            try:
                validate_json_instance(output_schema, output_path)
            except HarnessError as exc:
                meta["status"] = "invalid_output"
                meta["output_schema_error"] = str(exc)
                failures.append(arm)
                append_audit_event(
                    root,
                    "ARM_OUTPUT_INVALID",
                    {
                        "case_id": args.case_id,
                        "run_id": run_id,
                        "arm": arm,
                        "output_sha256": meta["output_sha256"],
                    },
                )
            else:
                meta["status"] = "completed"
                meta["output_schema_valid"] = True

        write_json(
            arm_dir
            / config["execution"].get("metadata_filename", "execution.json"),
            meta,
        )
        run_manifest["arms"][arm] = meta
        write_json(base_run_dir / "run_manifest.json", run_manifest)

    run_manifest["finished_at"] = utc_now()
    run_manifest["status"] = (
        "completed" if not failures else "completed_with_failures"
    )
    run_manifest["failed_arms"] = failures
    write_json(base_run_dir / "run_manifest.json", run_manifest)

    with case_index_lock(root):
        index = load_case_index(root)
        index["cases"][args.case_id]["seen_outputs"] = any(
            meta.get("output_exists")
            for meta in run_manifest["arms"].values()
        )
        index["cases"][args.case_id]["completed_at"] = utc_now()
        index["cases"][args.case_id]["run_status"] = run_manifest["status"]
        save_case_index(root, index)
        write_json(case_dir / "case.json", index["cases"][args.case_id])

    append_audit_event(
        root,
        "CASE_RUN_COMPLETED",
        {
            "case_id": args.case_id,
            "pool": pool,
            "run_id": run_id,
            "arms": randomized_arms,
            "failed_arms": failures,
            "status": run_manifest["status"],
        },
    )
    if failures:
        raise HarnessError(
            "Execução terminou com falhas simétricas registradas nos braços: "
            + ", ".join(failures)
        )
    print(base_run_dir)


def blind_run(args: argparse.Namespace) -> None:
    root = resolve_existing(args.root)
    pool, _, _ = find_case(root, args.case_id)
    run_dir = root / "runs" / pool / args.case_id / args.run_id
    if not run_dir.exists():
        raise HarnessError(f"Execução não encontrada: {run_dir}")

    config = load_config(root)
    prefix = config.get("custody", {}).get("blind_id_prefix", "OUT")
    secret = custody_secret(root)
    nonce = secrets.token_hex(16)

    manifest = read_json(run_dir / "run_manifest.json")
    if manifest.get("status") != "completed":
        raise HarnessError(
            "Somente execução completa e sem falhas pode ser cegada."
        )
    arms = list(manifest.get("arms", {}).keys())
    if not arms:
        raise HarnessError("run_manifest não contém braços.")
    invalid = [
        arm
        for arm, meta in manifest["arms"].items()
        if not isinstance(meta, dict) or meta.get("output_schema_valid") is not True
    ]
    if invalid:
        raise HarnessError(
            "Outputs sem validação bloqueante: " + ", ".join(invalid)
        )

    shuffled = list(arms)
    secrets.SystemRandom().shuffle(shuffled)

    packet_dir = (
        root / "rater_packets" / pool / args.case_id / args.run_id
    )
    if packet_dir.exists():
        raise HarnessError(f"Pacote cego já existe: {packet_dir}")
    packet_dir.mkdir(parents=True)

    map_dir = root / "_custody" / "maps" / pool / args.case_id
    map_dir.mkdir(parents=True, exist_ok=True)
    map_path = map_dir / f"{args.run_id}.json"

    mapping: dict[str, Any] = {
        "case_id": args.case_id,
        "pool": pool,
        "run_id": args.run_id,
        "created_at": utc_now(),
        "nonce": nonce,
        "map": {},
    }
    public_manifest = {
        "case_id": args.case_id,
        "packet_id": f"packet_{secrets.token_hex(8)}",
        "created_at": utc_now(),
        "outputs": [],
    }

    output_name = config["execution"].get("output_filename", "output.json")
    for arm in shuffled:
        source = run_dir / arm / output_name
        if not source.exists():
            raise HarnessError(f"Output ausente para {arm}: {source}")

        bid = blind_id(secret, args.case_id, arm, nonce, prefix)
        suffix = source.suffix or ".json"
        dest = packet_dir / f"{bid}{suffix}"
        shutil.copy2(source, dest)

        mapping["map"][bid] = {
            "arm": arm,
            "source_sha256": sha256_file(source),
            "blinded_sha256": sha256_file(dest),
        }
        public_manifest["outputs"].append(
            {
                "blind_id": bid,
                "filename": dest.name,
                "sha256": sha256_file(dest),
                "size_bytes": dest.stat().st_size,
            }
        )

    write_json(map_path, mapping)
    write_json(packet_dir / "packet_manifest.json", public_manifest)

    index = load_case_index(root)
    index["cases"][args.case_id]["seen_outputs"] = True
    save_case_index(root, index)

    append_audit_event(
        root,
        "RUN_BLINDED",
        {
            "case_id": args.case_id,
            "pool": pool,
            "run_id": args.run_id,
            "packet_manifest_sha256": sha256_file(
                packet_dir / "packet_manifest.json"
            ),
            "mapping_sha256": sha256_file(map_path),
        },
    )
    print(packet_dir)


def validate_json(args: argparse.Namespace) -> None:
    schema_path = resolve_existing(args.schema)
    instance_path = resolve_existing(args.instance)
    validate_json_instance(schema_path, instance_path)
    print("VALID")


def record_external_timestamp(args: argparse.Namespace) -> None:
    root = resolve_existing(args.root)
    freeze_dir = root / "_freeze" / args.freeze_id
    receipt_path = freeze_dir / "FREEZE_RECEIPT.json"
    receipt = read_json(receipt_path)

    external = resolve_existing(args.receipt)
    dest = freeze_dir / external.name
    if external.resolve() != dest.resolve():
        shutil.copy2(external, dest)

    receipt["external_timestamp"] = {
        "status": "RECEIVED_UNVERIFIED",
        "provider": args.provider,
        "receipt_path": dest.name,
        "receipt_sha256": sha256_file(dest),
        "recorded_at": utc_now(),
    }
    write_json(receipt_path, receipt)

    append_audit_event(
        root,
        "EXTERNAL_TIMESTAMP_RECORDED",
        {
            "freeze_id": args.freeze_id,
            "provider": args.provider,
            "receipt_sha256": sha256_file(dest),
        },
    )
    print(receipt_path)


def verify_rfc3161_timestamp(args: argparse.Namespace) -> None:
    root = resolve_existing(args.root)
    freeze_dir = root / "_freeze" / args.freeze_id
    receipt_path = freeze_dir / "FREEZE_RECEIPT.json"
    receipt = read_json(receipt_path)
    external = receipt.get("external_timestamp", {})
    if (
        not isinstance(external, dict)
        or external.get("status") != "RECEIVED_UNVERIFIED"
    ):
        raise HarnessError("Não há resposta RFC 3161 pendente de verificação.")

    tsr_path = freeze_dir / str(external.get("receipt_path", ""))
    query = receipt.get("rfc3161_query", {})
    tsq_path = Path(str(query.get("path", "")))
    if not tsq_path.is_absolute():
        tsq_path = freeze_dir / tsq_path.name
    ca_file = resolve_existing(args.ca_file)
    if not tsr_path.is_file() or not tsq_path.is_file():
        raise HarnessError("Resposta .tsr ou requisição .tsq ausente.")
    if sha256_file(tsr_path) != external.get("receipt_sha256"):
        raise HarnessError("Hash da resposta RFC 3161 divergiu.")

    openssl = shutil.which("openssl")
    if not openssl:
        raise HarnessError("OpenSSL não encontrado para verificar RFC 3161.")
    argv = [
        openssl,
        "ts",
        "-verify",
        "-queryfile",
        str(tsq_path),
        "-in",
        str(tsr_path),
        "-CAfile",
        str(ca_file),
    ]
    if args.untrusted:
        argv.extend(["-untrusted", str(resolve_existing(args.untrusted))])
    result = run_process(argv)
    if result["return_code"] != 0:
        raise HarnessError(
            "Verificação criptográfica RFC 3161 falhou: "
            + result["stderr"].strip()
        )

    ca_dest = freeze_dir / ca_file.name
    if ca_file.resolve() != ca_dest.resolve():
        shutil.copy2(ca_file, ca_dest)
    external.update(
        {
            "status": "VERIFIED",
            "verified_at": utc_now(),
            "verification": "openssl ts -verify",
            "ca_file": ca_dest.name,
            "ca_sha256": sha256_file(ca_dest),
        }
    )
    receipt["external_timestamp"] = external
    write_json(receipt_path, receipt)
    append_audit_event(
        root,
        "EXTERNAL_TIMESTAMP_VERIFIED",
        {
            "freeze_id": args.freeze_id,
            "provider": external.get("provider"),
            "receipt_sha256": external.get("receipt_sha256"),
            "ca_sha256": external.get("ca_sha256"),
        },
    )
    print(receipt_path)


def audit(args: argparse.Namespace) -> None:
    root = resolve_existing(args.root)
    problems: list[str] = []

    problems.extend(verify_audit_chain(root))

    index = load_case_index(root)
    seen_hashes: dict[str, str] = {}

    for case_id, meta in index["cases"].items():
        pool = meta.get("pool")
        if pool not in POOLS:
            problems.append(f"{case_id}: pool inválido {pool}")

        h = meta.get("source_sha256")
        if h:
            if h in seen_hashes:
                problems.append(
                    f"Conteúdo duplicado: {case_id} e {seen_hashes[h]} "
                    f"têm o mesmo SHA-256."
                )
            else:
                seen_hashes[h] = case_id

        case_dir = root / "cases" / str(pool) / case_id
        if not (case_dir / "case.json").exists():
            problems.append(f"{case_id}: case.json ausente")

        status_value = meta.get("status")
        if meta.get("burned") and status_value != "exposed":
            problems.append(
                f"{case_id}: burned=true sem status exposed."
            )
        if status_value == "exposed" and not meta.get("exposed_at"):
            problems.append(f"{case_id}: exposição sem exposed_at.")

    freeze_root = root / "_freeze"
    if freeze_root.exists():
        for freeze_dir in freeze_root.iterdir():
            if not freeze_dir.is_dir():
                continue
            manifest_path = freeze_dir / "preregistration_manifest.json"
            receipt_path = freeze_dir / "FREEZE_RECEIPT.json"

            if not manifest_path.exists():
                problems.append(
                    f"{freeze_dir.name}: manifesto de freeze ausente"
                )
                continue

            if receipt_path.exists():
                receipt = read_json(receipt_path)
                expected = receipt.get("manifest_sha256")
                actual = sha256_file(manifest_path)
                if expected and expected != actual:
                    problems.append(
                        f"{freeze_dir.name}: hash do manifesto divergiu do recibo."
                    )

    if problems:
        for p in problems:
            print(f"- {p}", file=sys.stderr)
        raise HarnessError(
            f"Auditoria falhou com {len(problems)} problema(s)."
        )

    print("AUDIT_OK")


def status(args: argparse.Namespace) -> None:
    root = resolve_existing(args.root)
    index = load_case_index(root)

    summary = {
        "harness_version": HARNESS_VERSION,
        "root": str(root),
        "cases": {
            pool: {
                "count": 0,
                "burned": 0,
                "seen_outputs": 0,
            }
            for pool in POOLS
        },
        "freezes": [],
    }

    for meta in index["cases"].values():
        pool = meta.get("pool")
        if pool in summary["cases"]:
            summary["cases"][pool]["count"] += 1
            summary["cases"][pool]["burned"] += int(
                bool(meta.get("burned"))
            )
            summary["cases"][pool]["seen_outputs"] += int(
                bool(meta.get("seen_outputs"))
            )

    freeze_root = root / "_freeze"
    if freeze_root.exists():
        for d in sorted(freeze_root.iterdir()):
            if d.is_dir():
                receipt = d / "FREEZE_RECEIPT.json"
                external = None
                if receipt.exists():
                    external = read_json(receipt).get(
                        "external_timestamp", {}
                    ).get("status")
                summary["freezes"].append(
                    {
                        "freeze_id": d.name,
                        "external_timestamp": external,
                    }
                )

    print(
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="atrio_eval_harness",
        description="Harness experimental do ATRIO.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=HARNESS_VERSION,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser(
        "init",
        help="Inicializa a estrutura do experimento.",
    )
    p.add_argument("root")
    p.set_defaults(func=init_experiment)

    p = sub.add_parser(
        "freeze",
        help="Congela pacote metodológico, instrumento e candidato Git.",
    )
    p.add_argument("root")
    p.add_argument("--package", required=True)
    p.add_argument("--instrument", action="append", required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--freeze-id")
    p.set_defaults(func=freeze)

    p = sub.add_parser(
        "record-timestamp",
        help="Registra recibo externo de timestamp.",
    )
    p.add_argument("root")
    p.add_argument("--freeze-id", required=True)
    p.add_argument("--provider", required=True)
    p.add_argument("--receipt", required=True)
    p.set_defaults(func=record_external_timestamp)

    p = sub.add_parser(
        "verify-timestamp",
        help="Verifica criptograficamente uma resposta RFC 3161.",
    )
    p.add_argument("root")
    p.add_argument("--freeze-id", required=True)
    p.add_argument("--ca-file", required=True)
    p.add_argument("--untrusted")
    p.set_defaults(func=verify_rfc3161_timestamp)

    p = sub.add_parser(
        "add-case",
        help="Cadastra caso em smoke/calibration/test.",
    )
    p.add_argument("root")
    p.add_argument("--pool", choices=POOLS, required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--case-id")
    p.set_defaults(func=add_case)

    p = sub.add_parser(
        "run",
        help="Executa todos os braços habilitados para um caso.",
    )
    p.add_argument("root")
    p.add_argument("--case-id", required=True)
    p.add_argument("--run-id")
    p.add_argument("--confirm-test", action="store_true")
    p.set_defaults(func=run_case)

    p = sub.add_parser(
        "blind",
        help="Permuta/rerrotula outputs e separa mapa de custódia.",
    )
    p.add_argument("root")
    p.add_argument("--case-id", required=True)
    p.add_argument("--run-id", required=True)
    p.set_defaults(func=blind_run)

    p = sub.add_parser(
        "validate",
        help="Valida JSON contra o JSON Schema.",
    )
    p.add_argument("--schema", required=True)
    p.add_argument("--instance", required=True)
    p.set_defaults(func=validate_json)

    p = sub.add_parser(
        "audit",
        help="Audita integridade, pools, hashes e cadeia de log.",
    )
    p.add_argument("root")
    p.set_defaults(func=audit)

    p = sub.add_parser(
        "status",
        help="Exibe estado resumido do experimento.",
    )
    p.add_argument("root")
    p.set_defaults(func=status)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        args.func(args)
        return 0
    except HarnessError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Interrompido.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
