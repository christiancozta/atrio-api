from __future__ import annotations

import asyncio
import hashlib
import json
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

SERVICE_ROOT = Path(__file__).resolve().parents[1]
SRC = SERVICE_ROOT / "src"
sys.path.insert(0, str(SRC))

from atrio_api.corpus_intake import (  # noqa: E402
    EncryptedCorpusStore,
    document_id_for,
)
from atrio_api.api import create_app  # noqa: E402
from atrio_api.corpus_processing import (  # noqa: E402
    CORPUS_PIPELINE_VERSION,
    CorpusProcessor,
    ExtractionMethod,
    ExtractionResult,
    PiiFinding,
    ProcessingStatus,
)
from atrio_api.corpus_service import (  # noqa: E402
    CorpusDocumentRecord,
    CorpusFinalizeResult,
    CorpusProcessingIncomplete,
    CorpusProcessingRecordResult,
    CorpusReviewDecision,
    CorpusReviewResult,
    CorpusWorkflowService,
)
from atrio_api.domain import (  # noqa: E402
    Command,
    CommandKind,
    Destination,
    ExecutionState,
    RatioModule,
    ReleaseEnvelope,
)
from atrio_api.repository import InMemoryExecutionRepository  # noqa: E402
from atrio_api.service import ExecutionService  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


async def stream(value: bytes):
    yield value


class TextExtractor:
    def extract(self, media_type: str, content: bytes) -> ExtractionResult:
        text = content.decode("utf-8")
        method = (
            ExtractionMethod.OCR_IMAGE
            if text.startswith("OCR:")
            else ExtractionMethod.TEXT_UTF8
        )
        return ExtractionResult(
            text=text,
            method=method,
            page_count=1,
            ocr_mean_confidence=91.0 if method is ExtractionMethod.OCR_IMAGE else None,
        )

    def verify(self):
        return {"tesseract": "fake", "poppler": "fake"}


class PersonPii:
    version = "1.0.0"

    def detect(self, text: str) -> tuple[PiiFinding, ...]:
        value = "Maria da Silva"
        start = text.find(value)
        if start < 0:
            return ()
        return (
            PiiFinding(
                start=start,
                end=start + len(value),
                kind="PESSOA",
                value=value,
            ),
        )

    def secrecy(self, text: str):
        return (None, None)


class MemoryCorpusRepository:
    def __init__(self, state: ExecutionState):
        self.core = InMemoryExecutionRepository()
        self.core.create(
            state,
            idempotency_key="execution",
            request_fingerprint="fingerprint",
        )
        self.documents: dict[str, CorpusDocumentRecord] = {}

    def get(self, execution_id: str):
        return self.core.get(execution_id)

    def list_corpus_documents(self, execution_id: str):
        if self.core.get(execution_id):
            return tuple(self.documents.values())

    def record_corpus_processing(
        self,
        document,
        *,
        processed_storage_key,
        actor_id,
        expected_version,
    ):
        previous = self.documents[document.intake.document_id]
        if previous.inventory is not None:
            return CorpusProcessingRecordResult(
                state=self.get(document.intake.execution_id),
                document=previous,
                created=False,
            )
        self.documents[document.intake.document_id] = document
        state = self.get(document.intake.execution_id)
        if document.inventory.status is ProcessingStatus.REVIEW_REQUIRED:
            state = self.core.apply(
                state.execution_id,
                Command(
                    kind=CommandKind.REQUEST_CORPUS_REVIEW,
                    expected_version=expected_version,
                    actor_id=actor_id,
                    payload={
                        "review_type": document.inventory.review_type.value
                    },
                ),
            ).state
        return CorpusProcessingRecordResult(
            state=state,
            document=document,
            created=True,
        )

    def record_corpus_review(
        self,
        *,
        execution_id,
        document_id,
        decision,
        actor_id,
        expected_version,
    ):
        previous = self.documents[document_id]
        updated = replace(
            previous,
            review_decision=decision,
            reviewed_by=actor_id,
        )
        self.documents[document_id] = updated
        state = self.core.apply(
            execution_id,
            Command(
                kind=CommandKind.RESUME_CORPUS,
                expected_version=expected_version,
                actor_id=actor_id,
                payload={"decision_code": decision.value},
            ),
        ).state
        return CorpusReviewResult(state=state, document=updated)

    def finalize_corpus(
        self,
        *,
        execution_id,
        artifact,
        storage_key,
        document_count,
        pipeline_version,
        actor_id,
        expected_version,
    ):
        return self.core.apply(
            execution_id,
            Command(
                kind=CommandKind.COMPLETE_CORPUS,
                expected_version=expected_version,
                actor_id=actor_id,
                payload={"artifact": artifact},
            ),
        ).state


class CorpusWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = EncryptedCorpusStore(self.root / "vault", b"k" * 32)
        self.execution_id = str(uuid4())
        self.release = ReleaseEnvelope(
            release_id="test-release",
            atrio_api_version="0.0.0",
            corpus_version=CORPUS_PIPELINE_VERSION,
            ratio_version="1.0.0",
            cerne_module_version="1.0.0",
            cerne_service_build="1.0.0",
            lux_version="1.0.0",
            atrio_pii_version="1.0.0",
            prompt_bundle_hash="a" * 64,
            schema_version="1.0.0",
        )
        state = ExecutionState(
            execution_id=self.execution_id,
            tenant_id="tenant-test",
            created_by="operator-test",
            ratio_module=RatioModule.RI,
            destination=Destination.INTERNO,
            release=self.release,
        )
        self.repository = MemoryCorpusRepository(state)
        self.repository.core.apply(
            self.execution_id,
            Command(
                kind=CommandKind.START_INGESTION,
                expected_version=0,
                actor_id="operator-test",
            ),
        )
        extractor = TextExtractor()
        self.workflow = CorpusWorkflowService(
            self.repository,
            self.store,
            CorpusProcessor(extractor, PersonPii()),
            extractor,
        )

    def tearDown(self):
        self.temp.cleanup()

    def add_document(self, text: str, key: str = "document-1") -> str:
        document_id = document_id_for(self.execution_id, key)
        stored = asyncio.run(
            self.store.encrypt_stream(
                stream(text.encode("utf-8")),
                document_id=document_id,
                execution_id=self.execution_id,
                idempotency_key=key,
                created_by="operator-test",
                media_type="text/plain",
            )
        )
        self.repository.documents[document_id] = CorpusDocumentRecord(
            intake=stored.intake
        )
        return document_id

    def test_process_and_finalize_builds_encrypted_handoff(self):
        self.add_document(
            "Processo 1234567-89.2026.8.26.0001. SENTENCA. "
            "Maria da Silva figura como parte. Texto suficiente para "
            "concluir o processamento documental com segurança."
        )

        batch = self.workflow.process_pending(
            execution_id=self.execution_id,
            actor_id="operator-test",
            expected_version=1,
        )
        finalized = self.workflow.finalize(
            execution_id=self.execution_id,
            actor_id="operator-test",
            expected_version=1,
        )

        self.assertEqual(batch.processed_count, 1)
        self.assertFalse(batch.halted_for_review)
        self.assertEqual(finalized.state.stage.value, "CORPUS_READY")
        self.assertEqual(finalized.document_count, 1)
        artifact_key = (
            f"artifacts/{self.execution_id}/"
            f"{finalized.artifact.artifact_id}.atrio"
        )
        envelope = (self.root / "vault" / artifact_key).read_bytes()
        self.assertNotIn(b"Maria da Silva", envelope)
        payload = json.loads(
            self.store.read_private_record(artifact_key).decode("utf-8")
        )
        text = payload["documents"][0]["pseudonymized_text"]
        self.assertIn("[PESSOA_0001]", text)
        self.assertNotIn("Maria da Silva", text)
        self.assertEqual(
            hashlib.sha256(
                self.store.read_private_record(artifact_key)
            ).hexdigest(),
            finalized.artifact.sha256,
        )

    def test_ocr_requires_review_before_handoff(self):
        document_id = self.add_document(
            "OCR: Conteudo suficientemente longo para exigir revisao humana "
            "antes de autorizar a transferencia ao modulo RATIO."
        )
        batch = self.workflow.process_pending(
            execution_id=self.execution_id,
            actor_id="operator-test",
            expected_version=1,
        )

        self.assertTrue(batch.halted_for_review)
        self.assertEqual(
            batch.state.stage.value,
            "CORPUS_REVIEW_REQUIRED",
        )
        with self.assertRaises(Exception):
            self.workflow.finalize(
                execution_id=self.execution_id,
                actor_id="operator-test",
                expected_version=2,
            )

        reviewed = self.workflow.review(
            execution_id=self.execution_id,
            document_id=document_id,
            decision=CorpusReviewDecision.APPROVE,
            actor_id="reviewer-test",
            expected_version=2,
        )
        finalized = self.workflow.finalize(
            execution_id=self.execution_id,
            actor_id="operator-test",
            expected_version=3,
        )
        self.assertEqual(reviewed.document.effective_status, "APPROVED")
        self.assertEqual(finalized.state.stage.value, "CORPUS_READY")

    def test_excluding_every_document_blocks_finalize(self):
        document_id = self.add_document(
            "OCR: Documento longo o bastante para revisao, mas excluido "
            "expressamente pelo operador responsavel."
        )
        self.workflow.process_pending(
            execution_id=self.execution_id,
            actor_id="operator-test",
            expected_version=1,
        )
        self.workflow.review(
            execution_id=self.execution_id,
            document_id=document_id,
            decision=CorpusReviewDecision.EXCLUDE,
            actor_id="reviewer-test",
            expected_version=2,
        )

        with self.assertRaises(Exception):
            self.workflow.finalize(
                execution_id=self.execution_id,
                actor_id="operator-test",
                expected_version=3,
            )

    def test_pseudonym_map_is_isolated_by_execution(self):
        document_id = self.add_document(
            "Texto extenso com Maria da Silva e contexto documental "
            "suficiente para evitar revisao de qualidade automatica."
        )
        self.workflow.process_pending(
            execution_id=self.execution_id,
            actor_id="operator-test",
            expected_version=1,
        )
        map_path = (
            self.root
            / "vault"
            / "maps"
            / self.execution_id
            / "pseudonym-map.atrio"
        )
        self.assertTrue(map_path.is_file())
        self.assertNotIn(b"Maria da Silva", map_path.read_bytes())
        self.assertEqual(
            self.repository.documents[document_id].effective_status,
            "READY",
        )

    def test_http_surface_returns_only_safe_inventory(self):
        self.add_document(
            "Processo 1234567-89.2026.8.26.0001. SENTENCA. "
            "requerente Maria da Silva, CPF 123.456.789-09. "
            "Texto adicional suficiente para o processamento seguro."
        )
        app = create_app(
            ExecutionService(self.repository.core),
            release=self.release,
            readiness_check=lambda: None,
            corpus_workflow=self.workflow,
        )
        client = TestClient(app)
        response = client.post(
            f"/v1/executions/{self.execution_id}/corpus/process",
            json={
                "expected_version": 1,
                "actor_id": "operator-test",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        serialized = json.dumps(body, ensure_ascii=False)
        self.assertEqual(body["processed_count"], 1)
        self.assertNotIn("Maria da Silva", serialized)
        self.assertNotIn("123.456.789-09", serialized)
        self.assertNotIn("pseudonymized_text", serialized)
        self.assertNotIn("storage_key", serialized)


if __name__ == "__main__":
    unittest.main()
