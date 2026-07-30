from __future__ import annotations

from pathlib import Path
import unittest

from atrio_api.domain import RatioModule
from atrio_api.ratio import (
    HardStopPhaseMismatch,
    RatioPhase,
    RatioPhaseStatus,
    RatioTransitionError,
    TroiaGateError,
    TroiaStatus,
    TroiaTrigger,
    UnknownHardStop,
    advance_phase,
    block_troia,
    configure_ed_troia,
    create_ratio_run,
    load_hard_stop_catalog,
    resume_troia,
    return_after_substantial_change,
    validate_current_phase,
    validate_troia,
)


_RATIO_ROOT = Path(__file__).resolve().parents[3] / "ratio"


class RatioEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_hard_stop_catalog(_RATIO_ROOT)

    def _advance_to(
        self,
        module: RatioModule,
        target: RatioPhase,
    ):
        state = create_ratio_run(module)

        while state.current_phase is not target:
            state = validate_current_phase(state)
            state = advance_phase(state)

        return state

    def test_run_starts_in_first_phase(self) -> None:
        state = create_ratio_run(RatioModule.RI)

        self.assertIs(state.current_phase, RatioPhase.RI_01)
        self.assertIs(
            state.phase_status(RatioPhase.RI_01),
            RatioPhaseStatus.ANALYZING,
        )

    def test_validation_does_not_advance_automatically(self) -> None:
        state = create_ratio_run(RatioModule.RI)

        state = validate_current_phase(state)

        self.assertIs(state.current_phase, RatioPhase.RI_01)
        self.assertIs(
            state.phase_status(RatioPhase.RI_01),
            RatioPhaseStatus.VALIDATED,
        )

    def test_unvalidated_phase_cannot_advance(self) -> None:
        state = create_ratio_run(RatioModule.RI)

        with self.assertRaises(RatioTransitionError):
            advance_phase(state)

    def test_entering_ri_03_starts_troia(self) -> None:
        state = self._advance_to(
            RatioModule.RI,
            RatioPhase.RI_03,
        )

        self.assertIs(state.troia.status, TroiaStatus.RUNNING)

    def test_ri_03_cannot_validate_before_troia(self) -> None:
        state = self._advance_to(
            RatioModule.RI,
            RatioPhase.RI_03,
        )

        with self.assertRaises(TroiaGateError):
            validate_current_phase(state)

        state = validate_troia(state)
        state = validate_current_phase(state)

        self.assertIs(
            state.phase_status(RatioPhase.RI_03),
            RatioPhaseStatus.VALIDATED,
        )

    def test_troia_block_requires_normative_code_and_remediation(self) -> None:
        state = self._advance_to(
            RatioModule.RI,
            RatioPhase.RI_03,
        )

        state = block_troia(
            state,
            blocking_code="HS-RI3.1",
            catalog=self.catalog,
        )

        self.assertIs(state.troia.status, TroiaStatus.BLOCKED)
        self.assertIs(
            state.phase_status(RatioPhase.RI_03),
            RatioPhaseStatus.BLOCKED,
        )

        with self.assertRaises(TroiaGateError):
            validate_troia(state)

        state = resume_troia(state)
        state = validate_troia(state)

        self.assertIs(state.troia.status, TroiaStatus.VALIDATED)

    def test_troia_rejects_invented_hard_stop(self) -> None:
        state = self._advance_to(
            RatioModule.RI,
            RatioPhase.RI_03,
        )

        with self.assertRaises(UnknownHardStop):
            block_troia(
                state,
                blocking_code="HS-RI3.999",
                catalog=self.catalog,
            )

    def test_troia_rejects_hard_stop_from_other_phase(self) -> None:
        state = self._advance_to(
            RatioModule.RI,
            RatioPhase.RI_03,
        )

        with self.assertRaises(HardStopPhaseMismatch):
            block_troia(
                state,
                blocking_code="HS-RI2.1",
                catalog=self.catalog,
            )

    def test_ed_can_formally_dispense_troia(self) -> None:
        state = self._advance_to(
            RatioModule.ED,
            RatioPhase.ED_03,
        )

        state = configure_ed_troia(
            state,
            frozenset(),
        )

        self.assertIs(state.troia.status, TroiaStatus.DISPENSED)

        state = validate_current_phase(state)

        self.assertIs(
            state.phase_status(RatioPhase.ED_03),
            RatioPhaseStatus.VALIDATED,
        )

    def test_ed_trigger_requires_troia_validation(self) -> None:
        state = self._advance_to(
            RatioModule.ED,
            RatioPhase.ED_03,
        )

        state = configure_ed_troia(
            state,
            frozenset(
                {
                    TroiaTrigger.INFRINGING_EFFECT_REQUEST,
                }
            ),
        )

        with self.assertRaises(TroiaGateError):
            validate_current_phase(state)

        state = validate_troia(state)
        state = validate_current_phase(state)

        self.assertIs(
            state.phase_status(RatioPhase.ED_03),
            RatioPhaseStatus.VALIDATED,
        )

    def test_substantial_return_invalidates_downstream_and_troia(self) -> None:
        state = self._advance_to(
            RatioModule.RI,
            RatioPhase.RI_03,
        )

        state = validate_troia(state)
        state = validate_current_phase(state)
        state = advance_phase(state)

        self.assertIs(state.current_phase, RatioPhase.RI_04)

        state = return_after_substantial_change(
            state,
            target_phase=RatioPhase.RI_02,
        )

        self.assertIs(state.current_phase, RatioPhase.RI_02)
        self.assertIs(
            state.phase_status(RatioPhase.RI_03),
            RatioPhaseStatus.INVALIDATED_BY_SUBSTANTIAL_CHANGE,
        )
        self.assertIs(state.troia.status, TroiaStatus.INVALIDATED)


if __name__ == "__main__":
    unittest.main()