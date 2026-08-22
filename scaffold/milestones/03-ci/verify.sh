#!/usr/bin/env bash
# shellcheck disable=SC1091,SC2015,SC2250,SC2310
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../scripts/verify-lib.sh
source "$SCRIPT_DIR/../../scripts/verify-lib.sh"

# ci.yml
if [[ -f .github/workflows/ci.yml ]]; then
  ok ".github/workflows/ci.yml exists"
  grep -q 'mise-action' .github/workflows/ci.yml \
    && ok "ci.yml: jdx/mise-action" || fail "ci.yml: jdx/mise-action missing"
  grep -q 'pre-commit' .github/workflows/ci.yml \
    && ok "ci.yml: pre-commit step" || fail "ci.yml: pre-commit step missing"
  grep -q 'type-check\|type_check' .github/workflows/ci.yml \
    && ok "ci.yml: type-check step" || fail "ci.yml: type-check step missing"
  grep -q 'just test' .github/workflows/ci.yml \
    && ok "ci.yml: test step" || fail "ci.yml: test step missing"
  grep -q 'cache/uv\|\.cache/uv' .github/workflows/ci.yml \
    && ok "ci.yml: uv cache" || fail "ci.yml: uv cache missing"
else
  fail ".github/workflows/ci.yml missing"
fi

# dependabot.yml
if [[ -f .github/dependabot.yml ]]; then
  ok ".github/dependabot.yml exists"
  count=$(grep -c 'open-pull-requests-limit: 0' .github/dependabot.yml || true)
  [[ $count -ge 2 ]] \
    && ok "dependabot.yml: open-pull-requests-limit: 0 on both ecosystems" \
    || fail "dependabot.yml: open-pull-requests-limit: 0 missing (found ${count}, need 2)"
else
  fail ".github/dependabot.yml missing"
fi

# renovate.json
if [[ -f .github/renovate.json ]]; then
  ok ".github/renovate.json exists"
  grep -q 'config:recommended' .github/renovate.json \
    && ok "renovate.json: config:recommended" || fail "renovate.json: config:recommended missing"
else
  fail ".github/renovate.json missing"
fi

emit_result "03-ci"
