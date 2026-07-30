from __future__ import annotations

import unittest

from atrio_api.domain import RatioModule
from atrio_api.ratio.contract import (
    PHASE_TITLES,
    RatioPhase,
    RatioPhaseStatus,
    TroiaMode,
    TroiaStatus,
    TroiaTrigger,
    phases_for,
    troia_policy_for,
)


class RatioContractTests(unittest.TestCase):
    def test_phase_sequences_match_normative_contract(self) -> None:
        self.assertEqual(
            phases_for(RatioModule.RI),
            (
                RatioPhase.RI_01,
                RatioPhase.RI_02,
                RatioPhase.RI_03,
                RatioPhase.RI_04,
                RatioPhase.RI_05,
                RatioPhase.RI_06,
            ),
        )
        self.assertEqual(len(phases_for(RatioModule.ED)), 5)
        self.assertEqual(len(phases_for(RatioModule.MS)), 7)

    def test_troia_is_user_facing_identity_of_ri_03(self) -> None:
        self.assertEqual(
            PHASE_TITLES[RatioPhase.RI_03],
            "TROIA — Matriz Contrafactual e Risco Decisório",
        )

    def test_troia_is_autonomous_and_required_in_ri(self) -> None:
        policy = troia_policy_for(RatioModule.RI)

        self.assertIs(policy.mode, TroiaMode.AUTONOMOUS_REQUIRED)
        self.assertIs(policy.phase, RatioPhase.RI_03)
        self.assertFalse(policy.triggers)

    def test_troia_is_conditional_and_embedded_in_ed(self) -> None:
        policy = troia_policy_for(RatioModule.ED)

        self.assertIs(policy.mode, TroiaMode.EMBEDDED_CONDITIONAL)
        self.assertIs(policy.phase, RatioPhase.ED_03)
        self.assertIn(
            TroiaTrigger.INFRINGING_EFFECT_REQUEST,
            policy.triggers,
        )
        self.assertIn(
            TroiaTrigger.BREAKING_POINT_IDENTIFIED,
            policy.triggers,
        )
        self.assertEqual(len(policy.triggers), 7)

    def test_troia_is_not_normatively_defined_in_ms(self) -> None:
        policy = troia_policy_for(RatioModule.MS)

        self.assertIs(policy.mode, TroiaMode.NOT_DEFINED)
        self.assertIsNone(policy.phase)
        self.assertFalse(policy.triggers)

    def test_phase_statuses_preserve_case_state_contract(self) -> None:
        self.assertEqual(
            set(RatioPhaseStatus),
            {
                RatioPhaseStatus.NOT_STARTED,
                RatioPhaseStatus.ANALYZING,
                RatioPhaseStatus.BLOCKED,
                RatioPhaseStatus.PENDING_REMEDIATION,
                RatioPhaseStatus.VALIDATED,
                RatioPhaseStatus.VALIDATED_WITH_NONBLOCKING_CAVEAT,
                RatioPhaseStatus.DISPENSED_BY_EXCEPTION,
                RatioPhaseStatus.INVALIDATED_BY_SUBSTANTIAL_CHANGE,
                RatioPhaseStatus.ENDED_FOR_NOW_AFTER_INJUNCTION,
            },
        )

    def test_troia_has_independent_internal_state(self) -> None:
        self.assertIn(TroiaStatus.RUNNING, TroiaStatus)
        self.assertIn(TroiaStatus.BLOCKED, TroiaStatus)
        self.assertIn(TroiaStatus.VALIDATED, TroiaStatus)
        self.assertIn(TroiaStatus.DISPENSED, TroiaStatus)


if __name__ == "__main__":
    unittest.main()