from __future__ import annotations

from pathlib import Path
import re
import unittest

from atrio_api.domain import RatioModule
from atrio_api.ratio import (
    HardStopPhaseMismatch,
    RatioPhase,
    UnknownHardStop,
    load_hard_stop_catalog,
)


_RATIO_ROOT = Path(__file__).resolve().parents[3] / "ratio"
_PATTERN = re.compile(
    r"^(HS-(?:RI|ED|MS)\d+\.\d+)\s+"
)


class RatioHardStopCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_hard_stop_catalog(_RATIO_ROOT)

    def test_catalog_contains_known_phase_codes(self) -> None:
        self.assertIs(
            self.catalog.get("HS-RI3.1").phase,
            RatioPhase.RI_03,
        )
        self.assertIs(
            self.catalog.get("HS-ED3.5").phase,
            RatioPhase.ED_03,
        )
        self.assertIs(
            self.catalog.get("HS-MS5.6").phase,
            RatioPhase.MS_05,
        )

    def test_ms_zero_codes_are_module_wide_not_phase_zero(self) -> None:
        rule = self.catalog.get("HS-MS0.1")

        self.assertIs(rule.module, RatioModule.MS)
        self.assertIsNone(rule.phase)
        self.assertTrue(rule.is_module_wide)

    def test_module_wide_ms_code_applies_to_any_ms_phase(self) -> None:
        rule = self.catalog.require_for_phase(
            "HS-MS0.1",
            RatioPhase.MS_03,
        )

        self.assertEqual(rule.code, "HS-MS0.1")

    def test_module_wide_ms_code_cannot_cross_modules(self) -> None:
        with self.assertRaises(HardStopPhaseMismatch):
            self.catalog.require_for_phase(
                "HS-MS0.1",
                RatioPhase.RI_03,
            )

    def test_catalog_has_rules_for_all_three_modules(self) -> None:
        self.assertTrue(self.catalog.for_module(RatioModule.RI))
        self.assertTrue(self.catalog.for_module(RatioModule.ED))
        self.assertTrue(self.catalog.for_module(RatioModule.MS))

    def test_for_phase_includes_specific_and_module_wide_rules(self) -> None:
        codes = {
            rule.code
            for rule in self.catalog.for_phase(RatioPhase.MS_03)
        }

        self.assertIn("HS-MS0.1", codes)
        self.assertIn("HS-MS3.1", codes)

    def test_unknown_code_fails_closed(self) -> None:
        with self.assertRaises(UnknownHardStop):
            self.catalog.get("HS-RI3.999")

    def test_phase_specific_code_cannot_be_used_in_another_phase(self) -> None:
        with self.assertRaises(HardStopPhaseMismatch):
            self.catalog.require_for_phase(
                "HS-RI3.1",
                RatioPhase.RI_02,
            )

    def test_catalog_matches_every_code_in_canonical_module_files(self) -> None:
        source_codes: set[str] = set()

        for path in sorted((_RATIO_ROOT / "modulos").glob("modulo_*.md")):
            for line in path.read_text(encoding="utf-8").splitlines():
                match = _PATTERN.match(line.strip())
                if match is not None:
                    source_codes.add(match.group(1))

        self.assertEqual(
            set(self.catalog.rules),
            source_codes,
        )

    def test_catalog_and_sources_have_stable_hashes(self) -> None:
        self.assertRegex(self.catalog.catalog_sha256, r"^[0-9a-f]{64}$")
        self.assertEqual(len(self.catalog.source_sha256), 3)

        for digest in self.catalog.source_sha256.values():
            self.assertRegex(digest, r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
