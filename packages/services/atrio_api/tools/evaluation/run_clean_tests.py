#!/usr/bin/env python3
"""Testa um commit exportado e produz evidência reproduzível com hashes."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import tarfile
import tempfile
from xml.etree import ElementTree


APP_RELATIVE = Path("CORPUS/.ATRIO/atrio")


class EvidenceError(RuntimeError):
    pass


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def run(
    argv: list[str],
    *,
    cwd: Path,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=cwd,
        env=environment,
        capture_output=True,
        check=False,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def required_success(result: subprocess.CompletedProcess[str], label: str) -> str:
    if result.returncode != 0:
        raise EvidenceError(f"{label} falhou: {result.stderr.strip()}")
    return result.stdout.strip()


def junit_counts(path: Path) -> dict[str, int]:
    root = ElementTree.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    names = ("tests", "failures", "errors", "skipped")
    return {
        name: sum(int(suite.attrib.get(name, "0")) for suite in suites)
        for name in names
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    repo = args.repo.resolve()
    python = args.python.resolve()
    output = args.output.resolve()
    if output.exists():
        raise EvidenceError(f"Diretório de evidência já existe: {output}")
    if not python.is_file():
        raise EvidenceError(f"Python isolado ausente: {python}")

    commit = required_success(
        run(["git", "rev-parse", f"{args.commit}^{{commit}}"], cwd=repo),
        "Resolução do commit",
    )
    output.mkdir(parents=True)
    archive_path = output / "source.tar"
    archive_result = run(
        [
            "git",
            "archive",
            "--format=tar",
            "-o",
            str(archive_path),
            commit,
        ],
        cwd=repo,
    )
    required_success(archive_result, "Exportação Git")

    junit_path = output / "junit.xml"
    stdout_path = output / "pytest.stdout.txt"
    stderr_path = output / "pytest.stderr.txt"
    started_at = now()
    with tempfile.TemporaryDirectory(prefix="atrio-clean-test-") as temporary:
        export_root = Path(temporary)
        with tarfile.open(archive_path, "r") as archive:
            archive.extractall(export_root, filter="data")
        app_root = export_root / APP_RELATIVE
        if not app_root.is_dir():
            raise EvidenceError(f"Raiz ATRIO ausente no export: {app_root}")

        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(
            app_root / "packages/services/atrio_api/src"
        )
        test_result = run(
            [
                str(python),
                "-m",
                "pytest",
                "-q",
                "packages/services/atrio_api/tests",
                f"--junitxml={junit_path}",
            ],
            cwd=app_root,
            environment=environment,
        )
    finished_at = now()

    stdout_path.write_text(test_result.stdout, encoding="utf-8", newline="\n")
    stderr_path.write_text(test_result.stderr, encoding="utf-8", newline="\n")
    if not junit_path.is_file():
        raise EvidenceError("Pytest não produziu JUnit.")

    python_version = required_success(
        run([str(python), "--version"], cwd=repo),
        "Versão Python",
    )
    pip_freeze = required_success(
        run([str(python), "-m", "pip", "freeze", "--all"], cwd=repo),
        "Inventário de dependências",
    ).splitlines()
    commit_description = required_success(
        run(
            ["git", "show", "-s", "--format=%H%n%cI%n%s", commit],
            cwd=repo,
        ),
        "Descrição do commit",
    ).splitlines()

    artifacts = {}
    for path in (archive_path, junit_path, stdout_path, stderr_path):
        artifacts[path.name] = {
            "sha256": sha256(path),
            "size_bytes": path.stat().st_size,
        }
    counts = junit_counts(junit_path)
    manifest = {
        "format_version": "1",
        "commit": commit,
        "commit_timestamp": commit_description[1],
        "commit_subject": commit_description[2],
        "started_at": started_at,
        "finished_at": finished_at,
        "platform": platform.platform(),
        "python": python_version,
        "test_command": [
            str(python),
            "-m",
            "pytest",
            "-q",
            "packages/services/atrio_api/tests",
            "--junitxml=junit.xml",
        ],
        "return_code": test_result.returncode,
        "junit": counts,
        "dependencies": pip_freeze,
        "artifacts": artifacts,
    }
    manifest_path = output / "evidence_manifest.json"
    manifest_path.write_text(
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
    print(manifest_path)
    print(json.dumps(counts, sort_keys=True))
    if test_result.returncode != 0:
        raise EvidenceError(
            f"Suíte limpa falhou com código {test_result.returncode}."
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EvidenceError as exc:
        raise SystemExit(f"ERRO: {exc}") from exc
