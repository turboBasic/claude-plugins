#!/usr/bin/env bash
# shellcheck disable=SC1091,SC2015,SC2250,SC2310
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../scripts/verify-lib.sh
source "$SCRIPT_DIR/../../scripts/verify-lib.sh"

# git repo
[[ -d .git ]] && ok "git repo initialised" || fail ".git directory missing — git init not run"

# README.md
if [[ -f README.md ]]; then
  ok "README.md exists"
  [[ -n "${1:-}" ]] && { grep -qF "$1" README.md \
    && ok "README.md contains project name" \
    || fail "README.md does not contain project name '$1'"; }
else
  fail "README.md missing"
fi

# pyproject.toml
if [[ -f pyproject.toml ]]; then
  ok "pyproject.toml exists"
  while IFS= read -r line; do
    if [[ "$line" == ok:* ]]; then
      ok "${line#ok: }"
    elif [[ "$line" == fail:* ]]; then
      fail "${line#fail: }"
    fi
  done < <(mise exec -- python "$SCRIPT_DIR/../../scripts/validate_pyproject.py" pyproject.toml \
    --build-backend hatchling \
    --requires-python \
    --ruff-select E RUF \
    --scripts \
    --scripts-after-deps \
    --dep typer structlog \
    --pyright-strict \
    --pyright-include \
    --asyncio-mode)
else
  fail "pyproject.toml missing"
fi

# uv.lock must exist in the project root (not absorbed by a parent workspace)
if [[ -f uv.lock ]]; then
  ok "uv.lock exists in project root"
else
  fail "uv.lock missing in project root — run: uv sync --all-groups"
fi

# no pyrightconfig.json (pyright config lives in [tool.pyright] in pyproject.toml)
[[ ! -f pyrightconfig.json ]] \
  && ok "no pyrightconfig.json (config in pyproject.toml)" \
  || fail "pyrightconfig.json exists — remove it, use [tool.pyright] in pyproject.toml"

# mise.toml
if [[ -f mise.toml ]]; then
  ok "mise.toml exists"
  grep -q 'python' mise.toml && ok "mise.toml: python" || fail "mise.toml: python missing"
  grep -q 'uv' mise.toml && ok "mise.toml: uv" || fail "mise.toml: uv missing"
  grep -q 'just' mise.toml && ok "mise.toml: just" || fail "mise.toml: just missing"
  grep -q '\.python\.venv' mise.toml && ok "mise.toml: _.python.venv" || fail "mise.toml: _.python.venv missing — add [env] section with venv auto-activation"
  grep -q 'VIRTUAL_ENV_PROMPT' mise.toml && ok "mise.toml: VIRTUAL_ENV_PROMPT" || fail "mise.toml: VIRTUAL_ENV_PROMPT missing — add VIRTUAL_ENV_PROMPT = \"<project_name>\" to [env]"
else
  fail "mise.toml missing"
fi

# .editorconfig
if [[ -f .editorconfig ]]; then
  ok ".editorconfig exists"
  grep -q 'root = true' .editorconfig && ok ".editorconfig: root = true" || fail ".editorconfig: root = true missing"
  grep -q 'end_of_line = lf' .editorconfig && ok ".editorconfig: end_of_line = lf" || fail ".editorconfig: end_of_line = lf missing"
else
  fail ".editorconfig missing"
fi

# .gitignore
if [[ -f .gitignore ]]; then
  ok ".gitignore exists"
  grep -q '\.venv' .gitignore && ok ".gitignore: .venv" || fail ".gitignore: .venv missing"
  grep -q '__pycache__' .gitignore && ok ".gitignore: __pycache__" || fail ".gitignore: __pycache__ missing"
else
  fail ".gitignore missing"
fi

# .gitattributes
if [[ -f .gitattributes ]]; then
  ok ".gitattributes exists"
  grep -q 'eol=lf' .gitattributes && ok ".gitattributes: eol=lf" || fail ".gitattributes: eol=lf missing"
else
  fail ".gitattributes missing"
fi

# justfile
if [[ -f justfile ]]; then
  ok "justfile exists"
  for recipe in install lock lint test type-check; do
    grep -q "^${recipe}:" justfile \
      && ok "justfile: ${recipe}" || fail "justfile: ${recipe} recipe missing"
  done
else
  fail "justfile missing"
fi

# src package
PKG=$(find src -maxdepth 1 -mindepth 1 -type d 2>/dev/null | head -1)
if [[ -n "$PKG" ]]; then
  ok "src package found: $PKG"
  [[ -f "${PKG}/__init__.py" ]] \
    && ok "${PKG}/__init__.py exists" || fail "${PKG}/__init__.py missing"
  if [[ -f "${PKG}/logging.py" ]]; then
    ok "${PKG}/logging.py exists"
    grep -q 'logging\.root\.setLevel' "${PKG}/logging.py" \
      && ok "logging.py: logging.root.setLevel" \
      || fail "logging.py: logging.root.setLevel missing — do not use basicConfig"
    grep -q 'ExceptionRenderer' "${PKG}/logging.py" \
      && ok "logging.py: ExceptionRenderer in processor chain" \
      || fail "logging.py: ExceptionRenderer missing — tracebacks will be silently dropped"
  else
    fail "${PKG}/logging.py missing"
  fi
  if [[ -f "${PKG}/cli.py" ]]; then
    ok "${PKG}/cli.py exists"
    grep -qi 'typer' "${PKG}/cli.py" \
      && ok "cli.py: Typer app" || fail "cli.py: Typer app missing"
  else
    fail "${PKG}/cli.py missing"
  fi
else
  fail "src/<package> directory missing"
fi

# tests
[[ -f tests/__init__.py ]] && ok "tests/__init__.py exists" || fail "tests/__init__.py missing"
[[ -f tests/conftest.py ]] && ok "tests/conftest.py exists" || fail "tests/conftest.py missing"
grep -q 'FIXTURES_DIR' tests/conftest.py \
  && ok "tests/conftest.py: FIXTURES_DIR" || fail "tests/conftest.py: FIXTURES_DIR missing"
[[ -f tests/fixtures/.gitkeep ]] \
  && ok "tests/fixtures/.gitkeep exists" || fail "tests/fixtures/.gitkeep missing"

# CLAUDE.md
[[ -f CLAUDE.md ]] && ok "CLAUDE.md exists" || fail "CLAUDE.md missing"

# no stray root-level main.py
[[ ! -f main.py ]] && ok "no stray main.py at project root" || fail "main.py at project root — delete it, entry point is in pyproject.toml"

# no .python-version (mise.toml is the authoritative Python version pin)
[[ ! -f .python-version ]] && ok "no .python-version at project root" || fail ".python-version at project root — delete it, mise.toml pins the Python version"

emit_result "01-scaffold"
