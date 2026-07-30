from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

SERVICE_ROOT = Path(__file__).resolve().parents[1]
SRC = SERVICE_ROOT / "src"
sys.path.insert(0, str(SRC))

from atrio_api.database import (  # noqa: E402
    DATABASE_MIGRATIONS,
    DATABASE_SCHEMA_VERSION,
)
from atrio_api.postgres_repository import (  # noqa: E402
    PostgresExecutionRepository,
    _payload_fingerprint,
)


class DatabaseContractTests(unittest.TestCase):
    def test_applied_migration_checksums_are_frozen(self):
        migration_root = SERVICE_ROOT / "migrations"
        actual = {
            "1.0.0": hashlib.sha256(
                (migration_root / "0001_initial.sql").read_bytes()
            ).hexdigest(),
            "1.1.0": hashlib.sha256(
                (migration_root / "0002_corpus_intake.sql").read_bytes()
            ).hexdigest(),
            "1.1.1": hashlib.sha256(
                (
                    migration_root / "0003_corpus_event_metadata.sql"
                ).read_bytes()
            ).hexdigest(),
            "1.2.0": hashlib.sha256(
                (
                    migration_root / "0004_corpus_processing.sql"
                ).read_bytes()
            ).hexdigest(),
            "1.3.0": hashlib.sha256(
                (
                    migration_root / "0005_ratio_runtime.sql"
                ).read_bytes()
            ).hexdigest(),
        }

        self.assertEqual(DATABASE_SCHEMA_VERSION, "1.3.0")
        self.assertEqual(actual, DATABASE_MIGRATIONS)

    def test_payload_fingerprint_is_canonical(self):
        first = _payload_fingerprint({"phase": "A", "nested": {"b": 2, "a": 1}})
        second = _payload_fingerprint({"nested": {"a": 1, "b": 2}, "phase": "A"})

        self.assertEqual(first, second)
        self.assertRegex(first, r"^[0-9a-f]{64}$")

    def test_empty_conninfo_is_rejected_before_loading_driver(self):
        with self.assertRaises(ValueError):
            PostgresExecutionRepository.from_conninfo(" ")


if __name__ == "__main__":
    unittest.main()
