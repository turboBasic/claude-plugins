from __future__ import annotations

from milestone_runner.milestone.verify import parse_verify_output


def test_valid_json_all_pass() -> None:
    json_line = '{"checks": [{"name": "pyproject_exists", "ok": true}], "passed": 1, "failed": 0}'
    raw = f"Running: checks\n{json_line}"
    result = parse_verify_output(0, raw)
    assert result.exit_code == 0
    assert result.parsed is not None
    assert result.failures == []
    assert len(result.checks) == 1
    assert result.checks[0].ok is True


def test_valid_json_with_failures() -> None:
    raw = (
        '{"checks": [{"name": "src_exists", "ok": true}, {"name": "pyproject_valid", "ok": false}]}'
    )
    result = parse_verify_output(1, raw)
    assert result.exit_code == 1
    assert "pyproject_valid" in result.failures
    assert "src_exists" not in result.failures


def test_fallback_fail_lines() -> None:
    raw = "Running checks\nPASS: file exists\nFAIL: missing pyproject.toml\nFAIL: missing src/"
    result = parse_verify_output(1, raw)
    assert result.parsed is None
    assert len(result.failures) == 2
    assert "FAIL: missing pyproject.toml" in result.failures
    assert "FAIL: missing src/" in result.failures


def test_empty_input() -> None:
    result = parse_verify_output(0, "")
    assert result.parsed is None
    assert result.failures == []
    assert result.checks == []


def test_broken_json_falls_back() -> None:
    raw = "{not valid json}\nFAIL: something broke"
    result = parse_verify_output(1, raw)
    assert result.parsed is None
    assert "FAIL: something broke" in result.failures


def test_last_json_line_wins() -> None:
    raw = (
        'some output\n{"checks": [{"name": "a", "ok": false}]}\n'
        '{"checks": [{"name": "b", "ok": true}]}'
    )
    result = parse_verify_output(0, raw)
    assert result.parsed is not None
    assert len(result.checks) == 1
    assert result.checks[0].name == "b"
