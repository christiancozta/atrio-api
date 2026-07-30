from __future__ import annotations

import asyncio
import codecs
import hashlib
import json
import os
import re
from collections.abc import AsyncIterable
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Protocol
from uuid import UUID, uuid4, uuid5

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers import (
    Cipher,
    algorithms,
    modes,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from atrio_api.domain import ExecutionState


INTAKE_VERSION = "1.0.0"
ENVELOPE_VERSION = "ATRIO-V1"
ENCRYPTION_ALGORITHM = "AES-256-GCM"
MAX_DOCUMENT_BYTES = 50 * 1024 * 1024
_MAGIC = b"ATRIOV1\x00"
_PRIVATE_MAGIC = b"ATRIOP1\x00"
_CHECK_MAGIC = b"ATRIO-CHECK-V1\x00"
_CHECK_PLAINTEXT = b"ATRIO vault key is valid."
_CHECK_AAD = b"ATRIO-VAULT-CHECK-V1"
_NONCE_BYTES = 12
_TAG_BYTES = 16
_SALT_BYTES = 16
_IO_CHUNK_BYTES = 1024 * 1024
_DOCUMENT_NAMESPACE = UUID("17ec9b7e-92f0-4d9b-aec3-71ed7e150c2c")
_STORAGE_KEY = re.compile(
    r"^corpus/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
    r"[0-9a-f]{4}-[0-9a-f]{12}[.]atrio$"
)
_PRIVATE_STORAGE_KEY = re.compile(
    r"^(?:processed|artifacts)/"
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
    r"[0-9a-f]{4}-[0-9a-f]{12}/"
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
    r"[0-9a-f]{4}-[0-9a-f]{12}[.]atrio$"
    r"|^maps/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
    r"[0-9a-f]{4}-[0-9a-f]{12}/pseudonym-map[.]atrio$"
)

ALLOWED_MEDIA_TYPES = frozenset(
    {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/jpeg",
        "image/png",
        "image/tiff",
        "text/plain",
    }
)


class CorpusIntakeError(ValueError):
    pass


class UnsupportedDocumentType(CorpusIntakeError):
    pass


class InvalidDocumentSignature(CorpusIntakeError):
    pass


class DocumentTooLarge(CorpusIntakeError):
    pass


class CorpusIntakeConflict(CorpusIntakeError):
    pass


class VaultIntegrityError(CorpusIntakeError):
    pass


@dataclass(frozen=True, slots=True)
class CorpusIntakeRef:
    document_id: str
    execution_id: str
    idempotency_key: str
    created_by: str
    sha256: str
    byte_length: int
    media_type: str
    storage_key: str
    encryption_algorithm: str = ENCRYPTION_ALGORITHM
    envelope_version: str = ENVELOPE_VERSION
    intake_version: str = INTAKE_VERSION

    def __post_init__(self) -> None:
        UUID(self.document_id)
        UUID(self.execution_id)
        if not self.idempotency_key.strip():
            raise ValueError("idempotency_key é obrigatório.")
        if not self.created_by.strip():
            raise ValueError("created_by é obrigatório.")
        if not re.fullmatch(r"[0-9a-f]{64}", self.sha256):
            raise ValueError("sha256 inválido.")
        if not 0 < self.byte_length <= MAX_DOCUMENT_BYTES:
            raise ValueError("byte_length inválido.")
        if self.media_type not in ALLOWED_MEDIA_TYPES:
            raise ValueError("media_type inválido.")
        if not _STORAGE_KEY.fullmatch(self.storage_key):
            raise ValueError("storage_key inválida.")


@dataclass(frozen=True, slots=True)
class StoredCorpusIntake:
    intake: CorpusIntakeRef
    blob_created: bool


@dataclass(frozen=True, slots=True)
class CorpusIntakeRecordResult:
    state: ExecutionState
    intake: CorpusIntakeRef
    created: bool


class CorpusIntakeRepository(Protocol):
    def record_corpus_intake(
        self,
        intake: CorpusIntakeRef,
        *,
        expected_version: int,
    ) -> CorpusIntakeRecordResult: ...


class CorpusIntakeService:
    def __init__(
        self,
        repository: CorpusIntakeRepository,
        store: EncryptedCorpusStore,
    ):
        self._repository = repository
        self._store = store

    async def ingest(
        self,
        chunks: AsyncIterable[bytes],
        *,
        execution_id: str,
        idempotency_key: str,
        actor_id: str,
        expected_version: int,
        media_type: str,
    ) -> CorpusIntakeRecordResult:
        document_id = document_id_for(execution_id, idempotency_key)
        stored = await self._store.encrypt_stream(
            chunks,
            document_id=document_id,
            execution_id=execution_id,
            idempotency_key=idempotency_key,
            created_by=actor_id,
            media_type=media_type,
        )
        # Um erro após a gravação do blob não o apaga: a transação pode ter
        # sido confirmada antes de a conexão falhar. A identidade determinística
        # permite repetir a chamada e reconciliar o mesmo arquivo com segurança.
        return await asyncio.to_thread(
            self._repository.record_corpus_intake,
            stored.intake,
            expected_version=expected_version,
        )


class EncryptedCorpusStore:
    def __init__(
        self,
        root: Path,
        key: bytes,
        *,
        max_document_bytes: int = MAX_DOCUMENT_BYTES,
    ):
        if len(key) != 32:
            raise ValueError("A chave do cofre deve ter 32 bytes.")
        if not 0 < max_document_bytes <= MAX_DOCUMENT_BYTES:
            raise ValueError("Limite documental inválido.")
        self._root = root.resolve()
        self._key = key
        self._max_document_bytes = max_document_bytes
        self._private_lock = RLock()
        (self._root / "corpus").mkdir(parents=True, exist_ok=True)
        self._verify_or_create_key_check()

    @classmethod
    def from_passphrase(
        cls,
        root: Path,
        passphrase: str,
        *,
        max_document_bytes: int = MAX_DOCUMENT_BYTES,
    ) -> EncryptedCorpusStore:
        if len(passphrase) < 16:
            raise ValueError(
                "A frase secreta do cofre deve ter pelo menos 16 caracteres."
            )
        resolved_root = root.resolve()
        resolved_root.mkdir(parents=True, exist_ok=True)
        salt = _load_or_create_salt(resolved_root / "vault.salt")
        key = Scrypt(
            salt=salt,
            length=32,
            n=2**15,
            r=8,
            p=1,
        ).derive(passphrase.encode("utf-8"))
        return cls(
            resolved_root,
            key,
            max_document_bytes=max_document_bytes,
        )

    def verify(self) -> None:
        self._verify_key_check()

    async def encrypt_stream(
        self,
        chunks: AsyncIterable[bytes],
        *,
        document_id: str,
        execution_id: str,
        idempotency_key: str,
        created_by: str,
        media_type: str,
    ) -> StoredCorpusIntake:
        UUID(document_id)
        UUID(execution_id)
        if media_type not in ALLOWED_MEDIA_TYPES:
            raise UnsupportedDocumentType(
                f"Tipo documental não permitido: {media_type}."
            )

        storage_key = f"corpus/{document_id}.atrio"
        final_path = self._storage_path(storage_key)
        temp_path = final_path.with_name(
            f".{final_path.name}.{uuid4().hex}.tmp"
        )
        nonce = os.urandom(_NONCE_BYTES)
        aad = _associated_data(document_id, execution_id, media_type)
        encryptor = Cipher(
            algorithms.AES(self._key),
            modes.GCM(nonce),
        ).encryptor()
        encryptor.authenticate_additional_data(aad)
        sha256 = hashlib.sha256()
        byte_length = 0
        signature = bytearray()
        text_decoder = (
            codecs.getincrementaldecoder("utf-8")("strict")
            if media_type == "text/plain"
            else None
        )

        try:
            with temp_path.open("xb") as output:
                output.write(_MAGIC)
                output.write(nonce)
                async for chunk in chunks:
                    if not isinstance(chunk, bytes):
                        raise TypeError("O stream documental deve produzir bytes.")
                    if not chunk:
                        continue
                    byte_length += len(chunk)
                    if byte_length > self._max_document_bytes:
                        raise DocumentTooLarge(
                            "Documento excede o limite de 50 MiB."
                        )
                    if len(signature) < 16:
                        needed = 16 - len(signature)
                        signature.extend(chunk[:needed])
                    if text_decoder is not None:
                        decoded = text_decoder.decode(chunk)
                        if "\x00" in decoded:
                            raise InvalidDocumentSignature(
                                "Texto contém byte nulo."
                            )
                    sha256.update(chunk)
                    output.write(encryptor.update(chunk))

                if byte_length == 0:
                    raise InvalidDocumentSignature("Documento vazio.")
                if text_decoder is not None:
                    text_decoder.decode(b"", final=True)
                _validate_signature(media_type, bytes(signature))
                output.write(encryptor.finalize())
                output.write(encryptor.tag)
                output.flush()
                os.fsync(output.fileno())

            digest = sha256.hexdigest()
            blob_created = self._install_blob(
                temp_path,
                final_path,
                document_id=document_id,
                execution_id=execution_id,
                media_type=media_type,
                expected_sha256=digest,
                expected_length=byte_length,
            )
            return StoredCorpusIntake(
                intake=CorpusIntakeRef(
                    document_id=document_id,
                    execution_id=execution_id,
                    idempotency_key=idempotency_key,
                    created_by=created_by,
                    sha256=digest,
                    byte_length=byte_length,
                    media_type=media_type,
                    storage_key=storage_key,
                ),
                blob_created=blob_created,
            )
        except UnicodeDecodeError as exc:
            raise InvalidDocumentSignature(
                "Conteúdo text/plain não é UTF-8 válido."
            ) from exc
        finally:
            temp_path.unlink(missing_ok=True)

    def decrypt_bytes(self, intake: CorpusIntakeRef) -> bytes:
        path = self._storage_path(intake.storage_key)
        plaintext, digest, byte_length = self._decrypt_blob(
            path,
            document_id=intake.document_id,
            execution_id=intake.execution_id,
            media_type=intake.media_type,
            collect=True,
        )
        if digest != intake.sha256 or byte_length != intake.byte_length:
            raise VaultIntegrityError(
                "Metadados do documento divergem do cofre."
            )
        return plaintext

    def write_private_record(
        self,
        storage_key: str,
        plaintext: bytes,
        *,
        replace: bool = False,
    ) -> bool:
        """Cifra um registro interno sem expor texto ou mapas no PostgreSQL.

        Registros de processamento e artefato são imutáveis. Somente o mapa
        global de pseudônimos pode usar ``replace=True``; a troca do envelope
        é atômica e sempre usa nonce novo.
        """
        if not isinstance(plaintext, bytes):
            raise ValueError("Registro privado deve ser binário.")
        if replace and not storage_key.startswith("maps/"):
            raise ValueError(
                "Somente o mapa de pseudônimos admite substituição."
            )
        path = self._private_storage_path(storage_key)
        path.parent.mkdir(parents=True, exist_ok=True)
        nonce = os.urandom(_NONCE_BYTES)
        ciphertext = AESGCM(self._key).encrypt(
            nonce,
            plaintext,
            _private_associated_data(storage_key),
        )
        envelope = _PRIVATE_MAGIC + nonce + ciphertext
        temp_path = path.with_name(f".{path.name}.{uuid4().hex}.tmp")

        with self._private_lock:
            try:
                with temp_path.open("xb") as output:
                    output.write(envelope)
                    output.flush()
                    os.fsync(output.fileno())
                if replace:
                    os.replace(temp_path, path)
                    return True
                try:
                    os.link(temp_path, path)
                    return True
                except FileExistsError:
                    if self.read_private_record(storage_key) != plaintext:
                        raise CorpusIntakeConflict(
                            "Registro privado imutável já possui outro conteúdo."
                        )
                    return False
            finally:
                temp_path.unlink(missing_ok=True)

    def read_private_record(self, storage_key: str) -> bytes:
        path = self._private_storage_path(storage_key)
        try:
            envelope = path.read_bytes()
        except FileNotFoundError:
            raise
        minimum = len(_PRIVATE_MAGIC) + _NONCE_BYTES + _TAG_BYTES
        if len(envelope) < minimum or not envelope.startswith(_PRIVATE_MAGIC):
            raise VaultIntegrityError("Envelope privado inválido.")
        offset = len(_PRIVATE_MAGIC)
        nonce = envelope[offset : offset + _NONCE_BYTES]
        ciphertext = envelope[offset + _NONCE_BYTES :]
        try:
            return AESGCM(self._key).decrypt(
                nonce,
                ciphertext,
                _private_associated_data(storage_key),
            )
        except InvalidTag as exc:
            raise VaultIntegrityError(
                "Autenticidade do registro privado não pôde ser confirmada."
            ) from exc

    def discard(self, storage_key: str) -> None:
        self._storage_path(storage_key).unlink(missing_ok=True)

    def _install_blob(
        self,
        temp_path: Path,
        final_path: Path,
        *,
        document_id: str,
        execution_id: str,
        media_type: str,
        expected_sha256: str,
        expected_length: int,
    ) -> bool:
        try:
            os.link(temp_path, final_path)
            return True
        except FileExistsError:
            try:
                _, digest, byte_length = self._decrypt_blob(
                    final_path,
                    document_id=document_id,
                    execution_id=execution_id,
                    media_type=media_type,
                    collect=False,
                )
            except VaultIntegrityError as exc:
                raise CorpusIntakeConflict(
                    "A chave idempotente já possui outro envelope."
                ) from exc
            if (
                digest != expected_sha256
                or byte_length != expected_length
            ):
                raise CorpusIntakeConflict(
                    "A chave idempotente já possui outro conteúdo."
                )
            return False

    def _decrypt_blob(
        self,
        path: Path,
        *,
        document_id: str,
        execution_id: str,
        media_type: str,
        collect: bool,
    ) -> tuple[bytes, str, int]:
        file_size = path.stat().st_size
        header_size = len(_MAGIC) + _NONCE_BYTES
        if file_size <= header_size + _TAG_BYTES:
            raise VaultIntegrityError("Envelope criptográfico truncado.")

        sha256 = hashlib.sha256()
        byte_length = 0
        collected = bytearray()
        try:
            with path.open("rb") as source:
                if source.read(len(_MAGIC)) != _MAGIC:
                    raise VaultIntegrityError(
                        "Versão do envelope criptográfico inválida."
                    )
                nonce = source.read(_NONCE_BYTES)
                source.seek(-_TAG_BYTES, os.SEEK_END)
                tag = source.read(_TAG_BYTES)
                ciphertext_length = file_size - header_size - _TAG_BYTES
                source.seek(header_size)
                decryptor = Cipher(
                    algorithms.AES(self._key),
                    modes.GCM(nonce, tag),
                ).decryptor()
                decryptor.authenticate_additional_data(
                    _associated_data(document_id, execution_id, media_type)
                )
                remaining = ciphertext_length
                while remaining:
                    block = source.read(min(_IO_CHUNK_BYTES, remaining))
                    if not block:
                        raise VaultIntegrityError(
                            "Envelope criptográfico truncado."
                        )
                    remaining -= len(block)
                    plaintext = decryptor.update(block)
                    sha256.update(plaintext)
                    byte_length += len(plaintext)
                    if collect:
                        collected.extend(plaintext)
                tail = decryptor.finalize()
                sha256.update(tail)
                byte_length += len(tail)
                if collect:
                    collected.extend(tail)
        except InvalidTag as exc:
            raise VaultIntegrityError(
                "Autenticidade do documento não pôde ser confirmada."
            ) from exc

        return bytes(collected), sha256.hexdigest(), byte_length

    def _verify_or_create_key_check(self) -> None:
        path = self._root / "vault.check"
        if path.exists():
            self._verify_key_check()
            return

        nonce = os.urandom(_NONCE_BYTES)
        encryptor = Cipher(
            algorithms.AES(self._key),
            modes.GCM(nonce),
        ).encryptor()
        encryptor.authenticate_additional_data(_CHECK_AAD)
        ciphertext = (
            encryptor.update(_CHECK_PLAINTEXT)
            + encryptor.finalize()
        )
        envelope = (
            _CHECK_MAGIC
            + nonce
            + ciphertext
            + encryptor.tag
        )
        temp_path = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
        try:
            with temp_path.open("xb") as output:
                output.write(envelope)
                output.flush()
                os.fsync(output.fileno())
            try:
                os.link(temp_path, path)
            except FileExistsError:
                pass
            self._verify_key_check()
        finally:
            temp_path.unlink(missing_ok=True)

    def _verify_key_check(self) -> None:
        path = self._root / "vault.check"
        try:
            envelope = path.read_bytes()
        except FileNotFoundError as exc:
            raise VaultIntegrityError(
                "Verificador da chave do cofre está ausente."
            ) from exc
        minimum = len(_CHECK_MAGIC) + _NONCE_BYTES + _TAG_BYTES + 1
        if len(envelope) < minimum or not envelope.startswith(_CHECK_MAGIC):
            raise VaultIntegrityError(
                "Verificador da chave do cofre é inválido."
            )
        offset = len(_CHECK_MAGIC)
        nonce = envelope[offset : offset + _NONCE_BYTES]
        ciphertext_and_tag = envelope[offset + _NONCE_BYTES :]
        ciphertext = ciphertext_and_tag[:-_TAG_BYTES]
        tag = ciphertext_and_tag[-_TAG_BYTES:]
        try:
            decryptor = Cipher(
                algorithms.AES(self._key),
                modes.GCM(nonce, tag),
            ).decryptor()
            decryptor.authenticate_additional_data(_CHECK_AAD)
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        except InvalidTag as exc:
            raise VaultIntegrityError(
                "Frase secreta incorreta ou cofre adulterado."
            ) from exc
        if plaintext != _CHECK_PLAINTEXT:
            raise VaultIntegrityError(
                "Verificador da chave do cofre é inválido."
            )

    def _storage_path(self, storage_key: str) -> Path:
        if not _STORAGE_KEY.fullmatch(storage_key):
            raise ValueError("storage_key inválida.")
        candidate = (self._root / storage_key).resolve()
        if not candidate.is_relative_to(self._root):
            raise ValueError("storage_key escapa do cofre.")
        return candidate

    def _private_storage_path(self, storage_key: str) -> Path:
        if not _PRIVATE_STORAGE_KEY.fullmatch(storage_key):
            raise ValueError("storage_key privada inválida.")
        candidate = (self._root / storage_key).resolve()
        if not candidate.is_relative_to(self._root):
            raise ValueError("storage_key privada escapa do cofre.")
        return candidate


def _associated_data(
    document_id: str,
    execution_id: str,
    media_type: str,
) -> bytes:
    return json.dumps(
        {
            "document_id": document_id,
            "envelope_version": ENVELOPE_VERSION,
            "execution_id": execution_id,
            "intake_version": INTAKE_VERSION,
            "media_type": media_type,
        },
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def _private_associated_data(storage_key: str) -> bytes:
    return (
        b"ATRIO-PRIVATE-V1\x00"
        + storage_key.encode("ascii")
    )


def document_id_for(execution_id: str, idempotency_key: str) -> str:
    UUID(execution_id)
    if not idempotency_key.strip():
        raise ValueError("idempotency_key é obrigatório.")
    return str(
        uuid5(
            _DOCUMENT_NAMESPACE,
            f"{execution_id}\x1f{idempotency_key}",
        )
    )


def _load_or_create_salt(path: Path) -> bytes:
    if path.exists():
        salt = path.read_bytes()
    else:
        candidate = os.urandom(_SALT_BYTES)
        temp_path = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
        try:
            descriptor = os.open(
                temp_path,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o600,
            )
            with os.fdopen(descriptor, "wb") as output:
                output.write(candidate)
                output.flush()
                os.fsync(output.fileno())
            try:
                os.link(temp_path, path)
            except FileExistsError:
                pass
            salt = path.read_bytes()
        finally:
            temp_path.unlink(missing_ok=True)
    if len(salt) != _SALT_BYTES:
        raise VaultIntegrityError("Salt do cofre possui tamanho inválido.")
    return salt


def _validate_signature(media_type: str, signature: bytes) -> None:
    valid = {
        "application/pdf": signature.startswith(b"%PDF-"),
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": (
            signature.startswith(b"PK\x03\x04")
        ),
        "image/jpeg": signature.startswith(b"\xff\xd8\xff"),
        "image/png": signature.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/tiff": signature.startswith((b"II*\x00", b"MM\x00*")),
        "text/plain": True,
    }[media_type]
    if not valid:
        raise InvalidDocumentSignature(
            "Assinatura do arquivo não corresponde ao Content-Type."
        )
