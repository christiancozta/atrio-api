from __future__ import annotations

from dataclasses import replace
import unittest
from uuid import uuid4

from fastapi.testclient import TestClient

from atrio_api.api import create_app
from atrio_api.domain import (
    ArtifactRef,
    CerneGate,
    ComponentName,
    Destination,
    ExecutionStage,
    ExecutionState,
    RatioModule,
)
from atrio_api.lux.execution import LuxDataMode, LuxMode, LuxOutput
from atrio_api.lux.service import LuxRefinementResult
from atrio_api.release_catalog import ACTIVE_RELEASE
from atrio_api.repository import InMemoryExecutionRepository
from atrio_api.service import ExecutionService


def _artifact() -> ArtifactRef:
    return ArtifactRef(
        artifact_id=str(uuid4()),
        sha256="d" * 64,
        media_type="application/vnd.atrio.lux+json",
        classification="INTERNAL_CONTROLLED",
        producer=ComponentName.LUX,
        producer_version=ACTIVE_RELEASE.lux_version,
        release_id=ACTIVE_RELEASE.release_id,
        schema_version=ACTIVE_RELEASE.schema_version,
    )


class FakeLuxWorkflow:
    def __init__(self) -> None:
        self.execution = ExecutionState(
            execution_id=str(uuid4()),
            tenant_id="api-test",
            created_by="tester",
            ratio_module=RatioModule.RI,
            destination=Destination.PUBLICO,
            release=ACTIVE_RELEASE,
            stage=ExecutionStage.CERNE_APPROVED,
            state_version=7,
            cerne_gate=CerneGate.AVANCA,
        )
        self.artifact = _artifact()
        self.created = True
        self.last = None

    def refine(
        self,
        execution_id,
        *,
        expected_version,
        actor_id,
        idempotency_key,
        mode=LuxMode.PADRAO,
        profile=None,
        data_mode=None,
    ):
        self.last = {
            "execution_id": execution_id,
            "expected_version": expected_version,
            "actor_id": actor_id,
            "idempotency_key": idempotency_key,
            "mode": mode,
            "profile": profile,
            "data_mode": data_mode,
        }
        finished = replace(
            self.execution,
            stage=ExecutionStage.FINAL_INTEGRITY_CHECK,
            state_version=9,
            lux_artifact=self.artifact,
        )
        return LuxRefinementResult(
            execution_state=finished,
            artifact=self.artifact,
            output=LuxOutput(
                marked_text="Texto **revisado**.",
                changes=("Ajuste formal.",),
                final_text="Texto revisado.",
            ),
            mode=str(mode),
            data_mode=LuxDataMode.PUBLICO,
            profile=profile,
            privacy_applied=True,
            suppression_reinforced=False,
            created=self.created,
        )


class LuxApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = FakeLuxWorkflow()
        self.client = TestClient(
            create_app(
                ExecutionService(InMemoryExecutionRepository()),
                release=ACTIVE_RELEASE,
                readiness_check=lambda: None,
                lux_workflow=self.workflow,
            )
        )

    def test_refine_route_returns_three_blocks_and_boundary_state(self):
        response = self.client.post(
            f"/v1/executions/{self.workflow.execution.execution_id}/lux/refine",
            headers={"Idempotency-Key": "lux-refine"},
            json={
                "expected_version": 7,
                "actor_id": "tester",
                "mode": "PADRAO",
            },
        )
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["execution"]["stage"], "FINAL_INTEGRITY_CHECK")
        self.assertTrue(body["privacy_applied"])
        self.assertEqual(body["artifact"]["producer"], "lux")
        self.assertNotIn("texto_com_marcacoes", body)
        self.assertNotIn("alteracoes_realizadas", body)
        self.assertNotIn("versao_final_limpa", body)

    def test_retry_returns_200(self):
        self.workflow.created = False
        response = self.client.post(
            f"/v1/executions/{self.workflow.execution.execution_id}/lux/refine",
            headers={"Idempotency-Key": "lux-refine"},
            json={
                "expected_version": 7,
                "actor_id": "tester",
                "mode": "ESTILO",
                "profile": "CHRISTIAN",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["created"])

    def test_generic_api_blocks_lux_and_release_boundary_commands(self):
        for command in (
            "START_LUX",
            "COMPLETE_LUX",
            "PASS_FINAL_INTEGRITY",
            "FAIL_FINAL_INTEGRITY",
            "RETRY_LUX",
            "RELEASE",
        ):
            response = self.client.post(
                f"/v1/executions/{uuid4()}/commands",
                json={
                    "kind": command,
                    "expected_version": 0,
                    "actor_id": "tester",
                    "payload": {},
                },
            )
            self.assertEqual(response.status_code, 422, command)
            self.assertEqual(
                response.json()["error"]["code"],
                "INVALID_COMMAND_PAYLOAD",
            )

    def test_lux_route_fails_closed_without_workflow(self):
        client = TestClient(
            create_app(
                ExecutionService(InMemoryExecutionRepository()),
                release=ACTIVE_RELEASE,
                readiness_check=lambda: None,
            )
        )
        response = client.post(
            f"/v1/executions/{uuid4()}/lux/refine",
            headers={"Idempotency-Key": "lux-refine"},
            json={"expected_version": 7, "actor_id": "tester"},
        )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json()["error"]["code"],
            "LUX_WORKFLOW_UNAVAILABLE",
        )


if __name__ == "__main__":
    unittest.main()
