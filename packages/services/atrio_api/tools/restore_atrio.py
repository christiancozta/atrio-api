from __future__ import annotations

import argparse
from datetime import UTC, datetime
import getpass
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import uuid

from atrio_api.database import DATABASE_SCHEMA_VERSION
from atrio_api.operations.backup import verify_authenticated_backup


SERVICE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VAULT_ROOT = SERVICE_ROOT / "var" / "vault"
DEFAULT_AUTHENTICATION_KEY = (
    SERVICE_ROOT / "var" / "backup-authentication.key"
)
_IDENTIFIER = re.compile(r"[a-z_][a-z0-9_]{0,47}")
SCRIPT_VERSION = "1.0.0"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Restauração nativa reversível do ATRIO. "
            "O banco e o vault anteriores são preservados."
        )
    )
    parser.add_argument("backup", type=Path)
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
    parser.add_argument("--database-admin", default="postgres")
    parser.add_argument("--database-owner", default="atrio_app")
    args = parser.parse_args()

    _validate_identifier(args.database_name, "banco")
    _validate_identifier(args.database_admin, "administrador")
    _validate_identifier(args.database_owner, "proprietário")
    _require_api_stopped(args.api_port)
    if not args.authentication_key.is_file():
        raise RuntimeError("Chave HMAC local não encontrada.")
    manifest = verify_authenticated_backup(
        args.backup,
        authentication_key=args.authentication_key.read_bytes(),
    )
    metadata = manifest["metadata"]
    if metadata.get("database_schema_version") != DATABASE_SCHEMA_VERSION:
        raise RuntimeError(
            "Versão do schema no backup diverge do runtime atual."
        )

    database_dump = args.backup.resolve() / "database" / "atrio.custom"
    source_vault = args.backup.resolve() / "vault"
    if not database_dump.is_file() or not source_vault.is_dir():
        raise RuntimeError("Backup não contém banco e vault obrigatórios.")

    restore_id = uuid.uuid4().hex[:12]
    staging_database = f"atrio_restore_{restore_id}"
    previous_database = (
        "atrio_pre_" + datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    )
    vault_root = args.vault_root.resolve()
    staged_vault = vault_root.with_name(f"vault.restore.{restore_id}")
    previous_vault = vault_root.with_name(
        "vault.pre." + datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    )
    if staged_vault.exists() or previous_vault.exists():
        raise RuntimeError("Diretório de segurança da restauração já existe.")
    shutil.copytree(source_vault, staged_vault)

    confirmation = input(
        "Digite RESTAURAR para trocar banco e vault, preservando os atuais: "
    )
    if confirmation != "RESTAURAR":
        shutil.rmtree(staged_vault)
        print("Restauração cancelada.")
        return 0

    psql = _find_postgres_tool("psql")
    pg_restore = _find_postgres_tool("pg_restore")
    admin_password = getpass.getpass(
        f"Senha PostgreSQL de {args.database_admin}: "
    )
    environment = os.environ.copy()
    environment["PGPASSWORD"] = admin_password
    admin_password = ""

    database_swapped = False
    vault_swapped = False
    try:
        _psql(
            psql,
            args,
            environment,
            (
                f'CREATE DATABASE "{staging_database}" '
                f'OWNER "{args.database_owner}"'
            ),
        )
        _run(
            [
                str(pg_restore),
                "--host",
                args.database_host,
                "--port",
                str(args.database_port),
                "--username",
                args.database_admin,
                "--dbname",
                staging_database,
                "--exit-on-error",
                "--no-owner",
                "--no-privileges",
                "--role",
                args.database_owner,
                str(database_dump),
            ],
            environment=environment,
        )
        schema_version = _psql(
            psql,
            args,
            environment,
            (
                "SELECT version FROM atrio.schema_migrations "
                "ORDER BY applied_at DESC LIMIT 1"
            ),
            database=staging_database,
            tuples_only=True,
        ).stdout.strip()
        if schema_version != DATABASE_SCHEMA_VERSION:
            raise RuntimeError(
                "Banco temporário não confirmou a versão esperada."
            )

        _psql(
            psql,
            args,
            environment,
            (
                "SELECT pg_terminate_backend(pid) "
                "FROM pg_stat_activity "
                f"WHERE datname = '{args.database_name}' "
                "AND pid <> pg_backend_pid()"
            ),
        )
        _psql(
            psql,
            args,
            environment,
            (
                f'ALTER DATABASE "{args.database_name}" '
                f'RENAME TO "{previous_database}"'
            ),
        )
        try:
            _psql(
                psql,
                args,
                environment,
                (
                    f'ALTER DATABASE "{staging_database}" '
                    f'RENAME TO "{args.database_name}"'
                ),
            )
        except BaseException:
            _psql(
                psql,
                args,
                environment,
                (
                    f'ALTER DATABASE "{previous_database}" '
                    f'RENAME TO "{args.database_name}"'
                ),
            )
            raise
        database_swapped = True

        if vault_root.exists():
            vault_root.rename(previous_vault)
        staged_vault.rename(vault_root)
        vault_swapped = True
    except BaseException:
        if database_swapped and not vault_swapped:
            _psql(
                psql,
                args,
                environment,
                (
                    f'ALTER DATABASE "{args.database_name}" '
                    f'RENAME TO "{staging_database}"'
                ),
            )
            _psql(
                psql,
                args,
                environment,
                (
                    f'ALTER DATABASE "{previous_database}" '
                    f'RENAME TO "{args.database_name}"'
                ),
            )
        if previous_vault.exists() and not vault_root.exists():
            previous_vault.rename(vault_root)
        raise
    finally:
        environment.pop("PGPASSWORD", None)

    print("Restauração concluída e reversível.")
    print(f"Banco anterior preservado como: {previous_database}")
    if previous_vault.exists():
        print(f"Vault anterior preservado em: {previous_vault}")
    print("Inicie a API e valide /v1/health/ready antes de remover salvaguardas.")
    return 0


def _psql(
    executable: Path,
    args: argparse.Namespace,
    environment: dict[str, str],
    sql: str,
    *,
    database: str = "postgres",
    tuples_only: bool = False,
) -> subprocess.CompletedProcess[str]:
    command = [
        str(executable),
        "--host",
        args.database_host,
        "--port",
        str(args.database_port),
        "--username",
        args.database_admin,
        "--dbname",
        database,
        "--set",
        "ON_ERROR_STOP=1",
    ]
    if tuples_only:
        command.extend(["--tuples-only", "--no-align"])
    command.extend(["--command", sql])
    return _run(command, environment=environment)


def _run(
    command: list[str],
    *,
    environment: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Comando operacional falhou: {Path(command[0]).name}."
        )
    return result


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
            return max(
                candidates,
                key=lambda path: tuple(
                    int(item)
                    for item in path.parents[1].name.split(".")
                    if item.isdigit()
                ),
            )
    raise RuntimeError(f"Ferramenta PostgreSQL não encontrada: {executable}.")


def _validate_identifier(value: str, label: str) -> None:
    if not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"Identificador de {label} inválido.")


def _require_api_stopped(port: int) -> None:
    if not 1 <= port <= 65535:
        raise ValueError("Porta da API inválida.")
    with socket.socket() as connection:
        connection.settimeout(0.25)
        if connection.connect_ex(("127.0.0.1", port)) == 0:
            raise RuntimeError(
                f"API responde em 127.0.0.1:{port}. "
                "Encerre-a antes da restauração."
            )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        raise
