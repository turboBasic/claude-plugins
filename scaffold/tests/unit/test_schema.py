from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest

from milestone_runner.events.run_log_summary import display_run_log_summary
from milestone_runner.events.schema import (
    RunStarted,
    UnknownEvent,
    parse_line,
)


def _jsonl(path: Path, *events: dict) -> None:
    path.write_text("\n".join(json.dumps(e) for e in events) + "\n")


# --- parse_line ---


def test_parse_line_valid_known_event() -> None:
    line = json.dumps(
        {
            "event": "run_started",
            "timestamp": "2024-01-01T00:00:00Z",
            "project": "my-proj",
            "milestones": ["01-scaffold"],
        }
    )
    result = parse_line(line)
    assert isinstance(result, RunStarted)
    assert result.project == "my-proj"


def test_parse_line_unknown_event_name_is_silent() -> None:
    line = json.dumps({"event": "future_event", "timestamp": "2024-01-01T00:00:00Z"})
    result = parse_line(line)
    assert isinstance(result, UnknownEvent)
    assert result.event == "future_event"


def test_parse_line_known_event_missing_field_warns(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # run_started requires project and milestones — omit both
    line = json.dumps({"event": "run_started", "timestamp": "2024-01-01T00:00:00Z"})
    result = parse_line(line)
    assert result is None
    captured = capsys.readouterr()
    assert "warning" in captured.err
    assert "run_started" in captured.err


def test_parse_line_known_event_wrong_field_type_warns(
    capsys: pytest.CaptureFixture[str],
) -> None:
    line = json.dumps(
        {
            "event": "milestone_started",
            "timestamp": "2024-01-01T00:00:00Z",
            "milestone": "01-scaffold",
            "attempt": "not-an-int",  # should be int
            "model": "haiku",
        }
    )
    result = parse_line(line)
    assert result is None
    assert "warning" in capsys.readouterr().err


def test_parse_line_empty_line_returns_none() -> None:
    assert parse_line("") is None
    assert parse_line("   ") is None


def test_parse_line_invalid_json_returns_none() -> None:
    assert parse_line("{not valid json}") is None


# --- print_summary with malformed line mid-stream ---


def test_print_summary_skips_malformed_line_with_warning(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    log = tmp_path / "test.log.jsonl"
    _jsonl(
        log,
        {
            "event": "run_started",
            "timestamp": "2024-01-01T00:00:00Z",
            "project": "p",
            "milestones": ["01-scaffold"],
        },
        # malformed known event: milestone_started missing attempt/model
        {
            "event": "milestone_started",
            "timestamp": "2024-01-01T00:00:01Z",
            "milestone": "01-scaffold",
        },
        {"event": "run_completed", "timestamp": "2024-01-01T00:01:00Z", "project": "p"},
    )
    display_run_log_summary(log)
    captured = capsys.readouterr()
    assert "warning" in captured.err
    assert "milestone_started" in captured.err
    # summary still completes
    assert "Run:" in captured.out
