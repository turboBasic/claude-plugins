#!/usr/bin/env python3
"""Validate pyproject.toml structure and dependency presence.

Outputs ok: / fail: lines to stdout for each check performed.
Exit 0 if all checks pass, 1 otherwise.
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path


def _norm_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _dep_name(spec: str) -> str:
    return _norm_name(re.split(r"[\[>=<!;@\s]", spec.strip())[0])


def _all_dep_names(data: dict) -> set[str]:
    names: set[str] = set()
    for spec in data.get("project", {}).get("dependencies", []):
        if isinstance(spec, str):
            names.add(_dep_name(spec))
    for group_specs in data.get("dependency-groups", {}).values():
        for spec in group_specs:
            if isinstance(spec, str):
                names.add(_dep_name(spec))
    return names


def _group_dep_names(data: dict, group: str) -> set[str]:
    names: set[str] = set()
    for spec in data.get("dependency-groups", {}).get(group, []):
        if isinstance(spec, str):
            names.add(_dep_name(spec))
    return names


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate pyproject.toml structure and deps.")
    ap.add_argument("path", nargs="?", default="pyproject.toml")
    ap.add_argument("--build-backend", metavar="BACKEND")
    ap.add_argument("--requires-python", action="store_true")
    ap.add_argument("--ruff-select", nargs="+", metavar="CODE")
    ap.add_argument("--scripts", action="store_true")
    ap.add_argument("--scripts-after-deps", action="store_true")
    ap.add_argument("--dep", nargs="+", metavar="NAME", default=[])
    ap.add_argument("--test-dep", nargs="+", metavar="NAME", default=[])
    ap.add_argument("--pyright-strict", action="store_true")
    ap.add_argument("--pyright-include", action="store_true")
    ap.add_argument("--asyncio-mode", action="store_true")
    ap.add_argument("--coverage-run", action="store_true")
    ap.add_argument("--coverage-fail-under", action="store_true")

    args = ap.parse_args()

    path = Path(args.path)
    fails = 0

    def ok(msg: str) -> None:
        print(f"ok: {msg}")

    def fail(msg: str) -> None:
        nonlocal fails
        fails += 1
        print(f"fail: {msg}")

    if not path.exists():
        fail("pyproject.toml missing")
        return 1

    try:
        raw = path.read_text(encoding="utf-8")
        data: dict = tomllib.loads(raw)
    except tomllib.TOMLDecodeError as exc:
        fail(f"pyproject.toml: TOML parse error — {exc}")
        return 1

    if args.build_backend:
        backend: str = data.get("build-system", {}).get("build-backend", "")
        if args.build_backend in backend:
            ok(f"pyproject.toml: {args.build_backend} build backend")
        else:
            fail(f"pyproject.toml: {args.build_backend} build backend missing (got: {backend!r})")

    if args.requires_python:
        if data.get("project", {}).get("requires-python"):
            ok("pyproject.toml: requires-python set")
        else:
            fail("pyproject.toml: requires-python missing")

    if args.ruff_select:
        select: list = data.get("tool", {}).get("ruff", {}).get("lint", {}).get("select", [])
        missing = [c for c in args.ruff_select if c not in select]
        if not missing:
            codes = ", ".join(args.ruff_select)
            ok(f"pyproject.toml: ruff select configured ({codes})")
        else:
            fail(f"pyproject.toml: ruff select missing codes: {', '.join(missing)}")

    if args.scripts:
        if data.get("project", {}).get("scripts"):
            ok("pyproject.toml: [project.scripts] defined")
        else:
            fail("pyproject.toml: [project.scripts] missing or empty")

    if args.scripts_after_deps:
        scripts_idx = raw.find("[project.scripts]")
        deps_match = re.search(r"^dependencies\s*=", raw, re.MULTILINE)
        deps_idx = deps_match.start() if deps_match else -1
        if scripts_idx != -1 and deps_idx != -1 and scripts_idx > deps_idx:
            ok("pyproject.toml: [project.scripts] after dependencies")
        else:
            fail("pyproject.toml: [project.scripts] must appear after dependencies key")

    all_deps = _all_dep_names(data)
    for name in args.dep:
        if _norm_name(name) in all_deps:
            ok(f"pyproject.toml: {name} dependency")
        else:
            fail(f"pyproject.toml: {name} missing")

    test_deps = _group_dep_names(data, "test")
    for name in args.test_dep:
        if _norm_name(name) in test_deps:
            ok(f"pyproject.toml: {name} in test deps")
        else:
            fail(f"pyproject.toml: {name} missing from test group")

    if args.pyright_strict:
        mode = data.get("tool", {}).get("pyright", {}).get("typeCheckingMode")
        if mode == "strict":
            ok("pyproject.toml: pyright strict mode")
        else:
            fail(f'pyproject.toml: pyright typeCheckingMode = "strict" missing (got: {mode!r})')

    if args.pyright_include:
        include = data.get("tool", {}).get("pyright", {}).get("include", [])
        if "src" in include:
            ok("pyproject.toml: pyright include src")
        else:
            fail('pyproject.toml: pyright include = ["src"] missing')

    if args.asyncio_mode:
        mode = data.get("tool", {}).get("pytest", {}).get("ini_options", {}).get("asyncio_mode")
        if mode:
            ok("pyproject.toml: asyncio_mode set")
        else:
            fail("pyproject.toml: asyncio_mode missing")

    if args.coverage_run:
        if "run" in data.get("tool", {}).get("coverage", {}):
            ok("pyproject.toml: [tool.coverage.run]")
        else:
            fail("pyproject.toml: [tool.coverage.run] missing")

    if args.coverage_fail_under:
        if data.get("tool", {}).get("coverage", {}).get("report", {}).get("fail_under"):
            ok("pyproject.toml: coverage fail_under")
        else:
            fail("pyproject.toml: coverage fail_under missing")

    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
