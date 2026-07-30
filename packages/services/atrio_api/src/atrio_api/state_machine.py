from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Any, Mapping

from atrio_api.domain import (
    ArtifactRef,
    CerneGate,
    Command,
    CommandKind,
    ComponentName,
    ExecutionStage,
    ExecutionState,
    ExecutionStatus,
)


class StateMachineError(ValueError):
    """Erro de contrato ou transição que não pode ser repetido automaticamente."""


class VersionConflict(StateMachineError):
    def __init__(self, expected: int, actual: int):
        super().__init__(
            f"Conflito de versão: comando esperava {expected}, estado atual é {actual}."
        )
        self.expected = expected
        self.actual = actual


class InvalidTransition(StateMachineError):
    def __init__(self, stage: ExecutionStage, command: CommandKind):
        super().__init__(f"Comando {command.value} não é permitido em {stage.value}.")
        self.stage = stage
        self.command = command


class InvalidCommandPayload(StateMachineError):
    pass


@dataclass(frozen=True, slots=True)
class TransitionEvent:
    execution_id: str
    sequence: int
    command: CommandKind
    from_stage: ExecutionStage
    to_stage: ExecutionStage
    component: ComponentName
    component_version: str
    release_id: str
    actor_id: str
    occurred_at: datetime
    metadata: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class TransitionResult:
    state: ExecutionState
    event: TransitionEvent


_TERMINAL = frozenset({ExecutionStage.RELEASED, ExecutionStage.CANCELLED})

_WAITING = frozenset(
    {
        ExecutionStage.CORPUS_REVIEW_REQUIRED,
        ExecutionStage.RATIO_WAITING_OPERATOR,
        ExecutionStage.CERNE_HUMAN_REVIEW,
    }
)

_BLOCKED = frozenset(
    {
        ExecutionStage.CERNE_PARTIAL_BLOCK,
        ExecutionStage.CERNE_TOTAL_BLOCK,
        ExecutionStage.FINAL_INTEGRITY_BLOCK,
    }
)

_EVENT_KEYS = frozenset(
    {
        "decision_code",
        "document_id",
        "document_sha256",
        "error_code",
        "gate",
        "phase",
        "reason_code",
        "review_type",
    }
)


def status_for(stage: ExecutionStage) -> ExecutionStatus:
    if stage in _WAITING:
        return ExecutionStatus.WAITING_HUMAN
    if stage in _BLOCKED:
        return ExecutionStatus.BLOCKED
    if stage is ExecutionStage.RELEASED:
        return ExecutionStatus.COMPLETED
    if stage is ExecutionStage.TECHNICAL_FAILURE:
        return ExecutionStatus.FAILED
    if stage is ExecutionStage.CANCELLED:
        return ExecutionStatus.CANCELLED
    return ExecutionStatus.ACTIVE


def transition(state: ExecutionState, command: Command) -> TransitionResult:
    if command.expected_version != state.state_version:
        raise VersionConflict(command.expected_version, state.state_version)
    if state.stage in _TERMINAL:
        raise InvalidTransition(state.stage, command.kind)

    previous_stage = state.stage
    updated = _dispatch(state, command)
    updated = replace(
        updated,
        status=status_for(updated.stage),
        state_version=state.state_version + 1,
    )
    event = TransitionEvent(
        execution_id=state.execution_id,
        sequence=updated.state_version,
        command=command.kind,
        from_stage=previous_stage,
        to_stage=updated.stage,
        component=_component_for(command.kind),
        component_version=state.release.version_for(
            _component_for(command.kind)
        ),
        release_id=state.release.release_id,
        actor_id=command.actor_id,
        occurred_at=datetime.now(UTC),
        metadata=MappingProxyType(_safe_event_metadata(command.payload)),
    )
    return TransitionResult(state=updated, event=event)


def _dispatch(state: ExecutionState, command: Command) -> ExecutionState:
    kind = command.kind

    if kind is CommandKind.CANCEL:
        return replace(state, stage=ExecutionStage.CANCELLED, waiting_reason=None)

    if kind is CommandKind.FAIL_TECHNICAL:
        if state.stage is ExecutionStage.TECHNICAL_FAILURE:
            raise InvalidTransition(state.stage, kind)
        error_code = _required(command.payload, "error_code")
        return replace(
            state,
            stage=ExecutionStage.TECHNICAL_FAILURE,
            last_error_code=error_code,
            retry_stage=state.stage,
            waiting_reason=None,
        )

    if kind is CommandKind.RETRY_TECHNICAL:
        _require_stage(state, kind, ExecutionStage.TECHNICAL_FAILURE)
        if state.retry_stage is None:
            raise InvalidCommandPayload("Falha técnica não registra etapa de retorno.")
        return replace(
            state,
            stage=state.retry_stage,
            last_error_code=None,
            retry_stage=None,
        )

    if kind is CommandKind.START_INGESTION:
        _require_stage(state, kind, ExecutionStage.CREATED)
        return replace(state, stage=ExecutionStage.CORPUS_INGESTING)

    if kind is CommandKind.REGISTER_CORPUS_DOCUMENT:
        _require_stage(state, kind, ExecutionStage.CORPUS_INGESTING)
        _required(command.payload, "document_id")
        document_sha256 = _required(command.payload, "document_sha256")
        if not re.fullmatch(r"[0-9a-f]{64}", document_sha256):
            raise InvalidCommandPayload(
                "document_sha256 deve ter 64 caracteres hexadecimais."
            )
        return state

    if kind is CommandKind.REQUEST_CORPUS_REVIEW:
        _require_stage(state, kind, ExecutionStage.CORPUS_INGESTING)
        review_type = _required(command.payload, "review_type")
        if review_type not in {"ocr", "secrecy", "quality"}:
            raise InvalidCommandPayload(
                "review_type deve ser ocr, secrecy ou quality."
            )
        return replace(
            state,
            stage=ExecutionStage.CORPUS_REVIEW_REQUIRED,
            waiting_reason=review_type,
        )

    if kind is CommandKind.RESUME_CORPUS:
        _require_stage(state, kind, ExecutionStage.CORPUS_REVIEW_REQUIRED)
        return replace(
            state,
            stage=ExecutionStage.CORPUS_INGESTING,
            waiting_reason=None,
            last_operator_actor=command.actor_id,
            last_operator_decision=_required(command.payload, "decision_code"),
        )

    if kind is CommandKind.COMPLETE_CORPUS:
        _require_stage(state, kind, ExecutionStage.CORPUS_INGESTING)
        artifact = _artifact(state, command.payload, ComponentName.CORPUS)
        return replace(
            state,
            stage=ExecutionStage.CORPUS_READY,
            corpus_artifact=artifact,
        )

    if kind is CommandKind.START_RATIO:
        _require_stage(state, kind, ExecutionStage.CORPUS_READY)
        return replace(state, stage=ExecutionStage.RATIO_RUNNING)

    if kind is CommandKind.REQUEST_OPERATOR_DECISION:
        _require_stage(state, kind, ExecutionStage.RATIO_RUNNING)
        phase = _required(command.payload, "phase")
        reason = _required(command.payload, "reason_code")
        return replace(
            state,
            stage=ExecutionStage.RATIO_WAITING_OPERATOR,
            current_ratio_phase=phase,
            waiting_reason=reason,
        )

    if kind is CommandKind.RECORD_OPERATOR_DECISION:
        _require_stage(state, kind, ExecutionStage.RATIO_WAITING_OPERATOR)
        return replace(
            state,
            stage=ExecutionStage.RATIO_RUNNING,
            waiting_reason=None,
            last_operator_actor=command.actor_id,
            last_operator_decision=_required(command.payload, "decision_code"),
        )

    if kind is CommandKind.COMPLETE_RATIO:
        _require_stage(state, kind, ExecutionStage.RATIO_RUNNING)
        artifact = _artifact(state, command.payload, ComponentName.RATIO)
        return replace(
            state,
            stage=ExecutionStage.RATIO_READY,
            ratio_artifact=artifact,
        )

    if kind is CommandKind.START_CERNE:
        _require_stage(state, kind, ExecutionStage.RATIO_READY)
        return replace(
            state,
            stage=ExecutionStage.CERNE_AUDITING,
            cerne_gate=None,
            cerne_artifact=None,
        )

    if kind is CommandKind.APPLY_CERNE_GATE:
        _require_stage(state, kind, ExecutionStage.CERNE_AUDITING)
        gate = _gate(command.payload)
        artifact = _artifact(state, command.payload, ComponentName.CERNE)
        target = {
            CerneGate.AVANCA: ExecutionStage.CERNE_APPROVED,
            CerneGate.AVANCA_COM_AJUSTE: ExecutionStage.RATIO_REWORK,
            CerneGate.REVISAO_HUMANA: ExecutionStage.CERNE_HUMAN_REVIEW,
            CerneGate.BLOQUEIO_PARCIAL: ExecutionStage.CERNE_PARTIAL_BLOCK,
            CerneGate.BLOQUEIO_TOTAL: ExecutionStage.CERNE_TOTAL_BLOCK,
        }[gate]
        reason = None if gate is CerneGate.AVANCA else _required(
            command.payload, "reason_code"
        )
        return replace(
            state,
            stage=target,
            cerne_gate=gate,
            cerne_artifact=artifact,
            waiting_reason=reason,
        )

    if kind is CommandKind.RETURN_TO_RATIO:
        _require_stage(
            state,
            kind,
            ExecutionStage.RATIO_REWORK,
            ExecutionStage.CERNE_HUMAN_REVIEW,
            ExecutionStage.CERNE_PARTIAL_BLOCK,
        )
        return replace(
            state,
            stage=ExecutionStage.RATIO_REWORK,
            waiting_reason=None,
            last_operator_actor=command.actor_id,
            last_operator_decision=_required(command.payload, "decision_code"),
        )

    if kind is CommandKind.REOPEN_TOTAL_BLOCK:
        _require_stage(state, kind, ExecutionStage.CERNE_TOTAL_BLOCK)
        return replace(
            state,
            stage=ExecutionStage.RATIO_REWORK,
            waiting_reason=None,
            last_operator_actor=command.actor_id,
            last_operator_decision=_required(command.payload, "decision_code"),
        )

    if kind is CommandKind.COMPLETE_RATIO_REWORK:
        _require_stage(state, kind, ExecutionStage.RATIO_REWORK)
        artifact = _artifact(state, command.payload, ComponentName.RATIO)
        return replace(
            state,
            stage=ExecutionStage.RATIO_READY,
            ratio_artifact=artifact,
            cerne_gate=None,
        )

    if kind is CommandKind.START_LUX:
        _require_stage(state, kind, ExecutionStage.CERNE_APPROVED)
        return replace(
            state,
            stage=ExecutionStage.LUX_REFINING,
            waiting_reason=None,
        )

    if kind is CommandKind.COMPLETE_LUX:
        _require_stage(state, kind, ExecutionStage.LUX_REFINING)
        artifact = _artifact(state, command.payload, ComponentName.LUX)
        return replace(
            state,
            stage=ExecutionStage.FINAL_INTEGRITY_CHECK,
            lux_artifact=artifact,
        )

    if kind is CommandKind.PASS_FINAL_INTEGRITY:
        _require_stage(state, kind, ExecutionStage.FINAL_INTEGRITY_CHECK)
        return replace(state, stage=ExecutionStage.READY_FOR_RELEASE)

    if kind is CommandKind.FAIL_FINAL_INTEGRITY:
        _require_stage(state, kind, ExecutionStage.FINAL_INTEGRITY_CHECK)
        return replace(
            state,
            stage=ExecutionStage.FINAL_INTEGRITY_BLOCK,
            waiting_reason=_required(command.payload, "reason_code"),
        )

    if kind is CommandKind.RETRY_LUX:
        _require_stage(state, kind, ExecutionStage.FINAL_INTEGRITY_BLOCK)
        return replace(
            state,
            stage=ExecutionStage.LUX_REFINING,
            waiting_reason=None,
            lux_artifact=None,
            last_operator_actor=command.actor_id,
            last_operator_decision=_required(command.payload, "decision_code"),
        )

    if kind is CommandKind.RELEASE:
        _require_stage(state, kind, ExecutionStage.READY_FOR_RELEASE)
        if state.lux_artifact is None:
            raise InvalidCommandPayload("Liberação exige artefato LUX versionado.")
        return replace(
            state,
            stage=ExecutionStage.RELEASED,
            released_artifact=state.lux_artifact,
        )

    raise InvalidTransition(state.stage, kind)


def _required(payload: Mapping[str, Any], key: str) -> str:
    value = str(payload.get(key, "")).strip()
    if not value:
        raise InvalidCommandPayload(f"Campo obrigatório ausente: {key}.")
    return value


def _gate(payload: Mapping[str, Any]) -> CerneGate:
    raw = _required(payload, "gate")
    try:
        return CerneGate(raw)
    except ValueError as exc:
        raise InvalidCommandPayload(f"Gate CERNE inválido: {raw}.") from exc


def _artifact(
    state: ExecutionState,
    payload: Mapping[str, Any],
    expected_producer: ComponentName,
) -> ArtifactRef:
    artifact = payload.get("artifact")
    if not isinstance(artifact, ArtifactRef):
        raise InvalidCommandPayload(
            f"Handoff de {expected_producer.value} exige ArtifactRef versionado."
        )
    try:
        state.release.assert_artifact(
            artifact,
            expected_producer=expected_producer,
        )
    except ValueError as exc:
        raise InvalidCommandPayload(str(exc)) from exc
    return artifact


def _require_stage(
    state: ExecutionState,
    command: CommandKind,
    *allowed: ExecutionStage,
) -> None:
    if state.stage not in allowed:
        raise InvalidTransition(state.stage, command)


def _safe_event_metadata(payload: Mapping[str, Any]) -> dict[str, str]:
    metadata = {
        key: str(payload[key])
        for key in sorted(_EVENT_KEYS & payload.keys())
        if str(payload[key]).strip()
    }
    artifact = payload.get("artifact")
    if isinstance(artifact, ArtifactRef):
        metadata.update(
            {
                "artifact_id": artifact.artifact_id,
                "artifact_producer": artifact.producer.value,
                "artifact_version": artifact.producer_version,
                "artifact_release_id": artifact.release_id,
                "artifact_schema_version": artifact.schema_version,
            }
        )
    return metadata


def _component_for(command: CommandKind) -> ComponentName:
    if command in {
        CommandKind.START_INGESTION,
        CommandKind.REGISTER_CORPUS_DOCUMENT,
        CommandKind.REQUEST_CORPUS_REVIEW,
        CommandKind.RESUME_CORPUS,
        CommandKind.COMPLETE_CORPUS,
    }:
        return ComponentName.CORPUS
    if command in {
        CommandKind.START_RATIO,
        CommandKind.REQUEST_OPERATOR_DECISION,
        CommandKind.RECORD_OPERATOR_DECISION,
        CommandKind.COMPLETE_RATIO,
        CommandKind.RETURN_TO_RATIO,
        CommandKind.REOPEN_TOTAL_BLOCK,
        CommandKind.COMPLETE_RATIO_REWORK,
    }:
        return ComponentName.RATIO
    if command in {
        CommandKind.START_CERNE,
        CommandKind.APPLY_CERNE_GATE,
    }:
        return ComponentName.CERNE
    if command in {
        CommandKind.START_LUX,
        CommandKind.COMPLETE_LUX,
        CommandKind.PASS_FINAL_INTEGRITY,
        CommandKind.FAIL_FINAL_INTEGRITY,
        CommandKind.RETRY_LUX,
    }:
        return ComponentName.LUX
    return ComponentName.ATRIO_API
