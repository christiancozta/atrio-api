from __future__ import annotations

import getpass
import hashlib
from uuid import uuid4

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
from atrio_api.ratio import (
    validate_current_phase,
)
from atrio_api.release_catalog import ACTIVE_RELEASE


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
    actor = "ratio-postgres-smoke"

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
            {"execution_id": execution_id, "smoke": "ratio-postgres"}
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
        artifact_id=f"smoke-corpus-{token}",
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

    started = repository.start_ratio_runtime(
        execution_id,
        actor_id=actor,
        expected_version=corpus_ready.state.state_version,
        idempotency_key=f"ratio-start-{token}",
    )
    assert started.created
    assert started.ratio_state.revision == 0

    restarted_repository = PostgresExecutionRepository.from_parameters(
        host="127.0.0.1",
        port=5432,
        dbname="atrio",
        user="atrio_app",
        password=password,
    )
    loaded_zero = restarted_repository.get_ratio_runtime(execution_id)
    assert loaded_zero == started.ratio_state

    revision_one = validate_current_phase(loaded_zero)
    persisted = restarted_repository.persist_ratio_transition(
        execution_id,
        previous=loaded_zero,
        updated=revision_one,
        action="VALIDATE",
        actor_id=actor,
        idempotency_key=f"ratio-r1-{token}",
    )
    assert persisted.created
    assert persisted.ratio_state == revision_one

    retried = restarted_repository.persist_ratio_transition(
        execution_id,
        previous=loaded_zero,
        updated=revision_one,
        action="VALIDATE",
        actor_id=actor,
        idempotency_key=f"ratio-r1-{token}",
    )
    assert not retried.created
    assert retried.ratio_state == revision_one

    loaded_one = repository.get_ratio_runtime(execution_id)
    assert loaded_one == revision_one

    repository.apply(
        execution_id,
        Command(
            kind=CommandKind.CANCEL,
            expected_version=started.execution_state.state_version,
            actor_id=actor,
        ),
    )

    print("OK: RATIO PostgreSQL start transacional")
    print("OK: snapshot r0 reconstruído após novo repository")
    print("OK: transição r0 -> r1 persistida")
    print("OK: retry idempotente não duplicou revisão")
    print("OK: snapshot r1 reconstruído e hash validado")
    print(f"execution_id: {execution_id}")


if __name__ == "__main__":
    main()
