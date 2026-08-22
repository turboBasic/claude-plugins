#!/usr/bin/env bash
# shellcheck disable=SC1091,SC2015,SC2250,SC2310
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../scripts/verify-lib.sh
source "$SCRIPT_DIR/../../scripts/verify-lib.sh"

PKG=$(find src -maxdepth 1 -mindepth 1 -type d 2>/dev/null | head -1)
if [[ -z "$PKG" ]]; then
  fail "src/<package> directory missing"
  emit_result "06-aws"
fi
ok "src package found: $PKG"

# aws directory
if [[ -d "${PKG}/aws" ]]; then
  ok "${PKG}/aws/ directory exists"
else
  fail "${PKG}/aws/ directory missing"
  emit_result "06-aws"
fi

[[ -f "${PKG}/aws/__init__.py" ]] \
  && ok "${PKG}/aws/__init__.py exists" || fail "${PKG}/aws/__init__.py missing"

# models.py
if [[ -f "${PKG}/aws/models.py" ]]; then
  ok "${PKG}/aws/models.py exists"
  grep -q 'BaseModel' "${PKG}/aws/models.py" \
    && ok "aws/models.py: Pydantic BaseModel" || fail "aws/models.py: Pydantic BaseModel missing"
else
  fail "${PKG}/aws/models.py missing"
fi

# at least one service module
service_files=$(find "${PKG}/aws" -maxdepth 1 -name '*.py' ! -name '__init__.py' ! -name 'models.py')
if [[ -n "$service_files" ]]; then
  ok "${PKG}/aws: service module(s) found"
  while IFS= read -r svc; do
    name=$(basename "$svc")
    grep -q 'structlog' "$svc" \
      && ok "${name}: structlog" || fail "${name}: structlog missing"
    grep -q 'AppConfig' "$svc" \
      && ok "${name}: AppConfig injection" || fail "${name}: AppConfig injection missing"
    grep -q 'boto3' "$svc" \
      && ok "${name}: boto3" || fail "${name}: boto3 missing"
    grep -q 'get_client' "$svc" \
      && ok "${name}: get_client factory" || fail "${name}: get_client factory missing"
  done <<< "$service_files"
else
  fail "${PKG}/aws: no service module found"
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
    --dep boto3 boto3-stubs)
else
  fail "pyproject.toml missing"
fi

# config.py has aws_region
if [[ -f "${PKG}/config.py" ]]; then
  grep -q 'aws_region' "${PKG}/config.py" \
    && ok "config.py: aws_region field" || fail "config.py: aws_region field missing"
else
  fail "${PKG}/config.py missing"
fi

emit_result "06-aws"
