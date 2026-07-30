"""Operações locais, explícitas e auditáveis do ATRIO."""

from atrio_api.operations.backup import (
    BACKUP_FORMAT_VERSION,
    BackupVerificationError,
    create_authenticated_manifest,
    ensure_authentication_key,
    verify_authenticated_backup,
)

__all__ = [
    "BACKUP_FORMAT_VERSION",
    "BackupVerificationError",
    "create_authenticated_manifest",
    "ensure_authentication_key",
    "verify_authenticated_backup",
]
