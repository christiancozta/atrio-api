from __future__ import annotations

from dataclasses import replace
import unittest
from uuid import uuid4

from fastapi.testclient import TestClient

from atrio_api.api import create_app
from atrio_api.domain import (
    Destination,
    ExecutionStage,
    ExecutionState,
    RatioModule,
)
from atrio_api.ratio.persistence import RatioPersistResult, RatioRuntimeStartResult
from atrio_api.ratio.state import create_ratio_run
from atrio_api.ratio.engine import validate_current_phase
from atrio_api.release_catalog import ACTIVE_RELEASE
from atrio_api.repository import InMemoryExecutionRepository
from atrio_api.service import ExecutionService


class FakeRatioWorkflow:
    def __init__(self) -> None:
        self.execution = ExecutionState(
            execution_id=str(uuid4()),
            tenant_id="api-test",
            created_by="tester",
            ratio_module=RatioModule.RI,
            destination=Destination.INTERNO,
            release=ACTIVE_RELEASE,
            stage=ExecutionStage.RATIO_RUNNING,
            state_version=4,
        )
        self.state = create_ratio_run(RatioModule.RI)
        self.keys = {}

    def start(self, execution_id, *, actor_id, expected_version, idempotency_key):
        return RatioRuntimeStartResult(self.execution, self.state, True)

    def get(self, execution_id):
        return self.state

    def act(
        self,
        execution_id,
        *,
        action,
        expected_revision,
        actor_id,
        idempotency_key,
        troia_triggers=frozenset(),
        blocking_code=None,
        target_phase=None,
    ):
        if idempotency_key in self.keys:
            return replace(self.keys[idempotency_key], created=False)
        updated = validate_current_phase(self.state)
        self.state = updated
        result = RatioPersistResult(self.execution, updated, True)
        self.keys[idempotency_key] = result
        return result


class RatioApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ratio = FakeRatioWorkflow()
        self.client = TestClient(
            create_app(
                ExecutionService(InMemoryExecutionRepository()),
                release=ACTIVE_RELEASE,
                readiness_check=lambda: None,
                ratio_workflow=self.ratio,
            )
        )

    def test_get_ratio_state(self):
        response = self.client.get(
            f"/v1/executions/{self.ratio.execution.execution_id}/ratio"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["module"], "RI")
        self.assertEqual(response.json()["current_phase"], "RI_01")
        self.assertEqual(response.json()["troia"]["phase"], "RI_03")

    def test_start_ratio_governed_route(self):
        response = self.client.post(
            f"/v1/executions/{self.ratio.execution.execution_id}/ratio/start",
            headers={"Idempotency-Key": "start"},
            json={"expected_version": 3, "actor_id": "tester"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["created"])

    def test_action_route_returns_revision(self):
        response = self.client.post(
            f"/v1/executions/{self.ratio.execution.execution_id}/ratio/actions",
            headers={"Idempotency-Key": "validate"},
            json={
                "action": "VALIDATE",
                "expected_revision": 0,
                "actor_id": "tester",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ratio"]["revision"], 1)

    def test_generic_api_blocks_ratio_macro_commands(self):
        for command in (
            "START_RATIO",
            "REQUEST_OPERATOR_DECISION",
            "RECORD_OPERATOR_DECISION",
            "COMPLETE_RATIO",
            "COMPLETE_RATIO_REWORK",
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
            self.assertEqual(response.status_code, 422)
            self.assertEqual(
                response.json()["error"]["code"],
                "INVALID_COMMAND_PAYLOAD",
            )

    def test_ratio_unavailable_fails_closed(self):
        client = TestClient(
            create_app(
                ExecutionService(InMemoryExecutionRepository()),
                release=ACTIVE_RELEASE,
                readiness_check=lambda: None,
            )
        )
        response = client.get(f"/v1/executions/{uuid4()}/ratio")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json()["error"]["code"],
            "RATIO_WORKFLOW_UNAVAILABLE",
        )


if __name__ == "__main__":
    unittest.main()
