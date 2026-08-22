from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from milestone_runner.events.run_logger import RunLogger
from milestone_runner.prompt_builder import MILESTONE_PROMPT_FILE, MILESTONES_DIR
from milestone_runner.run_context import RunContext


@pytest.fixture
def make_run_context(tmp_path: Path) -> Callable[[str], RunContext]:
    def _make(milestone: str = "04-config") -> RunContext:
        plugin_dir = tmp_path / "plugin"
        ms_dir = plugin_dir / MILESTONES_DIR / milestone
        ms_dir.mkdir(parents=True, exist_ok=True)
        (ms_dir / MILESTONE_PROMPT_FILE).write_text("# config\n")
        (ms_dir / "verify.sh").write_text("#!/bin/bash\nexit 0\n")
        project_dir = tmp_path / "myapp"
        project_dir.mkdir(exist_ok=True)
        return RunContext(
            project_name="myapp",
            package_name="myapp",
            description="test",
            project_dir=project_dir,
            plugin_dir=plugin_dir,
            enabled_milestones=[],
            milestones=[milestone],
        )

    return _make


@pytest.fixture
def make_event_log(tmp_path: Path) -> Callable[[str], RunLogger]:
    def _make(filename: str = "test.log.jsonl") -> RunLogger:
        return RunLogger(tmp_path / filename)

    return _make
