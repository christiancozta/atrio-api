from __future__ import annotations

import getpass
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from fastapi.testclient import TestClient

from atrio_api.api import create_app
from atrio_api.cerne.service import default_cerne_workflow
from atrio_api.cerne_core.domain import (
    AxisCode,
    ClientOutput,
    DecisionMode,
    GateDecision,
    GateState,
    LensResult,
    Priority,
    TriageResult,
    ValidityCheck,
)
from atrio_api.cerne_core.provider import StageCallResult
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
from atrio_api.release_catalog import ACTIVE_RELEASE
from atrio_api.service import ExecutionService


SERVICE_ROOT = Path(__file__).resolve().parents[1]
PACKAGES_ROOT = SERVICE_ROOT.parents[1]


class DeterministicCerneProvider:
    def __init__(self) -> None:
        self.calls: list[str] = []

    @property
    def name(self) -> str:
        return "cerne-deterministic-smoke"

    @property
    def configured(self) -> bool:
        return True

    @property
    def model(self) -> str:
        return "cerne-deterministic-smoke"

    async def run(self, *, stage, instructions, payload, response_model):
        if not instructions:
            raise AssertionError("instructions vazias")
        self.calls.append(stage)
        if stage == "triagem":
            value = TriageResult(
                tipo_objeto_detectado=payload["tipo_objeto_declarado"],
                tese_principal="Tese controlada do smoke CERNE.",
                checagem_validade=ValidityCheck(
                    necessaria=False,
                    suspender_auditoria=False,
                    fontes_a_validar=[],
                    fundamento="Entrada ATRIO íntegra.",
                ),
                modo_decisorio=DecisionMode.CONSTRUCAO_PROPRIA,
                prioridade=Priority.BAIXA,
                trechos_de_risco=[],
                resultado_limpo_preliminar=True,
                justificativa_operacional="Executar os onze eixos por contrato 0.2.",
            )
        elif stage.startswith("lente:"):
            axis = AxisCode(stage.split(":", 1)[1])
            value = LensResult(
                eixo=axis,
                sintese=f"{axis.value} executado sem achado.",
                achados=[],
                achados_descartados=[],
                sinalizacoes=[],
                gate_preliminar=GateState.AVANCA,
                produto_exportavel=None,
                resultado_negativo="Nenhum risco relevante.",
                observacao_de_contencao="Escopo isolado preservado.",
            )
        elif stage == "gate":
            value = GateDecision(
                estado=GateState.AVANCA,
                fundamento_sintetico="Os onze eixos não confirmaram risco relevante.",
                achados_considerados=[],
                ponto_de_bloqueio_ou_ajuste="Nenhum.",
                pode_ser_preservado=["Documento integral."],
                condicoes_de_avanco=[],
                encaminhamento="LUX",
                revisao_humana=None,
                observacao_final="Resultado limpo.",
            )
        elif stage == "saida_cliente":
            value = ClientOutput(
                estado_documento="Pode avançar.",
                sintese_objetiva="Auditoria completa concluída.",
                ponto_principal_atencao="Nenhum risco estrutural relevante.",
                impacto_pratico="O documento pode seguir ao refinamento.",
                ajustes_necessarios=[],
                pode_ser_preservado=["Documento integral."],
                recomendacao_final="Prosseguir.",
            )
        else:
            raise AssertionError(f"Confronto inesperado no smoke limpo: {stage}")
        if not isinstance(value, response_model):
            raise AssertionError(stage)
        return StageCallResult(
            parsed=value,
            response_id=f"smoke:{len(self.calls)}",
            model=self.model,
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
        store = EncryptedCorpusStore(Path(temp) / "vault", b"n" * 32)
        token = uuid4().hex
        execution_id = str(uuid4())
        actor = "cerne-smoke"

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
                {"execution_id": execution_id, "smoke": "cerne"}
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
            artifact_id=str(uuid4()),
            sha256="1" * 64,
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
        ratio_running = repository.apply(
            execution_id,
            Command(
                kind=CommandKind.START_RATIO,
                expected_version=corpus_ready.state.state_version,
                actor_id=actor,
            ),
        )

        ratio_id = str(uuid4())
        ratio_bundle = {
            "artifact_roles": ["FINAL_HANDOFF"],
            "audit_target": {
                "object_type": "voto",
                "text": (
                    "VOTO. Conheço do recurso. A controvérsia foi examinada a partir "
                    "do material pseudonimizado e dos fundamentos pertinentes. Não foi "
                    "identificado motivo para reforma, razão pela qual voto pelo "
                    "desprovimento do recurso, nos termos da fundamentação consolidada."
                ),
            },
            "execution_id": execution_id,
            "kind": "RATIO_HANDOFF",
            "module": "RI",
            "operation": "FINALIZE_RATIO",
            "phase_outputs": [],
            "ratio_revision": 18,
            "ratio_version": ACTIVE_RELEASE.ratio_version,
            "release_id": ACTIVE_RELEASE.release_id,
            "request_fingerprint": "2" * 64,
            "schema_version": ACTIVE_RELEASE.schema_version,
            "troia": {
                "mode": "AUTONOMOUS_REQUIRED",
                "phase": "RI_03",
                "status": "VALIDATED",
                "triggers": [],
            },
        }
        ratio_bytes = json.dumps(
            ratio_bundle,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
        store.write_private_record(
            f"artifacts/{execution_id}/{ratio_id}.atrio",
            ratio_bytes,
        )
        ratio_artifact = ArtifactRef(
            artifact_id=ratio_id,
            sha256=hashlib.sha256(ratio_bytes).hexdigest(),
            media_type="application/vnd.atrio.ratio+json",
            classification="INTERNAL_PSEUDONYMIZED",
            producer=ComponentName.RATIO,
            producer_version=ACTIVE_RELEASE.ratio_version,
            release_id=ACTIVE_RELEASE.release_id,
            schema_version=ACTIVE_RELEASE.schema_version,
        )
        ratio_ready = repository.apply(
            execution_id,
            Command(
                kind=CommandKind.COMPLETE_RATIO,
                expected_version=ratio_running.state.state_version,
                actor_id=actor,
                payload={"artifact": ratio_artifact},
            ),
        )

        provider = DeterministicCerneProvider()
        workflow = default_cerne_workflow(
            repository,
            store,
            provider,
            knowledge_root=PACKAGES_ROOT / "cerne",
        )
        app = create_app(
            ExecutionService(repository),
            release=ACTIVE_RELEASE,
            readiness_check=repository.verify_schema,
            cerne_workflow=workflow,
        )
        client = TestClient(app)

        key = f"cerne-{token}"
        body = {
            "expected_version": ratio_ready.state.state_version,
            "actor_id": actor,
        }
        audited = client.post(
            f"/v1/executions/{execution_id}/cerne/audit",
            headers={"Idempotency-Key": key},
            json=body,
        )
        assert audited.status_code == 201, audited.text
        result = audited.json()
        assert result["execution"]["stage"] == "CERNE_APPROVED"
        assert result["gate"] == "AVANCA"
        assert result["artifact"]["producer"] == "cerne"
        assert len(provider.calls) == 14

        retry = client.post(
            f"/v1/executions/{execution_id}/cerne/audit",
            headers={"Idempotency-Key": key},
            json=body,
        )
        assert retry.status_code == 200, retry.text
        assert retry.json()["created"] is False
        assert retry.json()["artifact"] == result["artifact"]
        assert len(provider.calls) == 14

        artifact_id = result["artifact"]["artifact_id"]
        private = store.read_private_record(
            f"artifacts/{execution_id}/{artifact_id}.atrio"
        )
        bundle = json.loads(private)
        assert len(bundle["audit_response"]["lentes"]) == 11
        assert bundle["audit_response"]["gate"]["estado"] == "AVANCA"

        events = repository.events(execution_id)
        commands = [event.command for event in events]
        assert CommandKind.START_CERNE in commands
        assert CommandKind.APPLY_CERNE_GATE in commands

        blocked = client.post(
            f"/v1/executions/{execution_id}/commands",
            json={
                "kind": "START_LUX",
                "expected_version": result["execution"]["state_version"],
                "actor_id": actor,
                "payload": {},
            },
        )
        assert blocked.status_code == 422, blocked.text

        print("OK: RATIO_READY -> CERNE executou o motor 0.2 existente")
        print("OK: 11 eixos foram executados; confrontos ficaram condicionais")
        print("OK: AuditResponse completo ficou cifrado no cofre")
        print("OK: PostgreSQL recebeu somente ArtifactRef, gate e eventos seguros")
        print("OK: START_CERNE + APPLY_CERNE_GATE foram transacionais")
        print("OK: retry HTTP idempotente não reexecutou a auditoria")
        print("OK: gate AVANCA terminou em CERNE_APPROVED")
        print("OK: START_LUX permanece bloqueado até a próxima entrega")
        print(f"execution_id: {execution_id}")


if __name__ == "__main__":
    main()
