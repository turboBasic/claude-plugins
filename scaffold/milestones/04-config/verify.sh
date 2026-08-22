#!/usr/bin/env bash
# shellcheck disable=SC1091,SC2015,SC2250,SC2310
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../scripts/verify-lib.sh
source "$SCRIPT_DIR/../../scripts/verify-lib.sh"

PKG=$(find src -maxdepth 1 -mindepth 1 -type d 2>/dev/null | head -1)
if [[ -z "$PKG" ]]; then
  fail "src/<package> directory missing"
  emit_result "04-config"
fi
ok "src package found: $PKG"

# config.py
if [[ -f "${PKG}/config.py" ]]; then
  ok "${PKG}/config.py exists"
  grep -q 'class AppConfig' "${PKG}/config.py" \
    && ok "config.py: AppConfig class" || fail "config.py: AppConfig class missing"
  grep -q 'BaseModel' "${PKG}/config.py" \
    && ok "config.py: Pydantic BaseModel" || fail "config.py: Pydantic BaseModel missing"
  grep -q 'def load_config' "${PKG}/config.py" \
    && ok "config.py: load_config function" || fail "config.py: load_config function missing"
  grep -q 'log_level' "${PKG}/config.py" \
    && ok "config.py: log_level field" || fail "config.py: log_level field missing"
  if grep -qE 'from dynaconf|import dynaconf' "${PKG}/config.py"; then
    fail "config.py: imports dynaconf (boundary violation — only bootstrap.py may import dynaconf)"
  else
    ok "config.py: no dynaconf import (boundary respected)"
  fi
else
  fail "${PKG}/config.py missing"
fi

# bootstrap.py
if [[ -f "${PKG}/bootstrap.py" ]]; then
  ok "${PKG}/bootstrap.py exists"
  grep -qE 'from dynaconf|import dynaconf' "${PKG}/bootstrap.py" \
    && ok "bootstrap.py: dynaconf import" || fail "bootstrap.py: dynaconf import missing"
  grep -q 'platformdirs' "${PKG}/bootstrap.py" \
    && ok "bootstrap.py: platformdirs (XDG config path)" || fail "bootstrap.py: platformdirs missing"
  grep -q 'load_raw_config' "${PKG}/bootstrap.py" \
    && ok "bootstrap.py: load_raw_config function" || fail "bootstrap.py: load_raw_config function missing"
  grep -q '\.lower()' "${PKG}/bootstrap.py" \
    && ok "bootstrap.py: lowercase key normalisation" || fail "bootstrap.py: load_raw_config must return lowercase keys (Dynaconf returns uppercase; Pydantic silently ignores them)"
else
  fail "${PKG}/bootstrap.py missing"
fi

# dynaconf boundary — no file other than bootstrap.py may import dynaconf
if grep -rlE 'from dynaconf|import dynaconf' src/ | grep -v "${PKG}/bootstrap.py" | grep -q .; then
  violators=$(grep -rlE 'from dynaconf|import dynaconf' src/ | grep -v "${PKG}/bootstrap.py" | tr '\n' ' ')
  fail "dynaconf imported outside bootstrap.py: ${violators}"
else
  ok "dynaconf boundary: only bootstrap.py imports dynaconf"
fi

# config.example.yaml
[[ -f config.example.yaml ]] \
  && ok "config.example.yaml exists" || fail "config.example.yaml missing"

# pyproject.toml dependencies
if [[ -f pyproject.toml ]]; then
  while IFS= read -r line; do
    if [[ "$line" == ok:* ]]; then
      ok "${line#ok: }"
    elif [[ "$line" == fail:* ]]; then
      fail "${line#fail: }"
    fi
  done < <(mise exec -- python "$SCRIPT_DIR/../../scripts/validate_pyproject.py" pyproject.toml \
    --dep dynaconf pydantic platformdirs)
else
  fail "pyproject.toml missing"
fi

# cli.py uses AppConfig
if [[ -f "${PKG}/cli.py" ]]; then
  grep -q 'load_config' "${PKG}/cli.py" \
    && ok "cli.py: calls load_config" || fail "cli.py: load_config call missing"
  grep -q 'AppConfig' "${PKG}/cli.py" \
    && ok "cli.py: AppConfig used" || fail "cli.py: AppConfig not referenced"
else
  fail "${PKG}/cli.py missing"
fi

emit_result "04-config"
