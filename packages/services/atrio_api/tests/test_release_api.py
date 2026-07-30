from __future__ import annotations

from dataclasses import replace
import unittest
from uuid import uuid4

from fastapi.testclient import TestClient

from atrio_api.api import create_app
from atrio_api.domain import (
    ArtifactRef,
    ComponentName,
    Destination,
    ExecutionStage,
    ExecutionState,
    RatioModule,
)
from atrio_api.release_catalog import ACTIVE_RELEASE
from atrio_api.repository import InMemoryExecutionRepository
from atrio_api.service import ExecutionService


def _lux_artifact() -> ArtifactRef:
    return ArtifactRef(
        artifact_id=str(uuid4()),
        sha256="e" * 64,
        media_type="application/vnd.atrio.lux+json",
        classification="INTERNAL_CONTROLLED",
        producer=ComponentName.LUX,
        producer_version=ACTIVE_RELEASE.lux_version,
        release_id=ACTIVE_RELEASE.release_id,
        schema_version=ACTIVE_RELEASE.schema_version,
    )


def _execution(
    stage: ExecutionStage,
    *,
    state_version: int = 11,
) -> ExecutionState:
    return ExecutionState(
        execution_id=str(uuid4()),
        tenant_id="release-api-test",
        created_by="tester",
        ratio_module=RatioModule.RI,
        destination=Destination.PUBLICO,
        release=ACTIVE_RELEASE,
        stage=stage,
        state_version=state_version,
        lux_artifact=_lux_artifact(),
    )


class ReleaseApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = InMemoryExecutionRepository()
        self.service = ExecutionService(self.repository)
        self.client = TestClient(
            create_app(
                self.service,
                release=ACTIVE_RELEASE,
                readiness_check=lambda: None,
            )
        )

    def _store(self, state: ExecutionState) -> None:
        self.repository.create(
            state,
            idempotency_key=f"store-{state.execution_id}",
            request_fingerprint=state.execution_id,
        )

    def test_pass_final_integrity_marks_execution_ready(self):
        state = _execution(ExecutionStage.FINAL_INTEGRITY_CHECK)
        self._store(state)

        response = self.client.post(
            f"/v1/executions/{state.execution_id}/final-integrity/pass",
            json={
                "expected_version": state.state_version,
                "actor_id": "revisor_final",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["stage"], "READY_FOR_RELEASE")
        event = self.repository.events(state.execution_id)[-1]
        self.assertEqual(event.command.value, "PASS_FINAL_INTEGRITY")
        self.assertEqual(event.actor_id, "revisor_final")

    def test_fail_final_integrity_records_reason_and_blocks(self):
        state = _execution(ExecutionStage.FINAL_INTEGRITY_CHECK)
        self._store(state)

        response = self.client.post(
            f"/v1/executions/{state.execution_id}/final-integrity/fail",
            json={
                "expected_version": state.state_version,
                "actor_id": "revisor_final",
                "reason_code": "DIVERGENCIA_DE_INTEGRIDADE",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["stage"], "FINAL_INTEGRITY_BLOCK")
        self.assertEqual(
            body["waiting_reason"],
            "DIVERGENCIA_DE_INTEGRIDADE",
        )

    def test_retry_lux_clears_artifact_and_records_decision(self):
        state = _execution(ExecutionStage.FINAL_INTEGRITY_BLOCK)
        state = replace(
            state,
            waiting_reason="DIVERGENCIA_DE_INTEGRIDADE",
        )
        self._store(state)

        response = self.client.post(
            f"/v1/executions/{state.execution_id}/final-integrity/retry-lux",
            json={
                "expected_version": state.state_version,
                "actor_id": "revisor_final",
                "decision_code": "RETORNAR_AO_LUX",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["stage"], "LUX_REFINING")
        self.assertIsNone(body["lux_artifact"])
        self.assertEqual(body["last_operator_actor"], "revisor_final")
        self.assertEqual(body["last_operator_decision"], "RETORNAR_AO_LUX")

    def test_release_marks_execution_completed_and_pins_artifact(self):
        state = _execution(ExecutionStage.READY_FOR_RELEASE)
        self._store(state)

        response = self.client.post(
            f"/v1/executions/{state.execution_id}/release",
            json={
                "expected_version": state.state_version,
                "actor_id": "operador_release",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["stage"], "RELEASED")
        self.assertEqual(body["status"], "COMPLETED")
        self.assertEqual(
            body["released_artifact"]["artifact_id"],
            state.lux_artifact.artifact_id,
        )

    def test_final_routes_keep_version_and_stage_guards(self):
        state = _execution(ExecutionStage.FINAL_INTEGRITY_CHECK)
        self._store(state)

        stale = self.client.post(
            f"/v1/executions/{state.execution_id}/final-integrity/pass",
            json={
                "expected_version": state.state_version - 1,
                "actor_id": "revisor_final",
            },
        )
        wrong_stage = self.client.post(
            f"/v1/executions/{state.execution_id}/release",
            json={
                "expected_version": state.state_version,
                "actor_id": "operador_release",
            },
        )

        self.assertEqual(stale.status_code, 409)
        self.assertEqual(
            stale.json()["error"]["code"],
            "STATE_VERSION_CONFLICT",
        )
        self.assertEqual(wrong_stage.status_code, 409)
        self.assertEqual(
            wrong_stage.json()["error"]["code"],
            "INVALID_TRANSITION",
        )

    def test_failure_and_retry_codes_are_required(self):
        state = _execution(ExecutionStage.FINAL_INTEGRITY_CHECK)
        blocked = _execution(ExecutionStage.FINAL_INTEGRITY_BLOCK)
        self._store(state)
        self._store(blocked)

        missing_reason = self.client.post(
            f"/v1/executions/{state.execution_id}/final-integrity/fail",
            json={
                "expected_version": state.state_version,
                "actor_id": "revisor_final",
            },
        )
        missing_decision = self.client.post(
            f"/v1/executions/{blocked.execution_id}/final-integrity/retry-lux",
            json={
                "expected_version": blocked.state_version,
                "actor_id": "revisor_final",
            },
        )

        self.assertEqual(missing_reason.status_code, 422)
        self.assertEqual(missing_decision.status_code, 422)
        self.assertEqual(
            missing_reason.json()["error"]["code"],
            "REQUEST_VALIDATION_FAILED",
        )
        self.assertEqual(
            missing_decision.json()["error"]["code"],
            "REQUEST_VALIDATION_FAILED",
        )


if __name__ == "__main__":
    unittest.main()
