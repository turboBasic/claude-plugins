#!/usr/bin/env bash
# shellcheck disable=SC1091,SC2015,SC2250,SC2310
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../scripts/verify-lib.sh
source "$SCRIPT_DIR/../../scripts/verify-lib.sh"

# tests/unit
[[ -f tests/unit/__init__.py ]] \
  && ok "tests/unit/__init__.py exists" || fail "tests/unit/__init__.py missing"
if find tests/unit -maxdepth 1 -name 'test_*.py' | grep -q .; then
  ok "tests/unit: at least one test file"
else
  fail "tests/unit: no test_*.py files"
fi
if [[ -f tests/unit/test_cli.py ]]; then
  ok "tests/unit/test_cli.py exists"
  grep -q 'CliRunner' tests/unit/test_cli.py \
    && ok "test_cli.py: uses CliRunner" || fail "test_cli.py: CliRunner missing"
else
  fail "tests/unit/test_cli.py missing"
fi

# tests/integration
[[ -f tests/integration/__init__.py ]] \
  && ok "tests/integration/__init__.py exists" || fail "tests/integration/__init__.py missing"
[[ -f tests/integration/conftest.py ]] \
  && ok "tests/integration/conftest.py exists" || fail "tests/integration/conftest.py missing"
if [[ -f tests/integration/conftest.py ]]; then
  grep -q 'app_config' tests/integration/conftest.py \
    && ok "integration/conftest.py: app_config fixture" || fail "integration/conftest.py: app_config fixture missing"
fi

# http integration test
if find tests/integration -maxdepth 1 -name 'test_http*.py' | grep -q .; then
  ok "tests/integration: http test file found"
else
  fail "tests/integration: no test_http*.py file"
fi

# cli integration test
if [[ -f tests/integration/test_cli.py ]]; then
  ok "tests/integration/test_cli.py exists"
  grep -q 'CliRunner' tests/integration/test_cli.py \
    && ok "tests/integration/test_cli.py: uses CliRunner" || fail "tests/integration/test_cli.py: CliRunner missing"
  grep -q 'respx' tests/integration/test_cli.py \
    && ok "tests/integration/test_cli.py: uses respx" || fail "tests/integration/test_cli.py: respx missing"
else
  fail "tests/integration/test_cli.py missing"
fi

# pyproject.toml
if [[ -f pyproject.toml ]]; then
  while IFS= read -r line; do
    if [[ "$line" == ok:* ]]; then
      ok "${line#ok: }"
    elif [[ "$line" == fail:* ]]; then
      fail "${line#fail: }"
    fi
  done < <(mise exec -- python "$SCRIPT_DIR/../../scripts/validate_pyproject.py" pyproject.toml \
    --test-dep respx pytest-asyncio \
    --coverage-run \
    --coverage-fail-under)
else
  fail "pyproject.toml missing"
fi

# justfile recipes
if [[ -f justfile ]]; then
  for recipe in test-unit test-integration test-cov; do
    grep -q "^${recipe}:" justfile \
      && ok "justfile: ${recipe}" || fail "justfile: ${recipe} recipe missing"
  done
else
  fail "justfile missing"
fi

# run the test suite — structural checks mean nothing if the code doesn't execute
if [[ ${FAIL} -eq 0 ]]; then
  echo "Running: mise exec -- just test" >&2
  if mise exec -- just --quiet test; then
    ok "test suite passed"
  else
    fail "test suite failed — fix the generated code before marking this milestone complete"
  fi
fi

emit_result "07-tests"
