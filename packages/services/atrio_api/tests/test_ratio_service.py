from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import unittest

from atrio_api.domain import (
    Destination,
    ExecutionStage,
    ExecutionState,
    RatioModule,
)
from atrio_api.ratio.contract import RatioPhase, TroiaStatus
from atrio_api.ratio.persistence import (
    RatioPersistResult,
    RatioRevisionConflict,
    RatioRuntimeStartResult,
)
from atrio_api.ratio.service import (
    RatioActionKind,
    RatioActionPayloadError,
    default_ratio_workflow,
)
from atrio_api.ratio.state import create_ratio_run
from atrio_api.release_catalog import ACTIVE_RELEASE


_RATIO_ROOT = Path(__file__).resolve().parents[3] / "ratio"


class FakeRatioRepository:
    def __init__(self, module: RatioModule) -> None:
        self.execution = ExecutionState(
            execution_id="ratio-service-test",
            tenant_id="test",
            created_by="tester",
            ratio_module=module,
            destination=Destination.INTERNO,
            release=ACTIVE_RELEASE,
            stage=ExecutionStage.RATIO_RUNNING,
            state_version=3,
        )
        self.history = {0: create_ratio_run(module)}
        self.head = self.history[0]
        self.keys = {}

    def start_ratio_runtime(
        self, execution_id, *, actor_id, expected_version, idempotency_key
    ):
        return RatioRuntimeStartResult(self.execution, self.head, True)

    def get_ratio_runtime(self, execution_id, *, revision=None):
        if revision is None:
            return self.head
        if revision > self.head.revision:
            raise RatioRevisionConflict(revision, self.head.revision)
        return self.history[revision]

    def persist_ratio_transition(
        self,
        execution_id,
        *,
        previous,
        updated,
        action,
        actor_id,
        idempotency_key,
        external_command=None,
        artifact_refs=(),
        operator_decision_code=None,
    ):
        if idempotency_key in self.keys:
            return replace(self.keys[idempotency_key], created=False)
        if previous.revision != self.head.revision:
            raise RatioRevisionConflict(previous.revision, self.head.revision)
        self.history[updated.revision] = updated
        self.head = updated
        result = RatioPersistResult(self.execution, updated, True)
        self.keys[idempotency_key] = result
        return result


class RatioWorkflowServiceTests(unittest.TestCase):
    def _make(self, module=RatioModule.RI):
        repo = FakeRatioRepository(module)
        service = default_ratio_workflow(
            repo,
            ratio_root=_RATIO_ROOT,
            enforce_execution=False,
        )
        return repo, service

    def test_validate_and_advance(self):
        repo, service = self._make()
        one = service.act(
            repo.execution.execution_id,
            action=RatioActionKind.VALIDATE,
            expected_revision=0,
            actor_id="tester",
            idempotency_key="v0",
        )
        two = service.act(
            repo.execution.execution_id,
            action=RatioActionKind.ADVANCE,
            expected_revision=1,
            actor_id="tester",
            idempotency_key="a1",
        )
        self.assertEqual(one.ratio_state.revision, 1)
        self.assertIs(two.ratio_state.current_phase, RatioPhase.RI_02)

    def test_exact_retry_uses_historical_snapshot(self):
        repo, service = self._make()
        first = service.act(
            repo.execution.execution_id,
            action=RatioActionKind.VALIDATE,
            expected_revision=0,
            actor_id="tester",
            idempotency_key="same",
        )
        retry = service.act(
            repo.execution.execution_id,
            action=RatioActionKind.VALIDATE,
            expected_revision=0,
            actor_id="tester",
            idempotency_key="same",
        )
        self.assertTrue(first.created)
        self.assertFalse(retry.created)
        self.assertEqual(first.ratio_state, retry.ratio_state)

    def test_ed_troia_can_be_dispensed(self):
        repo, service = self._make(RatioModule.ED)
        for action, revision, key in (
            (RatioActionKind.VALIDATE, 0, "v1"),
            (RatioActionKind.ADVANCE, 1, "a1"),
            (RatioActionKind.VALIDATE, 2, "v2"),
            (RatioActionKind.ADVANCE, 3, "a2"),
        ):
            service.act(
                repo.execution.execution_id,
                action=action,
                expected_revision=revision,
                actor_id="tester",
                idempotency_key=key,
            )
        result = service.act(
            repo.execution.execution_id,
            action=RatioActionKind.CONFIGURE_TROIA,
            expected_revision=4,
            actor_id="tester",
            idempotency_key="troia",
        )
        self.assertIs(result.ratio_state.current_phase, RatioPhase.ED_03)
        self.assertIs(result.ratio_state.troia.status, TroiaStatus.DISPENSED)

    def test_irrelevant_payload_is_rejected(self):
        repo, service = self._make()
        with self.assertRaises(RatioActionPayloadError):
            service.act(
                repo.execution.execution_id,
                action=RatioActionKind.VALIDATE,
                expected_revision=0,
                actor_id="tester",
                idempotency_key="bad",
                blocking_code="HS-RI3.1",
            )


if __name__ == "__main__":
    unittest.main()
