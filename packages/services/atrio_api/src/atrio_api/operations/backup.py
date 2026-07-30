"""Manifesto autenticado compartilhado por backup e restauração."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import hmac
import json
import os
from pathlib import Path, PurePosixPath
import secrets
from typing import Any


BACKUP_FORMAT_VERSION = "1.0.0"
MANIFEST_NAME = "MANIFEST.json"
AUTHENTICATION_NAME = "MANIFEST.hmac"


class BackupVerificationError(RuntimeError):
    """Backup incompleto, adulterado ou fora do contrato."""


def ensure_authentication_key(path: Path) -> bytes:
    """Carrega ou cria uma chave local que nunca integra o backup."""

    resolved = path.resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    try:
        key = resolved.read_bytes()
    except FileNotFoundError:
        key = secrets.token_bytes(32)
        try:
            with resolved.open("xb") as stream:
                stream.write(key)
        except FileExistsError:
            key = resolved.read_bytes()
        if os.name != "nt":
            resolved.chmod(0o600)
    if len(key) != 32:
        raise BackupVerificationError(
            "Chave de autenticação do backup deve possuir 32 bytes."
        )
    return key


def create_authenticated_manifest(
    backup_root: Path,
    *,
    authentication_key: bytes,
    metadata: Mapping[str, Any],
) -> dict[str, Any]:
    root = backup_root.resolve()
    _validate_key(authentication_key)
    entries = _collect_entries(root)
    manifest = {
        "format_version": BACKUP_FORMAT_VERSION,
        "metadata": _json_object(metadata),
        "files": entries,
    }
    manifest_bytes = _canonical_json(manifest)
    (root / MANIFEST_NAME).write_bytes(manifest_bytes)
    signature = hmac.new(
        authentication_key,
        manifest_bytes,
        hashlib.sha256,
    ).hexdigest()
    (root / AUTHENTICATION_NAME).write_text(
        signature + "\n",
        encoding="ascii",
    )
    return manifest


def verify_authenticated_backup(
    backup_root: Path,
    *,
    authentication_key: bytes,
) -> dict[str, Any]:
    root = backup_root.resolve()
    _validate_key(authentication_key)
    if not root.is_dir():
        raise BackupVerificationError("Diretório de backup inexistente.")
    try:
        manifest_bytes = (root / MANIFEST_NAME).read_bytes()
        actual_signature = (
            root / AUTHENTICATION_NAME
        ).read_text(encoding="ascii").strip()
    except OSError as exc:
        raise BackupVerificationError(
            "Manifesto autenticado está incompleto."
        ) from exc
    expected_signature = hmac.new(
        authentication_key,
        manifest_bytes,
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(actual_signature, expected_signature):
        raise BackupVerificationError(
            "Assinatura HMAC do backup não confere."
        )
    try:
        manifest = json.loads(manifest_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BackupVerificationError("Manifesto JSON inválido.") from exc
    if (
        not isinstance(manifest, dict)
        or manifest.get("format_version") != BACKUP_FORMAT_VERSION
        or not isinstance(manifest.get("metadata"), dict)
        or not isinstance(manifest.get("files"), list)
    ):
        raise BackupVerificationError("Contrato do manifesto inválido.")

    declared: dict[str, tuple[int, str]] = {}
    for item in manifest["files"]:
        if not isinstance(item, dict) or set(item) != {
            "path",
            "sha256",
            "size",
        }:
            raise BackupVerificationError(
                "Entrada inválida no manifesto."
            )
        relative = _safe_relative_path(item["path"])
        size = item["size"]
        digest = item["sha256"]
        if (
            not isinstance(size, int)
            or isinstance(size, bool)
            or size < 0
            or not isinstance(digest, str)
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
            or relative in declared
        ):
            raise BackupVerificationError(
                "Metadados de arquivo inválidos no manifesto."
            )
        declared[relative] = (size, digest)

    actual = {
        item["path"]: (item["size"], item["sha256"])
        for item in _collect_entries(root)
    }
    if declared != actual:
        raise BackupVerificationError(
            "Conteúdo do backup diverge do manifesto autenticado."
        )
    return manifest


def _collect_entries(root: Path) -> list[dict[str, Any]]:
    if not root.is_dir():
        raise BackupVerificationError("Raiz de backup inexistente.")
    entries: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise BackupVerificationError(
                "Links simbólicos não são aceitos no backup."
            )
        if not path.is_file() or path in {
            root / MANIFEST_NAME,
            root / AUTHENTICATION_NAME,
        }:
            continue
        relative = path.relative_to(root).as_posix()
        entries.append(
            {
                "path": _safe_relative_path(relative),
                "sha256": _file_sha256(path),
                "size": path.stat().st_size,
            }
        )
    if not entries:
        raise BackupVerificationError("Backup não contém arquivos.")
    return entries


def _safe_relative_path(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise BackupVerificationError("Caminho vazio no manifesto.")
    candidate = PurePosixPath(value)
    if (
        candidate.is_absolute()
        or ".." in candidate.parts
        or "." in candidate.parts
        or "\\" in value
    ):
        raise BackupVerificationError(
            "Caminho inseguro no manifesto."
        )
    return candidate.as_posix()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _json_object(value: Mapping[str, Any]) -> dict[str, Any]:
    try:
        decoded = json.loads(_canonical_json(dict(value)))
    except (TypeError, ValueError) as exc:
        raise BackupVerificationError(
            "Metadados do backup não são JSON válido."
        ) from exc
    if not isinstance(decoded, dict):
        raise BackupVerificationError(
            "Metadados do backup devem formar objeto JSON."
        )
    return decoded


def _validate_key(value: bytes) -> None:
    if not isinstance(value, bytes) or len(value) != 32:
        raise BackupVerificationError(
            "Chave HMAC de backup inválida."
        )
