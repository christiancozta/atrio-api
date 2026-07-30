from __future__ import annotations

import hashlib
import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from uuid import uuid4

SERVICE_ROOT = Path(__file__).resolve().parents[1]
PACKAGES_ROOT = SERVICE_ROOT.parents[1]
SRC = SERVICE_ROOT / "src"
sys.path.insert(0, str(SRC))

from atrio_api.corpus_processing import (  # noqa: E402
    CorpusIntegrityMismatch,
    CorpusProcessor,
    ExtractionMethod,
    ExtractionResult,
    LocalCorpusExtractor,
    PiiFinding,
    ProcessingStatus,
    PseudonymMap,
    ReviewType,
    load_pii_engine,
)


class FakeExtractor:
    def __init__(self, result: ExtractionResult):
        self.result = result

    def extract(self, media_type: str, content: bytes) -> ExtractionResult:
        return self.result


class FakePii:
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

    def secrecy(self, text: str) -> tuple[str | None, str | None]:
        if "SEGREDO DE JUSTICA" in text.upper():
            return "forte", "SEGREDO DE JUSTICA"
        return None, None


def process(
    text: str,
    *,
    method: ExtractionMethod = ExtractionMethod.TEXT_UTF8,
    confidence: float | None = None,
    pseudonym_map: PseudonymMap | None = None,
):
    content = text.encode("utf-8")
    processor = CorpusProcessor(
        FakeExtractor(
            ExtractionResult(
                text=text,
                method=method,
                page_count=1,
                ocr_mean_confidence=confidence,
            )
        ),
        FakePii(),
    )
    return processor.process(
        execution_id=str(uuid4()),
        document_id=str(uuid4()),
        input_sha256=hashlib.sha256(content).hexdigest(),
        media_type="text/plain",
        content=content,
        pseudonym_map=pseudonym_map or PseudonymMap.empty(),
    )


class CorpusProcessingTests(unittest.TestCase):
    def test_ready_document_has_safe_inventory_and_stable_token(self):
        text = (
            "Processo 1234567-89.2026.8.26.0001. SENTENCA. "
            "Maria da Silva figura como parte. "
            "Conteudo adicional suficiente para validacao automatica segura."
        )
        pseudonym_map = PseudonymMap.empty()
        first = process(text, pseudonym_map=pseudonym_map)
        second = process(text, pseudonym_map=pseudonym_map)

        self.assertEqual(first.inventory.status, ProcessingStatus.READY)
        self.assertIsNone(first.inventory.review_type)
        self.assertEqual(first.inventory.cnj, "1234567-89.2026.8.26.0001")
        self.assertEqual(first.inventory.procedural_class, "SENTENCA")
        self.assertNotIn("Maria da Silva", first.pseudonymized_text)
        self.assertIn("[PESSOA_0001]", first.pseudonymized_text)
        self.assertEqual(
            first.pseudonymized_text,
            second.pseudonymized_text,
        )
        inventory = first.inventory.safe_dict()
        self.assertNotIn("raw_value", str(inventory))
        self.assertNotIn("Maria da Silva", str(inventory))
        self.assertEqual(inventory["pii_counts"], {"PESSOA": 1})

    def test_pseudonym_map_round_trip_keeps_global_identity(self):
        mapping = PseudonymMap.empty()
        mapping.token_for("PESSOA", "Maria da Silva", origin_cnj=None)
        restored = PseudonymMap.from_bytes(mapping.to_bytes())

        self.assertEqual(
            restored.token_for(
                "PESSOA",
                "  MARIA   DA SILVA ",
                origin_cnj="1234567-89.2026.8.26.0001",
            ),
            "[PESSOA_0001]",
        )
        self.assertEqual(
            restored.token_for("PESSOA", "Joao Souza", origin_cnj=None),
            "[PESSOA_0002]",
        )

    def test_ocr_always_requires_explicit_review(self):
        result = process(
            "Texto extraido por OCR com quantidade suficiente de caracteres "
            "para nao ser classificado apenas como documento curto.",
            method=ExtractionMethod.OCR_IMAGE,
            confidence=99.0,
        )

        self.assertEqual(
            result.inventory.status,
            ProcessingStatus.REVIEW_REQUIRED,
        )
        self.assertEqual(result.inventory.review_type, ReviewType.OCR)

    def test_secrecy_review_has_precedence_over_ocr(self):
        result = process(
            "SEGREDO DE JUSTICA. Texto extraido por OCR com informacoes "
            "suficientes para acionar o controle de sigilo.",
            method=ExtractionMethod.OCR_PDF,
            confidence=88.0,
        )

        self.assertEqual(result.inventory.review_type, ReviewType.SECRECY)
        self.assertEqual(result.inventory.secrecy_level, "forte")

    def test_short_native_text_requires_quality_review(self):
        result = process("Documento curto.")
        self.assertEqual(result.inventory.review_type, ReviewType.QUALITY)

    def test_input_hash_mismatch_fails_closed(self):
        processor = CorpusProcessor(
            FakeExtractor(
                ExtractionResult(
                    text="texto",
                    method=ExtractionMethod.TEXT_UTF8,
                    page_count=1,
                )
            ),
            FakePii(),
        )
        with self.assertRaises(CorpusIntegrityMismatch):
            processor.process(
                execution_id=str(uuid4()),
                document_id=str(uuid4()),
                input_sha256="0" * 64,
                media_type="text/plain",
                content=b"texto",
                pseudonym_map=PseudonymMap.empty(),
            )

    def test_docx_extraction_uses_only_document_xml(self):
        xml = (
            b'<?xml version="1.0" encoding="UTF-8"?>'
            b'<w:document '
            b'xmlns:w="http://schemas.openxmlformats.org/'
            b'wordprocessingml/2006/main"><w:body>'
            b"<w:p><w:r><w:t>Primeiro</w:t></w:r></w:p>"
            b"<w:p><w:r><w:t>Segundo</w:t></w:r></w:p>"
            b"</w:body></w:document>"
        )
        content = io.BytesIO()
        with zipfile.ZipFile(content, "w") as archive:
            archive.writestr("word/document.xml", xml)
        with tempfile.TemporaryDirectory() as directory:
            extractor = LocalCorpusExtractor(
                tesseract=Path(directory) / "tesseract",
                pdftotext=Path(directory) / "pdftotext",
                pdfinfo=Path(directory) / "pdfinfo",
                pdftoppm=Path(directory) / "pdftoppm",
                scratch_root=Path(directory) / "scratch",
            )
            result = extractor.extract(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document",
                content.getvalue(),
            )
        self.assertEqual(result.text, "Primeiro\nSegundo")
        self.assertEqual(result.method, ExtractionMethod.DOCX_XML)

    def test_shared_pii_module_is_version_checked(self):
        source = PACKAGES_ROOT / "atrio_pii" / "atrio_pii.py"
        engine = load_pii_engine(source, expected_version="1.0.0")
        self.assertEqual(engine.version, "1.0.0")
        with self.assertRaises(CorpusIntegrityMismatch):
            load_pii_engine(source, expected_version="9.9.9")


if __name__ == "__main__":
    unittest.main()
