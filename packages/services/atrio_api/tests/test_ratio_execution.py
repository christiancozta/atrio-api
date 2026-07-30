from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from uuid import uuid4

from atrio_api.adapters.ollama import InferenceMetadata, InferenceResult
from atrio_api.corpus_intake import EncryptedCorpusStore
from atrio_api.domain import (
    ArtifactRef,
    ComponentName,
    Destination,
    ExecutionStage,
    ExecutionState,
    RatioModule,
)
from atrio_api.ratio.contract import RatioPhase
from atrio_api.ratio.engine import (
    advance_phase,
    finalize_ratio_state,
    validate_current_phase,
)
from atrio_api.ratio.execution import (
    RatioGeneratedOutputInvalid,
    RatioPhaseExecutor,
)
from atrio_api.ratio.state import create_ratio_run
from atrio_api.release_catalog import ACTIVE_RELEASE


_RATIO_ROOT = Path(__file__).resolve().parents[3] / "ratio"


class FakeProvider:
    def __init__(self) -> None:
        self.calls = 0

    def generate(
        self,
        prompt,
        *,
        model,
        system=None,
        options=None,
        format_schema=None,
    ):
        self.calls += 1
        phase = format_schema["properties"]["phase"]["enum"][0]
        body = {
            "phase": phase,
            "analysis": "análise controlada",
            "findings": ["achado"],
            "conclusion": "conclusão",
            "risk_codes": [],
            "operator_attention": [],
        }
        if "counterfactual" in format_schema["properties"]:
            body["counterfactual"] = {
                "adversarial_route": "rota adversarial",
                "breaking_point": "ponto de ruptura",
                "alternative_route": "rota alternativa",
                "residual_risk": "risco residual",
            }
        content = json.dumps(body, ensure_ascii=False)
        return InferenceResult(
            content=content,
            metadata=InferenceMetadata(
                adapter_version="test",
                model=model,
                model_digest="0" * 64,
                prompt_sha256="1" * 64,
                response_sha256="2" * 64,
                options_sha256="3" * 64,
                prompt_chars=len(prompt),
                response_chars=len(content),
            ),
        )


def _fixture(tmp: Path):
    execution_id = str(uuid4())
    store = EncryptedCorpusStore(tmp / "vault", b"k" * 32)
    corpus_bytes = json.dumps(
        {
            "corpus_pipeline_version": "test",
            "corpus_version": ACTIVE_RELEASE.corpus_version,
            "documents": [],
            "execution_id": execution_id,
            "release_id": ACTIVE_RELEASE.release_id,
            "schema_version": ACTIVE_RELEASE.schema_version,
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    import hashlib
    corpus_id = str(uuid4())
    store.write_private_record(
        f"artifacts/{execution_id}/{corpus_id}.atrio",
        corpus_bytes,
    )
    artifact = ArtifactRef(
        artifact_id=corpus_id,
        sha256=hashlib.sha256(corpus_bytes).hexdigest(),
        media_type="application/vnd.atrio.corpus+json",
        classification="INTERNAL_PSEUDONYMIZED",
        producer=ComponentName.CORPUS,
        producer_version=ACTIVE_RELEASE.corpus_version,
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
        stage=ExecutionStage.RATIO_RUNNING,
        state_version=3,
        corpus_artifact=artifact,
    )
    provider = FakeProvider()
    executor = RatioPhaseExecutor(
        store,
        provider,
        model="test-model",
        ratio_root=_RATIO_ROOT,
    )
    return store, provider, executor, execution


class RatioExecutionTests(unittest.TestCase):
    def test_prepare_phase_is_idempotent_before_database(self):
        with TemporaryDirectory() as temp:
            _, provider, executor, execution = _fixture(Path(temp))
            state = create_ratio_run(RatioModule.RI)
            first = executor.prepare_phase(
                execution,
                state,
                (),
                actor_id="tester",
                idempotency_key="phase-1",
            )
            second = executor.prepare_phase(
                execution,
                state,
                (),
                actor_id="tester",
                idempotency_key="phase-1",
            )
            self.assertTrue(first.generated)
            self.assertFalse(second.generated)
            self.assertEqual(first.artifact, second.artifact)
            self.assertEqual(provider.calls, 1)

    def test_ri_03_execution_emits_troia_role(self):
        with TemporaryDirectory() as temp:
            _, _, executor, execution = _fixture(Path(temp))
            state = create_ratio_run(RatioModule.RI)
            for _ in range(2):
                state = validate_current_phase(state)
                state = advance_phase(state)
            self.assertIs(state.current_phase, RatioPhase.RI_03)
            draft = executor.prepare_phase(
                execution,
                state,
                (),
                actor_id="tester",
                idempotency_key="troia",
            )
            self.assertIn("PHASE:RI_03", draft.artifact_roles)
            self.assertIn("TROIA:RI_03", draft.artifact_roles)

    def test_ed_03_must_configure_troia_before_execution(self):
        with TemporaryDirectory() as temp:
            _, _, executor, execution = _fixture(Path(temp))
            execution = replace(execution, ratio_module=RatioModule.ED)
            state = create_ratio_run(RatioModule.ED)
            for _ in range(2):
                state = validate_current_phase(state)
                state = advance_phase(state)
            with self.assertRaises(RatioGeneratedOutputInvalid):
                executor.prepare_phase(
                    execution,
                    state,
                    (),
                    actor_id="tester",
                    idempotency_key="ed-03",
                )

    def test_incomplete_ratio_cannot_finalize(self):
        state = create_ratio_run(RatioModule.RI)
        with self.assertRaises(ValueError):
            finalize_ratio_state(state)


if __name__ == "__main__":
    unittest.main()
