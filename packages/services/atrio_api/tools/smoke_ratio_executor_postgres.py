from __future__ import annotations

import getpass
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from fastapi.testclient import TestClient

from atrio_api.adapters.ollama import InferenceMetadata, InferenceResult
from atrio_api.api import create_app
from atrio_api.corpus_intake import EncryptedCorpusStore
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
from atrio_api.ratio.execution import RatioPhaseExecutor
from atrio_api.ratio.service import default_ratio_workflow
from atrio_api.release_catalog import ACTIVE_RELEASE
from atrio_api.service import ExecutionService


SERVICE_ROOT = Path(__file__).resolve().parents[1]
PACKAGES_ROOT = SERVICE_ROOT.parents[1]


class DeterministicProvider:
    def generate(
        self,
        prompt,
        *,
        model,
        system=None,
        options=None,
        format_schema=None,
    ):
        phase = format_schema["properties"]["phase"]["enum"][0]
        payload = {
            "phase": phase,
            "analysis": f"analysis:{phase}",
            "findings": [f"finding:{phase}"],
            "conclusion": f"conclusion:{phase}",
            "risk_codes": [],
            "operator_attention": [],
        }
        if "counterfactual" in format_schema["properties"]:
            payload["counterfactual"] = {
                "adversarial_route": "adversarial",
                "breaking_point": "breaking-point",
                "alternative_route": "alternative",
                "residual_risk": "residual",
            }
        if "audit_target" in format_schema["properties"]:
            object_type = format_schema["properties"]["audit_target"][
                "properties"
            ]["object_type"]["enum"][0]
            payload["audit_target"] = {
                "object_type": object_type,
                "text": (
                    "VOTO. O recurso foi examinado a partir do material "
                    "pseudonimizado. A fundamentação final enfrenta os pontos "
                    "relevantes e apresenta conclusão decisória auditável."
                ),
            }
        content = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        return InferenceResult(
            content=content,
            metadata=InferenceMetadata(
                adapter_version="smoke",
                model=model,
                model_digest="0" * 64,
                prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                response_sha256=hashlib.sha256(content.encode()).hexdigest(),
                options_sha256="1" * 64,
                prompt_chars=len(prompt),
                response_chars=len(content),
            ),
        )


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

    with TemporaryDirectory() as temp:
        store = EncryptedCorpusStore(Path(temp) / "vault", b"s" * 32)
        token = uuid4().hex
        execution_id = str(uuid4())
        actor = "ratio-executor-smoke"

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
                {"execution_id": execution_id, "smoke": "ratio-executor"}
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

        corpus_bundle = json.dumps(
            {
                "corpus_pipeline_version": "smoke",
                "corpus_version": ACTIVE_RELEASE.corpus_version,
                "documents": [
                    {
                        "inventory": {"effective_status": "READY"},
                        "pseudonymized_text": "Fato pseudonimizado de teste.",
                    }
                ],
                "execution_id": execution_id,
                "release_id": ACTIVE_RELEASE.release_id,
                "schema_version": ACTIVE_RELEASE.schema_version,
            },
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        corpus_id = str(uuid4())
        store.write_private_record(
            f"artifacts/{execution_id}/{corpus_id}.atrio",
            corpus_bundle,
        )
        corpus_artifact = ArtifactRef(
            artifact_id=corpus_id,
            sha256=hashlib.sha256(corpus_bundle).hexdigest(),
            media_type="application/vnd.atrio.corpus+json",
            classification="INTERNAL_PSEUDONYMIZED",
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

        executor = RatioPhaseExecutor(
            store,
            DeterministicProvider(),
            model="deterministic-smoke",
            ratio_root=PACKAGES_ROOT / "ratio",
        )
        workflow = default_ratio_workflow(
            repository,
            ratio_root=PACKAGES_ROOT / "ratio",
            executor=executor,
        )
        client = TestClient(
            create_app(
                ExecutionService(repository),
                release=ACTIVE_RELEASE,
                readiness_check=repository.verify_schema,
                ratio_workflow=workflow,
            )
        )

        start = client.post(
            f"/v1/executions/{execution_id}/ratio/start",
            headers={"Idempotency-Key": f"start-{token}"},
            json={
                "expected_version": corpus_ready.state.state_version,
                "actor_id": actor,
            },
        )
        assert start.status_code == 201, start.text
        macro_version = start.json()["execution"]["state_version"]
        state = start.json()["ratio"]

        while True:
            phase = state["current_phase"]
            execute_key = f"exec-{phase}-{token}"
            executed = client.post(
                f"/v1/executions/{execution_id}/ratio/execute",
                headers={"Idempotency-Key": execute_key},
                json={
                    "expected_revision": state["revision"],
                    "actor_id": actor,
                },
            )
            assert executed.status_code == 200, executed.text
            state = executed.json()["ratio"]

            if phase == "RI_03":
                troia = client.post(
                    f"/v1/executions/{execution_id}/ratio/actions",
                    headers={"Idempotency-Key": f"troia-{token}"},
                    json={
                        "action": "VALIDATE_TROIA",
                        "expected_revision": state["revision"],
                        "actor_id": actor,
                    },
                )
                assert troia.status_code == 200, troia.text
                state = troia.json()["ratio"]

            validated = client.post(
                f"/v1/executions/{execution_id}/ratio/actions",
                headers={"Idempotency-Key": f"validate-{phase}-{token}"},
                json={
                    "action": "VALIDATE",
                    "expected_revision": state["revision"],
                    "actor_id": actor,
                },
            )
            assert validated.status_code == 200, validated.text
            state = validated.json()["ratio"]

            phases = [item["phase"] for item in state["phases"]]
            if phase == phases[-1]:
                break

            advanced = client.post(
                f"/v1/executions/{execution_id}/ratio/actions",
                headers={"Idempotency-Key": f"advance-{phase}-{token}"},
                json={
                    "action": "ADVANCE",
                    "expected_revision": state["revision"],
                    "actor_id": actor,
                },
            )
            assert advanced.status_code == 200, advanced.text
            state = advanced.json()["ratio"]

        final = client.post(
            f"/v1/executions/{execution_id}/ratio/finalize",
            headers={"Idempotency-Key": f"final-{token}"},
            json={
                "expected_revision": state["revision"],
                "expected_version": macro_version,
                "actor_id": actor,
            },
        )
        assert final.status_code == 200, final.text
        assert final.json()["execution"]["stage"] == "RATIO_READY"
        assert final.json()["execution"]["ratio_artifact"] is not None

        records = repository.list_ratio_artifacts(execution_id)
        assert any(item.role == "FINAL_HANDOFF" for item in records)
        assert any(item.role == "TROIA:RI_03" for item in records)

        blocked = client.post(
            f"/v1/executions/{execution_id}/commands",
            json={
                "kind": "START_CERNE",
                "expected_version": final.json()["execution"]["state_version"],
                "actor_id": actor,
                "payload": {},
            },
        )
        assert blocked.status_code == 422, blocked.text

        print("OK: RI_01 -> RI_06 executado por provedor estruturado")
        print("OK: cada fase gerou artefato criptografado e referenciado")
        print("OK: RI_03 gerou artefato TROIA e exigiu validação")
        print("OK: decisões do operador foram persistidas por revisão")
        print("OK: FINALIZE gerou handoff RATIO e COMPLETE_RATIO atômico")
        print("OK: execução terminou em RATIO_READY")
        print("OK: START_CERNE ficou bloqueado até o runtime CERNE governado")
        print(f"execution_id: {execution_id}")


if __name__ == "__main__":
    main()
