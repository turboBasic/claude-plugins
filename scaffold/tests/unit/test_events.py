from __future__ import annotations

import json
from pathlib import Path


def _read_events(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def test_run_started(make_event_log) -> None:
    log = make_event_log()
    log.run_started("my-proj", ["01-scaffold", "02-pre-commit"])
    events = _read_events(log.path)
    assert len(events) == 1
    assert events[0]["event"] == "run_started"
    assert events[0]["project"] == "my-proj"
    assert events[0]["milestones"] == ["01-scaffold", "02-pre-commit"]
    assert "timestamp" in events[0]


def test_multiple_events_appended(make_event_log) -> None:
    log = make_event_log()
    log.run_started("proj", [])
    log.milestone_started("01-scaffold", 1, "sonnet")
    log.milestone_completed("01-scaffold", 1, ["note1"])
    log.run_completed("proj")
    events = _read_events(log.path)
    assert len(events) == 4
    assert [e["event"] for e in events] == [
        "run_started",
        "milestone_started",
        "milestone_completed",
        "run_completed",
    ]


def test_milestone_failed_event(make_event_log) -> None:
    log = make_event_log()
    log.milestone_failed("01-scaffold", 2, ["FAIL: missing file"])
    events = _read_events(log.path)
    assert events[0]["event"] == "milestone_failed"
    assert events[0]["attempt"] == 2
    assert events[0]["failures"] == ["FAIL: missing file"]


def test_milestone_skipped_without_reason(make_event_log) -> None:
    log = make_event_log()
    log.milestone_skipped("02-pre-commit")
    events = _read_events(log.path)
    assert events[0]["event"] == "milestone_skipped"
    assert "reason" not in events[0]


def test_milestone_skipped_with_reason(make_event_log) -> None:
    log = make_event_log()
    log.milestone_skipped("02-pre-commit", reason="not implemented")
    events = _read_events(log.path)
    assert events[0]["reason"] == "not implemented"


def test_verify_result_event(make_event_log) -> None:
    log = make_event_log()
    result_data: dict[str, object] = {"checks": [], "passed": 1, "failed": 0}
    log.verify_result("01-scaffold", 0, result_data)
    events = _read_events(log.path)
    assert events[0]["exit_code"] == 0
    assert events[0]["result"] == result_data


def test_agent_output_event(make_event_log) -> None:
    log = make_event_log()
    log.agent_output('some output\n{"status": "done", "milestone": "01-scaffold", "notes": []}')
    events = _read_events(log.path)
    assert events[0]["event"] == "agent_output"
    assert "status" in events[0]["output"]  # type: ignore[operator]


def test_events_each_valid_jsonl(make_event_log) -> None:
    log = make_event_log()
    log.run_started("p", ["m1"])
    log.milestone_timeout(300)
    log.milestone_agent_exhausted("01-scaffold")
    log.run_aborted("01-scaffold")
    for line in log.path.read_text().splitlines():
        parsed = json.loads(line)
        assert "timestamp" in parsed
        assert "event" in parsed
