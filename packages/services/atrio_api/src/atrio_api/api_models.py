from __future__ import annotations

from typing import Annotated, Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
)

from atrio_api.cerne.service import CerneAuditResult
from atrio_api.lux.execution import LuxDataMode, LuxMode
from atrio_api.lux.service import LuxRefinementResult
from atrio_api.domain import (
    ArtifactRef,
    CerneGate,
    Command,
    CommandKind,
    ComponentName,
    Destination,
    ExecutionState,
    RatioModule,
    ReleaseEnvelope,
)
from atrio_api.corpus_intake import CorpusIntakeRef
from atrio_api.corpus_processing import CorpusInventoryRecord
from atrio_api.corpus_service import (
    CorpusBatchResult,
    CorpusDocumentRecord,
    CorpusFinalizeResult,
    CorpusReviewDecision,
    CorpusReviewResult,
)
from atrio_api.ratio.contract import (
    RatioPhase,
    RatioPhaseStatus,
    TroiaMode,
    TroiaStatus,
    TroiaTrigger,
    phase_title,
)
from atrio_api.ratio.service import RatioActionKind
from atrio_api.ratio.execution import (
    RatioFinalizeResult,
    RatioPhaseExecutionResult,
)
from atrio_api.ratio.state import RatioRunState
from atrio_api.state_machine import TransitionEvent


Identifier = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=200,
        pattern=r"^[A-Za-z0-9_][A-Za-z0-9_.:@/-]*$",
    ),
]
Code = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9_][A-Za-z0-9_.:-]*$",
    ),
]
Version = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=80,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9_.+-]*$",
    ),
]


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CreateExecutionBody(ApiModel):
    tenant_id: Identifier
    actor_id: Identifier
    ratio_module: RatioModule
    destination: Destination


class ArtifactBody(ApiModel):
    artifact_id: Identifier
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    media_type: Annotated[str, StringConstraints(min_length=1, max_length=120)]
    classification: Code
    producer: ComponentName
    producer_version: Version
    release_id: Identifier
    schema_version: Version

    def to_domain(self) -> ArtifactRef:
        return ArtifactRef(
            artifact_id=self.artifact_id,
            sha256=self.sha256,
            media_type=self.media_type,
            classification=self.classification,
            producer=self.producer,
            producer_version=self.producer_version,
            release_id=self.release_id,
            schema_version=self.schema_version,
        )


class CommandPayloadBody(ApiModel):
    artifact: ArtifactBody | None = None
    decision_code: Code | None = None
    error_code: Code | None = None
    gate: CerneGate | None = None
    phase: Code | None = None
    reason_code: Code | None = None
    review_type: Code | None = None

    def to_domain(self) -> dict[str, Any]:
        payload = self.model_dump(exclude_none=True)
        if self.artifact is not None:
            payload["artifact"] = self.artifact.to_domain()
        if self.gate is not None:
            payload["gate"] = self.gate.value
        return payload


class CommandBody(ApiModel):
    kind: CommandKind
    expected_version: int = Field(ge=0)
    actor_id: Identifier
    payload: CommandPayloadBody = Field(default_factory=CommandPayloadBody)

    def to_domain(self) -> Command:
        return Command(
            kind=self.kind,
            expected_version=self.expected_version,
            actor_id=self.actor_id,
            payload=self.payload.to_domain(),
        )


class ArtifactResponse(ApiModel):
    artifact_id: str
    sha256: str
    media_type: str
    classification: str
    producer: ComponentName
    producer_version: str
    release_id: str
    schema_version: str


class ReleaseResponse(ApiModel):
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


class ExecutionResponse(ApiModel):
    execution_id: str
    tenant_id: str
    created_by: str
    ratio_module: RatioModule
    destination: Destination
    release: ReleaseResponse
    stage: str
    status: str
    state_version: int
    corpus_artifact: ArtifactResponse | None
    ratio_artifact: ArtifactResponse | None
    cerne_artifact: ArtifactResponse | None
    lux_artifact: ArtifactResponse | None
    released_artifact: ArtifactResponse | None
    current_ratio_phase: str | None
    waiting_reason: str | None
    last_operator_actor: str | None
    last_operator_decision: str | None
    cerne_gate: CerneGate | None
    last_error_code: str | None
    retry_stage: str | None


class CreateExecutionResponse(ApiModel):
    created: bool
    execution: ExecutionResponse


class CorpusDocumentResponse(ApiModel):
    document_id: str
    execution_id: str
    sha256: str
    byte_length: int
    media_type: str
    encryption_algorithm: str
    envelope_version: str
    intake_version: str


class CreateCorpusDocumentResponse(ApiModel):
    created: bool
    document: CorpusDocumentResponse
    execution: ExecutionResponse


class CorpusActionBody(ApiModel):
    expected_version: int = Field(ge=0)
    actor_id: Identifier


class CorpusReviewBody(CorpusActionBody):
    decision: CorpusReviewDecision


class CorpusInventoryResponse(ApiModel):
    document_id: str
    execution_id: str
    input_sha256: str
    byte_length: int
    media_type: str
    extraction_method: str
    page_count: int
    extracted_char_count: int
    ocr_mean_confidence: float | None
    cnj: str | None
    procedural_class: str
    secrecy_level: str
    pii_counts: dict[str, int]
    pseudonym_count: int
    pseudonymized_sha256: str
    status: str
    review_type: str | None
    corpus_pipeline_version: str
    atrio_pii_version: str


class CorpusDocumentStatusResponse(ApiModel):
    document_id: str
    execution_id: str
    input_sha256: str
    byte_length: int
    media_type: str
    intake_version: str
    processing_id: str | None
    effective_status: str
    review_decision: CorpusReviewDecision | None
    inventory: CorpusInventoryResponse | None


class CorpusBatchResponse(ApiModel):
    execution: ExecutionResponse
    documents: list[CorpusDocumentStatusResponse]
    processed_count: int
    halted_for_review: bool


class CorpusReviewResponse(ApiModel):
    execution: ExecutionResponse
    document: CorpusDocumentStatusResponse


class CorpusFinalizeResponse(ApiModel):
    execution: ExecutionResponse
    artifact: ArtifactResponse
    document_count: int


class CerneAuditBody(ApiModel):
    expected_version: int = Field(ge=0)
    actor_id: Identifier


class CerneOperatorBody(CerneAuditBody):
    decision_code: Code


class CerneClientOutputResponse(ApiModel):
    estado_documento: str
    sintese_objetiva: str
    ponto_principal_atencao: str
    impacto_pratico: str
    ajustes_necessarios: list[str]
    pode_ser_preservado: list[str]
    recomendacao_final: str


class CerneAuditResponse(ApiModel):
    created: bool
    execution: ExecutionResponse
    artifact: ArtifactResponse
    gate: CerneGate
    client_output: CerneClientOutputResponse
    warnings: list[str]


class LuxRefineBody(ApiModel):
    expected_version: int = Field(ge=0)
    actor_id: Identifier
    mode: LuxMode = LuxMode.PADRAO
    profile: Code | None = None
    data_mode: LuxDataMode | None = None


class LuxRefineResponse(ApiModel):
    created: bool
    execution: ExecutionResponse
    artifact: ArtifactResponse
    mode: LuxMode
    data_mode: LuxDataMode
    profile: str | None
    privacy_applied: bool
    suppression_reinforced: bool


class FinalActionBody(ApiModel):
    expected_version: int = Field(ge=0)
    actor_id: Identifier


class FinalIntegrityFailureBody(FinalActionBody):
    reason_code: Code


class LuxRetryBody(FinalActionBody):
    decision_code: Code


class RatioStartBody(ApiModel):
    expected_version: int = Field(ge=0)
    actor_id: Identifier


class RatioActionBody(ApiModel):
    action: RatioActionKind
    expected_revision: int = Field(ge=0)
    actor_id: Identifier
    troia_triggers: list[TroiaTrigger] = Field(default_factory=list)
    blocking_code: Code | None = None
    target_phase: RatioPhase | None = None


class RatioExecuteBody(ApiModel):
    expected_revision: int = Field(ge=0)
    actor_id: Identifier


class RatioFinalizeBody(RatioExecuteBody):
    expected_version: int = Field(ge=0)


class RatioPhaseResponse(ApiModel):
    phase: RatioPhase
    title: str
    status: RatioPhaseStatus


class RatioTroiaResponse(ApiModel):
    mode: TroiaMode
    phase: RatioPhase | None
    status: TroiaStatus
    triggers: list[TroiaTrigger]
    blocking_code: str | None


class RatioStateResponse(ApiModel):
    module: RatioModule
    current_phase: RatioPhase
    current_phase_title: str
    revision: int
    last_operator_action: str | None
    phases: list[RatioPhaseResponse]
    troia: RatioTroiaResponse


class RatioMutationResponse(ApiModel):
    created: bool
    execution: ExecutionResponse
    ratio: RatioStateResponse


class RatioExecutionResponse(ApiModel):
    created: bool
    execution: ExecutionResponse
    ratio: RatioStateResponse
    artifact: ArtifactResponse
    artifact_roles: list[str]


class RatioFinalizeResponse(ApiModel):
    created: bool
    execution: ExecutionResponse
    ratio: RatioStateResponse
    artifact: ArtifactResponse


class EventResponse(ApiModel):
    execution_id: str
    sequence: int
    command: CommandKind
    from_stage: str
    to_stage: str
    component: ComponentName
    component_version: str
    release_id: str
    actor_id: str
    occurred_at: str
    metadata: dict[str, str]


def execution_response(state: ExecutionState) -> ExecutionResponse:
    return ExecutionResponse(
        execution_id=state.execution_id,
        tenant_id=state.tenant_id,
        created_by=state.created_by,
        ratio_module=state.ratio_module,
        destination=state.destination,
        release=_release_response(state.release),
        stage=state.stage.value,
        status=state.status.value,
        state_version=state.state_version,
        corpus_artifact=_artifact_response(state.corpus_artifact),
        ratio_artifact=_artifact_response(state.ratio_artifact),
        cerne_artifact=_artifact_response(state.cerne_artifact),
        lux_artifact=_artifact_response(state.lux_artifact),
        released_artifact=_artifact_response(state.released_artifact),
        current_ratio_phase=state.current_ratio_phase,
        waiting_reason=state.waiting_reason,
        last_operator_actor=state.last_operator_actor,
        last_operator_decision=state.last_operator_decision,
        cerne_gate=state.cerne_gate,
        last_error_code=state.last_error_code,
        retry_stage=state.retry_stage.value if state.retry_stage else None,
    )


def cerne_audit_response(result: CerneAuditResult) -> CerneAuditResponse:
    artifact = _artifact_response(result.artifact)
    if artifact is None:  # pragma: no cover
        raise ValueError("Artefato CERNE ausente.")
    return CerneAuditResponse(
        created=result.created,
        execution=execution_response(result.execution_state),
        artifact=artifact,
        gate=result.gate,
        client_output=CerneClientOutputResponse(
            **result.client_output.model_dump(mode="json")
        ),
        warnings=list(result.warnings),
    )


def lux_refinement_response(
    result: LuxRefinementResult,
) -> LuxRefineResponse:
    artifact = _artifact_response(result.artifact)
    if artifact is None:  # pragma: no cover
        raise ValueError("Artefato LUX ausente.")
    return LuxRefineResponse(
        created=result.created,
        execution=execution_response(result.execution_state),
        artifact=artifact,
        mode=LuxMode(result.mode),
        data_mode=LuxDataMode(result.data_mode),
        profile=result.profile,
        privacy_applied=result.privacy_applied,
        suppression_reinforced=result.suppression_reinforced,
    )


def ratio_state_response(state: RatioRunState) -> RatioStateResponse:
    return RatioStateResponse(
        module=state.module,
        current_phase=state.current_phase,
        current_phase_title=phase_title(state.current_phase),
        revision=state.revision,
        last_operator_action=state.last_operator_action,
        phases=[
            RatioPhaseResponse(
                phase=item.phase,
                title=phase_title(item.phase),
                status=item.status,
            )
            for item in state.phases
        ],
        troia=RatioTroiaResponse(
            mode=state.troia.mode,
            phase=state.troia.phase,
            status=state.troia.status,
            triggers=sorted(state.troia.triggers, key=lambda item: item.value),
            blocking_code=state.troia.blocking_code,
        ),
    )


def ratio_mutation_response(
    *,
    execution: ExecutionState,
    ratio: RatioRunState,
    created: bool,
) -> RatioMutationResponse:
    return RatioMutationResponse(
        created=created,
        execution=execution_response(execution),
        ratio=ratio_state_response(ratio),
    )


def ratio_execution_response(
    result: RatioPhaseExecutionResult,
) -> RatioExecutionResponse:
    artifact = _artifact_response(result.artifact)
    if artifact is None:  # pragma: no cover
        raise ValueError("Artefato de fase RATIO ausente.")
    return RatioExecutionResponse(
        created=result.created,
        execution=execution_response(result.execution_state),
        ratio=ratio_state_response(result.ratio_state),
        artifact=artifact,
        artifact_roles=list(result.artifact_roles),
    )


def ratio_finalize_response(
    result: RatioFinalizeResult,
) -> RatioFinalizeResponse:
    artifact = _artifact_response(result.artifact)
    if artifact is None:  # pragma: no cover
        raise ValueError("Handoff RATIO ausente.")
    return RatioFinalizeResponse(
        created=result.created,
        execution=execution_response(result.execution_state),
        ratio=ratio_state_response(result.ratio_state),
        artifact=artifact,
    )


def event_response(event: TransitionEvent) -> EventResponse:
    return EventResponse(
        execution_id=event.execution_id,
        sequence=event.sequence,
        command=event.command,
        from_stage=event.from_stage.value,
        to_stage=event.to_stage.value,
        component=event.component,
        component_version=event.component_version,
        release_id=event.release_id,
        actor_id=event.actor_id,
        occurred_at=event.occurred_at.isoformat(),
        metadata=dict(event.metadata),
    )


def corpus_document_response(
    intake: CorpusIntakeRef,
) -> CorpusDocumentResponse:
    return CorpusDocumentResponse(
        document_id=intake.document_id,
        execution_id=intake.execution_id,
        sha256=intake.sha256,
        byte_length=intake.byte_length,
        media_type=intake.media_type,
        encryption_algorithm=intake.encryption_algorithm,
        envelope_version=intake.envelope_version,
        intake_version=intake.intake_version,
    )


def corpus_document_status_response(
    document: CorpusDocumentRecord,
) -> CorpusDocumentStatusResponse:
    return CorpusDocumentStatusResponse(
        document_id=document.intake.document_id,
        execution_id=document.intake.execution_id,
        input_sha256=document.intake.sha256,
        byte_length=document.intake.byte_length,
        media_type=document.intake.media_type,
        intake_version=document.intake.intake_version,
        processing_id=document.processing_id,
        effective_status=document.effective_status,
        review_decision=document.review_decision,
        inventory=_corpus_inventory_response(document.inventory),
    )


def corpus_batch_response(
    result: CorpusBatchResult,
) -> CorpusBatchResponse:
    return CorpusBatchResponse(
        execution=execution_response(result.state),
        documents=[
            corpus_document_status_response(document)
            for document in result.documents
        ],
        processed_count=result.processed_count,
        halted_for_review=result.halted_for_review,
    )


def corpus_review_response(
    result: CorpusReviewResult,
) -> CorpusReviewResponse:
    return CorpusReviewResponse(
        execution=execution_response(result.state),
        document=corpus_document_status_response(result.document),
    )


def corpus_finalize_response(
    result: CorpusFinalizeResult,
) -> CorpusFinalizeResponse:
    artifact = _artifact_response(result.artifact)
    if artifact is None:  # pragma: no cover - contrato do resultado
        raise ValueError("Artefato CORPUS ausente.")
    return CorpusFinalizeResponse(
        execution=execution_response(result.state),
        artifact=artifact,
        document_count=result.document_count,
    )


def _corpus_inventory_response(
    inventory: CorpusInventoryRecord | None,
) -> CorpusInventoryResponse | None:
    if inventory is None:
        return None
    safe = inventory.safe_dict()
    return CorpusInventoryResponse.model_validate(safe)


def _artifact_response(
    artifact: ArtifactRef | None,
) -> ArtifactResponse | None:
    if artifact is None:
        return None
    return ArtifactResponse(
        artifact_id=artifact.artifact_id,
        sha256=artifact.sha256,
        media_type=artifact.media_type,
        classification=artifact.classification,
        producer=artifact.producer,
        producer_version=artifact.producer_version,
        release_id=artifact.release_id,
        schema_version=artifact.schema_version,
    )


def _release_response(release: ReleaseEnvelope) -> ReleaseResponse:
    return ReleaseResponse(
        release_id=release.release_id,
        atrio_api_version=release.atrio_api_version,
        corpus_version=release.corpus_version,
        ratio_version=release.ratio_version,
        cerne_module_version=release.cerne_module_version,
        cerne_service_build=release.cerne_service_build,
        lux_version=release.lux_version,
        atrio_pii_version=release.atrio_pii_version,
        prompt_bundle_hash=release.prompt_bundle_hash,
        schema_version=release.schema_version,
    )
