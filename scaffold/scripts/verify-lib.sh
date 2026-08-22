#!/usr/bin/env bash
# Sourced by all milestone verify scripts.
# ok()/fail() accumulate JSON checks; emit_result() writes JSON to stdout and exits.
# Human-readable PASS/FAIL lines go to stderr.

_VL_CHECKS=""
FAIL=0

_vl_json_str() {
    local s="${*//\\/\\\\}"
    s="${s//\"/\\\"}"
    printf '"%s"' "${s}"
}

ok() {
    local msg="$*"
    local entry
    entry="{\"name\":$(_vl_json_str "${msg}"),\"ok\":true}"
    _VL_CHECKS="${_VL_CHECKS:+${_VL_CHECKS},}${entry}"
    echo "PASS: ${msg}" >&2
}

fail() {
    local msg="$*"
    local entry
    entry="{\"name\":$(_vl_json_str "${msg}"),\"ok\":false}"
    _VL_CHECKS="${_VL_CHECKS:+${_VL_CHECKS},}${entry}"
    FAIL=1
    echo "FAIL: ${msg}" >&2
}

emit_result() {
    local milestone="${1:-unknown}"
    local passed="false"
    [[ ${FAIL} -eq 0 ]] && passed="true"
    local milestone_json
    milestone_json="$(_vl_json_str "${milestone}")"
    printf '{"milestone":%s,"passed":%s,"checks":[%s]}\n' \
        "${milestone_json}" "${passed}" "${_VL_CHECKS}"
    [[ ${FAIL} -eq 0 ]] && exit 0 || exit 1
}
