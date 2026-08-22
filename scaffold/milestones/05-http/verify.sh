#!/usr/bin/env bash
# shellcheck disable=SC1091,SC2015,SC2250,SC2310
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../scripts/verify-lib.sh
source "$SCRIPT_DIR/../../scripts/verify-lib.sh"

PKG=$(find src -maxdepth 1 -mindepth 1 -type d 2>/dev/null | head -1)
if [[ -z "$PKG" ]]; then
  fail "src/<package> directory missing"
  emit_result "05-http"
fi
ok "src package found: $PKG"

# http directory
if [[ -d "${PKG}/http" ]]; then
  ok "${PKG}/http/ directory exists"
else
  fail "${PKG}/http/ directory missing"
  emit_result "05-http"
fi

# __init__.py
[[ -f "${PKG}/http/__init__.py" ]] \
  && ok "${PKG}/http/__init__.py exists" || fail "${PKG}/http/__init__.py missing"

# models.py
if [[ -f "${PKG}/http/models.py" ]]; then
  ok "${PKG}/http/models.py exists"
  grep -q 'BaseModel' "${PKG}/http/models.py" \
    && ok "models.py: Pydantic BaseModel" || fail "models.py: Pydantic BaseModel missing"
else
  fail "${PKG}/http/models.py missing"
fi

# client.py
if [[ -f "${PKG}/http/client.py" ]]; then
  ok "${PKG}/http/client.py exists"
  grep -q 'httpx' "${PKG}/http/client.py" \
    && ok "client.py: httpx" || fail "client.py: httpx missing"
  grep -q 'AsyncClient' "${PKG}/http/client.py" \
    && ok "client.py: AsyncClient" || fail "client.py: AsyncClient missing"
  grep -q 'asynccontextmanager' "${PKG}/http/client.py" \
    && ok "client.py: asynccontextmanager" || fail "client.py: asynccontextmanager missing"
  grep -q 'tenacity' "${PKG}/http/client.py" \
    && ok "client.py: tenacity" || fail "client.py: tenacity missing"
  grep -q '_retryable' "${PKG}/http/client.py" \
    && ok "client.py: _retryable predicate" || fail "client.py: _retryable predicate missing"
  grep -q 'raise_for_status' "${PKG}/http/client.py" \
    && ok "client.py: raise_for_status" || fail "client.py: raise_for_status missing"
  grep -q 'AppConfig' "${PKG}/http/client.py" \
    && ok "client.py: AppConfig injection" || fail "client.py: AppConfig injection missing"
  grep -q 'structlog' "${PKG}/http/client.py" \
    && ok "client.py: structlog" || fail "client.py: structlog missing"
  grep -q 'Timeout' "${PKG}/http/client.py" \
    && ok "client.py: explicit Timeout" || fail "client.py: explicit Timeout missing"
  grep -qE '^async def fetch' "${PKG}/http/client.py" \
    && ok "client.py: fetch function" || fail "client.py: fetch function missing"
else
  fail "${PKG}/http/client.py missing"
fi

# cli.py wired to async layer
if [[ -f "${PKG}/cli.py" ]]; then
  grep -q 'asyncio' "${PKG}/cli.py" \
    && ok "cli.py: asyncio.run bridge" || fail "cli.py: asyncio.run bridge missing"
else
  fail "${PKG}/cli.py missing"
fi

# no requests or aiohttp anywhere in src
if grep -rlE 'import requests|from requests|import aiohttp|from aiohttp' src/ --include='*.py' 2>/dev/null | grep -q .; then
  fail "src/: requests or aiohttp found — must use httpx"
else
  ok "src/: no requests or aiohttp"
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
    --dep httpx tenacity)
else
  fail "pyproject.toml missing"
fi

emit_result "05-http"
