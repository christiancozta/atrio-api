from __future__ import annotations

import getpass
import hashlib
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from atrio_api.api import create_app
from atrio_api.domain import (
    ArtifactRef,
    Command,
    CommandKind,
    ComponentName,
    Destination,
    ExecutionState,
    RatioModule,
)
from atrio_api.postgres_repository import (
    PostgresExecutionRepository,
    _payload_fingerprint,
)
from atrio_api.ratio.service import default_ratio_workflow
from atrio_api.release_catalog import ACTIVE_RELEASE
from atrio_api.service import ExecutionService


SERVICE_ROOT = Path(__file__).resolve().parents[1]
PACKAGES_ROOT = SERVICE_ROOT.parents[1]


def main() -> None:
    password = getpass.getpass("Senha PostgreSQL: ")
    repository = PostgresExecutionRepository.from_parameters(
        host="127.0.0.1",
        port=5432,
        dbname="atrio",
        user="atrio_app",
        password=password,
    )
    repository.verify_schema()

    token = uuid4().hex
    execution_id = str(uuid4())
    actor = "ratio-api-smoke"

    initial = ExecutionState(
        execution_id=execution_id,
        tenant_id="smoke",
        created_by=actor,
        ratio_module=RatioModule.RI,
        destination=Destination.INTERNO,
        release=ACTIVE_RELEASE,
    )
    repository.create(
        initial,
        idempotency_key=f"create-{token}",
        request_fingerprint=_payload_fingerprint(
            {"execution_id": execution_id, "smoke": "ratio-api"}
        ),
    )
    ingestion = repository.apply(
        execution_id,
        Command(
            kind=CommandKind.START_INGESTION,
            expected_version=0,
            actor_id=actor,
        ),
    )
    corpus_artifact = ArtifactRef(
        artifact_id=f"smoke-api-corpus-{token}",
        sha256=hashlib.sha256(token.encode("utf-8")).hexdigest(),
        media_type="application/vnd.atrio.corpus+json",
        classification="internal",
        producer=ComponentName.CORPUS,
        producer_version=ACTIVE_RELEASE.corpus_version,
        release_id=ACTIVE_RELEASE.release_id,
        schema_version=ACTIVE_RELEASE.schema_version,
    )
    corpus_ready = repository.apply(
        execution_id,
        Command(
            kind=CommandKind.COMPLETE_CORPUS,
            expected_version=ingestion.state.state_version,
            actor_id=actor,
            payload={"artifact": corpus_artifact},
        ),
    )

    app = create_app(
        ExecutionService(repository),
        release=ACTIVE_RELEASE,
        readiness_check=repository.verify_schema,
        ratio_workflow=default_ratio_workflow(
            repository,
            ratio_root=PACKAGES_ROOT / "ratio",
        ),
    )
    client = TestClient(app)

    start_key = f"start-{token}"
    started = client.post(
        f"/v1/executions/{execution_id}/ratio/start",
        headers={"Idempotency-Key": start_key},
        json={
            "expected_version": corpus_ready.state.state_version,
            "actor_id": actor,
        },
    )
    assert started.status_code == 201, started.text
    assert started.json()["ratio"]["revision"] == 0

    state = client.get(f"/v1/executions/{execution_id}/ratio")
    assert state.status_code == 200, state.text
    assert state.json()["current_phase"] == "RI_01"

    action_key = f"validate-{token}"
    payload = {
        "action": "VALIDATE",
        "expected_revision": 0,
        "actor_id": actor,
    }
    validated = client.post(
        f"/v1/executions/{execution_id}/ratio/actions",
        headers={"Idempotency-Key": action_key},
        json=payload,
    )
    assert validated.status_code == 200, validated.text
    assert validated.json()["ratio"]["revision"] == 1

    retried = client.post(
        f"/v1/executions/{execution_id}/ratio/actions",
        headers={"Idempotency-Key": action_key},
        json=payload,
    )
    assert retried.status_code == 200, retried.text
    assert retried.json()["created"] is False
    assert retried.json()["ratio"]["revision"] == 1

    blocked = client.post(
        f"/v1/executions/{execution_id}/commands",
        json={
            "kind": "COMPLETE_RATIO",
            "expected_version": started.json()["execution"]["state_version"],
            "actor_id": actor,
            "payload": {},
        },
    )
    assert blocked.status_code == 422, blocked.text

    repository.apply(
        execution_id,
        Command(
            kind=CommandKind.CANCEL,
            expected_version=started.json()["execution"]["state_version"],
            actor_id=actor,
        ),
    )

    print("OK: /ratio/start -> START_RATIO + snapshot r0")
    print("OK: GET /ratio -> estado reconstruido do PostgreSQL")
    print("OK: /ratio/actions -> revisao r1 persistida")
    print("OK: retry HTTP idempotente -> mesma r1")
    print("OK: /commands bloqueia macro RATIO governada")
    print(f"execution_id: {execution_id}")


if __name__ == "__main__":
    main()
