#!/usr/bin/env python3
"""Deterministic scaffold generator for 01-scaffold milestone."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined


def _run(cmd: list[str], cwd: Path) -> None:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"command failed: {' '.join(cmd)}\n{result.stderr}")


def _python_version(project_dir: Path) -> str:
    result = subprocess.run(
        ["mise", "exec", "--", "python", "--version"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() or result.stderr.strip()


def _render_templates(
    templates_dir: Path,
    project_dir: Path,
    package_name: str,
    context: dict[str, str],
) -> None:
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )

    for src in sorted(templates_dir.rglob("*")):
        if src.is_dir():
            continue

        rel = src.relative_to(templates_dir)
        parts = list(rel.parts)

        # src/ → src/<package_name>/
        if parts[0] == "src" and len(parts) > 1:
            parts = ["src", package_name, *parts[1:]]

        # strip .j2 extension
        name = parts[-1]
        if name.endswith(".j2"):
            parts[-1] = name[:-3]
            target = project_dir / Path(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            template_key = str(rel).replace("\\", "/")
            rendered = env.get_template(template_key).render(**context)
            target.write_text(rendered, encoding="utf-8")
        else:
            target = project_dir / Path(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)


def main(project_dir: Path, context_path: Path) -> None:
    ctx = json.loads(context_path.read_text())
    project_name: str = ctx["project_name"]
    package_name: str = ctx["package_name"]
    description: str = ctx["description"]

    templates_dir = Path(__file__).parent / "templates"

    project_dir.mkdir(parents=True, exist_ok=True)

    _run(["git", "init", str(project_dir)], cwd=project_dir.parent)
    _run(
        [
            "mise",
            "exec",
            "--",
            "uv",
            "init",
            "--name",
            project_name,
            "--no-readme",
            "--no-workspace",
            ".",
        ],
        cwd=project_dir,
    )

    for remove in [".python-version", "main.py"]:
        p = project_dir / remove
        if p.exists():
            p.unlink()

    template_context = {
        "project_name": project_name,
        "package_name": package_name,
        "description": description,
    }
    _render_templates(templates_dir, project_dir, package_name, template_context)

    _run(["mise", "trust", str(project_dir / "mise.toml")], cwd=project_dir)
    _run(["mise", "exec", "--", "uv", "sync", "--all-groups"], cwd=project_dir)
    _run(["git", "add", "-A"], cwd=project_dir)

    python_ver = _python_version(project_dir)
    notes = [
        f"Python version resolved by mise: {python_ver}",
        "Base dependencies: typer, rich, structlog (versions resolved by uv)",
        "[tool.hatch.build.targets.wheel] packages set for src-layout",
        "Logging: structlog with ExceptionRenderer + make_filtering_bound_logger",
    ]
    print(json.dumps({"status": "done", "milestone": "01-scaffold", "notes": notes}))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <project_dir> <context_json_path>", file=sys.stderr)
        sys.exit(1)
    main(Path(sys.argv[1]), Path(sys.argv[2]))
