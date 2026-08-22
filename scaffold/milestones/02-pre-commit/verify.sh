#!/usr/bin/env bash
# shellcheck disable=SC1091,SC2015,SC2250,SC2310
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../scripts/verify-lib.sh
source "$SCRIPT_DIR/../../scripts/verify-lib.sh"

# .pre-commit-config.yaml
if [[ -f .pre-commit-config.yaml ]]; then
  ok ".pre-commit-config.yaml exists"
  grep -q 'ruff-pre-commit' .pre-commit-config.yaml \
    && ok "pre-commit: ruff hook" || fail "pre-commit: ruff-pre-commit hook missing"
  grep -q 'yamllint' .pre-commit-config.yaml \
    && ok "pre-commit: yamllint hook" || fail "pre-commit: yamllint hook missing"
  grep -q 'shellcheck' .pre-commit-config.yaml \
    && ok "pre-commit: shellcheck hook" || fail "pre-commit: shellcheck hook missing"
  grep -q 'actionlint' .pre-commit-config.yaml \
    && ok "pre-commit: actionlint hook" || fail "pre-commit: actionlint hook missing"
  grep -q 'conventional-pre-commit' .pre-commit-config.yaml \
    && ok "pre-commit: conventional-pre-commit hook" || fail "pre-commit: conventional-pre-commit hook missing"
  grep -q 'pyright' .pre-commit-config.yaml \
    && ok "pre-commit: pyright local hook" || fail "pre-commit: pyright local hook missing"
  if grep -q 'rev: <latest>' .pre-commit-config.yaml; then
    fail "pre-commit: unresolved <latest> placeholders — autoupdate not run"
  else
    ok "pre-commit: all revs resolved"
  fi
else
  fail ".pre-commit-config.yaml missing"
fi

# mise.toml has pre-commit
if [[ -f mise.toml ]]; then
  grep -q 'pre-commit' mise.toml \
    && ok "mise.toml: pre-commit tool" || fail "mise.toml: pre-commit missing"
else
  fail "mise.toml missing"
fi

# justfile
if [[ -f justfile ]]; then
  grep -q 'pre-commit run --all-files' justfile \
    && ok "justfile: lint delegates to pre-commit" || fail "justfile: lint recipe does not call pre-commit run --all-files"
  grep -q '^hooks:' justfile \
    && ok "justfile: hooks recipe" || fail "justfile: hooks recipe missing"
else
  fail "justfile missing"
fi

emit_result "02-pre-commit"
