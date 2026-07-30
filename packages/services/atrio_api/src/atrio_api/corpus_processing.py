from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from types import ModuleType
from typing import Protocol
from xml.etree import ElementTree


CORPUS_PIPELINE_VERSION = "1.5.0"
MIN_NATIVE_CHARS_PER_PAGE = 60
MIN_EXTRACTED_CHARS = 80
OCR_REVIEW_CONFIDENCE = 80.0
MAX_DOCX_EXPANDED_BYTES = 200 * 1024 * 1024
MAX_DOCX_XML_BYTES = 50 * 1024 * 1024
_CNJ = re.compile(r"\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b")
_TOKEN_PREFIX = {
    "PESSOA": "PESSOA",
    "CPF": "CPF",
    "CNPJ": "CNPJ",
    "OAB": "OAB",
    "RG": "RG",
    "EMAIL": "EMAIL",
    "CEP": "ENDERECO",
    "TELEFONE": "TELEFONE",
}


class CorpusProcessingError(RuntimeError):
    pass


class CorpusToolUnavailable(CorpusProcessingError):
    pass


class CorpusExtractionFailed(CorpusProcessingError):
    pass


class CorpusIntegrityMismatch(CorpusProcessingError):
    pass


class ExtractionMethod(StrEnum):
    TEXT_UTF8 = "text_utf8"
    DOCX_XML = "docx_xml"
    PDF_TEXT = "pdf_text"
    OCR_PDF = "ocr_pdf"
    OCR_IMAGE = "ocr_image"


class ProcessingStatus(StrEnum):
    READY = "READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class ReviewType(StrEnum):
    OCR = "ocr"
    SECRECY = "secrecy"
    QUALITY = "quality"


@dataclass(frozen=True, slots=True)
class PiiFinding:
    start: int
    end: int
    kind: str
    value: str

    def __post_init__(self) -> None:
        if self.start < 0 or self.end <= self.start:
            raise ValueError("Intervalo de identificador inválido.")
        if not self.kind.strip() or not self.value:
            raise ValueError("Identificador incompleto.")


class PiiEngine(Protocol):
    @property
    def version(self) -> str: ...

    def detect(self, text: str) -> tuple[PiiFinding, ...]: ...

    def secrecy(self, text: str) -> tuple[str | None, str | None]: ...


@dataclass(frozen=True, slots=True)
class ExtractionResult:
    text: str
    method: ExtractionMethod
    page_count: int
    ocr_mean_confidence: float | None = None

    def __post_init__(self) -> None:
        if self.page_count < 0:
            raise ValueError("page_count inválido.")
        if self.ocr_mean_confidence is not None and not (
            0 <= self.ocr_mean_confidence <= 100
        ):
            raise ValueError("Confiança OCR inválida.")


@dataclass(frozen=True, slots=True)
class CorpusInventoryRecord:
    document_id: str
    execution_id: str
    input_sha256: str
    byte_length: int
    media_type: str
    extraction_method: ExtractionMethod
    page_count: int
    extracted_char_count: int
    ocr_mean_confidence: float | None
    cnj: str | None
    procedural_class: str
    secrecy_level: str
    pii_counts: tuple[tuple[str, int], ...]
    pseudonym_count: int
    pseudonymized_sha256: str
    status: ProcessingStatus
    review_type: ReviewType | None
    corpus_pipeline_version: str
    atrio_pii_version: str

    def safe_dict(self) -> dict[str, object]:
        return {
            "atrio_pii_version": self.atrio_pii_version,
            "byte_length": self.byte_length,
            "cnj": self.cnj,
            "corpus_pipeline_version": self.corpus_pipeline_version,
            "document_id": self.document_id,
            "execution_id": self.execution_id,
            "extracted_char_count": self.extracted_char_count,
            "extraction_method": self.extraction_method.value,
            "input_sha256": self.input_sha256,
            "media_type": self.media_type,
            "ocr_mean_confidence": self.ocr_mean_confidence,
            "page_count": self.page_count,
            "pii_counts": dict(self.pii_counts),
            "procedural_class": self.procedural_class,
            "pseudonym_count": self.pseudonym_count,
            "pseudonymized_sha256": self.pseudonymized_sha256,
            "review_type": (
                self.review_type.value if self.review_type is not None else None
            ),
            "secrecy_level": self.secrecy_level,
            "status": self.status.value,
        }


@dataclass(frozen=True, slots=True)
class ProcessedCorpusDocument:
    inventory: CorpusInventoryRecord
    pseudonymized_text: str


class PseudonymMap:
    VERSION = "ATRIO-PSEUDONYM-MAP-1"

    def __init__(
        self,
        *,
        by_value: dict[str, dict[str, str]] | None = None,
        counters: dict[str, int] | None = None,
    ):
        self._by_value = dict(by_value or {})
        self._counters = dict(counters or {})
        self._validate()

    @classmethod
    def empty(cls) -> PseudonymMap:
        return cls()

    @classmethod
    def from_bytes(cls, value: bytes) -> PseudonymMap:
        try:
            decoded = json.loads(value.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CorpusIntegrityMismatch(
                "Mapa de pseudônimos inválido."
            ) from exc
        if (
            not isinstance(decoded, dict)
            or decoded.get("version") != cls.VERSION
            or not isinstance(decoded.get("by_value"), dict)
            or not isinstance(decoded.get("counters"), dict)
        ):
            raise CorpusIntegrityMismatch(
                "Contrato do mapa de pseudônimos inválido."
            )
        return cls(
            by_value=decoded["by_value"],
            counters=decoded["counters"],
        )

    def to_bytes(self) -> bytes:
        return json.dumps(
            {
                "by_value": self._by_value,
                "counters": self._counters,
                "version": self.VERSION,
            },
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

    def token_for(
        self,
        kind: str,
        raw_value: str,
        *,
        origin_cnj: str | None,
    ) -> str:
        normalized = " ".join(raw_value.casefold().split())
        lookup = f"{kind}::{normalized}"
        previous = self._by_value.get(lookup)
        if previous is not None:
            return previous["token"]
        prefix = _TOKEN_PREFIX.get(kind, kind)
        if not re.fullmatch(r"[A-Z][A-Z0-9_]{1,31}", prefix):
            raise CorpusIntegrityMismatch("Tipo de pseudônimo inválido.")
        number = self._counters.get(prefix, 0) + 1
        self._counters[prefix] = number
        token = f"[{prefix}_{number:04d}]"
        self._by_value[lookup] = {
            "origin_cnj": origin_cnj or "",
            "raw_value": raw_value.strip(),
            "token": token,
            "type": kind,
        }
        return token

    def _validate(self) -> None:
        for prefix, counter in self._counters.items():
            if not isinstance(prefix, str) or not isinstance(counter, int):
                raise CorpusIntegrityMismatch(
                    "Contador do mapa de pseudônimos inválido."
                )
            if counter < 0:
                raise CorpusIntegrityMismatch(
                    "Contador do mapa de pseudônimos negativo."
                )
        for lookup, record in self._by_value.items():
            if not isinstance(lookup, str) or not isinstance(record, dict):
                raise CorpusIntegrityMismatch(
                    "Entrada do mapa de pseudônimos inválida."
                )
            expected = {"origin_cnj", "raw_value", "token", "type"}
            if set(record) != expected or not all(
                isinstance(record[key], str) for key in expected
            ):
                raise CorpusIntegrityMismatch(
                    "Entrada do mapa de pseudônimos incompleta."
                )
            if not re.fullmatch(
                r"\[[A-Z][A-Z0-9_]{1,31}_[0-9]{4,}\]",
                record["token"],
            ):
                raise CorpusIntegrityMismatch(
                    "Token do mapa de pseudônimos inválido."
                )


class LocalCorpusExtractor:
    def __init__(
        self,
        *,
        tesseract: Path,
        pdftotext: Path,
        pdfinfo: Path,
        pdftoppm: Path,
        scratch_root: Path,
        ocr_languages: str = "por+eng",
        ocr_dpi: int = 300,
        command_timeout_seconds: int = 180,
    ):
        self._tesseract = tesseract.resolve()
        self._pdftotext = pdftotext.resolve()
        self._pdfinfo = pdfinfo.resolve()
        self._pdftoppm = pdftoppm.resolve()
        self._scratch_root = scratch_root.resolve()
        self._ocr_languages = ocr_languages
        self._ocr_dpi = ocr_dpi
        self._command_timeout_seconds = command_timeout_seconds
        if not 150 <= self._ocr_dpi <= 600:
            raise ValueError("DPI do OCR deve ficar entre 150 e 600.")
        self._scratch_root.mkdir(parents=True, exist_ok=True)

    @classmethod
    def discover(cls, *, scratch_root: Path) -> LocalCorpusExtractor:
        tesseract = _required_command("tesseract")
        pdftotext = _required_command("pdftotext")
        poppler_root = pdftotext.parent
        pdfinfo = _sibling_or_command(poppler_root, "pdfinfo")
        pdftoppm = _sibling_or_command(poppler_root, "pdftoppm")
        return cls(
            tesseract=tesseract,
            pdftotext=pdftotext,
            pdfinfo=pdfinfo,
            pdftoppm=pdftoppm,
            scratch_root=scratch_root,
        )

    def verify(self) -> dict[str, str]:
        tesseract_version = self._run(
            [str(self._tesseract), "--version"],
        ).stdout.decode("utf-8", errors="replace").splitlines()[0]
        languages = self._run(
            [str(self._tesseract), "--list-langs"],
        ).stdout.decode("utf-8", errors="replace").splitlines()
        available = {item.strip() for item in languages if item.strip()}
        required = set(self._ocr_languages.split("+"))
        if not required.issubset(available):
            missing = ", ".join(sorted(required - available))
            raise CorpusToolUnavailable(
                f"Idiomas ausentes no Tesseract: {missing}."
            )
        poppler_version = self._run(
            [str(self._pdftotext), "-v"],
            accept_stderr=True,
        )
        version_text = (
            poppler_version.stderr or poppler_version.stdout
        ).decode("utf-8", errors="replace").splitlines()[0]
        return {
            "ocr_languages": self._ocr_languages,
            "poppler": version_text,
            "tesseract": tesseract_version,
        }

    def extract(self, media_type: str, content: bytes) -> ExtractionResult:
        if media_type == "text/plain":
            return ExtractionResult(
                text=_normalize_text(content.decode("utf-8")),
                method=ExtractionMethod.TEXT_UTF8,
                page_count=1,
            )
        if (
            media_type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            return ExtractionResult(
                text=_extract_docx(content),
                method=ExtractionMethod.DOCX_XML,
                page_count=1,
            )
        if media_type == "application/pdf":
            return self._extract_pdf(content)
        if media_type in {"image/jpeg", "image/png", "image/tiff"}:
            text, confidence = self._ocr_image(content)
            return ExtractionResult(
                text=text,
                method=ExtractionMethod.OCR_IMAGE,
                page_count=1,
                ocr_mean_confidence=confidence,
            )
        raise CorpusExtractionFailed(
            f"Tipo não suportado pelo extrator: {media_type}."
        )

    def _extract_pdf(self, content: bytes) -> ExtractionResult:
        page_count = self._pdf_page_count(content)
        extracted = self._run(
            [
                str(self._pdftotext),
                "-layout",
                "-enc",
                "UTF-8",
                "-",
                "-",
            ],
            input_bytes=content,
        ).stdout.decode("utf-8", errors="strict")
        text = _normalize_text(extracted)
        density = len(text) / max(page_count, 1)
        if text and density >= MIN_NATIVE_CHARS_PER_PAGE:
            return ExtractionResult(
                text=text,
                method=ExtractionMethod.PDF_TEXT,
                page_count=page_count,
            )
        ocr_text, confidence, rendered_pages = self._ocr_pdf(content)
        return ExtractionResult(
            text=ocr_text,
            method=ExtractionMethod.OCR_PDF,
            page_count=rendered_pages or page_count,
            ocr_mean_confidence=confidence,
        )

    def _pdf_page_count(self, content: bytes) -> int:
        result = self._run(
            [str(self._pdfinfo), "-"],
            input_bytes=content,
        )
        match = re.search(
            rb"(?mi)^Pages:\s*([0-9]+)\s*$",
            result.stdout,
        )
        return int(match.group(1)) if match else 0

    def _ocr_pdf(self, content: bytes) -> tuple[str, float, int]:
        with tempfile.TemporaryDirectory(
            prefix="atrio-ocr-",
            dir=self._scratch_root,
        ) as directory:
            prefix = Path(directory) / "page"
            self._run(
                [
                    str(self._pdftoppm),
                    "-png",
                    "-r",
                    str(self._ocr_dpi),
                    "-",
                    str(prefix),
                ],
                input_bytes=content,
            )
            images = sorted(
                Path(directory).glob("page-*.png"),
                key=_page_sort_key,
            )
            if not images:
                raise CorpusExtractionFailed(
                    "Poppler não produziu páginas para OCR."
                )
            texts: list[str] = []
            confidences: list[float] = []
            for image in images:
                text, confidence = self._ocr_image(image.read_bytes())
                texts.append(text)
                if confidence is not None:
                    confidences.append(confidence)
            return (
                _normalize_text("\n\n".join(texts)),
                _mean(confidences),
                len(images),
            )

    def _ocr_image(self, content: bytes) -> tuple[str, float]:
        result = self._run(
            [
                str(self._tesseract),
                "stdin",
                "stdout",
                "-l",
                self._ocr_languages,
                "--psm",
                "6",
                "tsv",
            ],
            input_bytes=content,
        )
        try:
            decoded = result.stdout.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise CorpusExtractionFailed(
                "Tesseract devolveu TSV inválido."
            ) from exc
        return _text_from_tesseract_tsv(decoded)

    def _run(
        self,
        command: list[str],
        *,
        input_bytes: bytes | None = None,
        accept_stderr: bool = False,
    ) -> subprocess.CompletedProcess[bytes]:
        try:
            result = subprocess.run(
                command,
                input=input_bytes,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=self._command_timeout_seconds,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise CorpusExtractionFailed(
                f"Ferramenta local falhou: {Path(command[0]).name}."
            ) from exc
        if result.returncode != 0 and not (
            accept_stderr and result.returncode in {0, 1}
        ):
            raise CorpusExtractionFailed(
                f"Ferramenta local retornou código {result.returncode}: "
                f"{Path(command[0]).name}."
            )
        return result


class CorpusProcessor:
    def __init__(
        self,
        extractor: LocalCorpusExtractor,
        pii_engine: PiiEngine,
        *,
        pipeline_version: str = CORPUS_PIPELINE_VERSION,
    ):
        self._extractor = extractor
        self._pii = pii_engine
        self._pipeline_version = pipeline_version

    def process(
        self,
        *,
        execution_id: str,
        document_id: str,
        input_sha256: str,
        media_type: str,
        content: bytes,
        pseudonym_map: PseudonymMap,
    ) -> ProcessedCorpusDocument:
        digest = hashlib.sha256(content).hexdigest()
        if digest != input_sha256:
            raise CorpusIntegrityMismatch(
                "SHA-256 do documento diverge do intake."
            )
        extraction = self._extractor.extract(media_type, content)
        text = extraction.text
        cnj_match = _CNJ.search(text)
        cnj = cnj_match.group() if cnj_match else None
        secrecy_level, _ = self._pii.secrecy(text)
        findings = self._pii.detect(text)
        pseudonymized, counts = _apply_pseudonyms(
            text,
            findings,
            pseudonym_map,
            cnj=cnj,
        )
        review_type = _review_type(
            extraction,
            secrecy_level=secrecy_level,
        )
        status = (
            ProcessingStatus.REVIEW_REQUIRED
            if review_type is not None
            else ProcessingStatus.READY
        )
        output_sha256 = hashlib.sha256(
            pseudonymized.encode("utf-8")
        ).hexdigest()
        inventory = CorpusInventoryRecord(
            document_id=document_id,
            execution_id=execution_id,
            input_sha256=input_sha256,
            byte_length=len(content),
            media_type=media_type,
            extraction_method=extraction.method,
            page_count=extraction.page_count,
            extracted_char_count=len(text),
            ocr_mean_confidence=extraction.ocr_mean_confidence,
            cnj=cnj,
            procedural_class=_procedural_class(text),
            secrecy_level=secrecy_level or "none",
            pii_counts=tuple(sorted(counts.items())),
            pseudonym_count=sum(counts.values()),
            pseudonymized_sha256=output_sha256,
            status=status,
            review_type=review_type,
            corpus_pipeline_version=self._pipeline_version,
            atrio_pii_version=self._pii.version,
        )
        return ProcessedCorpusDocument(
            inventory=inventory,
            pseudonymized_text=pseudonymized,
        )


class ModulePiiEngine:
    def __init__(self, module: ModuleType, *, expected_version: str):
        version = getattr(module, "VERSAO", None)
        if version != expected_version:
            raise CorpusIntegrityMismatch(
                "Versão do atrio_pii diverge da release ativa."
            )
        for name in ("detectar", "eh_segredo"):
            if not callable(getattr(module, name, None)):
                raise CorpusIntegrityMismatch(
                    f"Contrato do atrio_pii incompleto: {name}."
                )
        self._module = module
        self._version = version

    @property
    def version(self) -> str:
        return self._version

    def detect(self, text: str) -> tuple[PiiFinding, ...]:
        findings = self._module.detectar(text)
        return tuple(
            PiiFinding(
                start=int(start),
                end=int(end),
                kind=str(kind),
                value=str(value),
            )
            for start, end, kind, value in findings
        )

    def secrecy(self, text: str) -> tuple[str | None, str | None]:
        level, term = self._module.eh_segredo(text)
        if level not in {None, "forte", "fraco"}:
            raise CorpusIntegrityMismatch(
                "Nível de sigilo inválido no atrio_pii."
            )
        return level, term


def load_pii_engine(
    source: Path,
    *,
    expected_version: str,
) -> ModulePiiEngine:
    resolved = source.resolve()
    if not resolved.is_file():
        raise CorpusToolUnavailable(
            f"Motor atrio_pii não encontrado: {resolved}."
        )
    spec = importlib.util.spec_from_file_location(
        "atrio_pii_runtime",
        resolved,
    )
    if spec is None or spec.loader is None:
        raise CorpusToolUnavailable(
            "Não foi possível carregar o motor atrio_pii."
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return ModulePiiEngine(
        module,
        expected_version=expected_version,
    )


def _apply_pseudonyms(
    text: str,
    findings: tuple[PiiFinding, ...],
    pseudonym_map: PseudonymMap,
    *,
    cnj: str | None,
) -> tuple[str, dict[str, int]]:
    ordered = sorted(findings, key=lambda item: (item.start, -item.end))
    previous_end = -1
    replacements: list[tuple[PiiFinding, str]] = []
    counts: dict[str, int] = {}
    for finding in ordered:
        if finding.end > len(text):
            raise CorpusIntegrityMismatch(
                "Identificador ultrapassa o texto extraído."
            )
        if finding.start < previous_end:
            raise CorpusIntegrityMismatch(
                "Identificadores sobrepostos no atrio_pii."
            )
        if text[finding.start : finding.end] != finding.value:
            raise CorpusIntegrityMismatch(
                "Identificador não corresponde ao texto extraído."
            )
        token = pseudonym_map.token_for(
            finding.kind,
            finding.value,
            origin_cnj=cnj,
        )
        replacements.append((finding, token))
        counts[finding.kind] = counts.get(finding.kind, 0) + 1
        previous_end = finding.end
    for finding, token in reversed(replacements):
        text = text[: finding.start] + token + text[finding.end :]
    return text, counts


def _review_type(
    extraction: ExtractionResult,
    *,
    secrecy_level: str | None,
) -> ReviewType | None:
    if secrecy_level is not None:
        return ReviewType.SECRECY
    if extraction.method in {
        ExtractionMethod.OCR_IMAGE,
        ExtractionMethod.OCR_PDF,
    }:
        return ReviewType.OCR
    if len(extraction.text) < MIN_EXTRACTED_CHARS:
        return ReviewType.QUALITY
    return None


def _procedural_class(text: str) -> str:
    normalized = text.upper()
    if "MANDADO DE SEGURAN" in normalized:
        return "MS"
    if "EMBARGOS DE DECLARA" in normalized:
        return "ED"
    if "RECURSO INOMINADO" in normalized:
        return "RI"
    if "AGRAVO" in normalized:
        return "AGRAVO"
    if "SENTEN" in normalized:
        return "SENTENCA"
    return "OUTRO"


def _normalize_text(text: str) -> str:
    if "\x00" in text:
        raise CorpusExtractionFailed("Texto extraído contém byte nulo.")
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def _extract_docx(content: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            total = sum(item.file_size for item in archive.infolist())
            if total > MAX_DOCX_EXPANDED_BYTES:
                raise CorpusExtractionFailed(
                    "DOCX excede o limite expandido."
                )
            info = archive.getinfo("word/document.xml")
            if info.file_size > MAX_DOCX_XML_BYTES:
                raise CorpusExtractionFailed(
                    "XML principal do DOCX excede o limite."
                )
            xml = archive.read(info)
    except (KeyError, zipfile.BadZipFile) as exc:
        raise CorpusExtractionFailed("DOCX inválido.") from exc
    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError as exc:
        raise CorpusExtractionFailed("XML principal do DOCX inválido.") from exc
    paragraphs: list[str] = []
    for paragraph in root.iter(
        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"
    ):
        pieces = [
            node.text or ""
            for node in paragraph.iter(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"
            )
        ]
        if pieces:
            paragraphs.append("".join(pieces))
    return _normalize_text("\n".join(paragraphs))


def _text_from_tesseract_tsv(value: str) -> tuple[str, float]:
    reader = csv.DictReader(io.StringIO(value), delimiter="\t")
    lines: list[str] = []
    current_key: tuple[str, str, str, str] | None = None
    current_words: list[str] = []
    confidences: list[float] = []
    required = {
        "page_num",
        "block_num",
        "par_num",
        "line_num",
        "conf",
        "text",
    }
    if reader.fieldnames is None or not required.issubset(reader.fieldnames):
        raise CorpusExtractionFailed("TSV do Tesseract incompleto.")
    for row in reader:
        word = (row.get("text") or "").strip()
        if not word:
            continue
        key = (
            row["page_num"],
            row["block_num"],
            row["par_num"],
            row["line_num"],
        )
        if current_key is not None and key != current_key:
            lines.append(" ".join(current_words))
            current_words = []
        current_key = key
        current_words.append(word)
        try:
            confidence = float(row["conf"])
        except (TypeError, ValueError):
            confidence = -1
        if confidence >= 0:
            confidences.append(confidence)
    if current_words:
        lines.append(" ".join(current_words))
    return _normalize_text("\n".join(lines)), _mean(confidences)


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 2)


def _required_command(name: str) -> Path:
    found = shutil.which(name)
    if found is None:
        raise CorpusToolUnavailable(
            f"Ferramenta local obrigatória ausente: {name}."
        )
    return Path(found)


def _sibling_or_command(root: Path, name: str) -> Path:
    for suffix in (".exe", ""):
        candidate = root / f"{name}{suffix}"
        if candidate.is_file():
            return candidate
    return _required_command(name)


def _page_sort_key(path: Path) -> tuple[int, str]:
    match = re.search(r"-([0-9]+)[.]png$", path.name)
    return (int(match.group(1)) if match else 0, path.name)
