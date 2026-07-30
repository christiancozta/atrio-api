"""Estado imutÃ¡vel do runtime interno do RATIO."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from atrio_api.domain import RatioModule
from atrio_api.ratio.contract import (
    RatioPhase,
    RatioPhaseStatus,
    TroiaMode,
    TroiaStatus,
    TroiaTrigger,
    phases_for,
    troia_policy_for,
)


@dataclass(frozen=True, slots=True)
class RatioPhaseSnapshot:
    phase: RatioPhase
    status: RatioPhaseStatus


@dataclass(frozen=True, slots=True)
class TroiaState:
    mode: TroiaMode
    phase: RatioPhase | None
    status: TroiaStatus
    triggers: frozenset[TroiaTrigger] = frozenset()
    blocking_code: str | None = None


@dataclass(frozen=True, slots=True)
class RatioRunState:
    module: RatioModule
    current_phase: RatioPhase
    phases: tuple[RatioPhaseSnapshot, ...]
    troia: TroiaState
    revision: int = 0
    last_operator_action: str | None = None

    def phase_status(self, phase: RatioPhase) -> RatioPhaseStatus:
        for item in self.phases:
            if item.phase is phase:
                return item.status
        raise KeyError(f"Fase nÃ£o pertence ao agregado: {phase.value}")


def create_ratio_run(module: RatioModule) -> RatioRunState:
    phases = phases_for(module)
    if not phases:
        raise ValueError("MÃ³dulo RATIO sem fases.")

    snapshots = tuple(
        RatioPhaseSnapshot(
            phase=phase,
            status=(
                RatioPhaseStatus.ANALYZING
                if index == 0
                else RatioPhaseStatus.NOT_STARTED
            ),
        )
        for index, phase in enumerate(phases)
    )

    policy = troia_policy_for(module)
    troia_status = (
        TroiaStatus.NOT_DEFINED
        if policy.mode is TroiaMode.NOT_DEFINED
        else TroiaStatus.NOT_STARTED
    )

    return RatioRunState(
        module=module,
        current_phase=phases[0],
        phases=snapshots,
        troia=TroiaState(
            mode=policy.mode,
            phase=policy.phase,
            status=troia_status,
        ),
    )


def replace_phase_status(
    state: RatioRunState,
    phase: RatioPhase,
    status: RatioPhaseStatus,
) -> tuple[RatioPhaseSnapshot, ...]:
    found = False
    updated: list[RatioPhaseSnapshot] = []

    for item in state.phases:
        if item.phase is phase:
            updated.append(
                RatioPhaseSnapshot(
                    phase=item.phase,
                    status=status,
                )
            )
            found = True
        else:
            updated.append(item)

    if not found:
        raise ValueError(
            f"Fase {phase.value} nÃ£o pertence ao mÃ³dulo {state.module.value}."
        )

    return tuple(updated)


def phase_index(state: RatioRunState, phase: RatioPhase) -> int:
    for index, item in enumerate(state.phases):
        if item.phase is phase:
            return index
    raise ValueError(
        f"Fase {phase.value} nÃ£o pertence ao mÃ³dulo {state.module.value}."
    )


def phase_statuses(
    state: RatioRunState,
) -> Iterable[tuple[RatioPhase, RatioPhaseStatus]]:
    return ((item.phase, item.status) for item in state.phases)