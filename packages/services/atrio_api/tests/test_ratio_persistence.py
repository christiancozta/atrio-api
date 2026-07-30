from __future__ import annotations

from dataclasses import replace
import unittest

from atrio_api.domain import RatioModule
from atrio_api.postgres_repository import (
    _ratio_state_sha256,
    _validate_ratio_state_shape,
    _validate_ratio_transition_pair,
)
from atrio_api.ratio import (
    RatioPersistenceIntegrityError,
    RatioRevisionConflict,
    advance_phase,
    create_ratio_run,
    validate_current_phase,
)


class RatioPersistenceContractTests(unittest.TestCase):
    def test_state_hash_is_stable(self) -> None:
        first = create_ratio_run(RatioModule.RI)
        second = create_ratio_run(RatioModule.RI)

        self.assertEqual(
            _ratio_state_sha256(first),
            _ratio_state_sha256(second),
        )
        self.assertRegex(_ratio_state_sha256(first), r"^[0-9a-f]{64}$")

    def test_state_hash_changes_with_revision_and_state(self) -> None:
        first = create_ratio_run(RatioModule.RI)
        second = validate_current_phase(first)

        self.assertNotEqual(
            _ratio_state_sha256(first),
            _ratio_state_sha256(second),
        )

    def test_transition_pair_requires_exact_next_revision(self) -> None:
        first = create_ratio_run(RatioModule.RI)
        invalid = replace(first, revision=2)

        with self.assertRaises(RatioRevisionConflict):
            _validate_ratio_transition_pair(
                first,
                invalid,
                "INVALID_TEST",
            )

    def test_state_shape_rejects_missing_phase(self) -> None:
        state = create_ratio_run(RatioModule.ED)
        invalid = replace(state, phases=state.phases[:-1])

        with self.assertRaises(RatioPersistenceIntegrityError):
            _validate_ratio_state_shape(invalid)

    def test_ms_persists_without_inventing_troia(self) -> None:
        state = create_ratio_run(RatioModule.MS)

        _validate_ratio_state_shape(state)
        self.assertIsNone(state.troia.phase)

    def test_engine_result_is_persistence_compatible(self) -> None:
        state = create_ratio_run(RatioModule.RI)
        validated = validate_current_phase(state)
        advanced = advance_phase(validated)

        _validate_ratio_transition_pair(
            state,
            validated,
            "VALIDATE",
        )
        _validate_ratio_transition_pair(
            validated,
            advanced,
            "ADVANCE",
        )


if __name__ == "__main__":
    unittest.main()
