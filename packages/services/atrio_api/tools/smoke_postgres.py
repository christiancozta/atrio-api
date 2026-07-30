from __future__ import annotations

import argparse
import getpass
import hashlib
import sys
from pathlib import Path

SERVICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_ROOT / "src"))

from atrio_api import __version__  # noqa: E402
from atrio_api.domain import (  # noqa: E402
    Command,
    CommandKind,
    CreateExecutionRequest,
    Destination,
    ExecutionStage,
    RatioModule,
    ReleaseEnvelope,
)
from atrio_api.postgres_repository import (  # noqa: E402
    PostgresExecutionRepository,
)
from atrio_api.service import ExecutionService  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida o adaptador PostgreSQL sem armazenar a senha."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=5432, type=int)
    parser.add_argument("--database", default="atrio")
    parser.add_argument("--user", default="atrio_app")
    args = parser.parse_args()

    password = getpass.getpass(f"Senha PostgreSQL de {args.user}: ")
    repository = PostgresExecutionRepository.from_parameters(
        host=args.host,
        port=args.port,
        dbname=args.database,
        user=args.user,
        password=password,
        connect_timeout=5,
        application_name=f"atrio-api/{__version__}/smoke",
    )
    password = ""

    repository.verify_schema()
    service = ExecutionService(repository)
    release = _smoke_release()
    request = CreateExecutionRequest(
        tenant_id="_atrio_system",
        actor_id="postgres-smoke",
        idempotency_key=f"postgres-adapter-smoke-{__version__}",
        ratio_module=RatioModule.RI,
        destination=Destination.INTERNO,
    )

    first = service.create(request, release)
    second = service.create(request, release)
    if first.state.execution_id != second.state.execution_id:
        raise RuntimeError("A idempotência retornou execuções diferentes.")

    state = second.state
    if state.stage is ExecutionStage.CREATED:
        state = service.command(
            state.execution_id,
            Command(
                kind=CommandKind.START_INGESTION,
                expected_version=state.state_version,
                actor_id="postgres-smoke",
            ),
        ).state

    if state.stage is not ExecutionStage.CANCELLED:
        if state.stage is ExecutionStage.RELEASED:
            raise RuntimeError("Execução smoke inesperadamente liberada.")
        state = service.command(
            state.execution_id,
            Command(
                kind=CommandKind.CANCEL,
                expected_version=state.state_version,
                actor_id="postgres-smoke",
            ),
        ).state

    persisted = service.get(state.execution_id)
    events = repository.events(state.execution_id)
    if persisted != state:
        raise RuntimeError("Estado lido difere do estado persistido.")
    if not events or events[-1].to_stage is not ExecutionStage.CANCELLED:
        raise RuntimeError("Trilha de eventos do smoke test está incompleta.")

    print(f"Schema PostgreSQL: OK")
    print(f"ATRIO API: {__version__}")
    print(f"Execução idempotente: {state.execution_id}")
    print(f"Estado final: {state.stage.value}")
    print(f"Eventos persistidos: {len(events)}")
    print("Adaptador PostgreSQL: OK")
    return 0


def _smoke_release() -> ReleaseEnvelope:
    prompt_hash = hashlib.sha256(
        f"atrio-smoke-prompt/{__version__}".encode("utf-8")
    ).hexdigest()
    return ReleaseEnvelope(
        release_id=f"atrio-local-smoke-{__version__}",
        atrio_api_version=__version__,
        corpus_version="1.5.0",
        ratio_version="7.0.0",
        cerne_module_version="1.2.0",
        cerne_service_build="0.2.0",
        lux_version="6.0.0",
        atrio_pii_version="1.0.0",
        prompt_bundle_hash=prompt_hash,
        schema_version="1.0.0",
    )


if __name__ == "__main__":
    raise SystemExit(main())
