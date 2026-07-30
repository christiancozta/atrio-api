from __future__ import annotations

import argparse
from datetime import UTC, datetime
import getpass
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import uuid

from atrio_api import __version__
from atrio_api.database import DATABASE_SCHEMA_VERSION
from atrio_api.operations.backup import (
    create_authenticated_manifest,
    ensure_authentication_key,
)
from atrio_api.release_catalog import ACTIVE_RELEASE


SERVICE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = SERVICE_ROOT.parents[2]
DEFAULT_VAULT_ROOT = SERVICE_ROOT / "var" / "vault"
DEFAULT_BACKUP_ROOT = REPOSITORY_ROOT / "_backups"
DEFAULT_AUTHENTICATION_KEY = (
    SERVICE_ROOT / "var" / "backup-authentication.key"
)
SCRIPT_VERSION = "1.0.0"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Backup autenticado do PostgreSQL e do vault ATRIO. "
            "Não remove backups antigos."
        )
    )
    parser.add_argument(
        "--mode",
        choices=("native", "container"),
        default="native",
    )
    parser.add_argument("--backup-root", type=Path, default=DEFAULT_BACKUP_ROOT)
    parser.add_argument("--vault-root", type=Path, default=DEFAULT_VAULT_ROOT)
    parser.add_argument(
        "--authentication-key",
        type=Path,
        default=DEFAULT_AUTHENTICATION_KEY,
    )
    parser.add_argument("--api-port", type=int, default=8080)
    parser.add_argument("--database-host", default="127.0.0.1")
    parser.add_argument("--database-port", type=int, default=5432)
    parser.add_argument("--database-name", default="atrio")
    parser.add_argument("--database-user", default="atrio_app")
    parser.add_argument("--runtime", choices=("docker", "podman"))
    args = parser.parse_args()

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    suffix = uuid.uuid4().hex[:8]
    final = args.backup_root.resolve() / f"atrio_{timestamp}_{suffix}"
    partial = final.with_name(final.name + ".partial")
    if final.exists() or partial.exists():
        raise RuntimeError("Destino de backup já existe.")
    partial.mkdir(parents=True)
    database_dump = partial / "database" / "atrio.custom"
    database_dump.parent.mkdir(parents=True)
    vault_destination = partial / "vault"

    runtime: str | None = None
    api_was_running = False
    try:
        if args.mode == "native":
            _require_api_stopped(args.api_port)
            password = getpass.getpass(
                f"Senha PostgreSQL de {args.database_user}: "
            )
            try:
                pg_dump = _find_postgres_tool("pg_dump")
                _run(
                    [
                        str(pg_dump),
                        "--host",
                        args.database_host,
                        "--port",
                        str(args.database_port),
                        "--username",
                        args.database_user,
                        "--dbname",
                        args.database_name,
                        "--format",
                        "custom",
                        "--file",
                        str(database_dump),
                    ],
                    password=password,
                )
            finally:
                password = ""
            _copy_vault(args.vault_root.resolve(), vault_destination)
            database_engine = _version_output([str(pg_dump), "--version"])
        else:
            runtime = _resolve_runtime(args.runtime)
            api_was_running = _container_running(runtime, "atrio_api")
            if api_was_running:
                _run([runtime, "stop", "atrio_api"])
            temporary_dump = f"/tmp/atrio-{uuid.uuid4().hex}.custom"
            try:
                _run(
                    [
                        runtime,
                        "exec",
                        "atrio_db",
                        "pg_dump",
                        "--username",
                        "atrio_app",
                        "--dbname",
                        "atrio",
                        "--format",
                        "custom",
                        "--file",
                        temporary_dump,
                    ]
                )
                _run(
                    [
                        runtime,
                        "cp",
                        f"atrio_db:{temporary_dump}",
                        str(database_dump),
                    ]
                )
                _run(
                    [
                        runtime,
                        "cp",
                        "atrio_api:/data/vault/.",
                        str(vault_destination),
                    ]
                )
            finally:
                _run(
                    [
                        runtime,
                        "exec",
                        "atrio_db",
                        "rm",
                        "-f",
                        temporary_dump,
                    ],
                    check=False,
                )
            database_engine = _version_output(
                [runtime, "exec", "atrio_db", "pg_dump", "--version"]
            )

        if not database_dump.is_file() or database_dump.stat().st_size == 0:
            raise RuntimeError("Dump PostgreSQL não foi produzido.")
        if not (vault_destination / "vault.salt").is_file():
            raise RuntimeError(
                "Vault copiado não contém vault.salt; backup recusado."
            )

        key = ensure_authentication_key(args.authentication_key)
        create_authenticated_manifest(
            partial,
            authentication_key=key,
            metadata={
                "api_version": __version__,
                "backup_script_version": SCRIPT_VERSION,
                "created_at": datetime.now(UTC).isoformat(),
                "database_engine": database_engine,
                "database_schema_version": DATABASE_SCHEMA_VERSION,
                "mode": args.mode,
                "release_id": ACTIVE_RELEASE.release_id,
            },
        )
        partial.rename(final)
    except BaseException:
        print(
            f"Backup incompleto preservado para diagnóstico: {partial}",
            file=sys.stderr,
        )
        raise
    finally:
        if runtime is not None and api_was_running:
            _run([runtime, "start", "atrio_api"], check=False)

    print(f"Backup autenticado concluído: {final}")
    print(f"Chave HMAC local: {args.authentication_key.resolve()}")
    print("Guarde uma cópia offline da chave HMAC e da frase do vault.")
    return 0


def _copy_vault(source: Path, destination: Path) -> None:
    if not source.is_dir():
        raise RuntimeError(f"Vault inexistente: {source}")
    shutil.copytree(source, destination)


def _require_api_stopped(port: int) -> None:
    if not 1 <= port <= 65535:
        raise ValueError("Porta da API inválida.")
    with socket.socket() as connection:
        connection.settimeout(0.25)
        if connection.connect_ex(("127.0.0.1", port)) == 0:
            raise RuntimeError(
                f"API responde em 127.0.0.1:{port}. "
                "Encerre-a antes do backup nativo."
            )


def _find_postgres_tool(name: str) -> Path:
    executable = f"{name}.exe" if os.name == "nt" else name
    discovered = shutil.which(executable)
    if discovered:
        return Path(discovered)
    if os.name == "nt":
        candidates = list(
            Path("C:/Program Files/PostgreSQL").glob(
                f"*/bin/{executable}"
            )
        )
        if candidates:
            return max(candidates, key=_postgres_version_key)
    raise RuntimeError(f"Ferramenta PostgreSQL não encontrada: {executable}.")


def _postgres_version_key(path: Path) -> tuple[int, ...]:
    try:
        return tuple(int(item) for item in path.parents[1].name.split("."))
    except ValueError:
        return (0,)


def _resolve_runtime(explicit: str | None) -> str:
    if explicit:
        if not shutil.which(explicit):
            raise RuntimeError(f"Runtime não encontrado: {explicit}.")
        return explicit
    for candidate in ("podman", "docker"):
        if shutil.which(candidate):
            return candidate
    raise RuntimeError("Docker ou Podman não encontrado.")


def _container_running(runtime: str, name: str) -> bool:
    result = _run(
        [runtime, "inspect", "--format", "{{.State.Running}}", name],
        check=False,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def _version_output(command: list[str]) -> str:
    return _run(command).stdout.strip()


def _run(
    command: list[str],
    *,
    password: str | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    if password is not None:
        environment["PGPASSWORD"] = password
    return subprocess.run(
        command,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
    )


if __name__ == "__main__":
    raise SystemExit(main())
