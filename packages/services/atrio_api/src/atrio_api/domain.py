from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping


class ComponentName(StrEnum):
    ATRIO_API = "atrio_api"
    CORPUS = "corpus"
    RATIO = "ratio"
    CERNE = "cerne"
    LUX = "lux"
    ATRIO_PII = "atrio_pii"


class RatioModule(StrEnum):
    RI = "RI"
    ED = "ED"
    MS = "MS"


class Destination(StrEnum):
    INTERNO = "interno"
    EXTERNO = "externo"
    PUBLICO = "publico"


class CerneGate(StrEnum):
    AVANCA = "AVANCA"
    AVANCA_COM_AJUSTE = "AVANCA_COM_AJUSTE"
    REVISAO_HUMANA = "REVISAO_HUMANA"
    BLOQUEIO_PARCIAL = "BLOQUEIO_PARCIAL"
    BLOQUEIO_TOTAL = "BLOQUEIO_TOTAL"


class ExecutionStage(StrEnum):
    CREATED = "CREATED"
    CORPUS_INGESTING = "CORPUS_INGESTING"
    CORPUS_REVIEW_REQUIRED = "CORPUS_REVIEW_REQUIRED"
    CORPUS_READY = "CORPUS_READY"
    RATIO_RUNNING = "RATIO_RUNNING"
    RATIO_WAITING_OPERATOR = "RATIO_WAITING_OPERATOR"
    RATIO_READY = "RATIO_READY"
    RATIO_REWORK = "RATIO_REWORK"
    CERNE_AUDITING = "CERNE_AUDITING"
    CERNE_APPROVED = "CERNE_APPROVED"
    CERNE_HUMAN_REVIEW = "CERNE_HUMAN_REVIEW"
    CERNE_PARTIAL_BLOCK = "CERNE_PARTIAL_BLOCK"
    CERNE_TOTAL_BLOCK = "CERNE_TOTAL_BLOCK"
    LUX_REFINING = "LUX_REFINING"
    FINAL_INTEGRITY_CHECK = "FINAL_INTEGRITY_CHECK"
    FINAL_INTEGRITY_BLOCK = "FINAL_INTEGRITY_BLOCK"
    READY_FOR_RELEASE = "READY_FOR_RELEASE"
    RELEASED = "RELEASED"
    TECHNICAL_FAILURE = "TECHNICAL_FAILURE"
    CANCELLED = "CANCELLED"


class ExecutionStatus(StrEnum):
    ACTIVE = "ACTIVE"
    WAITING_HUMAN = "WAITING_HUMAN"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class CommandKind(StrEnum):
    START_INGESTION = "START_INGESTION"
    REGISTER_CORPUS_DOCUMENT = "REGISTER_CORPUS_DOCUMENT"
    REQUEST_CORPUS_REVIEW = "REQUEST_CORPUS_REVIEW"
    RESUME_CORPUS = "RESUME_CORPUS"
    COMPLETE_CORPUS = "COMPLETE_CORPUS"
    START_RATIO = "START_RATIO"
    REQUEST_OPERATOR_DECISION = "REQUEST_OPERATOR_DECISION"
    RECORD_OPERATOR_DECISION = "RECORD_OPERATOR_DECISION"
    COMPLETE_RATIO = "COMPLETE_RATIO"
    START_CERNE = "START_CERNE"
    APPLY_CERNE_GATE = "APPLY_CERNE_GATE"
    RETURN_TO_RATIO = "RETURN_TO_RATIO"
    REOPEN_TOTAL_BLOCK = "REOPEN_TOTAL_BLOCK"
    COMPLETE_RATIO_REWORK = "COMPLETE_RATIO_REWORK"
    START_LUX = "START_LUX"
    COMPLETE_LUX = "COMPLETE_LUX"
    PASS_FINAL_INTEGRITY = "PASS_FINAL_INTEGRITY"
    FAIL_FINAL_INTEGRITY = "FAIL_FINAL_INTEGRITY"
    RETRY_LUX = "RETRY_LUX"
    RELEASE = "RELEASE"
    FAIL_TECHNICAL = "FAIL_TECHNICAL"
    RETRY_TECHNICAL = "RETRY_TECHNICAL"
    CANCEL = "CANCEL"


@dataclass(frozen=True, slots=True)
class ArtifactRef:
    artifact_id: str
    sha256: str
    media_type: str
    classification: str
    producer: ComponentName
    producer_version: str
    release_id: str
    schema_version: str

    def __post_init__(self) -> None:
        for name, value in (
            ("artifact_id", self.artifact_id),
            ("media_type", self.media_type),
            ("classification", self.classification),
            ("producer_version", self.producer_version),
            ("release_id", self.release_id),
            ("schema_version", self.schema_version),
        ):
            if not value.strip():
                raise ValueError(f"{name} é obrigatório.")
        if not re.fullmatch(r"[0-9a-f]{64}", self.sha256):
            raise ValueError("sha256 deve ter 64 caracteres hexadecimais minúsculos.")


@dataclass(frozen=True, slots=True)
class ReleaseEnvelope:
    release_id: str
    atrio_api_version: str
    corpus_version: str
    ratio_version: str
    cerne_module_version: str
    cerne_service_build: str
    lux_version: str
    atrio_pii_version: str
    prompt_bundle_hash: str
    schema_version: str

    def __post_init__(self) -> None:
        for name, value in (
            ("release_id", self.release_id),
            ("atrio_api_version", self.atrio_api_version),
            ("corpus_version", self.corpus_version),
            ("ratio_version", self.ratio_version),
            ("cerne_module_version", self.cerne_module_version),
            ("cerne_service_build", self.cerne_service_build),
            ("lux_version", self.lux_version),
            ("atrio_pii_version", self.atrio_pii_version),
            ("prompt_bundle_hash", self.prompt_bundle_hash),
            ("schema_version", self.schema_version),
        ):
            if not value.strip():
                raise ValueError(f"{name} é obrigatório.")

    def version_for(self, component: ComponentName) -> str:
        return {
            ComponentName.ATRIO_API: self.atrio_api_version,
            ComponentName.CORPUS: self.corpus_version,
            ComponentName.RATIO: self.ratio_version,
            ComponentName.CERNE: self.cerne_module_version,
            ComponentName.LUX: self.lux_version,
            ComponentName.ATRIO_PII: self.atrio_pii_version,
        }[component]

    def assert_artifact(
        self,
        artifact: ArtifactRef,
        *,
        expected_producer: ComponentName,
    ) -> None:
        if artifact.producer is not expected_producer:
            raise ValueError(
                f"Artefato de {artifact.producer.value} não pode ocupar handoff "
                f"de {expected_producer.value}."
            )
        expected_version = self.version_for(expected_producer)
        if artifact.producer_version != expected_version:
            raise ValueError(
                f"Versão do artefato divergente: esperado {expected_version}, "
                f"recebido {artifact.producer_version}."
            )
        if artifact.release_id != self.release_id:
            raise ValueError(
                f"Release do artefato divergente: esperado {self.release_id}, "
                f"recebido {artifact.release_id}."
            )
        if artifact.schema_version != self.schema_version:
            raise ValueError(
                f"Schema do artefato divergente: esperado {self.schema_version}, "
                f"recebido {artifact.schema_version}."
            )


@dataclass(frozen=True, slots=True)
class Command:
    kind: CommandKind
    expected_version: int
    actor_id: str
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.expected_version < 0:
            raise ValueError("expected_version não pode ser negativo.")
        if not self.actor_id.strip():
            raise ValueError("actor_id é obrigatório.")


@dataclass(frozen=True, slots=True)
class CreateExecutionRequest:
    tenant_id: str
    actor_id: str
    idempotency_key: str
    ratio_module: RatioModule
    destination: Destination
    input_artifact_id: str | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("tenant_id", self.tenant_id),
            ("actor_id", self.actor_id),
            ("idempotency_key", self.idempotency_key),
        ):
            if not value.strip():
                raise ValueError(f"{name} é obrigatório.")
        if len(self.idempotency_key) > 200:
            raise ValueError("idempotency_key excede 200 caracteres.")
        if self.input_artifact_id is not None and not self.input_artifact_id.strip():
            raise ValueError("input_artifact_id não pode ser vazio.")


@dataclass(frozen=True, slots=True)
class ExecutionState:
    execution_id: str
    tenant_id: str
    created_by: str
    ratio_module: RatioModule
    destination: Destination
    release: ReleaseEnvelope
    stage: ExecutionStage = ExecutionStage.CREATED
    status: ExecutionStatus = ExecutionStatus.ACTIVE
    state_version: int = 0
    corpus_artifact: ArtifactRef | None = None
    ratio_artifact: ArtifactRef | None = None
    cerne_artifact: ArtifactRef | None = None
    lux_artifact: ArtifactRef | None = None
    released_artifact: ArtifactRef | None = None
    current_ratio_phase: str | None = None
    waiting_reason: str | None = None
    last_operator_actor: str | None = None
    last_operator_decision: str | None = None
    cerne_gate: CerneGate | None = None
    last_error_code: str | None = None
    retry_stage: ExecutionStage | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("execution_id", self.execution_id),
            ("tenant_id", self.tenant_id),
            ("created_by", self.created_by),
        ):
            if not value.strip():
                raise ValueError(f"{name} é obrigatório.")
        if self.state_version < 0:
            raise ValueError("state_version não pode ser negativo.")

    @property
    def corpus_artifact_id(self) -> str | None:
        return self.corpus_artifact.artifact_id if self.corpus_artifact else None

    @property
    def ratio_artifact_id(self) -> str | None:
        return self.ratio_artifact.artifact_id if self.ratio_artifact else None

    @property
    def cerne_artifact_id(self) -> str | None:
        return self.cerne_artifact.artifact_id if self.cerne_artifact else None

    @property
    def lux_artifact_id(self) -> str | None:
        return self.lux_artifact.artifact_id if self.lux_artifact else None

    @property
    def released_artifact_id(self) -> str | None:
        return (
            self.released_artifact.artifact_id
            if self.released_artifact
            else None
        )
