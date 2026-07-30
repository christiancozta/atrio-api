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
from atrio_api.ratio.execution import (
    RatioFinalizeResult,
    RatioPhaseExecutionResult,
)
from atrio_api.ratio.state import create_ratio_run
from atrio_api.release_catalog import ACTIVE_RELEASE
from atrio_api.repository import InMemoryExecutionRepository
from atrio_api.service import ExecutionService


def _artifact() -> ArtifactRef:
    return ArtifactRef(
        artifact_id=str(uuid4()),
        sha256="a" * 64,
        media_type="application/vnd.atrio.ratio.phase+json",
        classification="INTERNAL_PSEUDONYMIZED",
        producer=ComponentName.RATIO,
        producer_version=ACTIVE_RELEASE.ratio_version,
        release_id=ACTIVE_RELEASE.release_id,
        schema_version=ACTIVE_RELEASE.schema_version,
    )


class FakeWorkflow:
    def __init__(self) -> None:
        self.execution = ExecutionState(
            execution_id=str(uuid4()),
            tenant_id="test",
            created_by="tester",
            ratio_module=RatioModule.RI,
            destination=Destination.INTERNO,
            release=ACTIVE_RELEASE,
            stage=ExecutionStage.RATIO_RUNNING,
            state_version=3,
        )
        self.ratio = create_ratio_run(RatioModule.RI)
        self.artifact = _artifact()

    def get(self, execution_id):
        return self.ratio

    def execute_phase(
        self,
        execution_id,
        *,
        expected_revision,
        actor_id,
        idempotency_key,
    ):
        updated = replace(
            self.ratio,
            revision=self.ratio.revision + 1,
            last_operator_action="EXECUTE_PHASE",
        )
        self.ratio = updated
        return RatioPhaseExecutionResult(
            execution_state=self.execution,
            ratio_state=updated,
            artifact=self.artifact,
            artifact_roles=("PHASE:RI_01",),
            created=True,
        )

    def finalize(
        self,
        execution_id,
        *,
        expected_revision,
        expected_version,
        actor_id,
        idempotency_key,
    ):
        ready = replace(
            self.execution,
            stage=ExecutionStage.RATIO_READY,
            state_version=self.execution.state_version + 1,
            ratio_artifact=self.artifact,
        )
        return RatioFinalizeResult(
            execution_state=ready,
            ratio_state=self.ratio,
            artifact=self.artifact,
            created=True,
        )


class RatioExecutionApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = FakeWorkflow()
        self.client = TestClient(
            create_app(
                ExecutionService(InMemoryExecutionRepository()),
                release=ACTIVE_RELEASE,
                readiness_check=lambda: None,
                ratio_workflow=self.workflow,
            )
        )

    def test_execute_route_returns_only_artifact_metadata(self):
        response = self.client.post(
            f"/v1/executions/{self.workflow.execution.execution_id}/ratio/execute",
            headers={"Idempotency-Key": "exec"},
            json={"expected_revision": 0, "actor_id": "tester"},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["ratio"]["revision"], 1)
        self.assertEqual(body["artifact_roles"], ["PHASE:RI_01"])
        self.assertNotIn("content", body)

    def test_finalize_route_returns_ratio_ready(self):
        response = self.client.post(
            f"/v1/executions/{self.workflow.execution.execution_id}/ratio/finalize",
            headers={"Idempotency-Key": "final"},
            json={
                "expected_revision": 0,
                "expected_version": 3,
                "actor_id": "tester",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["execution"]["stage"], "RATIO_READY")

    def test_generic_start_cerne_is_blocked(self):
        response = self.client.post(
            f"/v1/executions/{uuid4()}/commands",
            json={
                "kind": "START_CERNE",
                "expected_version": 0,
                "actor_id": "tester",
                "payload": {},
            },
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json()["error"]["code"],
            "INVALID_COMMAND_PAYLOAD",
        )


if __name__ == "__main__":
    unittest.main()
