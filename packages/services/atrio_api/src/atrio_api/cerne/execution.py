"""Execução confidencial do CERNE sobre o handoff final do RATIO."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping
from uuid import UUID, uuid5

from pydantic import ValidationError

from atrio_api.cerne_core.domain import (
    AuditRequest,
    AuditResponse,
    ClientOutput,
    ObjectType,
    SourceType,
)
from atrio_api.cerne_core.knowledge import KnowledgeBase
from atrio_api.cerne_core.orchestrator import CerneOrchestrator
from atrio_api.cerne_core.provider import ModelProvider
from atrio_api.cerne_core.repository import InMemoryAuditRepository
from atrio_api.corpus_intake import EncryptedCorpusStore
from atrio_api.domain import (
    ArtifactRef,
    CerneGate,
    ComponentName,
    ExecutionState,
)

CERNE_INTEGRATION_VERSION = "0.1.0"
CERNE_AUDIT_MEDIA_TYPE = "application/vnd.atrio.cerne.audit+json"
CERNE_ARTIFACT_CLASSIFICATION = "INTERNAL_PSEUDONYMIZED"
_ARTIFACT_NAMESPACE = UUID("d1e14e59-2e8d-45da-84ce-fd9c9b047a16")


class CerneExecutionError(RuntimeError):
    pass


class CerneExecutionUnavailable(CerneExecutionError):
    pass


class CerneArtifactMissing(CerneExecutionError):
    pass


class CerneIntegrityError(CerneExecutionError):
    pass


@dataclass(frozen=True, slots=True)
class CerneAuditDraft:
    artifact: ArtifactRef
    gate: CerneGate
    client_output: ClientOutput
    warnings: tuple[str, ...]
    request_fingerprint: str
    generated: bool


class CerneAuditExecutor:
    def __init__(
        self,
        store: EncryptedCorpusStore,
        provider: ModelProvider,
        *,
        knowledge_root: Path,
    ) -> None:
        self._store = store
        self._provider = provider
        self._knowledge_root = knowledge_root.resolve()
        self._knowledge = KnowledgeBase(self._knowledge_root)
        self._knowledge.assert_ready()
        self._knowledge_sha256 = _knowledge_sha256(self._knowledge_root)
        self._orchestrator = CerneOrchestrator(
            provider=provider,
            knowledge=self._knowledge,
            repository=InMemoryAuditRepository(),
        )

    @property
    def model(self) -> str:
        return self._provider.model

    def verify(self) -> None:
        self._knowledge.assert_ready()

    def has_prepared(
        self,
        execution_id: str,
        *,
        idempotency_key: str,
    ) -> bool:
        artifact_id = _artifact_id(execution_id, idempotency_key)
        try:
            self._store.read_private_record(
                _artifact_storage_key(execution_id, artifact_id)
            )
        except FileNotFoundError:
            return False
        return True

    async def prepare(
        self,
        execution: ExecutionState,
        *,
        actor_id: str,
        idempotency_key: str,
    ) -> CerneAuditDraft:
        handoff, ratio_sha256 = self._read_ratio_handoff(execution)
        audit_target = _audit_target(handoff)
        descriptor = {
            "actor_id": actor_id,
            "cerne_integration_version": CERNE_INTEGRATION_VERSION,
            "cerne_module_version": execution.release.cerne_module_version,
            "cerne_service_build": execution.release.cerne_service_build,
            "execution_id": execution.execution_id,
            "knowledge_sha256": self._knowledge_sha256,
            "model": self._provider.model,
            "operation": "AUDIT_RATIO_HANDOFF",
            "ratio_artifact_id": execution.ratio_artifact.artifact_id,
            "ratio_artifact_sha256": ratio_sha256,
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
            response = _audit_response_from_bundle(existing)
            return self._draft(
                execution,
                artifact_id=artifact_id,
                plaintext=existing,
                response=response,
                request_fingerprint=request_fingerprint,
                generated=False,
            )

        try:
            request = AuditRequest(
                caso_id=execution.execution_id,
                tipo_objeto=ObjectType(audit_target["object_type"]),
                natureza_fonte=SourceType.ATRIO_INTERNO,
                texto=audit_target["text"],
                origem=f"ATRIO/RATIO:{execution.ratio_artifact.artifact_id}",
            )
        except (ValueError, ValidationError) as exc:
            raise CerneIntegrityError(
                "audit_target do RATIO não satisfaz o contrato do CERNE."
            ) from exc

        response = await self._orchestrator.audit(request)
        bundle = {
            "audit_response": response.model_dump(mode="json"),
            "cerne_integration_version": CERNE_INTEGRATION_VERSION,
            "cerne_module_version": execution.release.cerne_module_version,
            "cerne_service_build": execution.release.cerne_service_build,
            "execution_id": execution.execution_id,
            "kind": "CERNE_AUDIT",
            "knowledge_sha256": self._knowledge_sha256,
            "operation": "AUDIT_RATIO_HANDOFF",
            "ratio_artifact_id": execution.ratio_artifact.artifact_id,
            "ratio_artifact_sha256": ratio_sha256,
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
            response=response,
            request_fingerprint=request_fingerprint,
            generated=True,
        )

    def _draft(
        self,
        execution: ExecutionState,
        *,
        artifact_id: str,
        plaintext: bytes,
        response: AuditResponse,
        request_fingerprint: str,
        generated: bool,
    ) -> CerneAuditDraft:
        try:
            gate = CerneGate(response.gate.estado.value)
        except ValueError as exc:  # pragma: no cover - enums espelhados
            raise CerneIntegrityError("Gate CERNE fora do contrato ATRIO.") from exc
        return CerneAuditDraft(
            artifact=ArtifactRef(
                artifact_id=artifact_id,
                sha256=hashlib.sha256(plaintext).hexdigest(),
                media_type=CERNE_AUDIT_MEDIA_TYPE,
                classification=CERNE_ARTIFACT_CLASSIFICATION,
                producer=ComponentName.CERNE,
                producer_version=execution.release.cerne_module_version,
                release_id=execution.release.release_id,
                schema_version=execution.release.schema_version,
            ),
            gate=gate,
            client_output=response.saida_cliente,
            warnings=tuple(response.avisos_operacionais),
            request_fingerprint=request_fingerprint,
            generated=generated,
        )

    def _read_ratio_handoff(
        self,
        execution: ExecutionState,
    ) -> tuple[dict[str, Any], str]:
        artifact = execution.ratio_artifact
        if artifact is None:
            raise CerneArtifactMissing("Handoff RATIO ausente.")
        try:
            execution.release.assert_artifact(
                artifact,
                expected_producer=ComponentName.RATIO,
            )
        except ValueError as exc:
            raise CerneIntegrityError(
                "Referência do handoff RATIO diverge da release ativa."
            ) from exc
        storage_key = _artifact_storage_key(
            execution.execution_id,
            artifact.artifact_id,
        )
        try:
            plaintext = self._store.read_private_record(storage_key)
        except FileNotFoundError as exc:
            raise CerneArtifactMissing(
                "Handoff RATIO não está disponível no cofre."
            ) from exc
        digest = hashlib.sha256(plaintext).hexdigest()
        if digest != artifact.sha256:
            raise CerneIntegrityError("Hash do handoff RATIO diverge do cofre.")
        payload = _decode_bundle(plaintext)
        if (
            payload.get("kind") != "RATIO_HANDOFF"
            or payload.get("execution_id") != execution.execution_id
            or payload.get("release_id") != execution.release.release_id
        ):
            raise CerneIntegrityError(
                "Handoff RATIO não pertence à execução/release corrente."
            )
        return payload, digest

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
            payload.get("kind") != "CERNE_AUDIT"
            or payload.get("operation") != "AUDIT_RATIO_HANDOFF"
            or payload.get("request_fingerprint")
            != expected_request_fingerprint
        ):
            raise CerneIntegrityError(
                "Chave idempotente já preparou outro artefato CERNE."
            )
        return plaintext


def _audit_target(handoff: Mapping[str, Any]) -> dict[str, str]:
    target = handoff.get("audit_target")
    if not isinstance(target, dict):
        raise CerneIntegrityError("Handoff RATIO não contém audit_target.")
    object_type = target.get("object_type")
    text = target.get("text")
    if (
        not isinstance(object_type, str)
        or object_type not in {item.value for item in ObjectType}
        or not isinstance(text, str)
        or len(text.strip()) < 40
    ):
        raise CerneIntegrityError("audit_target do RATIO é inválido.")
    return {"object_type": object_type, "text": text.strip()}


def _audit_response_from_bundle(plaintext: bytes) -> AuditResponse:
    payload = _decode_bundle(plaintext)
    try:
        return AuditResponse.model_validate(payload["audit_response"])
    except (KeyError, ValidationError) as exc:
        raise CerneIntegrityError(
            "Artefato CERNE preparado possui resposta inválida."
        ) from exc


def _artifact_id(execution_id: str, idempotency_key: str) -> str:
    UUID(execution_id)
    if not idempotency_key.strip():
        raise ValueError("idempotency_key é obrigatória.")
    return str(
        uuid5(
            _ARTIFACT_NAMESPACE,
            f"{execution_id}\x1fAUDIT_RATIO_HANDOFF\x1f{idempotency_key}",
        )
    )


def _artifact_storage_key(execution_id: str, artifact_id: str) -> str:
    UUID(execution_id)
    UUID(artifact_id)
    return f"artifacts/{execution_id}/{artifact_id}.atrio"


def _decode_bundle(plaintext: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(plaintext.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CerneIntegrityError("Artefato privado possui JSON inválido.") from exc
    if not isinstance(payload, dict):
        raise CerneIntegrityError("Artefato privado não é objeto JSON.")
    return payload


def _knowledge_sha256(root: Path) -> str:
    system = root / "00_sistema_cerne"
    if not system.is_dir():
        raise CerneExecutionUnavailable(
            f"Base de conhecimento CERNE ausente: {system}."
        )
    digest = hashlib.sha256()
    files = sorted(
        path
        for path in system.iterdir()
        if path.is_file() and path.suffix.lower() in {".md", ".txt"}
    )
    if not files:
        raise CerneExecutionUnavailable("Base de conhecimento CERNE vazia.")
    for path in files:
        relative = path.relative_to(root).as_posix().encode("utf-8")
        content = path.read_bytes()
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


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
