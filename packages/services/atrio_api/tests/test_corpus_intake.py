from __future__ import annotations

import asyncio
import sys
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4

SERVICE_ROOT = Path(__file__).resolve().parents[1]
SRC = SERVICE_ROOT / "src"
sys.path.insert(0, str(SRC))

from atrio_api.corpus_intake import (  # noqa: E402
    CorpusIntakeConflict,
    DocumentTooLarge,
    EncryptedCorpusStore,
    InvalidDocumentSignature,
    VaultIntegrityError,
    document_id_for,
)


async def stream(*chunks: bytes):
    for chunk in chunks:
        yield chunk


class CorpusIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = EncryptedCorpusStore(self.root, b"k" * 32)
        self.execution_id = str(uuid4())
        self.idempotency_key = "documento-001"
        self.document_id = document_id_for(
            self.execution_id,
            self.idempotency_key,
        )

    def tearDown(self):
        self.temp.cleanup()

    def _encrypt(
        self,
        *chunks: bytes,
        media_type: str = "application/pdf",
    ):
        return asyncio.run(
            self.store.encrypt_stream(
                stream(*chunks),
                document_id=self.document_id,
                execution_id=self.execution_id,
                idempotency_key=self.idempotency_key,
                created_by="operador-test",
                media_type=media_type,
            )
        )

    def test_encrypts_and_authenticates_document(self):
        plaintext = b"%PDF-1.7\nCONTEUDO_SIGILOSO\n%%EOF"
        stored = self._encrypt(plaintext[:9], plaintext[9:])
        envelope = (
            self.root / stored.intake.storage_key
        ).read_bytes()

        self.assertTrue(stored.blob_created)
        self.assertNotIn(b"CONTEUDO_SIGILOSO", envelope)
        self.assertEqual(
            self.store.decrypt_bytes(stored.intake),
            plaintext,
        )
        self.assertEqual(stored.intake.intake_version, "1.0.0")
        self.assertEqual(stored.intake.envelope_version, "ATRIO-V1")

    def test_exact_retry_reuses_same_encrypted_blob(self):
        plaintext = b"%PDF-1.7\nmesmo-documento"
        first = self._encrypt(plaintext)
        before = (self.root / first.intake.storage_key).read_bytes()
        second = self._encrypt(plaintext)
        after = (self.root / second.intake.storage_key).read_bytes()

        self.assertTrue(first.blob_created)
        self.assertFalse(second.blob_created)
        self.assertEqual(first.intake, second.intake)
        self.assertEqual(before, after)

    def test_retry_with_different_content_is_conflict(self):
        self._encrypt(b"%PDF-1.7\nprimeiro")

        with self.assertRaises(CorpusIntakeConflict):
            self._encrypt(b"%PDF-1.7\nsegundo")

    def test_signature_must_match_media_type(self):
        with self.assertRaises(InvalidDocumentSignature):
            self._encrypt(b"nao-e-pdf")

        self.assertEqual(
            list((self.root / "corpus").glob("*.atrio")),
            [],
        )
        self.assertEqual(
            list((self.root / "corpus").glob("*.tmp")),
            [],
        )

    def test_utf8_text_is_validated(self):
        with self.assertRaises(InvalidDocumentSignature):
            self._encrypt(
                b"\xff\xfe",
                media_type="text/plain",
            )

    def test_document_limit_is_enforced_while_streaming(self):
        limited = EncryptedCorpusStore(
            self.root / "limited",
            b"l" * 32,
            max_document_bytes=8,
        )

        with self.assertRaises(DocumentTooLarge):
            asyncio.run(
                limited.encrypt_stream(
                    stream(b"%PDF-1.", b"70"),
                    document_id=str(uuid4()),
                    execution_id=self.execution_id,
                    idempotency_key="limited",
                    created_by="operador-test",
                    media_type="application/pdf",
                )
            )

    def test_wrong_key_and_tampering_are_detected(self):
        stored = self._encrypt(b"%PDF-1.7\nintegridade")
        with self.assertRaises(VaultIntegrityError):
            EncryptedCorpusStore(self.root, b"x" * 32)

        path = self.root / stored.intake.storage_key
        envelope = bytearray(path.read_bytes())
        envelope[-17] ^= 1
        path.write_bytes(envelope)
        with self.assertRaises(VaultIntegrityError):
            self.store.decrypt_bytes(stored.intake)

    def test_passphrase_reopens_only_the_same_vault(self):
        root = self.root / "passphrase"
        phrase = "frase-secreta-de-teste-atrio"
        first = EncryptedCorpusStore.from_passphrase(root, phrase)
        second = EncryptedCorpusStore.from_passphrase(root, phrase)

        first.verify()
        second.verify()
        self.assertEqual(len((root / "vault.salt").read_bytes()), 16)
        with self.assertRaises(VaultIntegrityError):
            EncryptedCorpusStore.from_passphrase(
                root,
                "outra-frase-secreta-invalida",
            )

    def test_document_identity_is_deterministic_and_scoped(self):
        same = document_id_for(
            self.execution_id,
            self.idempotency_key,
        )
        other_key = document_id_for(self.execution_id, "documento-002")
        other_execution = document_id_for(
            str(uuid4()),
            self.idempotency_key,
        )

        self.assertEqual(self.document_id, same)
        self.assertNotEqual(self.document_id, other_key)
        self.assertNotEqual(self.document_id, other_execution)

    def test_private_record_is_encrypted_authenticated_and_immutable(self):
        storage_key = (
            f"processed/{self.execution_id}/{self.document_id}.atrio"
        )
        plaintext = b"texto pseudonimizado [PESSOA_0001]"

        self.assertTrue(
            self.store.write_private_record(storage_key, plaintext)
        )
        self.assertFalse(
            self.store.write_private_record(storage_key, plaintext)
        )
        envelope = (self.root / storage_key).read_bytes()
        self.assertNotIn(b"PESSOA_0001", envelope)
        self.assertEqual(
            self.store.read_private_record(storage_key),
            plaintext,
        )

        with self.assertRaises(CorpusIntakeConflict):
            self.store.write_private_record(storage_key, b"outro texto")

        tampered = bytearray(envelope)
        tampered[-1] ^= 1
        (self.root / storage_key).write_bytes(tampered)
        with self.assertRaises(VaultIntegrityError):
            self.store.read_private_record(storage_key)

    def test_only_pseudonym_map_can_be_atomically_replaced(self):
        storage_key = (
            f"maps/{self.execution_id}/pseudonym-map.atrio"
        )
        self.assertTrue(
            self.store.write_private_record(
                storage_key,
                b'{"version":1}',
                replace=True,
            )
        )
        self.assertTrue(
            self.store.write_private_record(
                storage_key,
                b'{"version":2}',
                replace=True,
            )
        )
        self.assertEqual(
            self.store.read_private_record(storage_key),
            b'{"version":2}',
        )

        immutable_key = (
            f"artifacts/{self.execution_id}/{uuid4()}.atrio"
        )
        with self.assertRaises(ValueError):
            self.store.write_private_record(
                immutable_key,
                b"artifact",
                replace=True,
            )

    def test_private_storage_key_cannot_escape_vault(self):
        with self.assertRaises(ValueError):
            self.store.write_private_record(
                "../maps/pseudonym-map.atrio",
                b"escape",
            )

    def test_empty_private_processing_result_is_authenticated(self):
        storage_key = (
            f"processed/{self.execution_id}/{self.document_id}.atrio"
        )
        self.assertTrue(
            self.store.write_private_record(storage_key, b"")
        )
        self.assertEqual(
            self.store.read_private_record(storage_key),
            b"",
        )


if __name__ == "__main__":
    unittest.main()
