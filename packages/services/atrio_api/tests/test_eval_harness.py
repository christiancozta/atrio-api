from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


_HARNESS_PATH = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "evaluation"
    / "atrio_eval_harness.py"
)
_SPEC = importlib.util.spec_from_file_location("atrio_eval_harness", _HARNESS_PATH)
assert _SPEC is not None and _SPEC.loader is not None
HARNESS = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(HARNESS)


class EvaluationHarnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "evaluation"
        for relative in (
            "_audit",
            "_custody",
            "_freeze/freeze-test",
            "cases/smoke/case-1",
            "runs/smoke",
            "prereg",
        ):
            (self.root / relative).mkdir(parents=True, exist_ok=True)

        source = self.root / "cases/smoke/case-1/source.txt"
        source.write_text("caso fictício", encoding="utf-8")
        metadata = {
            "case_id": "case-1",
            "pool": "smoke",
            "source_file": "source.txt",
            "source_sha256": HARNESS.sha256_file(source),
            "source_size_bytes": source.stat().st_size,
            "registered_at": HARNESS.utc_now(),
            "status": "registered",
            "burned": False,
            "seen_outputs": False,
        }
        HARNESS.write_json(
            self.root / "cases/smoke/case-1/case.json",
            metadata,
        )
        HARNESS.write_json(
            self.root / "_custody/case_index.json",
            {"cases": {"case-1": metadata}},
        )

        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "additionalProperties": False,
            "required": ["schema_version", "status", "text"],
            "properties": {
                "schema_version": {"const": "1.0.0"},
                "status": {"enum": ["completed", "blocked"]},
                "text": {"type": ["string", "null"]},
            },
        }
        HARNESS.write_json(self.root / "prereg/output.json", schema)

        manifest_path = (
            self.root
            / "_freeze/freeze-test/preregistration_manifest.json"
        )
        HARNESS.write_json(manifest_path, {"freeze_id": "freeze-test"})
        HARNESS.write_json(
            self.root / "_freeze/freeze-test/FREEZE_RECEIPT.json",
            {
                "manifest_sha256": HARNESS.sha256_file(manifest_path),
                "external_timestamp": {"status": "PENDING"},
            },
        )

        worker = self.root / "worker.py"
        worker.write_text(
            "\n".join(
                [
                    "import json, os, pathlib, sys",
                    "root = pathlib.Path(os.environ['EVAL_TEST_ROOT'])",
                    "index = json.loads((root / '_custody/case_index.json').read_text(encoding='utf-8'))",
                    "assert index['cases']['case-1']['burned'] is True",
                    "arm = os.environ['ATRIO_EVAL_ARM']",
                    "if arm == 'A0':",
                    "    raise SystemExit(3)",
                    "output = pathlib.Path(os.environ['ATRIO_EVAL_OUTPUT_PATH'])",
                    "output.write_text(json.dumps({'schema_version':'1.0.0','status':'completed','text':'ok'}), encoding='utf-8')",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        self.worker = worker

    def _config(self, arms: tuple[str, ...], *, gate_enabled: bool = True) -> None:
        command = f'"{sys.executable}" "{self.worker}"'
        config = {
            "harness_version": HARNESS.HARNESS_VERSION,
            "arms": {
                arm: {
                    "enabled": True,
                    "kind": "automated",
                    "command": command,
                    "timeout_seconds": 10,
                    "env": {"EVAL_TEST_ROOT": str(self.root)},
                }
                for arm in arms
            },
            "execution": {
                "working_directory": str(self.root),
                "output_filename": "output.json",
                "stdout_filename": "stdout.txt",
                "stderr_filename": "stderr.txt",
                "metadata_filename": "execution.json",
                "output_schema": "prereg/output.json",
                "gate": {
                    "enabled": gate_enabled,
                    "freeze_id": "freeze-test",
                    "require_external_timestamp": False,
                },
            },
            "custody": {"blind_id_prefix": "OUT"},
        }
        HARNESS.write_json(self.root / "harness_config.json", config)

    def _run(self, run_id: str = "run-1") -> None:
        HARNESS.run_case(
            argparse.Namespace(
                root=str(self.root),
                case_id="case-1",
                run_id=run_id,
                confirm_test=False,
            )
        )

    def test_case_is_burned_before_worker_reads_input(self) -> None:
        self._config(("A1",))
        self._run()
        index = HARNESS.read_json(self.root / "_custody/case_index.json")
        case = index["cases"]["case-1"]
        self.assertTrue(case["burned"])
        self.assertEqual(case["status"], "exposed")
        self.assertEqual(case["run_status"], "completed")

    def test_arm_failure_does_not_prevent_other_arms(self) -> None:
        self._config(("A0", "A1"))
        with self.assertRaisesRegex(HARNESS.HarnessError, "falhas simétricas"):
            self._run()
        manifest = HARNESS.read_json(
            self.root / "runs/smoke/case-1/run-1/run_manifest.json"
        )
        self.assertEqual(set(manifest["arms"]), {"A0", "A1"})
        self.assertEqual(manifest["arms"]["A0"]["status"], "failed")
        self.assertEqual(manifest["arms"]["A1"]["status"], "completed")
        self.assertEqual(manifest["status"], "completed_with_failures")

    def test_exposed_case_cannot_be_reused(self) -> None:
        self._config(("A1",))
        self._run()
        with self.assertRaisesRegex(HARNESS.HarnessError, "não pode ser reutilizado"):
            self._run("run-2")

    def test_disabled_gate_blocks_before_burn(self) -> None:
        self._config(("A1",), gate_enabled=False)
        with self.assertRaisesRegex(HARNESS.HarnessError, "gate"):
            self._run()
        index = HARNESS.read_json(self.root / "_custody/case_index.json")
        self.assertFalse(index["cases"]["case-1"]["burned"])


if __name__ == "__main__":
    unittest.main()
