from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from uuid import uuid4

from atrio_api.adapters.ollama import InferenceMetadata, InferenceResult
from atrio_api.corpus_intake import EncryptedCorpusStore
from atrio_api.domain import (
    ArtifactRef,
    CerneGate,
    ComponentName,
    Destination,
    ExecutionStage,
    ExecutionState,
    RatioModule,
)
from atrio_api.lux.execution import (
    LuxDataMode,
    LuxExecutor,
    LuxGeneratedOutputInvalid,
    LuxIntegrityError,
    LuxMode,
    LuxPrivacyError,
)
from atrio_api.release_catalog import ACTIVE_RELEASE


PACKAGES_ROOT = Path(__file__).resolve().parents[3]
LUX_ROOT = PACKAGES_ROOT / "lux"
PII_SOURCE = PACKAGES_ROOT / "atrio_pii" / "atrio_pii.py"


class FakeProvider:
    def __init__(self, transform=None):
        self.calls = 0
        self.prompts: list[str] = []
        self.transform = transform

    def generate(
        self,
        prompt,
        *,
        model,
        system=None,
        options=None,
        format_schema=None,
    ):
        del system, options
        self.calls += 1
        self.prompts.append(prompt)
        source = prompt.split(
            "TEXTO JÁ TRATADO PELA CAMADA 0:\n",
            1,
        )[1]
        marked = source
        final = source
        changes = []
        if self.transform is not None:
            marked, final, changes = self.transform(source)
        content = json.dumps(
            {
                "marked_text": marked,
                "changes": changes,
                "final_text": final,
            },
            ensure_ascii=False,
        )
        return InferenceResult(
            content=content,
            metadata=InferenceMetadata(
                adapter_version="test",
                model=model,
                model_digest="a" * 64,
                prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                response_sha256=hashlib.sha256(content.encode()).hexdigest(),
                options_sha256="b" * 64,
                prompt_chars=len(prompt),
                response_chars=len(content),
            ),
        )


class LuxExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = EncryptedCorpusStore(Path(self.temp.name), b"k" * 32)

    def _state(
        self,
        destination=Destination.INTERNO,
        *,
        mismatched_cerne_ratio: bool = False,
    ):
        execution_id = str(uuid4())
        ratio_payload = {
            "kind": "RATIO_HANDOFF",
            "execution_id": execution_id,
            "release_id": ACTIVE_RELEASE.release_id,
            "audit_target": {
                "object_type": "voto",
                "text": (
                    "VOTO. A parte [PESSOA_0001] interpôs o recurso no processo "
                    "0001234-56.2025.8.16.0001. A fundamentação permanece íntegra. "
                    "Em razão da sucumbência, os honorários são de 20%. "
                    "Ante o exposto, voto pelo CONHECIMENTO e DESPROVIMENTO do recurso."
                ),
            },
        }
        ratio_bytes = json.dumps(
            ratio_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        ratio_id = str(uuid4())
        self.store.write_private_record(
            f"artifacts/{execution_id}/{ratio_id}.atrio",
            ratio_bytes,
        )
        ratio = ArtifactRef(
            artifact_id=ratio_id,
            sha256=hashlib.sha256(ratio_bytes).hexdigest(),
            media_type="application/vnd.atrio.ratio+json",
            classification="INTERNAL_PSEUDONYMIZED",
            producer=ComponentName.RATIO,
            producer_version=ACTIVE_RELEASE.ratio_version,
            release_id=ACTIVE_RELEASE.release_id,
            schema_version=ACTIVE_RELEASE.schema_version,
        )

        cerne_payload = {
            "kind": "CERNE_AUDIT",
            "execution_id": execution_id,
            "release_id": ACTIVE_RELEASE.release_id,
            "ratio_artifact_id": (
                str(uuid4()) if mismatched_cerne_ratio else ratio_id
            ),
            "audit_response": {"gate": {"estado": "AVANCA"}},
        }
        cerne_bytes = json.dumps(
            cerne_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        cerne_id = str(uuid4())
        self.store.write_private_record(
            f"artifacts/{execution_id}/{cerne_id}.atrio",
            cerne_bytes,
        )
        cerne = ArtifactRef(
            artifact_id=cerne_id,
            sha256=hashlib.sha256(cerne_bytes).hexdigest(),
            media_type="application/vnd.atrio.cerne.audit+json",
            classification="INTERNAL_PSEUDONYMIZED",
            producer=ComponentName.CERNE,
            producer_version=ACTIVE_RELEASE.cerne_module_version,
            release_id=ACTIVE_RELEASE.release_id,
            schema_version=ACTIVE_RELEASE.schema_version,
        )
        return ExecutionState(
            execution_id=execution_id,
            tenant_id="test",
            created_by="tester",
            ratio_module=RatioModule.RI,
            destination=destination,
            release=ACTIVE_RELEASE,
            stage=ExecutionStage.CERNE_APPROVED,
            state_version=20,
            ratio_artifact=ratio,
            cerne_artifact=cerne,
            cerne_gate=CerneGate.AVANCA,
        )

    def _executor(self, provider):
        return LuxExecutor(
            self.store,
            provider,
            model="fake",
            knowledge_root=LUX_ROOT,
            pii_source=PII_SOURCE,
        )

    def test_public_mode_anonymizes_before_provider(self):
        state = self._state(Destination.PUBLICO)
        provider = FakeProvider()
        draft = self._executor(provider).prepare(
            state,
            actor_id="tester",
            idempotency_key="public-1",
        )
        self.assertEqual(draft.data_mode, LuxDataMode.PUBLICO)
        self.assertTrue(draft.privacy_applied)
        self.assertNotIn("[PESSOA_0001]", draft.output.final_text)
        self.assertNotIn("0001234-56.2025.8.16.0001", draft.output.final_text)
        self.assertIn("[pessoa]", draft.output.final_text)
        self.assertIn("[processo]", draft.output.final_text)
        self.assertTrue(
            any("anonimização" in item for item in draft.output.changes)
        )

    def test_internal_mode_preserves_corpus_pseudotokens(self):
        state = self._state(Destination.INTERNO)
        draft = self._executor(FakeProvider()).prepare(
            state,
            actor_id="tester",
            idempotency_key="internal-1",
        )
        self.assertEqual(draft.data_mode, LuxDataMode.CORPUS)
        self.assertIn("[PESSOA_0001]", draft.output.final_text)
        self.assertIn("0001234-56.2025.8.16.0001", draft.output.final_text)

    def test_named_profile_is_loaded(self):
        state = self._state()
        provider = FakeProvider()
        self._executor(provider).prepare(
            state,
            actor_id="tester",
            idempotency_key="style-1",
            mode=LuxMode.ESTILO,
            profile="Christian",
        )
        self.assertIn("PERFIL CHRISTIAN", provider.prompts[0])
        self.assertIn("clareza decisória acima de efeito estilístico", provider.prompts[0])

    def test_protected_result_change_is_rejected(self):
        def mutate(source):
            changed = source.replace("DESPROVIMENTO", "PROVIMENTO")
            return changed, changed, ["resultado alterado"]

        state = self._state()
        with self.assertRaises(LuxGeneratedOutputInvalid):
            self._executor(FakeProvider(mutate)).prepare(
                state,
                actor_id="tester",
                idempotency_key="bad-result",
            )

    def test_idempotent_prepare_does_not_call_provider_twice(self):
        state = self._state()
        provider = FakeProvider()
        executor = self._executor(provider)
        first = executor.prepare(
            state,
            actor_id="tester",
            idempotency_key="same",
        )
        second = executor.prepare(
            state,
            actor_id="tester",
            idempotency_key="same",
        )
        self.assertTrue(first.generated)
        self.assertFalse(second.generated)
        self.assertEqual(first.artifact, second.artifact)
        self.assertEqual(provider.calls, 1)

    def test_cerne_must_reference_current_ratio_artifact(self):
        state = self._state(mismatched_cerne_ratio=True)
        with self.assertRaises(LuxIntegrityError):
            self._executor(FakeProvider()).prepare(
                state,
                actor_id="tester",
                idempotency_key="mismatch",
            )

    def test_public_provider_cannot_reintroduce_raw_identifier(self):
        def leak(source):
            changed = source + " CPF 123.456.789-00."
            return changed, changed, []

        state = self._state(Destination.PUBLICO)
        with self.assertRaises(LuxPrivacyError):
            self._executor(FakeProvider(leak)).prepare(
                state,
                actor_id="tester",
                idempotency_key="leak",
            )


if __name__ == "__main__":
    unittest.main()
