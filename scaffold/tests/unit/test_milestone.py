from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from milestone_runner.milestone import (
    DEFAULT_MODELS,
    Milestone,
    MilestoneConfig,
    MilestoneEntry,
    MilestoneState,
)
from milestone_runner.models import VerifyResult


def _make_entry(name: str = "01-scaffold", type_: str = "agent") -> MilestoneEntry:
    return MilestoneEntry(name=name, models=DEFAULT_MODELS, type=type_, optional=False)


def _make_milestone(tmp_path: Path, name: str = "01-scaffold") -> Milestone:
    directory = tmp_path / "milestones" / name
    directory.mkdir(parents=True)
    return Milestone(name=name, entry=_make_entry(name), directory=directory)


def test_short_name() -> None:
    m = Milestone(name="01-scaffold", entry=_make_entry(), directory=Path("/x"))
    assert m.short_name == "scaffold"


def test_model_for_attempt_clamps_to_last() -> None:
    m = Milestone(name="01-scaffold", entry=_make_entry(), directory=Path("/x"))
    assert m.model_for_attempt(1) == "haiku"
    assert m.model_for_attempt(2) == "sonnet"
    assert m.model_for_attempt(3) == "opus"
    assert m.model_for_attempt(99) == "opus"


def test_is_complete_false_when_not_recorded(tmp_path: Path) -> None:
    m = _make_milestone(tmp_path)
    state = MilestoneState(tmp_path / "project")
    (tmp_path / "project").mkdir()
    assert m.is_complete(state) is False


def test_is_complete_true_after_record(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    m = _make_milestone(tmp_path)
    state = MilestoneState(project_dir)
    m.record_completion(state, ["done"])
    assert m.is_complete(state) is True


def test_record_completion_uses_short_name_as_key(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    m = _make_milestone(tmp_path)
    state = MilestoneState(project_dir)
    m.record_completion(state, ["note"])
    assert "scaffold" in state.completed()


def test_run_verify_delegates_to_verify_module(tmp_path: Path) -> None:
    m = _make_milestone(tmp_path)
    fake_result = VerifyResult(exit_code=0, raw="", failures=[])
    _TARGET = "milestone_runner.milestone.core.run_verify"
    with patch(_TARGET, return_value=fake_result) as mock_verify:
        result = m.run_verify(tmp_path / "project", "myapp", timeout=30)
    mock_verify.assert_called_once_with(m.directory, tmp_path / "project", "myapp", 30)
    assert result is fake_result


def test_load_uses_config_entry(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "plugin"
    ms_dir = plugin_dir / "milestones" / "01-scaffold"
    ms_dir.mkdir(parents=True)
    (ms_dir / "milestone.toml").write_text('models = ["sonnet"]\n')
    config = MilestoneConfig.load(plugin_dir)
    m = Milestone.load("01-scaffold", config, plugin_dir)
    assert m.name == "01-scaffold"
    assert m.directory == ms_dir
    assert m.entry.models == ["sonnet"]


def test_load_falls_back_to_defaults_for_unknown_milestone(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "plugin"
    (plugin_dir / "milestones").mkdir(parents=True)
    config = MilestoneConfig.load(plugin_dir)
    m = Milestone.load("99-unknown", config, plugin_dir)
    assert m.entry.models == DEFAULT_MODELS
    assert m.entry.type == "agent"
