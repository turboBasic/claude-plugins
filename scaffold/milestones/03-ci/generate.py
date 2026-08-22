#!/usr/bin/env python3
"""Deterministic generator for 03-ci milestone."""

from __future__ import annotations

import json
import shutil
import sys
import urllib.request
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

_FALLBACKS = {
    "actions/checkout": "v6.0.2",
    "jdx/mise-action": "v4.0.1",
    "actions/cache": "v4.0.2",
    "tj-actions/changed-files": "v47.0.6",
}


def _latest_release(repo: str, timeout: int = 10) -> str | None:
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
            return str(data["tag_name"])
    except Exception:
        return None


def _resolve_versions() -> tuple[dict[str, str], list[str]]:
    resolved: dict[str, str] = {}
    fallbacks_used: list[str] = []

    for repo, fallback in _FALLBACKS.items():
        tag = _latest_release(repo)
        if tag:
            resolved[repo] = tag
        else:
            resolved[repo] = fallback
            fallbacks_used.append(f"{repo}@{fallback} (fallback)")

    return resolved, fallbacks_used


def main(project_dir: Path, context_path: Path) -> None:
    templates_dir = Path(__file__).parent / "templates"
    workflows_dir = project_dir / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    versions, fallbacks_used = _resolve_versions()

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )
    ci_yml = env.get_template("ci.yml.j2").render(
        checkout_version=versions["actions/checkout"],
        mise_action_version=versions["jdx/mise-action"],
        cache_version=versions["actions/cache"],
        changed_files_version=versions["tj-actions/changed-files"],
    )
    (workflows_dir / "ci.yml").write_text(ci_yml, encoding="utf-8")

    shutil.copy2(templates_dir / "dependabot.yml", project_dir / ".github" / "dependabot.yml")
    shutil.copy2(templates_dir / "renovate.json", project_dir / ".github" / "renovate.json")

    resolved_list = [f"{repo}@{ver}" for repo, ver in versions.items()]
    notes = [
        "Resolved action versions: " + ", ".join(resolved_list),
    ]
    if fallbacks_used:
        notes.append("Fallbacks used (API unavailable): " + ", ".join(fallbacks_used))

    print(json.dumps({"status": "done", "milestone": "03-ci", "notes": notes}))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <project_dir> <context_json_path>", file=sys.stderr)
        sys.exit(1)
    main(Path(sys.argv[1]), Path(sys.argv[2]))
