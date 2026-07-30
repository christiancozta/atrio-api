#!/usr/bin/env python3
"""Gera o manifesto exato das bases normativas copiadas para o runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "infra" / "atrio_api" / "RUNTIME_NORMATIVE_MANIFEST.json"
ROOTS = (
    ROOT / "packages" / "ratio",
    ROOT / "packages" / "cerne" / "00_sistema_cerne",
)
FILES = (
    ROOT / "packages" / "lux" / "00_KERNEL_CURTO_UNIVERSAL_GPT_SAFE.txt",
    ROOT / "packages" / "lux" / "01_UPLOAD_CONHECIMENTO_PERFIS_DE_ESTILO.txt",
    ROOT / "packages" / "lux" / "02_UPLOAD_CONHECIMENTO_GUIA_E_TEMPLATES.txt",
    ROOT / "packages" / "atrio_pii" / "atrio_pii.py",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest() -> dict[str, object]:
    paths = list(FILES)
    for root in ROOTS:
        paths.extend(
            path
            for path in root.rglob("*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.name != ".gitkeep"
        )
    paths = sorted(set(paths), key=lambda path: path.relative_to(ROOT).as_posix())
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise SystemExit(f"Arquivo normativo ausente: {missing[0]}")

    artifacts = [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": digest(path),
            "size_bytes": path.stat().st_size,
        }
        for path in paths
    ]
    digest_input = "\n".join(
        f"{item['path']}\0{item['sha256']}" for item in artifacts
    ).encode("utf-8")
    return {
        "format_version": "1",
        "artifact_count": len(artifacts),
        "content_digest": hashlib.sha256(digest_input).hexdigest(),
        "artifacts": artifacts,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest = build_manifest()
    if args.check:
        if not OUTPUT.is_file():
            raise SystemExit(f"Manifesto ausente: {OUTPUT}")
        current = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if current != manifest:
            raise SystemExit("RUNTIME_NORMATIVE_MANIFEST.json está desatualizado.")
        print(f"RUNTIME_NORMATIVE_OK {manifest['content_digest']}")
        return 0

    OUTPUT.write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(OUTPUT)
    print(manifest["content_digest"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
