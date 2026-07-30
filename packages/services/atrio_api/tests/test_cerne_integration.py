from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from uuid import uuid4

from atrio_api.adapters.ollama import InferenceMetadata, InferenceResult
from atrio_api.cerne.execution import (
    CerneAuditExecutor,
    CerneIntegrityError,
)
from atrio_api.cerne.provider import AtrioOllamaCerneProvider
from atrio_api.cerne_core.domain import (
    AuditRequest,
    AxisCode,
    ClientOutput,
    DecisionMode,
    GateDecision,
    GateState,
    LensResult,
    ObjectType,
    Priority,
    SourceType,
    TriageResult,
    ValidityCheck,
)
from atrio_api.cerne_core.knowledge import KnowledgeBase
from atrio_api.cerne_core.orchestrator import ALL_AXES
from atrio_api.cerne_core.provider import StageCallResult
from atrio_api.corpus_intake import EncryptedCorpusStore
from atrio_api.domain import (
    ArtifactRef,
    ComponentName,
    Destination,
    ExecutionStage,
    ExecutionState,
    RatioModule,
)
from atrio_api.release_catalog import ACTIVE_RELEASE


PACKAGES_ROOT = Path(__file__).resolve().parents[3]
CERNE_ROOT = PACKAGES_ROOT / "cerne"


class CleanCerneProvider:
    def __init__(self) -> None:
        self.calls: list[str] = []

    @property
    def name(self) -> str:
        return "clean-test-provider"

    @property
    def configured(self) -> bool:
        return True

    @property
    def model(self) -> str:
        return "clean-test-model"

    async def run(self, *, stage, instructions, payload, response_model):
        self.calls.append(stage)
        if stage == "triagem":
            value = TriageResult(
                tipo_objeto_detectado=payload["tipo_objeto_declarado"],
                tese_principal="Tese final submetida a auditoria.",
                checagem_validade=ValidityCheck(
                    necessaria=False,
                    suspender_auditoria=False,
                    fontes_a_validar=[],
                    fundamento="Handoff ATRIO íntegro.",
                ),
                modo_decisorio=DecisionMode.CONSTRUCAO_PROPRIA,
                prioridade=Priority.BAIXA,
                trechos_de_risco=[],
                resultado_limpo_preliminar=True,
                justificativa_operacional="Auditoria completa mantida.",
            )
        elif stage.startswith("lente:"):
            axis = AxisCode(stage.split(":", 1)[1])
            value = LensResult(
                eixo=axis,
                sintese="Lente executada sem achado relevante.",
                achados=[],
                achados_descartados=[],
                sinalizacoes=[],
                gate_preliminar=GateState.AVANCA,
                produto_exportavel=None,
                resultado_negativo="Nenhum risco relevante no escopo da lente.",
                observacao_de_contencao="Escopo preservado.",
            )
        elif stage == "gate":
            value = GateDecision(
                estado=GateState.AVANCA,
                fundamento_sintetico="Nenhum risco relevante confirmado.",
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
                sintese_objetiva="A auditoria foi concluída sem bloqueio.",
                ponto_principal_atencao="Nenhum risco estrutural relevante.",
                impacto_pratico="O documento pode seguir para refinamento.",
                ajustes_necessarios=[],
                pode_ser_preservado=["Documento integral."],
                recomendacao_final="Prosseguir.",
            )
        else:  # confrontos não devem ser acionados no cenário limpo
            raise AssertionError(stage)
        self.assert_model(value, response_model)
        return StageCallResult(
            parsed=value,
            response_id=f"test:{len(self.calls)}",
            model=self.model,
        )

    @staticmethod
    def assert_model(value, response_model):
        if not isinstance(value, response_model):
            raise AssertionError(
                f"{type(value).__name__} != {response_model.__name__}"
            )


class FakeOllama:
    def generate(
        self,
        prompt,
        *,
        model,
        system=None,
        options=None,
        format_schema=None,
    ):
        del system, options, format_schema
        content = json.dumps(
            {
                "estado_documento": "Pode avançar.",
                "sintese_objetiva": "Saída estruturada.",
                "ponto_principal_atencao": "Nenhum.",
                "impacto_pratico": "Prosseguir.",
                "ajustes_necessarios": [],
                "pode_ser_preservado": ["Tudo."],
                "recomendacao_final": "Prosseguir.",
            }
        )
        return InferenceResult(
            content=content,
            metadata=InferenceMetadata(
                adapter_version="test",
                model=model,
                model_digest="0" * 64,
                prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                response_sha256=hashlib.sha256(content.encode()).hexdigest(),
                options_sha256="1" * 64,
                prompt_chars=len(prompt),
                response_chars=len(content),
            ),
        )


def _execution_with_handoff(tmp: Path, *, include_target: bool = True):
    execution_id = str(uuid4())
    store = EncryptedCorpusStore(tmp / "vault", b"c" * 32)
    artifact_id = str(uuid4())
    bundle = {
        "artifact_roles": ["FINAL_HANDOFF"],
        "execution_id": execution_id,
        "kind": "RATIO_HANDOFF",
        "module": "RI",
        "operation": "FINALIZE_RATIO",
        "phase_outputs": [],
        "ratio_revision": 20,
        "ratio_version": ACTIVE_RELEASE.ratio_version,
        "release_id": ACTIVE_RELEASE.release_id,
        "request_fingerprint": "f" * 64,
        "schema_version": ACTIVE_RELEASE.schema_version,
        "troia": {
            "mode": "AUTONOMOUS_REQUIRED",
            "phase": "RI_03",
            "status": "VALIDATED",
            "triggers": [],
        },
    }
    if include_target:
        bundle["audit_target"] = {
            "object_type": "voto",
            "text": (
                "VOTO. Conheço do recurso e examino a controvérsia com base no "
                "material pseudonimizado. A fundamentação enfrenta os argumentos "
                "relevantes e conclui pelo desprovimento do recurso."
            ),
        }
    plaintext = json.dumps(
        bundle,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    store.write_private_record(
        f"artifacts/{execution_id}/{artifact_id}.atrio",
        plaintext,
    )
    artifact = ArtifactRef(
        artifact_id=artifact_id,
        sha256=hashlib.sha256(plaintext).hexdigest(),
        media_type="application/vnd.atrio.ratio+json",
        classification="INTERNAL_PSEUDONYMIZED",
        producer=ComponentName.RATIO,
        producer_version=ACTIVE_RELEASE.ratio_version,
        release_id=ACTIVE_RELEASE.release_id,
        schema_version=ACTIVE_RELEASE.schema_version,
    )
    execution = ExecutionState(
        execution_id=execution_id,
        tenant_id="test",
        created_by="tester",
        ratio_module=RatioModule.RI,
        destination=Destination.INTERNO,
        release=ACTIVE_RELEASE,
        stage=ExecutionStage.RATIO_READY,
        state_version=3,
        ratio_artifact=artifact,
    )
    return store, execution


class CerneCoreContractTests(unittest.TestCase):
    def test_core_preserves_eleven_axes_and_five_gates(self):
        self.assertEqual(len(ALL_AXES), 11)
        self.assertEqual(len(GateState), 5)
        self.assertEqual(tuple(ALL_AXES), tuple(AxisCode))

    def test_knowledge_bundle_is_ready(self):
        knowledge = KnowledgeBase(CERNE_ROOT)
        knowledge.assert_ready()
        self.assertIn("20_DECISAO_PRODUTO_API_V0_2", "20_DECISAO_PRODUTO_API_V0_2")

    def test_internal_atrio_source_is_typed(self):
        request = AuditRequest(
            tipo_objeto=ObjectType.VOTO,
            natureza_fonte=SourceType.ATRIO_INTERNO,
            texto="Voto interno com conteúdo suficiente para o contrato de auditoria.",
            origem="ATRIO/RATIO",
        )
        self.assertIs(request.natureza_fonte, SourceType.ATRIO_INTERNO)


class CerneOllamaProviderTests(unittest.IsolatedAsyncioTestCase):
    async def test_ollama_adapter_is_converted_to_cerne_provider(self):
        provider = AtrioOllamaCerneProvider(FakeOllama(), model="test-model")
        result = await provider.run(
            stage="saida_cliente",
            instructions="Produza somente o contrato solicitado.",
            payload={"gate": "AVANCA"},
            response_model=ClientOutput,
        )
        self.assertEqual(result.parsed.estado_documento, "Pode avançar.")
        self.assertTrue(result.response_id.startswith("sha256:"))


class CerneExecutorTests(unittest.IsolatedAsyncioTestCase):
    async def test_full_core_audit_is_idempotent_before_postgres(self):
        with TemporaryDirectory() as temp:
            store, execution = _execution_with_handoff(Path(temp))
            provider = CleanCerneProvider()
            executor = CerneAuditExecutor(
                store,
                provider,
                knowledge_root=CERNE_ROOT,
            )
            first = await executor.prepare(
                execution,
                actor_id="tester",
                idempotency_key="audit-1",
            )
            second = await executor.prepare(
                execution,
                actor_id="tester",
                idempotency_key="audit-1",
            )
            self.assertTrue(first.generated)
            self.assertFalse(second.generated)
            self.assertEqual(first.artifact, second.artifact)
            self.assertEqual(first.gate.value, "AVANCA")
            self.assertEqual(len(provider.calls), 14)

    async def test_handoff_without_audit_target_is_rejected(self):
        with TemporaryDirectory() as temp:
            store, execution = _execution_with_handoff(
                Path(temp),
                include_target=False,
            )
            executor = CerneAuditExecutor(
                store,
                CleanCerneProvider(),
                knowledge_root=CERNE_ROOT,
            )
            with self.assertRaises(CerneIntegrityError):
                await executor.prepare(
                    execution,
                    actor_id="tester",
                    idempotency_key="audit-bad",
                )


if __name__ == "__main__":
    unittest.main()
