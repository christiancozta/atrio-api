from __future__ import annotations

import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from atrio_api.domain import (  # noqa: E402
    Command,
    CommandKind,
    CreateExecutionRequest,
    Destination,
    RatioModule,
    ReleaseEnvelope,
)
from atrio_api.repository import (  # noqa: E402
    IdempotencyConflict,
    InMemoryExecutionRepository,
)
from atrio_api.service import ExecutionService  # noqa: E402
from atrio_api.state_machine import VersionConflict  # noqa: E402


def release() -> ReleaseEnvelope:
    return ReleaseEnvelope(
        release_id="atrio-local-test",
        atrio_api_version="0.1.0",
        corpus_version="1.5.0",
        ratio_version="7.0.0",
        cerne_module_version="1.2.0",
        cerne_service_build="0.2.0+test",
        lux_version="6.0.0",
        atrio_pii_version="1.0.0",
        prompt_bundle_hash="abc123",
        schema_version="1",
    )


def request(
    *,
    key: str = "idem-001",
    module: RatioModule = RatioModule.RI,
    tenant_id: str = "tenant-test",
) -> CreateExecutionRequest:
    return CreateExecutionRequest(
        tenant_id=tenant_id,
        actor_id="operador-test",
        idempotency_key=key,
        ratio_module=module,
        destination=Destination.INTERNO,
        input_artifact_id="upload-001",
    )


class ExecutionServiceTests(unittest.TestCase):
    def setUp(self):
        self.repository = InMemoryExecutionRepository()
        self.service = ExecutionService(self.repository)

    def test_same_idempotency_key_returns_same_execution(self):
        first = self.service.create(request(), release())
        second = self.service.create(request(), release())

        self.assertTrue(first.created)
        self.assertFalse(second.created)
        self.assertEqual(first.state.execution_id, second.state.execution_id)

    def test_same_key_with_different_parameters_is_conflict(self):
        self.service.create(request(), release())
        with self.assertRaises(IdempotencyConflict):
            self.service.create(request(module=RatioModule.ED), release())

    def test_same_key_is_isolated_by_tenant(self):
        first = self.service.create(request(tenant_id="tenant-a"), release())
        second = self.service.create(request(tenant_id="tenant-b"), release())

        self.assertTrue(first.created)
        self.assertTrue(second.created)
        self.assertNotEqual(first.state.execution_id, second.state.execution_id)

    def test_repository_serializes_state_and_event_update(self):
        created = self.service.create(request(), release()).state
        result = self.service.command(
            created.execution_id,
            Command(
                kind=CommandKind.START_INGESTION,
                expected_version=0,
                actor_id="operador-test",
            ),
        )

        persisted = self.service.get(created.execution_id)
        events = self.repository.events(created.execution_id)
        self.assertEqual(persisted, result.state)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].sequence, 1)

    def test_second_command_with_stale_version_is_rejected(self):
        created = self.service.create(request(), release()).state
        command = Command(
            kind=CommandKind.START_INGESTION,
            expected_version=0,
            actor_id="operador-test",
        )
        self.service.command(created.execution_id, command)
        with self.assertRaises(VersionConflict):
            self.service.command(created.execution_id, command)


if __name__ == "__main__":
    unittest.main()
