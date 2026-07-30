from __future__ import annotations

import unittest
from pathlib import Path


SERVICE_ROOT = Path(__file__).resolve().parents[1]
MIGRATION = SERVICE_ROOT / "migrations" / "0005_ratio_runtime.sql"


class RatioDatabaseSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sql = MIGRATION.read_text(encoding="utf-8")

    def test_schema_declares_all_ratio_runtime_tables(self) -> None:
        for table in (
            "atrio.ratio_runs",
            "atrio.ratio_snapshots",
            "atrio.ratio_snapshot_phases",
            "atrio.ratio_transitions",
            "atrio.ratio_operator_decisions",
            "atrio.ratio_artifact_refs",
            "atrio.ratio_idempotency_keys",
        ):
            self.assertIn(f"CREATE TABLE {table}", self.sql)

    def test_run_head_is_monotonic_and_bound_to_start_ratio(self) -> None:
        self.assertIn(
            "NEW.head_revision <> OLD.head_revision + 1",
            self.sql,
        )
        self.assertIn(
            "command_kind_value <> 'START_RATIO'",
            self.sql,
        )

    def test_snapshots_cover_runtime_and_troia_contract(self) -> None:
        for token in (
            "VALIDATED_WITH_NONBLOCKING_CAVEAT",
            "ENDED_FOR_NOW_AFTER_INJUNCTION",
            "AUTONOMOUS_REQUIRED",
            "EMBEDDED_CONDITIONAL",
            "FUTURE_VOTE_OMISSION_RISK",
            "state_sha256 character(64)",
        ):
            self.assertIn(token, self.sql)

    def test_ms_does_not_gain_a_fake_troia_phase(self) -> None:
        self.assertIn(
            "module = 'MS'\n            AND troia_mode = 'NOT_DEFINED'",
            self.sql,
        )
        self.assertIn("AND troia_phase IS NULL", self.sql)

    def test_transition_chain_links_previous_and_resulting_snapshots(self) -> None:
        self.assertIn(
            "FOREIGN KEY (execution_id, expected_revision)",
            self.sql,
        )
        self.assertIn(
            "FOREIGN KEY (execution_id, resulting_revision)",
            self.sql,
        )
        self.assertIn(
            "CHECK (resulting_revision = expected_revision + 1)",
            self.sql,
        )

    def test_external_command_link_is_explicit_but_optional(self) -> None:
        self.assertIn("external_command_sequence bigint", self.sql)
        self.assertIn(
            "REFERENCES atrio.command_log (execution_id, sequence)",
            self.sql,
        )
        self.assertIn(
            "WHERE external_command_sequence IS NOT NULL",
            self.sql,
        )

    def test_audit_records_are_immutable(self) -> None:
        for trigger in (
            "ratio_snapshots_are_immutable",
            "ratio_snapshot_phases_are_immutable",
            "ratio_transitions_are_immutable",
            "ratio_operator_decisions_are_immutable",
            "ratio_artifact_refs_are_immutable",
            "ratio_idempotency_keys_are_immutable",
        ):
            self.assertIn(f"CREATE TRIGGER {trigger}", self.sql)

    def test_artifact_refs_cannot_cross_execution_or_release(self) -> None:
        self.assertIn(
            "artifact_execution_id <> NEW.execution_id",
            self.sql,
        )
        self.assertIn(
            "artifact_release_id <> execution_release_id",
            self.sql,
        )


if __name__ == "__main__":
    unittest.main()
