from __future__ import annotations

from dataclasses import replace
import unittest
from uuid import uuid4

from fastapi.testclient import TestClient

from atrio_api.api import create_app
from atrio_api.cerne.service import CerneAuditResult
from atrio_api.cerne_core.domain import ClientOutput
from atrio_api.domain import (
    ArtifactRef,
    CerneGate,
    ComponentName,
    Destination,
    ExecutionStage,
    ExecutionState,
    RatioModule,
)
from atrio_api.release_catalog import ACTIVE_RELEASE
from atrio_api.repository import InMemoryExecutionRepository
from atrio_api.service import ExecutionService


def _artifact() -> ArtifactRef:
    return ArtifactRef(
        artifact_id=str(uuid4()),
        sha256="c" * 64,
        media_type="application/vnd.atrio.cerne.audit+json",
        classification="INTERNAL_PSEUDONYMIZED",
        producer=ComponentName.CERNE,
        producer_version=ACTIVE_RELEASE.cerne_module_version,
        release_id=ACTIVE_RELEASE.release_id,
        schema_version=ACTIVE_RELEASE.schema_version,
    )


class FakeCerneWorkflow:
    def __init__(self) -> None:
        self.execution = ExecutionState(
            execution_id=str(uuid4()),
            tenant_id="api-test",
            created_by="tester",
            ratio_module=RatioModule.RI,
            destination=Destination.INTERNO,
            release=ACTIVE_RELEASE,
            stage=ExecutionStage.RATIO_READY,
            state_version=3,
        )
        self.artifact = _artifact()

    async def audit(
        self,
        execution_id,
        *,
        expected_version,
        actor_id,
        idempotency_key,
    ):
        del execution_id, expected_version, actor_id, idempotency_key
        approved = replace(
            self.execution,
            stage=ExecutionStage.CERNE_APPROVED,
            state_version=5,
            cerne_gate=CerneGate.AVANCA,
            cerne_artifact=self.artifact,
        )
        return CerneAuditResult(
            execution_state=approved,
            artifact=self.artifact,
            gate=CerneGate.AVANCA,
            client_output=ClientOutput(
                estado_documento="Pode avançar.",
                sintese_objetiva="Auditoria concluída.",
                ponto_principal_atencao="Nenhum.",
                impacto_pratico="Pode seguir.",
                ajustes_necessarios=[],
                pode_ser_preservado=["Documento integral."],
                recomendacao_final="Prosseguir.",
            ),
            warnings=(),
            created=True,
        )

    def return_to_ratio(self, execution_id, *, expected_version, actor_id, decision_code):
        del execution_id, expected_version, actor_id, decision_code
        return replace(
            self.execution,
            stage=ExecutionStage.RATIO_REWORK,
            state_version=4,
        )

    def reopen_total_block(self, execution_id, *, expected_version, actor_id, decision_code):
        del execution_id, expected_version, actor_id, decision_code
        return replace(
            self.execution,
            stage=ExecutionStage.RATIO_REWORK,
            state_version=4,
        )


class CerneApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = FakeCerneWorkflow()
        self.client = TestClient(
            create_app(
                ExecutionService(InMemoryExecutionRepository()),
                release=ACTIVE_RELEASE,
                readiness_check=lambda: None,
                cerne_workflow=self.workflow,
            )
        )

    def test_audit_route_exposes_only_safe_client_result(self):
        response = self.client.post(
            f"/v1/executions/{self.workflow.execution.execution_id}/cerne/audit",
            headers={"Idempotency-Key": "cerne-audit"},
            json={"expected_version": 3, "actor_id": "tester"},
        )
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["gate"], "AVANCA")
        self.assertEqual(body["execution"]["stage"], "CERNE_APPROVED")
        self.assertEqual(body["client_output"]["estado_documento"], "Pode avançar.")
        self.assertNotIn("saida_interna", body)
        self.assertNotIn("relatorio", body)

    def test_operator_return_route_is_governed(self):
        response = self.client.post(
            f"/v1/executions/{self.workflow.execution.execution_id}/cerne/return-to-ratio",
            json={
                "expected_version": 3,
                "actor_id": "tester",
                "decision_code": "REWORK_ACCEPTED",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["stage"], "RATIO_REWORK")

    def test_generic_api_blocks_cerne_and_lux_commands(self):
        for command in (
            "START_CERNE",
            "APPLY_CERNE_GATE",
            "RETURN_TO_RATIO",
            "REOPEN_TOTAL_BLOCK",
            "START_LUX",
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

    def test_cerne_route_fails_closed_without_workflow(self):
        client = TestClient(
            create_app(
                ExecutionService(InMemoryExecutionRepository()),
                release=ACTIVE_RELEASE,
                readiness_check=lambda: None,
            )
        )
        response = client.post(
            f"/v1/executions/{uuid4()}/cerne/audit",
            headers={"Idempotency-Key": "cerne-audit"},
            json={"expected_version": 3, "actor_id": "tester"},
        )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json()["error"]["code"],
            "CERNE_WORKFLOW_UNAVAILABLE",
        )


if __name__ == "__main__":
    unittest.main()
