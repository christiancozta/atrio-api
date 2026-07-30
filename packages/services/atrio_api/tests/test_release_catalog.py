from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

SERVICE_ROOT = Path(__file__).resolve().parents[1]
SRC = SERVICE_ROOT / "src"
sys.path.insert(0, str(SRC))

from atrio_api import __version__  # noqa: E402
from atrio_api.release_catalog import (  # noqa: E402
    ACTIVE_RELEASE,
    MANIFEST_SHA256,
    NORMATIVE_BUNDLE_SHA256,
)


class ReleaseCatalogTests(unittest.TestCase):
    def test_release_matches_service_and_manifest(self):
        manifest = next(
            parent / "MANIFEST.yaml"
            for parent in SERVICE_ROOT.parents
            if (parent / "MANIFEST.yaml").is_file()
        )
        actual_manifest_hash = hashlib.sha256(manifest.read_bytes()).hexdigest()

        self.assertEqual(__version__, "0.7.0")
        self.assertEqual(ACTIVE_RELEASE.atrio_api_version, __version__)
        normative_manifest = (
            manifest.parent
            / "infra"
            / "atrio_api"
            / "RUNTIME_NORMATIVE_MANIFEST.json"
        )
        normative = json.loads(normative_manifest.read_text(encoding="utf-8"))
        self.assertEqual(
            ACTIVE_RELEASE.prompt_bundle_hash,
            NORMATIVE_BUNDLE_SHA256,
        )
        self.assertEqual(
            normative["content_digest"],
            NORMATIVE_BUNDLE_SHA256,
        )
        digest_lines = []
        for artifact in normative["artifacts"]:
            path = manifest.parent / artifact["path"]
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(actual, artifact["sha256"], artifact["path"])
            self.assertEqual(path.stat().st_size, artifact["size_bytes"])
            digest_lines.append(f"{artifact['path']}\0{artifact['sha256']}")
        calculated_bundle = hashlib.sha256(
            "\n".join(digest_lines).encode("utf-8")
        ).hexdigest()
        self.assertEqual(calculated_bundle, NORMATIVE_BUNDLE_SHA256)
        self.assertEqual(actual_manifest_hash, MANIFEST_SHA256)


if __name__ == "__main__":
    unittest.main()
