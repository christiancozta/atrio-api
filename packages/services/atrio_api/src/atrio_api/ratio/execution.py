"""Execução confidencial de fases do RATIO e construção do handoff."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Protocol
from uuid import UUID, uuid5

from atrio_api.adapters.ollama import InferenceResult
from atrio_api.corpus_intake import EncryptedCorpusStore
from atrio_api.domain import ArtifactRef, ComponentName, ExecutionState, RatioModule
from atrio_api.ratio.contract import (
    RatioPhase,
    RatioPhaseStatus,
    TroiaStatus,
)
from atrio_api.ratio.persistence import RatioArtifactRecord
from atrio_api.ratio.state import RatioRunState, phase_index


RATIO_EXECUTOR_VERSION = "0.1.0"
RATIO_PHASE_MEDIA_TYPE = "application/vnd.atrio.ratio.phase+json"
RATIO_HANDOFF_MEDIA_TYPE = "application/vnd.atrio.ratio+json"
RATIO_ARTIFACT_CLASSIFICATION = "INTERNAL_PSEUDONYMIZED"
_ARTIFACT_NAMESPACE = UUID("4c01854c-a794-45f6-bd64-e303385e192e")

_VALIDATED = frozenset(
    {
        RatioPhaseStatus.VALIDATED,
        RatioPhaseStatus.VALIDATED_WITH_NONBLOCKING_CAVEAT,
        RatioPhaseStatus.DISPENSED_BY_EXCEPTION,
    }
)


_FINAL_AUDIT_OBJECT_TYPES: dict[RatioPhase, tuple[str, ...]] = {
    RatioPhase.RI_06: ("voto",),
    RatioPhase.ED_05: ("voto",),
    RatioPhase.MS_07: ("sentenca", "acordao"),
}


class RatioExecutionError(RuntimeError):
    pass


class RatioExecutionUnavailable(RatioExecutionError):
    pass


class RatioArtifactMissing(RatioExecutionError):
    pass


class RatioExecutorIntegrityError(RatioExecutionError):
    pass


class RatioGeneratedOutputInvalid(RatioExecutionError):
    pass


class RatioInferenceProvider(Protocol):
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
class RatioExecutionDraft:
    artifact: ArtifactRef
    artifact_roles: tuple[str, ...]
    request_fingerprint: str
    generated: bool


@dataclass(frozen=True, slots=True)
class RatioPhaseExecutionResult:
    execution_state: ExecutionState
    ratio_state: RatioRunState
    artifact: ArtifactRef
    artifact_roles: tuple[str, ...]
    created: bool


@dataclass(frozen=True, slots=True)
class RatioFinalizeResult:
    execution_state: ExecutionState
    ratio_state: RatioRunState
    artifact: ArtifactRef
    created: bool


class RatioPhaseExecutor:
    def __init__(
        self,
        store: EncryptedCorpusStore,
        provider: RatioInferenceProvider,
        *,
        model: str,
        ratio_root: Path,
    ) -> None:
        if not model or model.strip() != model:
            raise ValueError("Modelo RATIO deve ser informado sem espaços externos.")
        self._store = store
        self._provider = provider
        self._model = model
        self._ratio_root = ratio_root.resolve()
        if not self._ratio_root.is_dir():
            raise FileNotFoundError(f"Pacote RATIO ausente: {self._ratio_root}")

    @property
    def model(self) -> str:
        return self._model

    def has_prepared(
        self,
        execution_id: str,
        *,
        operation: str,
        idempotency_key: str,
    ) -> bool:
        artifact_id = _artifact_id(execution_id, operation, idempotency_key)
        try:
            self._store.read_private_record(
                _artifact_storage_key(execution_id, artifact_id)
            )
        except FileNotFoundError:
            return False
        return True

    def prepare_phase(
        self,
        execution: ExecutionState,
        ratio: RatioRunState,
        artifacts: tuple[RatioArtifactRecord, ...],
        *,
        actor_id: str,
        idempotency_key: str,
    ) -> RatioExecutionDraft:
        if ratio.current_phase is RatioPhase.ED_03 and (
            ratio.troia.status is TroiaStatus.NOT_STARTED
        ):
            raise RatioGeneratedOutputInvalid(
                "ED_03 exige configuração prévia de TROIA."
            )

        corpus_text, corpus_sha = self._read_corpus(execution)
        normative = self._normative_text(ratio.module)
        normative_sha = hashlib.sha256(normative.encode("utf-8")).hexdigest()
        prior = self._prior_outputs(execution, ratio, artifacts)

        troia_active = (
            ratio.current_phase is ratio.troia.phase
            and ratio.troia.status
            in {TroiaStatus.RUNNING, TroiaStatus.PENDING_REMEDIATION}
        )
        roles = [f"PHASE:{ratio.current_phase.value}"]
        if troia_active:
            roles.append(f"TROIA:{ratio.current_phase.value}")

        request_descriptor = {
            "actor_id": actor_id,
            "corpus_sha256": corpus_sha,
            "execution_id": execution.execution_id,
            "model": self._model,
            "normative_sha256": normative_sha,
            "operation": "EXECUTE_PHASE",
            "phase": ratio.current_phase.value,
            "prior_artifacts": [
                {
                    "artifact_id": item["artifact_id"],
                    "revision": item["revision"],
                    "sha256": item["sha256"],
                }
                for item in prior
            ],
            "ratio_revision": ratio.revision,
            "release_id": execution.release.release_id,
            "troia_status": ratio.troia.status.value,
            "troia_triggers": sorted(
                trigger.value for trigger in ratio.troia.triggers
            ),
        }
        request_fingerprint = _json_sha256(request_descriptor)
        artifact_id = _artifact_id(
            execution.execution_id,
            "EXECUTE_PHASE",
            idempotency_key,
        )
        storage_key = _artifact_storage_key(execution.execution_id, artifact_id)

        existing = self._read_existing(
            storage_key,
            expected_request_fingerprint=request_fingerprint,
            expected_operation="EXECUTE_PHASE",
        )
        if existing is not None:
            artifact = _artifact_ref(
                execution,
                artifact_id,
                existing,
                RATIO_PHASE_MEDIA_TYPE,
            )
            existing_payload = _decode_private_bundle(existing)
            stored_roles = tuple(
                _string_list(existing_payload, "artifact_roles")
            )
            if stored_roles != tuple(roles):
                raise RatioExecutorIntegrityError(
                    "Papéis do artefato preparado divergem da requisição."
                )
            return RatioExecutionDraft(
                artifact=artifact,
                artifact_roles=stored_roles,
                request_fingerprint=request_fingerprint,
                generated=False,
            )

        prompt = _phase_prompt(
            ratio,
            corpus_text=corpus_text,
            normative=normative,
            prior=prior,
        )
        schema = _output_schema(ratio.current_phase, troia_active=troia_active)
        result = self._provider.generate(
            prompt,
            model=self._model,
            system=_SYSTEM_INSTRUCTION,
            format_schema=schema,
        )
        output = _parse_output(
            result.content,
            ratio.current_phase,
            troia_active=troia_active,
        )
        bundle = {
            "artifact_roles": roles,
            "executor_version": RATIO_EXECUTOR_VERSION,
            "inference_metadata": asdict(result.metadata),
            "kind": "RATIO_PHASE_OUTPUT",
            "module": ratio.module.value,
            "operation": "EXECUTE_PHASE",
            "output": output,
            "phase": ratio.current_phase.value,
            "ratio_revision": ratio.revision,
            "release_id": execution.release.release_id,
            "request_fingerprint": request_fingerprint,
            "schema_version": execution.release.schema_version,
        }
        plaintext = _canonical_bytes(bundle)
        self._store.write_private_record(storage_key, plaintext)
        return RatioExecutionDraft(
            artifact=_artifact_ref(
                execution,
                artifact_id,
                plaintext,
                RATIO_PHASE_MEDIA_TYPE,
            ),
            artifact_roles=tuple(roles),
            request_fingerprint=request_fingerprint,
            generated=True,
        )

    def prepare_handoff(
        self,
        execution: ExecutionState,
        ratio: RatioRunState,
        artifacts: tuple[RatioArtifactRecord, ...],
        *,
        actor_id: str,
        idempotency_key: str,
    ) -> RatioExecutionDraft:
        selected = _latest_phase_artifacts(ratio, artifacts)
        required = [item.phase for item in ratio.phases]
        missing = [
            phase.value
            for phase in required
            if phase not in selected
        ]
        if missing:
            raise RatioArtifactMissing(
                "Faltam artefatos de fase para o handoff: "
                + ", ".join(missing)
                + "."
            )

        final_phase = required[-1]
        final_private = self._read_ratio_artifact(
            execution,
            selected[final_phase],
        )
        audit_target = _audit_target_from_phase_output(
            final_private.get("output"),
            final_phase,
        )

        descriptor = {
            "actor_id": actor_id,
            "audit_target_sha256": _json_sha256(audit_target),
            "execution_id": execution.execution_id,
            "operation": "FINALIZE_RATIO",
            "ratio_revision": ratio.revision,
            "release_id": execution.release.release_id,
            "sources": [
                {
                    "artifact_id": selected[phase].artifact.artifact_id,
                    "phase": phase.value,
                    "revision": selected[phase].revision,
                    "sha256": selected[phase].artifact.sha256,
                }
                for phase in required
            ],
        }
        request_fingerprint = _json_sha256(descriptor)
        artifact_id = _artifact_id(
            execution.execution_id,
            "FINALIZE_RATIO",
            idempotency_key,
        )
        storage_key = _artifact_storage_key(execution.execution_id, artifact_id)

        existing = self._read_existing(
            storage_key,
            expected_request_fingerprint=request_fingerprint,
            expected_operation="FINALIZE_RATIO",
        )
        if existing is not None:
            existing_payload = _decode_private_bundle(existing)
            _audit_target_from_handoff(existing_payload)
            return RatioExecutionDraft(
                artifact=_artifact_ref(
                    execution,
                    artifact_id,
                    existing,
                    RATIO_HANDOFF_MEDIA_TYPE,
                ),
                artifact_roles=("FINAL_HANDOFF",),
                request_fingerprint=request_fingerprint,
                generated=False,
            )

        phase_outputs = []
        for phase in required:
            record = selected[phase]
            private = self._read_ratio_artifact(execution, record)
            phase_outputs.append(
                {
                    "artifact_id": record.artifact.artifact_id,
                    "artifact_sha256": record.artifact.sha256,
                    "output": private["output"],
                    "phase": phase.value,
                    "source_revision": record.revision,
                }
            )

        bundle = {
            "artifact_roles": ["FINAL_HANDOFF"],
            "audit_target": audit_target,
            "execution_id": execution.execution_id,
            "kind": "RATIO_HANDOFF",
            "module": ratio.module.value,
            "operation": "FINALIZE_RATIO",
            "phase_outputs": phase_outputs,
            "ratio_revision": ratio.revision,
            "ratio_version": execution.release.ratio_version,
            "release_id": execution.release.release_id,
            "request_fingerprint": request_fingerprint,
            "schema_version": execution.release.schema_version,
            "troia": {
                "mode": ratio.troia.mode.value,
                "phase": (
                    ratio.troia.phase.value
                    if ratio.troia.phase is not None
                    else None
                ),
                "status": ratio.troia.status.value,
                "triggers": sorted(
                    trigger.value for trigger in ratio.troia.triggers
                ),
            },
        }
        plaintext = _canonical_bytes(bundle)
        self._store.write_private_record(storage_key, plaintext)
        return RatioExecutionDraft(
            artifact=_artifact_ref(
                execution,
                artifact_id,
                plaintext,
                RATIO_HANDOFF_MEDIA_TYPE,
            ),
            artifact_roles=("FINAL_HANDOFF",),
            request_fingerprint=request_fingerprint,
            generated=True,
        )

    def _read_corpus(self, execution: ExecutionState) -> tuple[str, str]:
        artifact = execution.corpus_artifact
        if artifact is None:
            raise RatioArtifactMissing("Handoff CORPUS ausente.")
        storage_key = _artifact_storage_key(
            execution.execution_id,
            artifact.artifact_id,
        )
        try:
            plaintext = self._store.read_private_record(storage_key)
        except FileNotFoundError as exc:
            raise RatioArtifactMissing(
                "Artefato CORPUS não está disponível no cofre."
            ) from exc
        digest = hashlib.sha256(plaintext).hexdigest()
        if digest != artifact.sha256:
            raise RatioExecutorIntegrityError(
                "Hash do handoff CORPUS diverge do cofre."
            )
        try:
            decoded = plaintext.decode("utf-8")
            payload = json.loads(decoded)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RatioExecutorIntegrityError(
                "Handoff CORPUS possui formato inválido."
            ) from exc
        if (
            not isinstance(payload, dict)
            or payload.get("execution_id") != execution.execution_id
            or payload.get("release_id") != execution.release.release_id
        ):
            raise RatioExecutorIntegrityError(
                "Handoff CORPUS não pertence à execução/release."
            )
        return decoded, digest

    def _normative_text(self, module: RatioModule) -> str:
        module_name = {
            RatioModule.RI: "modulo_ri.md",
            RatioModule.ED: "modulo_ed.md",
            RatioModule.MS: "modulo_ms.md",
        }[module]
        paths = tuple(
            self._find_normative_file(name)
            for name in (
                "core_governanca.md",
                "_espelho.md",
                module_name,
            )
        )
        chunks = []
        for path in paths:
            try:
                chunks.append(path.read_text(encoding="utf-8"))
            except OSError as exc:
                raise RatioExecutionUnavailable(
                    f"Documento normativo RATIO indisponível: {path.name}."
                ) from exc
        return "\n\n---\n\n".join(chunks)

    def _find_normative_file(self, filename: str) -> Path:
        preferred = (
            self._ratio_root / "governanca" / filename,
            self._ratio_root / filename,
        )
        for candidate in preferred:
            if candidate.is_file():
                return candidate

        matches = sorted(
            candidate
            for candidate in self._ratio_root.rglob(filename)
            if candidate.is_file()
        )
        if not matches:
            raise RatioExecutionUnavailable(
                f"Documento normativo RATIO não encontrado: {filename}."
            )
        if len(matches) > 1:
            relative = ", ".join(
                str(candidate.relative_to(self._ratio_root))
                for candidate in matches
            )
            raise RatioExecutionUnavailable(
                f"Documento normativo RATIO ambíguo ({filename}): {relative}."
            )
        return matches[0]

    def _prior_outputs(
        self,
        execution: ExecutionState,
        ratio: RatioRunState,
        artifacts: tuple[RatioArtifactRecord, ...],
    ) -> list[dict[str, Any]]:
        current_index = phase_index(ratio, ratio.current_phase)
        selected: dict[RatioPhase, RatioArtifactRecord] = {}
        for record in artifacts:
            phase = _phase_from_role(record.role, "PHASE:")
            if phase is None:
                continue
            try:
                index = phase_index(ratio, phase)
            except ValueError:
                continue
            if index >= current_index:
                continue
            if ratio.phase_status(phase) not in _VALIDATED:
                continue
            previous = selected.get(phase)
            if previous is None or record.revision > previous.revision:
                selected[phase] = record

        result = []
        for phase in sorted(selected, key=lambda item: phase_index(ratio, item)):
            record = selected[phase]
            private = self._read_ratio_artifact(execution, record)
            result.append(
                {
                    "artifact_id": record.artifact.artifact_id,
                    "output": private["output"],
                    "phase": phase.value,
                    "revision": record.revision,
                    "sha256": record.artifact.sha256,
                }
            )
        return result

    def _read_ratio_artifact(
        self,
        execution: ExecutionState,
        record: RatioArtifactRecord,
    ) -> dict[str, Any]:
        storage_key = _artifact_storage_key(
            execution.execution_id,
            record.artifact.artifact_id,
        )
        try:
            plaintext = self._store.read_private_record(storage_key)
        except FileNotFoundError as exc:
            raise RatioArtifactMissing(
                f"Artefato RATIO ausente no cofre: {record.artifact.artifact_id}."
            ) from exc
        if hashlib.sha256(plaintext).hexdigest() != record.artifact.sha256:
            raise RatioExecutorIntegrityError(
                "Hash do artefato RATIO diverge do cofre."
            )
        payload = _decode_private_bundle(plaintext)
        if payload.get("release_id") != execution.release.release_id:
            raise RatioExecutorIntegrityError(
                "Artefato RATIO pertence a outra release."
            )
        return payload

    def _read_existing(
        self,
        storage_key: str,
        *,
        expected_request_fingerprint: str,
        expected_operation: str,
    ) -> bytes | None:
        try:
            plaintext = self._store.read_private_record(storage_key)
        except FileNotFoundError:
            return None
        payload = _decode_private_bundle(plaintext)
        if (
            payload.get("request_fingerprint")
            != expected_request_fingerprint
            or payload.get("operation") != expected_operation
        ):
            raise RatioExecutorIntegrityError(
                "Chave idempotente já preparou outro artefato RATIO."
            )
        return plaintext


_SYSTEM_INSTRUCTION = """\
Você executa uma única fase interna do RATIO.
Obedeça estritamente ao corpus pseudonimizado e aos documentos normativos fornecidos.
Não avance fases, não simule validação humana e não trate inferência como fato documental.
Não invente fontes, peças, fatos, pedidos, fundamentos ou precedentes ausentes.
Quando houver incerteza, registre-a explicitamente nos riscos e na atenção do operador.
Responda somente no objeto JSON exigido pelo schema.
"""


def _phase_prompt(
    ratio: RatioRunState,
    *,
    corpus_text: str,
    normative: str,
    prior: list[dict[str, Any]],
) -> str:
    context = {
        "current_phase": ratio.current_phase.value,
        "module": ratio.module.value,
        "prior_phase_outputs": prior,
        "ratio_revision": ratio.revision,
        "troia": {
            "mode": ratio.troia.mode.value,
            "phase": (
                ratio.troia.phase.value
                if ratio.troia.phase is not None
                else None
            ),
            "status": ratio.troia.status.value,
            "triggers": sorted(
                trigger.value for trigger in ratio.troia.triggers
            ),
        },
    }
    return (
        "ESTADO OPERACIONAL:\n"
        + json.dumps(context, ensure_ascii=False, sort_keys=True)
        + "\n\nCORPUS PSEUDONIMIZADO:\n"
        + corpus_text
        + "\n\nCONTRATO NORMATIVO RATIO:\n"
        + normative
    )


def _output_schema(
    phase: RatioPhase,
    *,
    troia_active: bool,
) -> dict[str, Any]:
    properties: dict[str, Any] = {
        "phase": {"type": "string", "enum": [phase.value]},
        "analysis": {"type": "string", "minLength": 1},
        "findings": {
            "type": "array",
            "items": {"type": "string"},
        },
        "conclusion": {"type": "string", "minLength": 1},
        "risk_codes": {
            "type": "array",
            "items": {"type": "string"},
        },
        "operator_attention": {
            "type": "array",
            "items": {"type": "string"},
        },
    }
    required = [
        "phase",
        "analysis",
        "findings",
        "conclusion",
        "risk_codes",
        "operator_attention",
    ]
    audit_types = _FINAL_AUDIT_OBJECT_TYPES.get(phase)
    if audit_types is not None:
        properties["audit_target"] = {
            "type": "object",
            "additionalProperties": False,
            "required": ["object_type", "text"],
            "properties": {
                "object_type": {
                    "type": "string",
                    "enum": list(audit_types),
                },
                "text": {"type": "string", "minLength": 40},
            },
        }
        required.append("audit_target")
    if troia_active:
        properties["counterfactual"] = {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "adversarial_route",
                "breaking_point",
                "alternative_route",
                "residual_risk",
            ],
            "properties": {
                "adversarial_route": {"type": "string", "minLength": 1},
                "breaking_point": {"type": "string", "minLength": 1},
                "alternative_route": {"type": "string", "minLength": 1},
                "residual_risk": {"type": "string", "minLength": 1},
            },
        }
        required.append("counterfactual")
    return {
        "type": "object",
        "additionalProperties": False,
        "required": required,
        "properties": properties,
    }


def _parse_output(
    content: str,
    phase: RatioPhase,
    *,
    troia_active: bool,
) -> dict[str, Any]:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RatioGeneratedOutputInvalid(
            "Executor RATIO devolveu JSON inválido."
        ) from exc
    if not isinstance(payload, dict) or payload.get("phase") != phase.value:
        raise RatioGeneratedOutputInvalid(
            "Executor RATIO devolveu fase incompatível."
        )
    for key in ("analysis", "conclusion"):
        if not isinstance(payload.get(key), str) or not payload[key].strip():
            raise RatioGeneratedOutputInvalid(
                f"Campo obrigatório inválido no executor RATIO: {key}."
            )
    for key in ("findings", "risk_codes", "operator_attention"):
        value = payload.get(key)
        if (
            not isinstance(value, list)
            or any(not isinstance(item, str) for item in value)
        ):
            raise RatioGeneratedOutputInvalid(
                f"Lista inválida no executor RATIO: {key}."
            )
    if phase in _FINAL_AUDIT_OBJECT_TYPES:
        _audit_target_from_phase_output(payload, phase)
    if troia_active:
        counterfactual = payload.get("counterfactual")
        if not isinstance(counterfactual, dict):
            raise RatioGeneratedOutputInvalid(
                "Saída de TROIA não contém bloco contrafactual."
            )
        for key in (
            "adversarial_route",
            "breaking_point",
            "alternative_route",
            "residual_risk",
        ):
            if (
                not isinstance(counterfactual.get(key), str)
                or not counterfactual[key].strip()
            ):
                raise RatioGeneratedOutputInvalid(
                    f"Campo contrafactual inválido: {key}."
                )
    return payload


def _audit_target_from_phase_output(
    output: Any,
    phase: RatioPhase,
) -> dict[str, str]:
    allowed = _FINAL_AUDIT_OBJECT_TYPES.get(phase)
    if allowed is None:
        raise RatioExecutorIntegrityError(
            f"Fase {phase.value} não define alvo final para o CERNE."
        )
    if not isinstance(output, Mapping):
        raise RatioExecutorIntegrityError(
            "Output final RATIO não é objeto estruturado."
        )
    target = output.get("audit_target")
    if not isinstance(target, Mapping):
        raise RatioExecutorIntegrityError(
            "Output final RATIO não contém audit_target."
        )
    object_type = target.get("object_type")
    text = target.get("text")
    if object_type not in allowed or not isinstance(text, str) or len(text.strip()) < 40:
        raise RatioExecutorIntegrityError(
            "audit_target final do RATIO diverge do contrato CERNE."
        )
    return {"object_type": str(object_type), "text": text.strip()}


def _audit_target_from_handoff(
    handoff: Mapping[str, Any],
) -> dict[str, str]:
    target = handoff.get("audit_target")
    if not isinstance(target, Mapping):
        raise RatioExecutorIntegrityError(
            "Handoff RATIO preparado não contém audit_target."
        )
    object_type = target.get("object_type")
    text = target.get("text")
    allowed = {"voto", "sentenca", "acordao", "decisao_liminar"}
    if object_type not in allowed or not isinstance(text, str) or len(text.strip()) < 40:
        raise RatioExecutorIntegrityError(
            "audit_target do handoff RATIO é inválido."
        )
    return {"object_type": str(object_type), "text": text.strip()}


def _latest_phase_artifacts(
    ratio: RatioRunState,
    artifacts: tuple[RatioArtifactRecord, ...],
) -> dict[RatioPhase, RatioArtifactRecord]:
    selected: dict[RatioPhase, RatioArtifactRecord] = {}
    for record in artifacts:
        phase = _phase_from_role(record.role, "PHASE:")
        if phase is None:
            continue
        try:
            ratio.phase_status(phase)
        except KeyError:
            continue
        previous = selected.get(phase)
        if previous is None or record.revision > previous.revision:
            selected[phase] = record
    return selected


def _phase_from_role(role: str, prefix: str) -> RatioPhase | None:
    if not role.startswith(prefix):
        return None
    try:
        return RatioPhase(role[len(prefix) :])
    except ValueError:
        return None


def _artifact_id(
    execution_id: str,
    operation: str,
    idempotency_key: str,
) -> str:
    UUID(execution_id)
    if not idempotency_key.strip():
        raise ValueError("idempotency_key é obrigatória.")
    return str(
        uuid5(
            _ARTIFACT_NAMESPACE,
            f"{execution_id}\x1f{operation}\x1f{idempotency_key}",
        )
    )


def _artifact_storage_key(execution_id: str, artifact_id: str) -> str:
    UUID(execution_id)
    UUID(artifact_id)
    return f"artifacts/{execution_id}/{artifact_id}.atrio"


def _artifact_ref(
    execution: ExecutionState,
    artifact_id: str,
    plaintext: bytes,
    media_type: str,
) -> ArtifactRef:
    return ArtifactRef(
        artifact_id=artifact_id,
        sha256=hashlib.sha256(plaintext).hexdigest(),
        media_type=media_type,
        classification=RATIO_ARTIFACT_CLASSIFICATION,
        producer=ComponentName.RATIO,
        producer_version=execution.release.ratio_version,
        release_id=execution.release.release_id,
        schema_version=execution.release.schema_version,
    )


def _decode_private_bundle(plaintext: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(plaintext.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RatioExecutorIntegrityError(
            "Artefato privado RATIO possui formato inválido."
        ) from exc
    if not isinstance(payload, dict):
        raise RatioExecutorIntegrityError(
            "Artefato privado RATIO não é objeto JSON."
        )
    return payload


def _string_list(payload: Mapping[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if (
        not isinstance(value, list)
        or any(not isinstance(item, str) for item in value)
    ):
        raise RatioExecutorIntegrityError(
            f"Campo privado inválido no artefato RATIO: {key}."
        )
    return value


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        dict(value),
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _json_sha256(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()
