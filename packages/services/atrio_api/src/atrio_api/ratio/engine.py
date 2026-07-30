"""Motor puro e determinÃ­stico do runtime governado do RATIO."""

from __future__ import annotations

from dataclasses import replace

from atrio_api.domain import RatioModule
from atrio_api.ratio.catalog import HardStopCatalog
from atrio_api.ratio.contract import (
    RatioPhase,
    RatioPhaseStatus,
    TroiaMode,
    TroiaStatus,
    TroiaTrigger,
)
from atrio_api.ratio.state import (
    RatioRunState,
    phase_index,
    replace_phase_status,
)


_VALIDATED_PHASE_STATUSES = frozenset(
    {
        RatioPhaseStatus.VALIDATED,
        RatioPhaseStatus.VALIDATED_WITH_NONBLOCKING_CAVEAT,
    }
)


class RatioEngineError(ValueError):
    """ViolaÃ§Ã£o controlada do contrato interno do RATIO."""


class RatioTransitionError(RatioEngineError):
    """TransiÃ§Ã£o incompatÃ­vel com o estado atual."""


class TroiaGateError(RatioTransitionError):
    """TROIA ainda nÃ£o autoriza o avanÃ§o da fase."""


def validate_current_phase(
    state: RatioRunState,
    *,
    with_caveat: bool = False,
) -> RatioRunState:
    """Valida a fase atual sem iniciar automaticamente a prÃ³xima."""

    current_status = state.phase_status(state.current_phase)

    if current_status not in {
        RatioPhaseStatus.ANALYZING,
        RatioPhaseStatus.PENDING_REMEDIATION,
    }:
        raise RatioTransitionError(
            f"Fase {state.current_phase.value} nÃ£o pode ser validada "
            f"a partir de {current_status.value}."
        )

    _assert_troia_gate(state)

    new_status = (
        RatioPhaseStatus.VALIDATED_WITH_NONBLOCKING_CAVEAT
        if with_caveat
        else RatioPhaseStatus.VALIDATED
    )

    return replace(
        state,
        phases=replace_phase_status(
            state,
            state.current_phase,
            new_status,
        ),
        revision=state.revision + 1,
        last_operator_action=(
            "VALIDATE_WITH_NONBLOCKING_CAVEAT"
            if with_caveat
            else "VALIDATE"
        ),
    )


def advance_phase(state: RatioRunState) -> RatioRunState:
    """Inicia a prÃ³xima fase somente apÃ³s validaÃ§Ã£o expressa da atual."""

    current_status = state.phase_status(state.current_phase)

    if current_status not in _VALIDATED_PHASE_STATUSES:
        raise RatioTransitionError(
            f"Fase {state.current_phase.value} ainda nÃ£o foi validada."
        )

    index = phase_index(state, state.current_phase)

    if index + 1 >= len(state.phases):
        raise RatioTransitionError(
            f"Fase {state.current_phase.value} Ã© a Ãºltima do mÃ³dulo."
        )

    next_phase = state.phases[index + 1].phase
    phases = replace_phase_status(
        state,
        next_phase,
        RatioPhaseStatus.ANALYZING,
    )

    troia = state.troia

    if next_phase is troia.phase:
        if troia.mode is TroiaMode.AUTONOMOUS_REQUIRED:
            troia = replace(
                troia,
                status=TroiaStatus.RUNNING,
                triggers=frozenset(),
                blocking_code=None,
            )
        elif troia.mode is TroiaMode.EMBEDDED_CONDITIONAL:
            troia = replace(
                troia,
                status=TroiaStatus.NOT_STARTED,
                triggers=frozenset(),
                blocking_code=None,
            )

    return replace(
        state,
        current_phase=next_phase,
        phases=phases,
        troia=troia,
        revision=state.revision + 1,
        last_operator_action="ADVANCE",
    )


def configure_ed_troia(
    state: RatioRunState,
    triggers: frozenset[TroiaTrigger],
) -> RatioRunState:
    """Ativa ou dispensa TROIA dentro da ED_03."""

    if state.module is not RatioModule.ED:
        raise RatioTransitionError(
            "ConfiguraÃ§Ã£o condicional de TROIA pertence ao mÃ³dulo ED."
        )

    if state.current_phase is not RatioPhase.ED_03:
        raise RatioTransitionError(
            "TROIA condicional de ED sÃ³ pode ser configurado na ED_03."
        )

    status = (
        TroiaStatus.RUNNING
        if triggers
        else TroiaStatus.DISPENSED
    )

    return replace(
        state,
        troia=replace(
            state.troia,
            status=status,
            triggers=frozenset(triggers),
            blocking_code=None,
        ),
        revision=state.revision + 1,
        last_operator_action="CONFIGURE_TROIA",
    )


def validate_troia(state: RatioRunState) -> RatioRunState:
    """Marca o autoconfronto como validado."""

    _assert_current_troia_phase(state)

    if state.troia.status not in {
        TroiaStatus.RUNNING,
        TroiaStatus.PENDING_REMEDIATION,
    }:
        raise TroiaGateError(
            f"TROIA nÃ£o pode ser validado a partir de "
            f"{state.troia.status.value}."
        )

    return replace(
        state,
        troia=replace(
            state.troia,
            status=TroiaStatus.VALIDATED,
            blocking_code=None,
        ),
        revision=state.revision + 1,
        last_operator_action="VALIDATE_TROIA",
    )


def block_troia(
    state: RatioRunState,
    *,
    blocking_code: str,
    catalog: HardStopCatalog,
) -> RatioRunState:
    """Aplica hard stop normativo Ã  manifestaÃ§Ã£o de TROIA."""

    _assert_current_troia_phase(state)
    catalog.require_for_phase(blocking_code, state.current_phase)

    if state.troia.status not in {
        TroiaStatus.RUNNING,
        TroiaStatus.PENDING_REMEDIATION,
    }:
        raise TroiaGateError(
            f"TROIA nÃ£o pode ser bloqueado a partir de "
            f"{state.troia.status.value}."
        )

    return replace(
        state,
        phases=replace_phase_status(
            state,
            state.current_phase,
            RatioPhaseStatus.BLOCKED,
        ),
        troia=replace(
            state.troia,
            status=TroiaStatus.BLOCKED,
            blocking_code=blocking_code,
        ),
        revision=state.revision + 1,
        last_operator_action="BLOCK_TROIA",
    )


def resume_troia(state: RatioRunState) -> RatioRunState:
    """Reabre TROIA apÃ³s saneamento de um bloqueio."""

    _assert_current_troia_phase(state)

    if state.troia.status is not TroiaStatus.BLOCKED:
        raise TroiaGateError("TROIA nÃ£o estÃ¡ bloqueado.")

    return replace(
        state,
        phases=replace_phase_status(
            state,
            state.current_phase,
            RatioPhaseStatus.PENDING_REMEDIATION,
        ),
        troia=replace(
            state.troia,
            status=TroiaStatus.PENDING_REMEDIATION,
            blocking_code=None,
        ),
        revision=state.revision + 1,
        last_operator_action="REMEDIATE_TROIA",
    )


def return_after_substantial_change(
    state: RatioRunState,
    *,
    target_phase: RatioPhase,
) -> RatioRunState:
    """Retorna a fase anterior e invalida resultados posteriores dependentes."""

    target_index = phase_index(state, target_phase)
    current_index = phase_index(state, state.current_phase)

    if target_index > current_index:
        raise RatioTransitionError(
            "Retorno sÃ³ pode apontar para a fase atual ou anterior."
        )

    updated = []

    for index, item in enumerate(state.phases):
        if index == target_index:
            status = RatioPhaseStatus.ANALYZING
        elif (
            index > target_index
            and item.status is not RatioPhaseStatus.NOT_STARTED
        ):
            status = RatioPhaseStatus.INVALIDATED_BY_SUBSTANTIAL_CHANGE
        else:
            status = item.status

        updated.append(replace(item, status=status))

    troia = state.troia

    if troia.phase is not None:
        troia_index = phase_index(state, troia.phase)

        if (
            troia_index >= target_index
            and troia.status
            not in {
                TroiaStatus.NOT_STARTED,
                TroiaStatus.NOT_DEFINED,
            }
        ):
            troia = replace(
                troia,
                status=TroiaStatus.INVALIDATED,
                blocking_code=None,
            )

    return replace(
        state,
        current_phase=target_phase,
        phases=tuple(updated),
        troia=troia,
        revision=state.revision + 1,
        last_operator_action="RETURN_AFTER_SUBSTANTIAL_CHANGE",
    )


def record_phase_execution(state: RatioRunState) -> RatioRunState:
    """Registra produção de artefato sem validar a fase."""

    current_status = state.phase_status(state.current_phase)
    if current_status not in {
        RatioPhaseStatus.ANALYZING,
        RatioPhaseStatus.PENDING_REMEDIATION,
    }:
        raise RatioTransitionError(
            f"Fase {state.current_phase.value} não aceita nova execução "
            f"a partir de {current_status.value}."
        )
    return replace(
        state,
        revision=state.revision + 1,
        last_operator_action="EXECUTE_PHASE",
    )


def finalize_ratio_state(state: RatioRunState) -> RatioRunState:
    """Fecha o agregado somente quando todas as fases estão terminalmente válidas."""

    allowed = {
        RatioPhaseStatus.VALIDATED,
        RatioPhaseStatus.VALIDATED_WITH_NONBLOCKING_CAVEAT,
        RatioPhaseStatus.DISPENSED_BY_EXCEPTION,
    }
    invalid = [
        item.phase.value
        for item in state.phases
        if item.status not in allowed
    ]
    if invalid:
        raise RatioTransitionError(
            "RATIO ainda possui fases não finalizáveis: "
            + ", ".join(invalid)
            + "."
        )
    if state.current_phase is not state.phases[-1].phase:
        raise RatioTransitionError("RATIO só finaliza na última fase do módulo.")
    _assert_troia_gate(state)
    return replace(
        state,
        revision=state.revision + 1,
        last_operator_action="FINALIZE",
    )


def _assert_troia_gate(state: RatioRunState) -> None:
    if state.current_phase is not state.troia.phase:
        return

    if state.troia.mode is TroiaMode.AUTONOMOUS_REQUIRED:
        if state.troia.status is not TroiaStatus.VALIDATED:
            raise TroiaGateError(
                "TROIA deve ser validado antes da fase."
            )

    elif state.troia.mode is TroiaMode.EMBEDDED_CONDITIONAL:
        if state.troia.status not in {
            TroiaStatus.VALIDATED,
            TroiaStatus.DISPENSED,
        }:
            raise TroiaGateError(
                "TROIA deve ser realizado ou formalmente dispensado."
            )


def _assert_current_troia_phase(state: RatioRunState) -> None:
    if state.troia.mode is TroiaMode.NOT_DEFINED:
        raise TroiaGateError(
            "TROIA nÃ£o possui ativaÃ§Ã£o normativa neste mÃ³dulo."
        )

    if state.current_phase is not state.troia.phase:
        raise TroiaGateError(
            "A fase atual nÃ£o Ã© a manifestaÃ§Ã£o normativa de TROIA."
        )