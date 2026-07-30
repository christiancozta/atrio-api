"""Factory da API para execução não interativa em container."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import os
from pathlib import Path
import re

from fastapi import FastAPI

from atrio_api import __version__
from atrio_api.api import create_app
from atrio_api.corpus_intake import CorpusIntakeService, EncryptedCorpusStore
from atrio_api.corpus_service import default_corpus_workflow
from atrio_api.cerne.provider import AtrioOllamaCerneProvider
from atrio_api.cerne.service import default_cerne_workflow
from atrio_api.lux.service import default_lux_workflow
from atrio_api.adapters.ollama import (
    DEFAULT_NUM_CTX,
    DEFAULT_NUM_PREDICT,
    OllamaAdapter,
)
from atrio_api.ratio.execution import RatioPhaseExecutor
from atrio_api.postgres_repository import PostgresExecutionRepository
from atrio_api.ratio.service import default_ratio_workflow
from atrio_api.release_catalog import ACTIVE_RELEASE
from atrio_api.service import ExecutionService


_DB_IDENTIFIER = re.compile(r"[a-z_][a-z0-9_]{0,62}")


@dataclass(frozen=True, slots=True)
class ContainerSettings:
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password_file: Path
    vault_root: Path
    vault_passphrase_file: Path
    packages_root: Path
    ui_path: Path

    @classmethod
    def from_environment(
        cls,
        environment: Mapping[str, str] | None = None,
    ) -> ContainerSettings:
        values = os.environ if environment is None else environment
        repository_root = Path(
            values.get("ATRIO_REPOSITORY_ROOT", "/app")
        )
        database_port = _positive_port(
            values.get("ATRIO_DB_PORT", "5432")
        )
        database_name = _database_identifier(
            values.get("ATRIO_DB_NAME", "atrio"),
            "banco",
        )
        database_user = _database_identifier(
            values.get("ATRIO_DB_USER", "atrio_app"),
            "usuário",
        )
        return cls(
            database_host=_required_text(
                values.get("ATRIO_DB_HOST", "atrio_db"),
                "host PostgreSQL",
            ),
            database_port=database_port,
            database_name=database_name,
            database_user=database_user,
            database_password_file=Path(
                values.get(
                    "ATRIO_DB_PASSWORD_FILE",
                    "/run/secrets/atrio_db_password",
                )
            ),
            vault_root=Path(
                values.get("ATRIO_VAULT_ROOT", "/data/vault")
            ),
            vault_passphrase_file=Path(
                values.get(
                    "ATRIO_VAULT_PASSPHRASE_FILE",
                    "/run/secrets/atrio_vault_passphrase",
                )
            ),
            packages_root=Path(
                values.get(
                    "ATRIO_PACKAGES_ROOT",
                    str(repository_root / "packages"),
                )
            ),
            ui_path=Path(
                values.get(
                    "ATRIO_UI_PATH",
                    str(repository_root / "ATRIO-Core-Orchestrator.html"),
                )
            ),
        )


def create_container_app() -> FastAPI:
    """Monta todas as dependências usando somente arquivos de segredo."""

    settings = ContainerSettings.from_environment()
    database_password = _read_secret(
        settings.database_password_file,
        "senha PostgreSQL",
    )
    repository = PostgresExecutionRepository.from_parameters(
        host=settings.database_host,
        port=settings.database_port,
        dbname=settings.database_name,
        user=settings.database_user,
        password=database_password,
        connect_timeout=5,
        application_name=f"atrio-api-container/{__version__}",
    )
    database_password = ""
    repository.verify_schema()

    vault_passphrase = _read_secret(
        settings.vault_passphrase_file,
        "frase secreta do cofre",
    )
    store = EncryptedCorpusStore.from_passphrase(
        settings.vault_root,
        vault_passphrase,
    )
    vault_passphrase = ""
    corpus_workflow = default_corpus_workflow(
        repository,
        store,
        packages_root=settings.packages_root,
        scratch_root=settings.vault_root / "scratch",
        expected_pii_version=ACTIVE_RELEASE.atrio_pii_version,
    )

    ollama_model = os.environ.get("ATRIO_OLLAMA_MODEL", "").strip()
    ollama = None
    ratio_executor = None
    cerne_workflow = None
    lux_workflow = None
    if ollama_model:
        ollama = OllamaAdapter(
            os.environ.get(
                "ATRIO_OLLAMA_URL",
                "http://atrio_ollama:11434",
            ),
            default_options={
                "num_ctx": _positive_int(
                    os.environ.get(
                        "ATRIO_OLLAMA_NUM_CTX",
                        str(DEFAULT_NUM_CTX),
                    ),
                    "ATRIO_OLLAMA_NUM_CTX",
                ),
                "num_predict": _positive_int(
                    os.environ.get(
                        "ATRIO_OLLAMA_NUM_PREDICT",
                        str(DEFAULT_NUM_PREDICT),
                    ),
                    "ATRIO_OLLAMA_NUM_PREDICT",
                ),
            },
        )
        ratio_executor = RatioPhaseExecutor(
            store,
            ollama,
            model=ollama_model,
            ratio_root=settings.packages_root / "ratio",
        )
        cerne_workflow = default_cerne_workflow(
            repository,
            store,
            AtrioOllamaCerneProvider(ollama, model=ollama_model),
            knowledge_root=settings.packages_root / "cerne",
        )
        lux_workflow = default_lux_workflow(
            repository,
            store,
            ollama,
            model=ollama_model,
            knowledge_root=settings.packages_root / "lux",
            pii_source=settings.packages_root / "atrio_pii" / "atrio_pii.py",
        )

    def readiness_check() -> None:
        repository.verify_schema()
        store.verify()
        corpus_workflow.verify_tools()
        if ollama is not None:
            ollama.healthcheck()
            ollama.model_identity(ollama_model)
        if cerne_workflow is not None:
            cerne_workflow.verify()
        if lux_workflow is not None:
            lux_workflow.verify()

    return create_app(
        ExecutionService(repository),
        release=ACTIVE_RELEASE,
        readiness_check=readiness_check,
        corpus_intake=CorpusIntakeService(repository, store),
        corpus_workflow=corpus_workflow,
        ratio_workflow=default_ratio_workflow(
            repository,
            ratio_root=settings.packages_root / "ratio",
            executor=ratio_executor,
        ),
        cerne_workflow=cerne_workflow,
        lux_workflow=lux_workflow,
        ui_path=settings.ui_path,
    )


def _read_secret(path: Path, label: str) -> str:
    try:
        value = path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise RuntimeError(
            f"Arquivo de {label} indisponível: {path}."
        ) from exc
    if not value:
        raise RuntimeError(f"Arquivo de {label} está vazio.")
    if "\x00" in value or "\n" in value or "\r" in value:
        raise RuntimeError(f"Arquivo de {label} contém formato inválido.")
    return value


def _positive_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise ValueError("Porta PostgreSQL inválida.") from exc
    if not 1 <= port <= 65535:
        raise ValueError("Porta PostgreSQL fora do intervalo válido.")
    return port


def _positive_int(value: str, name: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"{name} deve ser inteiro positivo.") from exc
    if parsed < 1:
        raise ValueError(f"{name} deve ser inteiro positivo.")
    return parsed


def _database_identifier(value: str, label: str) -> str:
    if not _DB_IDENTIFIER.fullmatch(value):
        raise ValueError(f"Identificador de {label} inválido.")
    return value


def _required_text(value: str, label: str) -> str:
    if not value or value.strip() != value:
        raise ValueError(f"{label.capitalize()} inválido.")
    return value
