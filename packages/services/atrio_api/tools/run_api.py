from __future__ import annotations

import argparse
import getpass
from pathlib import Path

import uvicorn

from atrio_api import __version__
from atrio_api.api import create_app
from atrio_api.corpus_intake import EncryptedCorpusStore, CorpusIntakeService
from atrio_api.corpus_service import default_corpus_workflow
from atrio_api.cerne.provider import AtrioOllamaCerneProvider
from atrio_api.cerne.service import default_cerne_workflow
from atrio_api.lux.service import default_lux_workflow
from atrio_api.adapters.ollama import OllamaAdapter
from atrio_api.ratio.execution import RatioPhaseExecutor
from atrio_api.postgres_repository import PostgresExecutionRepository
from atrio_api.ratio.service import default_ratio_workflow
from atrio_api.release_catalog import ACTIVE_RELEASE
from atrio_api.service import ExecutionService


SERVICE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = SERVICE_ROOT.parents[2]
PACKAGES_ROOT = SERVICE_ROOT.parents[1]
DEFAULT_UI_PATH = REPOSITORY_ROOT / "ATRIO-Core-Orchestrator.html"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inicia a API interna local do ATRIO."
    )
    parser.add_argument("--api-port", default=8080, type=int)
    parser.add_argument("--database-host", default="127.0.0.1")
    parser.add_argument("--database-port", default=5432, type=int)
    parser.add_argument("--database-name", default="atrio")
    parser.add_argument("--database-user", default="atrio_app")
    parser.add_argument(
        "--ollama-url",
        default="http://127.0.0.1:11434",
    )
    parser.add_argument(
        "--ollama-model",
        default=None,
        help="Modelo local pinado para execução generativa de RATIO, CERNE e LUX.",
    )
    parser.add_argument(
        "--vault-root",
        type=Path,
        default=SERVICE_ROOT / "var" / "vault",
    )
    parser.add_argument(
        "--ui-path",
        type=Path,
        default=DEFAULT_UI_PATH,
        help="Arquivo HTML servido em / pela API local.",
    )
    args = parser.parse_args()

    password = getpass.getpass(
        f"Senha PostgreSQL de {args.database_user}: "
    )
    repository = PostgresExecutionRepository.from_parameters(
        host=args.database_host,
        port=args.database_port,
        dbname=args.database_name,
        user=args.database_user,
        password=password,
        connect_timeout=5,
        application_name=f"atrio-api/{__version__}",
    )
    password = ""
    repository.verify_schema()

    first_vault_start = not (args.vault_root / "vault.salt").exists()
    vault_passphrase = getpass.getpass(
        "Frase secreta do cofre documental: "
    )
    if first_vault_start:
        confirmation = getpass.getpass(
            "Confirme a frase secreta do cofre: "
        )
        if confirmation != vault_passphrase:
            raise ValueError("As frases secretas do cofre não coincidem.")
        confirmation = ""
    store = EncryptedCorpusStore.from_passphrase(
        args.vault_root,
        vault_passphrase,
    )
    vault_passphrase = ""
    corpus_workflow = default_corpus_workflow(
        repository,
        store,
        packages_root=PACKAGES_ROOT,
        scratch_root=args.vault_root / "scratch",
        expected_pii_version=ACTIVE_RELEASE.atrio_pii_version,
    )

    ollama = None
    ratio_executor = None
    cerne_workflow = None
    lux_workflow = None
    if args.ollama_model:
        ollama = OllamaAdapter(args.ollama_url)
        ratio_executor = RatioPhaseExecutor(
            store,
            ollama,
            model=args.ollama_model,
            ratio_root=PACKAGES_ROOT / "ratio",
        )
        cerne_workflow = default_cerne_workflow(
            repository,
            store,
            AtrioOllamaCerneProvider(
                ollama,
                model=args.ollama_model,
            ),
            knowledge_root=PACKAGES_ROOT / "cerne",
        )
        lux_workflow = default_lux_workflow(
            repository,
            store,
            ollama,
            model=args.ollama_model,
            knowledge_root=PACKAGES_ROOT / "lux",
            pii_source=PACKAGES_ROOT / "atrio_pii" / "atrio_pii.py",
        )

    def readiness_check() -> None:
        repository.verify_schema()
        store.verify()
        corpus_workflow.verify_tools()
        if ollama is not None:
            ollama.healthcheck()
            ollama.model_identity(args.ollama_model)
        if cerne_workflow is not None:
            cerne_workflow.verify()
        if lux_workflow is not None:
            lux_workflow.verify()

    app = create_app(
        ExecutionService(repository),
        release=ACTIVE_RELEASE,
        readiness_check=readiness_check,
        corpus_intake=CorpusIntakeService(repository, store),
        corpus_workflow=corpus_workflow,
        ratio_workflow=default_ratio_workflow(
            repository,
            ratio_root=PACKAGES_ROOT / "ratio",
            executor=ratio_executor,
        ),
        cerne_workflow=cerne_workflow,
        lux_workflow=lux_workflow,
        ui_path=args.ui_path,
    )
    print(f"ATRIO API {__version__}")
    print(f"Release ativa: {ACTIVE_RELEASE.release_id}")
    print(f"Cofre documental: {args.vault_root.resolve()}")
    print(f"Interface: http://127.0.0.1:{args.api_port}/")
    print(f"API local: http://127.0.0.1:{args.api_port}")
    print(f"Documentação: http://127.0.0.1:{args.api_port}/docs")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=args.api_port,
        log_level="info",
        access_log=False,
        server_header=False,
        date_header=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
