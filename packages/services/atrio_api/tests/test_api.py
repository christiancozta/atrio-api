from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

SERVICE_ROOT = Path(__file__).resolve().parents[1]
SRC = SERVICE_ROOT / "src"
sys.path.insert(0, str(SRC))

from fastapi.testclient import TestClient  # noqa: E402

from atrio_api.api import create_app  # noqa: E402
from atrio_api.corpus_intake import (  # noqa: E402
    CorpusIntakeConflict,
    CorpusIntakeRecordResult,
    CorpusIntakeRef,
    document_id_for,
)
from atrio_api.domain import Command, CommandKind, ExecutionStage  # noqa: E402
from atrio_api.release_catalog import ACTIVE_RELEASE  # noqa: E402
from atrio_api.repository import InMemoryExecutionRepository  # noqa: E402
from atrio_api.service import ExecutionService  # noqa: E402


class FakeCorpusIntake:
    def __init__(self, repository):
        self.repository = repository
        self.intakes = {}

    async def ingest(
        self,
        chunks,
        *,
        execution_id,
        idempotency_key,
        actor_id,
        expected_version,
        media_type,
    ):
        content = b"".join([chunk async for chunk in chunks])
        document_id = document_id_for(execution_id, idempotency_key)
        intake = CorpusIntakeRef(
            document_id=document_id,
            execution_id=execution_id,
            idempotency_key=idempotency_key,
            created_by=actor_id,
            sha256=hashlib.sha256(content).hexdigest(),
            byte_length=len(content),
            media_type=media_type,
            storage_key=f"corpus/{document_id}.atrio",
        )
        previous = self.intakes.get(document_id)
        if previous is not None:
            if previous != intake:
                raise CorpusIntakeConflict
            return CorpusIntakeRecordResult(
                state=self.repository.get(execution_id),
                intake=previous,
                created=False,
            )
        current = self.repository.get(execution_id)
        kind = (
            CommandKind.START_INGESTION
            if current.stage is ExecutionStage.CREATED
            else CommandKind.REGISTER_CORPUS_DOCUMENT
        )
        result = self.repository.apply(
            execution_id,
            Command(
                kind=kind,
                expected_version=expected_version,
                actor_id=actor_id,
                payload={
                    "document_id": document_id,
                    "document_sha256": intake.sha256,
                },
            ),
        )
        self.intakes[document_id] = intake
        return CorpusIntakeRecordResult(
            state=result.state,
            intake=intake,
            created=True,
        )


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.repository = InMemoryExecutionRepository()
        self.app = create_app(
            ExecutionService(self.repository),
            release=ACTIVE_RELEASE,
            readiness_check=lambda: None,
            corpus_intake=FakeCorpusIntake(self.repository),
        )
        self.client = TestClient(self.app)
        self.create_body = {
            "tenant_id": "tenant-api-test",
            "actor_id": "operador-api-test",
            "ratio_module": "RI",
            "destination": "interno",
        }
        self.headers = {"Idempotency-Key": "api-test-001"}

    def _create(self):
        return self.client.post(
            "/v1/executions",
            headers=self.headers,
            json=self.create_body,
        )

    def test_health_exposes_versions_and_release(self):
        live = self.client.get("/v1/health/live")
        ready = self.client.get("/v1/health/ready")

        self.assertEqual(live.status_code, 200)
        self.assertEqual(live.json()["atrio_api_version"], "0.7.0")
        self.assertEqual(ready.status_code, 200)
        self.assertEqual(
            ready.json()["release_id"],
            ACTIVE_RELEASE.release_id,
        )
        self.assertEqual(
            ready.json()["database_schema_version"],
            "1.3.0",
        )
        self.assertEqual(
            ready.json()["corpus_intake_version"],
            "1.0.0",
        )
        self.assertEqual(
            ready.json()["vault_envelope_version"],
            "ATRIO-V1",
        )
        self.assertEqual(
            ready.json()["corpus_pipeline_version"],
            "1.5.0",
        )

    def test_root_serves_versioned_interface_without_cache(self):
        with TemporaryDirectory() as directory:
            ui_path = Path(directory) / "atrio.html"
            ui_path.write_text(
                "<!doctype html><title>ATRIO</title>",
                encoding="utf-8",
            )
            app = create_app(
                ExecutionService(self.repository),
                release=ACTIVE_RELEASE,
                readiness_check=lambda: None,
                corpus_intake=FakeCorpusIntake(self.repository),
                ui_path=ui_path,
            )

            response = TestClient(app).get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response.headers["content-type"].startswith("text/html")
        )
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual(
            response.headers["x-content-type-options"],
            "nosniff",
        )
        self.assertIn("<title>ATRIO</title>", response.text)

    def test_create_is_idempotent_and_server_pins_release(self):
        first = self._create()
        second = self._create()

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertTrue(first.json()["created"])
        self.assertFalse(second.json()["created"])
        self.assertEqual(
            first.json()["execution"]["execution_id"],
            second.json()["execution"]["execution_id"],
        )
        release = first.json()["execution"]["release"]
        self.assertEqual(release["corpus_version"], "1.5.0")
        self.assertEqual(release["ratio_version"], "7.0.0")
        self.assertEqual(release["cerne_module_version"], "1.2.0")
        self.assertEqual(release["lux_version"], "6.0.0")

    def test_command_persists_event_and_stale_version_is_conflict(self):
        created = self._create().json()["execution"]
        execution_id = created["execution_id"]
        command = {
            "kind": "START_INGESTION",
            "expected_version": 0,
            "actor_id": "operador-api-test",
        }

        accepted = self.client.post(
            f"/v1/executions/{execution_id}/commands",
            json=command,
        )
        stale = self.client.post(
            f"/v1/executions/{execution_id}/commands",
            json=command,
        )
        events = self.client.get(
            f"/v1/executions/{execution_id}/events"
        )

        self.assertEqual(accepted.status_code, 200)
        self.assertEqual(accepted.json()["stage"], "CORPUS_INGESTING")
        self.assertEqual(stale.status_code, 409)
        self.assertEqual(
            stale.json()["error"]["code"],
            "STATE_VERSION_CONFLICT",
        )
        self.assertEqual(events.status_code, 200)
        self.assertEqual(len(events.json()), 1)
        self.assertEqual(events.json()[0]["component_version"], "1.5.0")

    def test_validation_response_does_not_echo_forbidden_payload(self):
        created = self._create().json()["execution"]
        secret = "SEGREDO_JURIDICO_NAO_PODE_VAZAR"
        response = self.client.post(
            f"/v1/executions/{created['execution_id']}/commands",
            json={
                "kind": "START_INGESTION",
                "expected_version": 0,
                "actor_id": "operador-api-test",
                "payload": {"legal_text": secret},
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertNotIn(secret, response.text)
        self.assertEqual(
            response.json()["error"]["code"],
            "REQUEST_VALIDATION_FAILED",
        )

    def test_missing_execution_returns_stable_error_code(self):
        response = self.client.get(
            "/v1/executions/00000000-0000-0000-0000-000000000000"
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json()["error"]["code"],
            "EXECUTION_NOT_FOUND",
        )

    def test_corpus_document_intake_is_idempotent_and_versioned(self):
        created = self._create().json()["execution"]
        execution_id = created["execution_id"]
        headers = {
            "Idempotency-Key": "documento-api-001",
            "X-ATRIO-Expected-Version": "0",
            "X-ATRIO-Actor": "operador-api-test",
            "Content-Type": "application/pdf",
        }
        document = b"%PDF-1.7\nconteudo-de-teste"

        first = self.client.post(
            f"/v1/executions/{execution_id}/corpus/documents",
            headers=headers,
            content=document,
        )
        repeated = self.client.post(
            f"/v1/executions/{execution_id}/corpus/documents",
            headers=headers,
            content=document,
        )
        events = self.client.get(
            f"/v1/executions/{execution_id}/events"
        )

        self.assertEqual(first.status_code, 201)
        self.assertEqual(repeated.status_code, 200)
        self.assertTrue(first.json()["created"])
        self.assertFalse(repeated.json()["created"])
        self.assertEqual(
            first.json()["document"]["document_id"],
            repeated.json()["document"]["document_id"],
        )
        self.assertEqual(
            first.json()["execution"]["stage"],
            "CORPUS_INGESTING",
        )
        self.assertEqual(
            first.json()["execution"]["state_version"],
            1,
        )
        self.assertEqual(len(events.json()), 1)
        self.assertNotIn("storage_key", first.text)

    def test_generic_command_cannot_forge_document_registration(self):
        created = self._create().json()["execution"]
        started = self.client.post(
            f"/v1/executions/{created['execution_id']}/commands",
            json={
                "kind": "START_INGESTION",
                "expected_version": 0,
                "actor_id": "operador-api-test",
            },
        )
        forged = self.client.post(
            f"/v1/executions/{created['execution_id']}/commands",
            json={
                "kind": "REGISTER_CORPUS_DOCUMENT",
                "expected_version": 1,
                "actor_id": "operador-api-test",
            },
        )

        self.assertEqual(started.status_code, 200)
        self.assertEqual(forged.status_code, 422)
        self.assertEqual(
            forged.json()["error"]["code"],
            "INVALID_COMMAND_PAYLOAD",
        )

    def test_generic_command_cannot_forge_corpus_handoff(self):
        created = self._create().json()["execution"]
        response = self.client.post(
            f"/v1/executions/{created['execution_id']}/commands",
            json={
                "kind": "COMPLETE_CORPUS",
                "expected_version": 0,
                "actor_id": "operador-api-test",
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json()["error"]["code"],
            "INVALID_COMMAND_PAYLOAD",
        )

    def test_corpus_workflow_routes_fail_closed_when_not_configured(self):
        created = self._create().json()["execution"]
        response = self.client.get(
            (
                f"/v1/executions/{created['execution_id']}"
                "/corpus/documents"
            )
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json()["error"]["code"],
            "CORPUS_WORKFLOW_UNAVAILABLE",
        )

    def test_document_size_is_rejected_before_streaming(self):
        created = self._create().json()["execution"]
        response = self.client.post(
            (
                f"/v1/executions/{created['execution_id']}"
                "/corpus/documents"
            ),
            headers={
                "Idempotency-Key": "documento-grande",
                "X-ATRIO-Expected-Version": "0",
                "X-ATRIO-Actor": "operador-api-test",
                "Content-Type": "application/pdf",
                "Content-Length": str(50 * 1024 * 1024 + 1),
            },
            content=b"x",
        )

        self.assertEqual(response.status_code, 413)
        self.assertEqual(
            response.json()["error"]["code"],
            "DOCUMENT_TOO_LARGE",
        )


if __name__ == "__main__":
    unittest.main()
