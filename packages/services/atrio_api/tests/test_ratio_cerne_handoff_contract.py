from __future__ import annotations

import json
import unittest

from atrio_api.ratio.contract import RatioPhase
from atrio_api.ratio.execution import _output_schema, _parse_output


class RatioCerneHandoffContractTests(unittest.TestCase):
    def test_final_ri_phase_requires_audit_target(self):
        schema = _output_schema(RatioPhase.RI_06, troia_active=False)
        self.assertIn("audit_target", schema["required"])
        self.assertEqual(
            schema["properties"]["audit_target"]["properties"]["object_type"]["enum"],
            ["voto"],
        )

    def test_final_phase_parser_accepts_canonical_target(self):
        payload = {
            "phase": "RI_06",
            "analysis": "validação final",
            "findings": [],
            "conclusion": "voto estabilizado",
            "risk_codes": [],
            "operator_attention": [],
            "audit_target": {
                "object_type": "voto",
                "text": (
                    "VOTO. O recurso é conhecido e a controvérsia foi examinada com "
                    "fundamentação suficiente para permitir auditoria independente."
                ),
            },
        }
        parsed = _parse_output(
            json.dumps(payload, ensure_ascii=False),
            RatioPhase.RI_06,
            troia_active=False,
        )
        self.assertEqual(parsed["audit_target"]["object_type"], "voto")


if __name__ == "__main__":
    unittest.main()
