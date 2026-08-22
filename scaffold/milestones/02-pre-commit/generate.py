#!/usr/bin/env python3
"""Deterministic generator for 02-pre-commit milestone."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"command failed: {' '.join(cmd)}\n{result.stderr}")
    return result.stdout


def _patch_justfile(justfile_path: Path) -> None:
    text = justfile_path.read_text()

    # Replace lint recipe body (everything between "lint:" and next recipe or EOF)
    text = re.sub(
        r"^(lint:)\n([ \t]+.*\n)*",
        "lint:\n    mise exec -- pre-commit run --all-files\n",
        text,
        flags=re.MULTILINE,
    )

    if "hooks:" not in text:
        text = (
            text.rstrip("\n") + "\n\nhooks:\n    mise exec -- pre-commit install --install-hooks\n"
        )

    justfile_path.write_text(text)


def _resolved_versions(pre_commit_config: Path) -> list[str]:
    text = pre_commit_config.read_text()
    versions = re.findall(r"rev:\s+(\S+)", text)
    repos = re.findall(r"repo:\s+https://github\.com/([^\s]+)", text)
    return [f"{repo}@{ver}" for repo, ver in zip(repos, versions, strict=False)]


def main(project_dir: Path, context_path: Path) -> None:
    templates_dir = Path(__file__).parent / "templates"

    pre_commit_config = project_dir / ".pre-commit-config.yaml"
    shutil.copy2(templates_dir / "pre-commit-config.yaml", pre_commit_config)

    justfile = project_dir / "justfile"
    if justfile.exists():
        _patch_justfile(justfile)

    _run(["mise", "exec", "--", "pre-commit", "autoupdate"], cwd=project_dir)

    versions = _resolved_versions(pre_commit_config)
    unresolved = [v for v in versions if "<latest>" in v]

    notes = [
        "Resolved hook versions: " + ", ".join(versions),
    ]
    if unresolved:
        notes.append("Unresolved (kept placeholder): " + ", ".join(unresolved))

    print(json.dumps({"status": "done", "milestone": "02-pre-commit", "notes": notes}))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <project_dir> <context_json_path>", file=sys.stderr)
        sys.exit(1)
    main(Path(sys.argv[1]), Path(sys.argv[2]))
