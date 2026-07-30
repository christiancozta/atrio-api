from __future__ import annotations

import sys
import unittest
from typing import Any
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from atrio_api.domain import (  # noqa: E402
    ArtifactRef,
    CerneGate,
    Command,
    CommandKind,
    ComponentName,
    Destination,
    ExecutionStage,
    ExecutionState,
    ExecutionStatus,
    RatioModule,
    ReleaseEnvelope,
)
from atrio_api.state_machine import (  # noqa: E402
    InvalidTransition,
    VersionConflict,
    transition,
)


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


def initial() -> ExecutionState:
    return ExecutionState(
        execution_id="exec-test-001",
        tenant_id="tenant-test",
        created_by="criador-test",
        ratio_module=RatioModule.RI,
        destination=Destination.INTERNO,
        release=release(),
    )


def artifact(
    producer: ComponentName,
    artifact_id: str,
    *,
    producer_version: str | None = None,
    release_id: str = "atrio-local-test",
    schema_version: str = "1",
) -> ArtifactRef:
    versions = {
        ComponentName.CORPUS: "1.5.0",
        ComponentName.RATIO: "7.0.0",
        ComponentName.CERNE: "1.2.0",
        ComponentName.LUX: "6.0.0",
        ComponentName.ATRIO_API: "0.1.0",
        ComponentName.ATRIO_PII: "1.0.0",
    }
    return ArtifactRef(
        artifact_id=artifact_id,
        sha256="a" * 64,
        media_type="text/plain",
        classification="interno_pseudonimizado",
        producer=producer,
        producer_version=producer_version or versions[producer],
        release_id=release_id,
        schema_version=schema_version,
    )


def apply(
    state: ExecutionState,
    kind: CommandKind,
    actor: str = "teste",
    **payload: Any,
) -> ExecutionState:
    return transition(
        state,
        Command(
            kind=kind,
            expected_version=state.state_version,
            actor_id=actor,
            payload=payload,
        ),
    ).state


def until_cerne() -> ExecutionState:
    state = initial()
    state = apply(state, CommandKind.START_INGESTION)
    state = apply(
        state,
        CommandKind.COMPLETE_CORPUS,
        artifact=artifact(ComponentName.CORPUS, "corpus-1"),
    )
    state = apply(state, CommandKind.START_RATIO)
    state = apply(
        state,
        CommandKind.COMPLETE_RATIO,
        artifact=artifact(ComponentName.RATIO, "ratio-1"),
    )
    return apply(state, CommandKind.START_CERNE)


class StateMachineTests(unittest.TestCase):
    def test_happy_path_reaches_release(self):
        state = until_cerne()
        state = apply(
            state,
            CommandKind.APPLY_CERNE_GATE,
            gate=CerneGate.AVANCA,
            artifact=artifact(ComponentName.CERNE, "cerne-1"),
        )
        state = apply(state, CommandKind.START_LUX)
        state = apply(
            state,
            CommandKind.COMPLETE_LUX,
            artifact=artifact(ComponentName.LUX, "lux-1"),
        )
        state = apply(state, CommandKind.PASS_FINAL_INTEGRITY)
        state = apply(state, CommandKind.RELEASE)

        self.assertEqual(state.stage, ExecutionStage.RELEASED)
        self.assertEqual(state.status, ExecutionStatus.COMPLETED)
        self.assertEqual(state.released_artifact_id, "lux-1")

    def test_ratio_requires_explicit_operator_decision(self):
        state = initial()
        state = apply(state, CommandKind.START_INGESTION)
        state = apply(
            state,
            CommandKind.COMPLETE_CORPUS,
            artifact=artifact(ComponentName.CORPUS, "corpus-1"),
        )
        state = apply(state, CommandKind.START_RATIO)
        state = apply(
            state,
            CommandKind.REQUEST_OPERATOR_DECISION,
            phase="RI_01",
            reason_code="VALIDAR_ADMISSIBILIDADE",
        )

        self.assertEqual(state.status, ExecutionStatus.WAITING_HUMAN)
        with self.assertRaises(InvalidTransition):
            apply(
                state,
                CommandKind.COMPLETE_RATIO,
                artifact=artifact(ComponentName.RATIO, "ratio-1"),
            )

        state = apply(
            state,
            CommandKind.RECORD_OPERATOR_DECISION,
            actor="operador-1",
            decision_code="VALIDAR_E_AVANCAR",
        )
        self.assertEqual(state.stage, ExecutionStage.RATIO_RUNNING)
        self.assertEqual(state.last_operator_actor, "operador-1")

    def test_corpus_review_pauses_and_resumes(self):
        state = initial()
        state = apply(state, CommandKind.START_INGESTION)
        state = apply(
            state,
            CommandKind.REQUEST_CORPUS_REVIEW,
            review_type="ocr",
        )
        self.assertEqual(state.status, ExecutionStatus.WAITING_HUMAN)

        state = apply(
            state,
            CommandKind.RESUME_CORPUS,
            actor="revisor",
            decision_code="OCR_CONFERIDO",
        )
        self.assertEqual(state.stage, ExecutionStage.CORPUS_INGESTING)

    def test_corpus_accepts_multiple_versioned_document_registrations(self):
        state = apply(initial(), CommandKind.START_INGESTION)
        first = transition(
            state,
            Command(
                kind=CommandKind.REGISTER_CORPUS_DOCUMENT,
                expected_version=state.state_version,
                actor_id="operador",
                payload={
                    "document_id": "documento-001",
                    "document_sha256": "a" * 64,
                },
            ),
        )
        second = transition(
            first.state,
            Command(
                kind=CommandKind.REGISTER_CORPUS_DOCUMENT,
                expected_version=first.state.state_version,
                actor_id="operador",
                payload={
                    "document_id": "documento-002",
                    "document_sha256": "b" * 64,
                },
            ),
        )

        self.assertEqual(second.state.stage, ExecutionStage.CORPUS_INGESTING)
        self.assertEqual(second.state.state_version, 3)
        self.assertEqual(
            second.event.metadata["document_sha256"],
            "b" * 64,
        )

    def test_only_avanca_can_start_lux(self):
        blocked_gates = (
            CerneGate.AVANCA_COM_AJUSTE,
            CerneGate.REVISAO_HUMANA,
            CerneGate.BLOQUEIO_PARCIAL,
            CerneGate.BLOQUEIO_TOTAL,
        )
        for gate in blocked_gates:
            with self.subTest(gate=gate):
                state = until_cerne()
                state = apply(
                    state,
                    CommandKind.APPLY_CERNE_GATE,
                    gate=gate,
                    reason_code="TESTE_DE_BLOQUEIO",
                    artifact=artifact(ComponentName.CERNE, f"cerne-{gate.value}"),
                )
                with self.assertRaises(InvalidTransition):
                    apply(state, CommandKind.START_LUX)

    def test_adjustment_returns_to_ratio_and_requires_new_audit(self):
        state = until_cerne()
        state = apply(
            state,
            CommandKind.APPLY_CERNE_GATE,
            gate=CerneGate.AVANCA_COM_AJUSTE,
            reason_code="AJUSTAR_COERENCIA_DISPOSITIVO",
            artifact=artifact(ComponentName.CERNE, "cerne-ajuste-1"),
        )
        self.assertEqual(state.stage, ExecutionStage.RATIO_REWORK)

        state = apply(
            state,
            CommandKind.COMPLETE_RATIO_REWORK,
            artifact=artifact(ComponentName.RATIO, "ratio-2"),
        )
        self.assertEqual(state.stage, ExecutionStage.RATIO_READY)
        with self.assertRaises(InvalidTransition):
            apply(state, CommandKind.START_LUX)

        state = apply(state, CommandKind.START_CERNE)
        self.assertEqual(state.stage, ExecutionStage.CERNE_AUDITING)

    def test_total_block_requires_explicit_reopening(self):
        state = until_cerne()
        state = apply(
            state,
            CommandKind.APPLY_CERNE_GATE,
            gate=CerneGate.BLOQUEIO_TOTAL,
            reason_code="INCONSISTENCIA_MATERIAL",
            artifact=artifact(ComponentName.CERNE, "cerne-bloqueio-1"),
        )
        with self.assertRaises(InvalidTransition):
            apply(
                state,
                CommandKind.RETURN_TO_RATIO,
                decision_code="RETORNAR",
            )

        state = apply(
            state,
            CommandKind.REOPEN_TOTAL_BLOCK,
            actor="operador-responsavel",
            decision_code="REABRIR_PARA_SANEAMENTO",
        )
        self.assertEqual(state.stage, ExecutionStage.RATIO_REWORK)

    def test_integrity_failure_blocks_release_and_allows_lux_retry(self):
        state = until_cerne()
        state = apply(
            state,
            CommandKind.APPLY_CERNE_GATE,
            gate=CerneGate.AVANCA,
            artifact=artifact(ComponentName.CERNE, "cerne-1"),
        )
        state = apply(state, CommandKind.START_LUX)
        state = apply(
            state,
            CommandKind.COMPLETE_LUX,
            artifact=artifact(ComponentName.LUX, "lux-1"),
        )
        state = apply(
            state,
            CommandKind.FAIL_FINAL_INTEGRITY,
            reason_code="DISPOSITIVO_ALTERADO",
        )

        self.assertEqual(state.status, ExecutionStatus.BLOCKED)
        with self.assertRaises(InvalidTransition):
            apply(state, CommandKind.RELEASE)

        state = apply(
            state,
            CommandKind.RETRY_LUX,
            actor="revisor",
            decision_code="DESCARTAR_E_REPETIR",
        )
        self.assertEqual(state.stage, ExecutionStage.LUX_REFINING)
        self.assertIsNone(state.lux_artifact_id)

    def test_technical_failure_retries_same_stage(self):
        state = initial()
        state = apply(state, CommandKind.START_INGESTION)
        failed = apply(
            state,
            CommandKind.FAIL_TECHNICAL,
            error_code="OCR_TIMEOUT",
        )
        self.assertEqual(failed.status, ExecutionStatus.FAILED)

        resumed = apply(failed, CommandKind.RETRY_TECHNICAL)
        self.assertEqual(resumed.stage, ExecutionStage.CORPUS_INGESTING)
        self.assertIsNone(resumed.last_error_code)

    def test_stale_command_is_rejected(self):
        state = initial()
        stale = Command(
            kind=CommandKind.START_INGESTION,
            expected_version=9,
            actor_id="teste",
        )
        with self.assertRaises(VersionConflict):
            transition(state, stale)

    def test_events_do_not_copy_arbitrary_payload(self):
        state = initial()
        result = transition(
            state,
            Command(
                kind=CommandKind.START_INGESTION,
                expected_version=0,
                actor_id="teste",
                payload={"texto_juridico": "não pode entrar no evento"},
            ),
        )
        self.assertNotIn("texto_juridico", result.event.metadata)

    def test_handoff_rejects_unversioned_artifact(self):
        state = apply(initial(), CommandKind.START_INGESTION)
        with self.assertRaisesRegex(ValueError, "ArtifactRef versionado"):
            apply(
                state,
                CommandKind.COMPLETE_CORPUS,
                artifact_id="corpus-sem-versao",
            )

    def test_handoff_rejects_artifact_from_another_version(self):
        state = apply(initial(), CommandKind.START_INGESTION)
        with self.assertRaisesRegex(ValueError, "Versão do artefato divergente"):
            apply(
                state,
                CommandKind.COMPLETE_CORPUS,
                artifact=artifact(
                    ComponentName.CORPUS,
                    "corpus-versao-errada",
                    producer_version="1.3.9",
                ),
            )

    def test_handoff_rejects_artifact_from_another_release_or_schema(self):
        cases = (
            artifact(
                ComponentName.CORPUS,
                "corpus-release-errada",
                release_id="outra-release",
            ),
            artifact(
                ComponentName.CORPUS,
                "corpus-schema-errado",
                schema_version="2",
            ),
            artifact(ComponentName.RATIO, "ratio-no-handoff-corpus"),
        )
        for candidate in cases:
            with self.subTest(candidate=candidate.artifact_id):
                state = apply(initial(), CommandKind.START_INGESTION)
                with self.assertRaises(ValueError):
                    apply(
                        state,
                        CommandKind.COMPLETE_CORPUS,
                        artifact=candidate,
                    )

    def test_cerne_gate_requires_versioned_audit_artifact(self):
        state = until_cerne()
        with self.assertRaisesRegex(ValueError, "ArtifactRef versionado"):
            apply(
                state,
                CommandKind.APPLY_CERNE_GATE,
                gate=CerneGate.AVANCA,
            )

    def test_event_records_component_version_and_release(self):
        state = initial()
        result = transition(
            state,
            Command(
                kind=CommandKind.START_INGESTION,
                expected_version=0,
                actor_id="teste",
            ),
        )
        self.assertEqual(result.event.component, ComponentName.CORPUS)
        self.assertEqual(result.event.component_version, "1.5.0")
        self.assertEqual(result.event.release_id, "atrio-local-test")

    def test_cancelled_execution_is_terminal(self):
        state = apply(initial(), CommandKind.CANCEL)
        self.assertEqual(state.status, ExecutionStatus.CANCELLED)
        with self.assertRaises(InvalidTransition):
            apply(state, CommandKind.START_INGESTION)


if __name__ == "__main__":
    unittest.main()
