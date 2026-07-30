"""Contrato puro do runtime governado do RATIO.

Este módulo descreve fases, estados e a posição arquitetônica de TROIA.
Não executa inferência, não persiste estado e não autoriza transições.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping

from atrio_api.domain import RatioModule


RATIO_RUNTIME_CONTRACT_VERSION = "0.1.0"

TROIA_PROTOCOL_VERSION = "1.0.0"
TROIA_NAME = "TROIA"
TROIA_DESCRIPTION = "Protocolo contrafactual interno do RATIO"


class RatioPhaseStatus(StrEnum):
    NOT_STARTED = "NOT_STARTED"
    ANALYZING = "ANALYZING"
    BLOCKED = "BLOCKED"
    PENDING_REMEDIATION = "PENDING_REMEDIATION"
    VALIDATED = "VALIDATED"
    VALIDATED_WITH_NONBLOCKING_CAVEAT = "VALIDATED_WITH_NONBLOCKING_CAVEAT"
    DISPENSED_BY_EXCEPTION = "DISPENSED_BY_EXCEPTION"
    INVALIDATED_BY_SUBSTANTIAL_CHANGE = "INVALIDATED_BY_SUBSTANTIAL_CHANGE"
    ENDED_FOR_NOW_AFTER_INJUNCTION = "ENDED_FOR_NOW_AFTER_INJUNCTION"


class RatioPhase(StrEnum):
    RI_01 = "RI_01"
    RI_02 = "RI_02"
    RI_03 = "RI_03"
    RI_04 = "RI_04"
    RI_05 = "RI_05"
    RI_06 = "RI_06"

    ED_01 = "ED_01"
    ED_02 = "ED_02"
    ED_03 = "ED_03"
    ED_04 = "ED_04"
    ED_05 = "ED_05"

    MS_01 = "MS_01"
    MS_02 = "MS_02"
    MS_03 = "MS_03"
    MS_04 = "MS_04"
    MS_05 = "MS_05"
    MS_06 = "MS_06"
    MS_07 = "MS_07"


class TroiaMode(StrEnum):
    """Forma de presença de TROIA no módulo ativo."""

    AUTONOMOUS_REQUIRED = "AUTONOMOUS_REQUIRED"
    EMBEDDED_CONDITIONAL = "EMBEDDED_CONDITIONAL"
    NOT_DEFINED = "NOT_DEFINED"


class TroiaStatus(StrEnum):
    """Estado interno do protocolo TROIA."""

    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    PENDING_REMEDIATION = "PENDING_REMEDIATION"
    VALIDATED = "VALIDATED"
    DISPENSED = "DISPENSED"
    INVALIDATED = "INVALIDATED"
    NOT_DEFINED = "NOT_DEFINED"


class TroiaTrigger(StrEnum):
    """Gatilhos normativos do teste contrafactual interno do módulo ED."""

    INFRINGING_EFFECT_REQUEST = "INFRINGING_EFFECT_REQUEST"
    MATERIAL_RESULT_CHANGE = "MATERIAL_RESULT_CHANGE"
    RELEVANT_ADVERSARIAL_ROUTE = "RELEVANT_ADVERSARIAL_ROUTE"
    MERITS_REDISCUSSION_RISK = "MERITS_REDISCUSSION_RISK"
    REASONING_DISPOSITION_CONTRADICTION = (
        "REASONING_DISPOSITION_CONTRADICTION"
    )
    BREAKING_POINT_IDENTIFIED = "BREAKING_POINT_IDENTIFIED"
    FUTURE_VOTE_OMISSION_RISK = "FUTURE_VOTE_OMISSION_RISK"


@dataclass(frozen=True, slots=True)
class TroiaPolicy:
    """Posição normativa de TROIA dentro de um módulo RATIO."""

    mode: TroiaMode
    phase: RatioPhase | None
    triggers: frozenset[TroiaTrigger] = frozenset()


RI_PHASES = (
    RatioPhase.RI_01,
    RatioPhase.RI_02,
    RatioPhase.RI_03,
    RatioPhase.RI_04,
    RatioPhase.RI_05,
    RatioPhase.RI_06,
)

ED_PHASES = (
    RatioPhase.ED_01,
    RatioPhase.ED_02,
    RatioPhase.ED_03,
    RatioPhase.ED_04,
    RatioPhase.ED_05,
)

MS_PHASES = (
    RatioPhase.MS_01,
    RatioPhase.MS_02,
    RatioPhase.MS_03,
    RatioPhase.MS_04,
    RatioPhase.MS_05,
    RatioPhase.MS_06,
    RatioPhase.MS_07,
)


PHASES_BY_MODULE: Mapping[RatioModule, tuple[RatioPhase, ...]] = (
    MappingProxyType(
        {
            RatioModule.RI: RI_PHASES,
            RatioModule.ED: ED_PHASES,
            RatioModule.MS: MS_PHASES,
        }
    )
)


PHASE_TITLES: Mapping[RatioPhase, str] = MappingProxyType(
    {
        RatioPhase.RI_01: "Admissibilidade",
        RatioPhase.RI_02: "Relatório Técnico",
        RatioPhase.RI_03: (
            "TROIA — Matriz Contrafactual e Risco Decisório"
        ),
        RatioPhase.RI_04: "Parecer Estratégico",
        RatioPhase.RI_05: "Minuta/Voto",
        RatioPhase.RI_06: "Validação e Refinamento",
        RatioPhase.ED_01: "Admissibilidade",
        RatioPhase.ED_02: "Relatório Técnico",
        RatioPhase.ED_03: "Parecer Estratégico",
        RatioPhase.ED_04: "Minuta/Voto",
        RatioPhase.ED_05: "Validação e Refinamento",
        RatioPhase.MS_01: "Cabimento e Admissibilidade",
        RatioPhase.MS_02: "Mapa do Ato Coator",
        RatioPhase.MS_03: "Decisão Liminar",
        RatioPhase.MS_04: "Processamento Pós-Liminar",
        RatioPhase.MS_05: "Parecer de Mérito",
        RatioPhase.MS_06: "Sentença/Acórdão",
        RatioPhase.MS_07: "Validação e Refinamento",
    }
)


_ED_TROIA_TRIGGERS = frozenset(
    {
        TroiaTrigger.INFRINGING_EFFECT_REQUEST,
        TroiaTrigger.MATERIAL_RESULT_CHANGE,
        TroiaTrigger.RELEVANT_ADVERSARIAL_ROUTE,
        TroiaTrigger.MERITS_REDISCUSSION_RISK,
        TroiaTrigger.REASONING_DISPOSITION_CONTRADICTION,
        TroiaTrigger.BREAKING_POINT_IDENTIFIED,
        TroiaTrigger.FUTURE_VOTE_OMISSION_RISK,
    }
)


TROIA_POLICY_BY_MODULE: Mapping[RatioModule, TroiaPolicy] = (
    MappingProxyType(
        {
            RatioModule.RI: TroiaPolicy(
                mode=TroiaMode.AUTONOMOUS_REQUIRED,
                phase=RatioPhase.RI_03,
            ),
            RatioModule.ED: TroiaPolicy(
                mode=TroiaMode.EMBEDDED_CONDITIONAL,
                phase=RatioPhase.ED_03,
                triggers=_ED_TROIA_TRIGGERS,
            ),
            RatioModule.MS: TroiaPolicy(
                mode=TroiaMode.NOT_DEFINED,
                phase=None,
            ),
        }
    )
)


def phases_for(module: RatioModule) -> tuple[RatioPhase, ...]:
    return PHASES_BY_MODULE[module]


def phase_title(phase: RatioPhase) -> str:
    return PHASE_TITLES[phase]


def troia_policy_for(module: RatioModule) -> TroiaPolicy:
    return TROIA_POLICY_BY_MODULE[module]