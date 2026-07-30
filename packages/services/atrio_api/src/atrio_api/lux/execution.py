"""Execução governada do LUX 6.0.0 sobre saída aprovada pelo CERNE."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from enum import StrEnum
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping, Protocol
from uuid import UUID, uuid5

from atrio_api.adapters.ollama import (
    InferenceResult,
    OllamaAdapterError,
)
from atrio_api.corpus_intake import EncryptedCorpusStore
from atrio_api.corpus_processing import PiiEngine, load_pii_engine
from atrio_api.domain import (
    ArtifactRef,
    CerneGate,
    ComponentName,
    Destination,
    ExecutionStage,
    ExecutionState,
)

LUX_PACKAGE_VERSION = "6.0.0"
LUX_RUNTIME_VERSION = "0.1.0"
LUX_ARTIFACT_MEDIA_TYPE = "application/vnd.atrio.lux+json"
LUX_ARTIFACT_CLASSIFICATION = "INTERNAL_CONTROLLED"
_NORMATIVE_FILES = (
    "00_KERNEL_CURTO_UNIVERSAL_GPT_SAFE.txt",
    "01_UPLOAD_CONHECIMENTO_PERFIS_DE_ESTILO.txt",
    "02_UPLOAD_CONHECIMENTO_GUIA_E_TEMPLATES.txt",
)
_ARTIFACT_NAMESPACE = UUID("41f0217f-7fd8-4a67-a77a-31563dc5da3b")
_CNJ = re.compile(r"\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b")
_RAW_TAX_ID = re.compile(r"\b(?:\d{3}\.?\d{3}\.?\d{3}-?\d{2}|\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})\b")
_PSEUDOTOKEN = re.compile(r"\[([A-Z][A-Z0-9_]{1,31})_(\d{4,})\]")
_SENSITIVE_CONTEXT = re.compile(
    r"\b(criança|adolescente|segredo de justiça|violência doméstica|"
    r"saúde|sexualidade|filiação|adoção|curatela|escola|"
    r"dado financeiro|pessoa vulnerável)\b",
    re.IGNORECASE,
)
_MARKDOWN_DELETION = re.compile(r"~~.*?~~", re.DOTALL)
_MARKDOWN_BOLD = re.compile(r"\*\*(.*?)\*\*", re.DOTALL)


class LuxExecutionError(RuntimeError):
    pass


class LuxExecutionUnavailable(LuxExecutionError):
    pass


class LuxArtifactMissing(LuxExecutionError):
    pass


class LuxIntegrityError(LuxExecutionError):
    pass


class LuxPrivacyError(LuxIntegrityError):
    pass


class LuxGeneratedOutputInvalid(LuxExecutionError):
    pass


class LuxProviderError(LuxExecutionError):
    pass


class LuxRequestError(ValueError):
    pass


class LuxMode(StrEnum):
    PADRAO = "PADRAO"
    CLAREZA = "CLAREZA"
    ESTILO = "ESTILO"


class LuxDataMode(StrEnum):
    PUBLICO = "PUBLICO"
    PSEUDONIMIZADO = "PSEUDONIMIZADO"
    CORPUS = "CORPUS"


LUX_PROFILES = frozenset({"CHRISTIAN", "ISABELLA", "LUARA"})


class LuxProvider(Protocol):
    def generate(
        self,
        prompt: str,
        *,
        model: str,
        system: str | None = None,
        options: Mapping[str, Any] | None = None,
        format_schema: Mapping[str, Any] | None = None,
    ) -> InferenceResult: ...


@dataclass(frozen=True, slots=True)
class LuxOutput:
    marked_text: str
    changes: tuple[str, ...]
    final_text: str


@dataclass(frozen=True, slots=True)
class LuxRefinementDraft:
    artifact: ArtifactRef
    output: LuxOutput
    mode: str
    data_mode: str
    profile: str | None
    privacy_applied: bool
    suppression_reinforced: bool
    request_fingerprint: str
    generated: bool


class LuxExecutor:
    def __init__(
        self,
        store: EncryptedCorpusStore,
        provider: LuxProvider,
        *,
        model: str,
        knowledge_root: Path,
        pii_source: Path,
    ) -> None:
        if not model.strip():
            raise ValueError("model é obrigatório.")
        self._store = store
        self._provider = provider
        self._model = model.strip()
        self._knowledge_root = knowledge_root.resolve()
        self._pii_source = pii_source.resolve()
        self._knowledge = self._load_knowledge()
        self._knowledge_sha256 = _knowledge_sha256(
            self._knowledge_root,
            _NORMATIVE_FILES,
        )

    @property
    def model(self) -> str:
        return self._model

    def verify(self) -> None:
        self._load_knowledge()
        if not self._pii_source.is_file():
            raise LuxExecutionUnavailable(
                f"Motor atrio_pii ausente: {self._pii_source}."
            )

    def prepare(
        self,
        execution: ExecutionState,
        *,
        actor_id: str,
        idempotency_key: str,
        mode: str = LuxMode.PADRAO,
        profile: str | None = None,
        data_mode: str | None = None,
    ) -> LuxRefinementDraft:
        if execution.release.lux_version != LUX_PACKAGE_VERSION:
            raise LuxExecutionUnavailable(
                "Release ativa não corresponde ao pacote LUX 6.0.0."
            )
        mode = _normalize_mode(mode)
        profile = _normalize_profile(mode, profile)
        resolved_data_mode = _resolve_data_mode(execution, data_mode)
        handoff, ratio_digest = self._read_ratio_handoff(execution)
        cerne_digest = self._read_cerne_audit(execution)
        source = _audit_target_text(handoff)

        pii = load_pii_engine(
            self._pii_source,
            expected_version=execution.release.atrio_pii_version,
        )
        sanitized, privacy_applied, reinforced = _privacy_layer(
            source,
            resolved_data_mode,
            pii,
        )
        protected = _protected_tokens(sanitized)
        profile_text = _profile_text(
            self._knowledge["01_UPLOAD_CONHECIMENTO_PERFIS_DE_ESTILO.txt"],
            profile,
        )

        descriptor = {
            "actor_id": actor_id,
            "cerne_artifact_id": execution.cerne_artifact.artifact_id,
            "cerne_artifact_sha256": cerne_digest,
            "data_mode": resolved_data_mode,
            "execution_id": execution.execution_id,
            "knowledge_sha256": self._knowledge_sha256,
            "lux_package_version": LUX_PACKAGE_VERSION,
            "lux_runtime_version": LUX_RUNTIME_VERSION,
            "mode": mode,
            "model": self._model,
            "operation": "REFINE_CERNE_APPROVED_RATIO_TARGET",
            "profile": profile,
            "ratio_artifact_id": execution.ratio_artifact.artifact_id,
            "ratio_artifact_sha256": ratio_digest,
            "release_id": execution.release.release_id,
        }
        request_fingerprint = _json_sha256(descriptor)
        artifact_id = _artifact_id(execution.execution_id, idempotency_key)
        storage_key = _artifact_storage_key(execution.execution_id, artifact_id)

        existing = self._read_existing(
            storage_key,
            expected_request_fingerprint=request_fingerprint,
        )
        if existing is not None:
            return self._draft_from_plaintext(
                execution,
                artifact_id,
                existing,
                request_fingerprint=request_fingerprint,
                generated=False,
            )
        if execution.stage is ExecutionStage.FINAL_INTEGRITY_CHECK:
            raise LuxRequestError(
                "LUX já foi concluído; nova execução exige RETRY_LUX governado."
            )

        prompt = _prompt(
            sanitized,
            mode=mode,
            data_mode=resolved_data_mode,
            profile=profile,
            profile_text=profile_text,
            protected=protected,
        )
        system = "\n\n---\n\n".join(
            self._knowledge[name] for name in _NORMATIVE_FILES
        )
        try:
            inference = self._provider.generate(
                prompt,
                model=self._model,
                system=system,
                format_schema=_response_schema(),
            )
        except (OllamaAdapterError, ValueError) as exc:
            raise LuxProviderError("Provedor LUX falhou.") from exc

        output = _parse_output(inference.content)
        if privacy_applied:
            treatment = (
                "anonimização"
                if resolved_data_mode == LuxDataMode.PUBLICO
                else "pseudonimização"
            )
            output = LuxOutput(
                marked_text=output.marked_text,
                changes=(
                    f"Aplicada {treatment} de identificadores, "
                    "com propagação aos três blocos.",
                    *output.changes,
                ),
                final_text=output.final_text,
            )
        _validate_output(
            sanitized,
            output,
            protected=protected,
            data_mode=resolved_data_mode,
            pii=pii,
        )
        privacy_note = (
            "ANONIMIZACAO_APLICADA"
            if privacy_applied
            else "ENTRADA_JA_COMPATIVEL"
        )
        bundle = {
            "cerne_artifact_id": execution.cerne_artifact.artifact_id,
            "data_mode": resolved_data_mode,
            "execution_id": execution.execution_id,
            "inference_metadata": asdict(inference.metadata),
            "kind": "LUX_REFINEMENT",
            "knowledge_sha256": self._knowledge_sha256,
            "lux_package_version": LUX_PACKAGE_VERSION,
            "lux_runtime_version": LUX_RUNTIME_VERSION,
            "mode": mode,
            "operation": "REFINE_CERNE_APPROVED_RATIO_TARGET",
            "output": {
                "alteracoes_realizadas": list(output.changes),
                "texto_com_marcacoes": output.marked_text,
                "versao_final_limpa": output.final_text,
            },
            "privacy": {
                "applied": privacy_applied,
                "note": privacy_note,
                "suppression_reinforced": reinforced,
            },
            "profile": profile,
            "ratio_artifact_id": execution.ratio_artifact.artifact_id,
            "ratio_artifact_sha256": ratio_digest,
            "release_id": execution.release.release_id,
            "request_fingerprint": request_fingerprint,
            "schema_version": execution.release.schema_version,
        }
        plaintext = _canonical_bytes(bundle)
        self._store.write_private_record(storage_key, plaintext)
        return self._draft(
            execution,
            artifact_id=artifact_id,
            plaintext=plaintext,
            output=output,
            mode=mode,
            data_mode=resolved_data_mode,
            profile=profile,
            privacy_applied=privacy_applied,
            suppression_reinforced=reinforced,
            request_fingerprint=request_fingerprint,
            generated=True,
        )

    def _load_knowledge(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for name in _NORMATIVE_FILES:
            path = self._knowledge_root / name
            if not path.is_file():
                raise LuxExecutionUnavailable(
                    f"Arquivo normativo LUX ausente: {name}."
                )
            result[name] = path.read_text(encoding="utf-8").strip()
            if not result[name]:
                raise LuxExecutionUnavailable(
                    f"Arquivo normativo LUX vazio: {name}."
                )
        return result

    def _read_ratio_handoff(
        self,
        execution: ExecutionState,
    ) -> tuple[dict[str, Any], str]:
        if execution.ratio_artifact is None:
            raise LuxArtifactMissing("Handoff RATIO ausente.")
        try:
            execution.release.assert_artifact(
                execution.ratio_artifact,
                expected_producer=ComponentName.RATIO,
            )
        except ValueError as exc:
            raise LuxIntegrityError(
                "Referência RATIO diverge da release ativa."
            ) from exc
        plaintext = _read_artifact(
            self._store,
            execution,
            execution.ratio_artifact,
        )
        payload = _decode_bundle(plaintext)
        if (
            payload.get("kind") != "RATIO_HANDOFF"
            or payload.get("execution_id") != execution.execution_id
            or payload.get("release_id") != execution.release.release_id
        ):
            raise LuxIntegrityError("Handoff RATIO não pertence à execução.")
        return payload, hashlib.sha256(plaintext).hexdigest()

    def _read_cerne_audit(self, execution: ExecutionState) -> str:
        if (
            execution.stage
            not in {
                ExecutionStage.CERNE_APPROVED,
                ExecutionStage.LUX_REFINING,
                ExecutionStage.FINAL_INTEGRITY_CHECK,
            }
            or execution.cerne_gate is not CerneGate.AVANCA
        ):
            raise LuxRequestError(
                "LUX exige CERNE aprovado com gate AVANCA."
            )
        if execution.cerne_artifact is None:
            raise LuxArtifactMissing("Artefato CERNE ausente.")
        try:
            execution.release.assert_artifact(
                execution.cerne_artifact,
                expected_producer=ComponentName.CERNE,
            )
        except ValueError as exc:
            raise LuxIntegrityError(
                "Referência CERNE diverge da release ativa."
            ) from exc
        plaintext = _read_artifact(
            self._store,
            execution,
            execution.cerne_artifact,
        )
        payload = _decode_bundle(plaintext)
        if (
            payload.get("kind") != "CERNE_AUDIT"
            or payload.get("execution_id") != execution.execution_id
            or payload.get("release_id") != execution.release.release_id
            or payload.get("ratio_artifact_id")
            != execution.ratio_artifact.artifact_id
        ):
            raise LuxIntegrityError(
                "CERNE não auditou o handoff RATIO corrente."
            )
        gate = (
            payload.get("audit_response", {})
            .get("gate", {})
            .get("estado")
        )
        if gate != CerneGate.AVANCA.value:
            raise LuxIntegrityError(
                "Artefato CERNE não registra gate AVANCA."
            )
        return hashlib.sha256(plaintext).hexdigest()

    def _read_existing(
        self,
        storage_key: str,
        *,
        expected_request_fingerprint: str,
    ) -> bytes | None:
        try:
            plaintext = self._store.read_private_record(storage_key)
        except FileNotFoundError:
            return None
        payload = _decode_bundle(plaintext)
        if (
            payload.get("kind") != "LUX_REFINEMENT"
            or payload.get("operation")
            != "REFINE_CERNE_APPROVED_RATIO_TARGET"
            or payload.get("request_fingerprint")
            != expected_request_fingerprint
        ):
            raise LuxIntegrityError(
                "Chave idempotente já preparou outro artefato LUX."
            )
        return plaintext

    def _draft_from_plaintext(
        self,
        execution: ExecutionState,
        artifact_id: str,
        plaintext: bytes,
        *,
        request_fingerprint: str,
        generated: bool,
    ) -> LuxRefinementDraft:
        payload = _decode_bundle(plaintext)
        raw_output = payload.get("output")
        if not isinstance(raw_output, dict):
            raise LuxIntegrityError("Artefato LUX não contém output.")
        output = LuxOutput(
            marked_text=_required_text(raw_output, "texto_com_marcacoes"),
            changes=tuple(
                _required_string_list(raw_output, "alteracoes_realizadas")
            ),
            final_text=_required_text(raw_output, "versao_final_limpa"),
        )
        privacy = payload.get("privacy")
        if not isinstance(privacy, dict):
            raise LuxIntegrityError("Artefato LUX não contém privacy.")
        return self._draft(
            execution,
            artifact_id=artifact_id,
            plaintext=plaintext,
            output=output,
            mode=_required_text(payload, "mode"),
            data_mode=_required_text(payload, "data_mode"),
            profile=payload.get("profile"),
            privacy_applied=bool(privacy.get("applied")),
            suppression_reinforced=bool(
                privacy.get("suppression_reinforced")
            ),
            request_fingerprint=request_fingerprint,
            generated=generated,
        )

    @staticmethod
    def _draft(
        execution: ExecutionState,
        *,
        artifact_id: str,
        plaintext: bytes,
        output: LuxOutput,
        mode: str,
        data_mode: str,
        profile: str | None,
        privacy_applied: bool,
        suppression_reinforced: bool,
        request_fingerprint: str,
        generated: bool,
    ) -> LuxRefinementDraft:
        return LuxRefinementDraft(
            artifact=ArtifactRef(
                artifact_id=artifact_id,
                sha256=hashlib.sha256(plaintext).hexdigest(),
                media_type=LUX_ARTIFACT_MEDIA_TYPE,
                classification=LUX_ARTIFACT_CLASSIFICATION,
                producer=ComponentName.LUX,
                producer_version=execution.release.lux_version,
                release_id=execution.release.release_id,
                schema_version=execution.release.schema_version,
            ),
            output=output,
            mode=mode,
            data_mode=data_mode,
            profile=profile,
            privacy_applied=privacy_applied,
            suppression_reinforced=suppression_reinforced,
            request_fingerprint=request_fingerprint,
            generated=generated,
        )


def _normalize_mode(value: str) -> str:
    normalized = str(value).strip().upper()
    if normalized not in {
        LuxMode.PADRAO,
        LuxMode.CLAREZA,
        LuxMode.ESTILO,
    }:
        raise LuxRequestError(f"Modo LUX inválido: {value}.")
    return normalized


def _normalize_profile(mode: str, profile: str | None) -> str | None:
    if profile is None:
        if mode == LuxMode.ESTILO:
            raise LuxRequestError("Modo ESTILO exige profile.")
        return None
    normalized = profile.strip().upper()
    if normalized not in LUX_PROFILES:
        raise LuxRequestError(f"Perfil LUX desconhecido: {profile}.")
    if mode != LuxMode.ESTILO:
        raise LuxRequestError("profile só é permitido no modo ESTILO.")
    return normalized


def _resolve_data_mode(
    execution: ExecutionState,
    requested: str | None,
) -> str:
    forced_public = execution.destination in {
        Destination.PUBLICO,
        Destination.EXTERNO,
    }
    if requested is None:
        return (
            LuxDataMode.PUBLICO
            if forced_public
            else LuxDataMode.CORPUS
        )
    normalized = requested.strip().upper()
    allowed = {
        LuxDataMode.PUBLICO,
        LuxDataMode.PSEUDONIMIZADO,
        LuxDataMode.CORPUS,
    }
    if normalized not in allowed:
        raise LuxRequestError(f"data_mode LUX inválido: {requested}.")
    if forced_public and normalized != LuxDataMode.PUBLICO:
        raise LuxRequestError(
            "Destino externo/público exige data_mode PUBLICO."
        )
    return normalized


def _privacy_layer(
    text: str,
    mode: str,
    pii: PiiEngine,
) -> tuple[str, bool, bool]:
    source = text.strip()
    reinforced = bool(_SENSITIVE_CONTEXT.search(source))
    if mode == LuxDataMode.CORPUS:
        findings = pii.detect(source)
        if findings:
            raise LuxPrivacyError(
                "Modo CORPUS recebeu identificador cru após o CORPUS."
            )
        return source, False, reinforced

    if mode == LuxDataMode.PUBLICO:
        result = _replace_findings_public(source, pii.detect(source))
        result = _CNJ.sub("[processo]", result)
        result = _PSEUDOTOKEN.sub(
            lambda match: _public_marker(match.group(1)),
            result,
        )
        return result, result != source, reinforced

    # PSEUDONIMIZADO
    counters: Counter[str] = Counter()
    result = source
    replacements: list[tuple[int, int, str]] = []
    for finding in pii.detect(source):
        kind = _pseudonym_kind(finding.kind)
        counters[kind] += 1
        replacements.append(
            (
                finding.start,
                finding.end,
                f"[{kind}_{counters[kind]:04d}]",
            )
        )
    cnj_counter = 0
    occupied = [(start, end) for start, end, _ in replacements]
    for match in _CNJ.finditer(source):
        if any(match.start() < end and start < match.end() for start, end in occupied):
            continue
        cnj_counter += 1
        replacements.append(
            (
                match.start(),
                match.end(),
                f"[PROCESSO_{cnj_counter:04d}]",
            )
        )
    for start, end, replacement in sorted(
        replacements,
        key=lambda item: item[0],
        reverse=True,
    ):
        result = result[:start] + replacement + result[end:]
    return result, result != source, reinforced


def _replace_findings_public(text: str, findings: tuple[Any, ...]) -> str:
    result = text
    for finding in sorted(findings, key=lambda item: item.start, reverse=True):
        result = (
            result[: finding.start]
            + _public_marker(finding.kind)
            + result[finding.end :]
        )
    return result


def _public_marker(kind: str) -> str:
    normalized = kind.upper()
    if normalized in {"PESSOA"}:
        return "[pessoa]"
    if normalized in {"CNPJ", "EMPRESA"}:
        return "[instituição]"
    if normalized in {"EMAIL", "TELEFONE"}:
        return "[contato]"
    if normalized in {"CEP", "ENDERECO"}:
        return "[local]"
    if normalized in {"CPF", "RG", "OAB"}:
        return "[documento]"
    if normalized in {"PROCESSO", "CNJ"}:
        return "[processo]"
    return "[identificador]"


def _pseudonym_kind(kind: str) -> str:
    normalized = kind.upper()
    return {
        "PESSOA": "PESSOA",
        "CNPJ": "EMPRESA",
        "EMAIL": "EMAIL",
        "TELEFONE": "TELEFONE",
        "CEP": "ENDERECO",
        "CPF": "CPF",
        "RG": "RG",
        "OAB": "OAB",
    }.get(normalized, "IDENTIFICADOR")


def _profile_text(knowledge: str, profile: str | None) -> str:
    if profile is None:
        return ""
    marker = f"## PERFIL {profile}"
    start = knowledge.find(marker)
    if start < 0:
        raise LuxExecutionUnavailable(
            f"Perfil LUX {profile} ausente da base normativa."
        )
    next_header = knowledge.find("\n## PERFIL ", start + len(marker))
    return (
        knowledge[start:]
        if next_header < 0
        else knowledge[start:next_header]
    ).strip()


def _prompt(
    text: str,
    *,
    mode: str,
    data_mode: str,
    profile: str | None,
    profile_text: str,
    protected: tuple[str, ...],
) -> str:
    mode_instruction = {
        LuxMode.PADRAO: "Revisão Padrão de Gabinete.",
        LuxMode.CLAREZA: "Revisão Padrão + Clareza e Fluidez.",
        LuxMode.ESTILO: (
            f"Revisão Padrão + Clareza e Fluidez + perfil {profile}."
        ),
    }[mode]
    return (
        "Execute LUX 6.0.0 sobre o texto abaixo.\n"
        f"MODO: {mode} — {mode_instruction}\n"
        f"TRATAMENTO DE DADOS: {data_mode}.\n"
        "A Camada 0 já foi aplicada deterministicamente antes desta chamada. "
        "Não reverta, detalhe ou tente reidentificar qualquer marcador.\n"
        "Preserve literalmente todos os tokens protegidos listados. "
        "Não crie nova norma, precedente, valor, data, dispositivo, tese ou conclusão.\n"
        "A saída deve seguir estritamente o schema JSON fornecido e representar "
        "os três blocos do LUX: texto com marcações, alterações realizadas e versão final limpa.\n"
        "A versão final deve ser exatamente o texto marcado depois de removidas "
        "as marcações **...** e as exclusões ~~...~~.\n\n"
        f"PERFIL ATIVO:\n{profile_text or 'nenhum'}\n\n"
        "TOKENS PROTEGIDOS:\n"
        + json.dumps(list(protected), ensure_ascii=False)
        + "\n\nTEXTO JÁ TRATADO PELA CAMADA 0:\n"
        + text
    )


def _response_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["marked_text", "changes", "final_text"],
        "properties": {
            "marked_text": {"type": "string", "minLength": 1},
            "changes": {
                "type": "array",
                "items": {"type": "string"},
            },
            "final_text": {"type": "string", "minLength": 1},
        },
    }


def _parse_output(content: str) -> LuxOutput:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise LuxGeneratedOutputInvalid(
            "LUX devolveu JSON inválido."
        ) from exc
    if not isinstance(payload, dict) or set(payload) != {
        "marked_text",
        "changes",
        "final_text",
    }:
        raise LuxGeneratedOutputInvalid(
            "LUX devolveu campos fora do contrato."
        )
    marked = payload["marked_text"]
    final = payload["final_text"]
    changes = payload["changes"]
    if (
        not isinstance(marked, str)
        or not marked.strip()
        or not isinstance(final, str)
        or not final.strip()
        or not isinstance(changes, list)
        or not all(isinstance(item, str) for item in changes)
    ):
        raise LuxGeneratedOutputInvalid(
            "LUX devolveu tipos incompatíveis com o contrato."
        )
    return LuxOutput(
        marked_text=marked.strip(),
        changes=tuple(item.strip() for item in changes if item.strip()),
        final_text=final.strip(),
    )


def _validate_output(
    source: str,
    output: LuxOutput,
    *,
    protected: tuple[str, ...],
    data_mode: str,
    pii: PiiEngine,
) -> None:
    # Camada 0 é hard-stop: vazamento de PII tem precedência sobre
    # qualquer diagnóstico formal ou semântico do texto gerado.
    blocks = (
        output.marked_text,
        output.final_text,
        *output.changes,
    )
    if data_mode in {
        LuxDataMode.PUBLICO,
        LuxDataMode.PSEUDONIMIZADO,
    }:
        for block in blocks:
            _assert_no_raw_identifiers(block, pii)

    if data_mode == LuxDataMode.PUBLICO:
        for block in blocks:
            if _CNJ.search(block) or _PSEUDOTOKEN.search(block):
                raise LuxPrivacyError(
                    "Saída pública LUX preservou identificador estável."
                )

    clean_from_marked = _marked_to_clean(output.marked_text)
    if _canonical_text(clean_from_marked) != _canonical_text(output.final_text):
        raise LuxGeneratedOutputInvalid(
            "Versão final não corresponde ao texto marcado."
        )

    for token in protected:
        if source.count(token) != output.final_text.count(token):
            raise LuxGeneratedOutputInvalid(
                f"Token intocável alterado pelo LUX: {token!r}."
            )

    source_protected = Counter(_protected_tokens(source))
    output_protected = Counter(_protected_tokens(output.final_text))
    for token, count in output_protected.items():
        if count > source_protected[token]:
            raise LuxGeneratedOutputInvalid(
                f"LUX introduziu token jurídico/estrutural novo: {token!r}."
            )


def _assert_no_raw_identifiers(text: str, pii: PiiEngine) -> None:
    # O motor PII pode validar estrutura/checksum. Para a fronteira de saída
    # do LUX, a política é mais conservadora: qualquer sequência lexical com
    # formato de CPF/CNPJ também é tratada como identificador cru.
    if (
        pii.detect(text)
        or _CNJ.search(text)
        or _RAW_TAX_ID.search(text)
    ):
        raise LuxPrivacyError(
            "Saída LUX contém identificador cru."
        )


def _marked_to_clean(text: str) -> str:
    without_deleted = _MARKDOWN_DELETION.sub("", text)
    return _MARKDOWN_BOLD.sub(r"\1", without_deleted)


def _canonical_text(text: str) -> str:
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def _protected_tokens(text: str) -> tuple[str, ...]:
    patterns = (
        r"\[[^\[\]\n]{2,80}\]",
        r"“[^”\n]{1,500}”",
        r'"[^"\n]{1,500}"',
        r"\b(?:art\.?|arts\.)\s*\d+(?:[.\-º°]?\w+)*(?:\s*,?\s*(?:§|inciso)\s*\w+)?",
        r"\b(?:Lei|Resolução|Súmula|Tema|REsp|AREsp|AgInt|PUIL|IRDR|IAC)\s*(?:n[º°.]?\s*)?[A-Za-z0-9./-]+",
        r"\b\d{1,3}(?:[.,]\d+)?%",
        r"R\$\s*\d[\d.]*,\d{2}",
        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
        r"\b\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b",
        r"\bante o exposto\b[^.!?\n]*(?:[.!?]|$)",
        r"\bvoto pelo\b[^.!?\n]*(?:[.!?]|$)",
        r"\brecurso (?:não )?(?:conhecido|provido|desprovido)\b[^.!?\n]*(?:[.!?]|$)",
        r"\bembargos (?:acolhidos|rejeitados)\b[^.!?\n]*(?:[.!?]|$)",
    )
    found: list[tuple[int, str]] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            token = match.group(0).strip()
            if token:
                found.append((match.start(), token))
    found.sort(key=lambda item: (item[0], -len(item[1])))
    seen: set[tuple[int, str]] = set()
    ordered: list[str] = []
    for position, token in found:
        key = (position, token)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(token)
    return tuple(ordered)


def _audit_target_text(handoff: Mapping[str, Any]) -> str:
    target = handoff.get("audit_target")
    if not isinstance(target, dict):
        raise LuxIntegrityError("Handoff RATIO não contém audit_target.")
    text = target.get("text")
    if not isinstance(text, str) or len(text.strip()) < 40:
        raise LuxIntegrityError("audit_target RATIO é inválido.")
    return text.strip()


def _read_artifact(
    store: EncryptedCorpusStore,
    execution: ExecutionState,
    artifact: ArtifactRef,
) -> bytes:
    storage_key = _artifact_storage_key(
        execution.execution_id,
        artifact.artifact_id,
    )
    try:
        plaintext = store.read_private_record(storage_key)
    except FileNotFoundError as exc:
        raise LuxArtifactMissing(
            f"Artefato {artifact.producer.value} não está no cofre."
        ) from exc
    if hashlib.sha256(plaintext).hexdigest() != artifact.sha256:
        raise LuxIntegrityError(
            f"Hash do artefato {artifact.producer.value} diverge do cofre."
        )
    return plaintext


def _artifact_id(execution_id: str, idempotency_key: str) -> str:
    UUID(execution_id)
    if not idempotency_key.strip():
        raise ValueError("idempotency_key é obrigatória.")
    return str(
        uuid5(
            _ARTIFACT_NAMESPACE,
            f"{execution_id}\x1fLUX_REFINEMENT\x1f{idempotency_key}",
        )
    )


def _artifact_storage_key(execution_id: str, artifact_id: str) -> str:
    UUID(execution_id)
    UUID(artifact_id)
    return f"artifacts/{execution_id}/{artifact_id}.atrio"


def _knowledge_sha256(root: Path, names: tuple[str, ...]) -> str:
    digest = hashlib.sha256()
    for name in names:
        path = root / name
        if not path.is_file():
            raise LuxExecutionUnavailable(
                f"Arquivo normativo LUX ausente: {name}."
            )
        relative = name.encode("utf-8")
        content = path.read_bytes()
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def _decode_bundle(plaintext: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(plaintext.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LuxIntegrityError("Artefato privado possui JSON inválido.") from exc
    if not isinstance(payload, dict):
        raise LuxIntegrityError("Artefato privado não é objeto JSON.")
    return payload


def _required_text(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise LuxIntegrityError(f"Campo LUX ausente/inválido: {key}.")
    return value.strip()


def _required_string_list(payload: Mapping[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise LuxIntegrityError(f"Lista LUX inválida: {key}.")
    return [item for item in value if item.strip()]


def _json_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
