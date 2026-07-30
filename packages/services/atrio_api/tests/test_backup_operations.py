from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from atrio_api.operations.backup import (
    AUTHENTICATION_NAME,
    BACKUP_FORMAT_VERSION,
    MANIFEST_NAME,
    BackupVerificationError,
    create_authenticated_manifest,
    ensure_authentication_key,
    verify_authenticated_backup,
)


class BackupOperationsTests(unittest.TestCase):
    def test_key_is_created_once_and_reused(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "private" / "backup.key"
            first = ensure_authentication_key(path)
            second = ensure_authentication_key(path)
            self.assertEqual(first, second)
            self.assertEqual(len(first), 32)

    def test_manifest_authenticates_every_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "database").mkdir()
            (root / "database" / "atrio.custom").write_bytes(b"db")
            (root / "vault").mkdir()
            (root / "vault" / "vault.salt").write_bytes(b"salt")
            key = b"k" * 32

            created = create_authenticated_manifest(
                root,
                authentication_key=key,
                metadata={"schema": "1.2.0"},
            )
            verified = verify_authenticated_backup(
                root,
                authentication_key=key,
            )

            self.assertEqual(created, verified)
            self.assertEqual(
                verified["format_version"],
                BACKUP_FORMAT_VERSION,
            )
            self.assertTrue((root / MANIFEST_NAME).is_file())
            self.assertTrue((root / AUTHENTICATION_NAME).is_file())

    def test_modified_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = root / "data.bin"
            payload.write_bytes(b"original")
            key = b"k" * 32
            create_authenticated_manifest(
                root,
                authentication_key=key,
                metadata={},
            )
            payload.write_bytes(b"modified")

            with self.assertRaises(BackupVerificationError):
                verify_authenticated_backup(
                    root,
                    authentication_key=key,
                )

    def test_modified_manifest_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data.bin").write_bytes(b"data")
            key = b"k" * 32
            create_authenticated_manifest(
                root,
                authentication_key=key,
                metadata={},
            )
            manifest_path = root / MANIFEST_NAME
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["metadata"]["forged"] = True
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            with self.assertRaisesRegex(
                BackupVerificationError,
                "HMAC",
            ):
                verify_authenticated_backup(
                    root,
                    authentication_key=key,
                )

    def test_unlisted_extra_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data.bin").write_bytes(b"data")
            key = b"k" * 32
            create_authenticated_manifest(
                root,
                authentication_key=key,
                metadata={},
            )
            (root / "injected.bin").write_bytes(b"injected")

            with self.assertRaises(BackupVerificationError):
                verify_authenticated_backup(
                    root,
                    authentication_key=key,
                )


if __name__ == "__main__":
    unittest.main()
