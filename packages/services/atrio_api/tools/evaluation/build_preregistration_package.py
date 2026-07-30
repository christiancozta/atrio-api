#!/usr/bin/env python3
"""Monta o pacote canônico sem alterar nem renomear os artefatos recebidos."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import tempfile


SOURCE_MAP = {
    "protocol_1.0.1.md": "protocol.md",
    "dataset_schema_1.0.1.json": "dataset_schema.json",
    "registro_exemplo_1.0.1.json": "example_record.json",
    "arm_output_schema_1.0.0.json": "arm_output_schema.json",
}
EXPECTED_INTERNAL_VERSIONS = {
    "protocol": "1.0",
    "dataset_schema": "1.0.0",
    "example_record": "1.0.0",
    "arm_output_schema": "1.0.0",
}


class PackageError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=path.parent,
        prefix=f".{path.name}.",
        delete=False,
    ) as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
        temporary = Path(handle.name)
    os.replace(temporary, path)


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def verify_internal_versions(source: Path) -> None:
    protocol = (source / "protocol_1.0.1.md").read_text(encoding="utf-8")
    if "**Versão do protocolo:** 1.0" not in protocol:
        raise PackageError("Versão interna do protocolo não é 1.0.")

    schema = json.loads(
        (source / "dataset_schema_1.0.1.json").read_text(encoding="utf-8")
    )
    schema_version = schema.get("properties", {}).get(
        "schema_version", {}
    ).get("const")
    if schema_version != "1.0.0":
        raise PackageError("Versão interna do dataset schema não é 1.0.0.")

    example = json.loads(
        (source / "registro_exemplo_1.0.1.json").read_text(encoding="utf-8")
    )
    if example.get("schema_version") != "1.0.0":
        raise PackageError("Versão interna do exemplo não é 1.0.0.")

    output_schema = json.loads(
        (source / "arm_output_schema_1.0.0.json").read_text(encoding="utf-8")
    )
    output_version = output_schema.get("properties", {}).get(
        "schema_version", {}
    ).get("const")
    if output_version != "1.0.0":
        raise PackageError("Versão do schema de output não é 1.0.0.")


def build(
    source: Path,
    destination: Path,
    *,
    candidate_product_commit: str,
) -> Path:
    source = source.resolve()
    destination = destination.resolve()
    verify_internal_versions(source)

    provenance: list[dict[str, object]] = []
    for source_name, canonical_name in SOURCE_MAP.items():
        source_path = source / source_name
        if not source_path.is_file():
            raise PackageError(f"Artefato-fonte ausente: {source_path}")
        destination_path = destination / canonical_name
        content = source_path.read_bytes()
        atomic_write(destination_path, content)
        if source_path.read_bytes() != destination_path.read_bytes():
            raise PackageError(f"Cópia canônica divergiu: {canonical_name}")
        provenance.append(
            {
                "source_name": source_name,
                "canonical_name": canonical_name,
                "sha256": sha256(destination_path),
                "size_bytes": destination_path.stat().st_size,
            }
        )

    included: list[dict[str, object]] = []
    for path in sorted(destination.rglob("*")):
        if (
            path.is_file()
            and path.name != "package_manifest.json"
            and not path.name.startswith(".")
        ):
            included.append(
                {
                    "path": path.relative_to(destination).as_posix(),
                    "sha256": sha256(path),
                    "size_bytes": path.stat().st_size,
                }
            )

    manifest = {
        "package_format_version": "1",
        "status": "DRAFT_BLOCKED",
        "created_at": dt.datetime.now(dt.timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "methodology_versions": EXPECTED_INTERNAL_VERSIONS,
        "candidate_product_commit": candidate_product_commit,
        "source_provenance": provenance,
        "artifacts": included,
        "external_timestamp": {
            "status": "PENDING",
            "provider": None,
            "receipt_sha256": None,
        },
        "execution_authorized": False,
    }
    manifest["content_digest"] = hashlib.sha256(
        canonical_json(manifest)
    ).hexdigest()
    manifest_path = destination / "package_manifest.json"
    atomic_write(manifest_path, canonical_json(manifest))
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--candidate-product-commit", required=True)
    args = parser.parse_args()
    commit = args.candidate_product_commit.lower()
    if (
        len(commit) != 40
        or any(character not in "0123456789abcdef" for character in commit)
    ):
        parser.error("--candidate-product-commit deve ser SHA-1 de 40 caracteres")
    try:
        print(
            build(
                args.source,
                args.destination,
                candidate_product_commit=commit,
            )
        )
    except PackageError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
