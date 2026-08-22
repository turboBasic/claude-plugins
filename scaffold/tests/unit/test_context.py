from __future__ import annotations

from pathlib import Path

import pytest

from milestone_runner.prompt_builder import MILESTONES_DIR
from milestone_runner.run_context import RunContext

_MILESTONE_NAMES = [
    "01-scaffold",
    "02-pre-commit",
    "03-ci",
    "04-config",
    "05-http",
    "06-aws",
    "07-tests",
]

_OPTIONAL_MILESTONES = {"06-aws"}


def _seed_milestones(plugin_dir: Path) -> None:
    ms_dir = plugin_dir / MILESTONES_DIR
    ms_dir.mkdir(parents=True, exist_ok=True)
    for name in _MILESTONE_NAMES:
        d = ms_dir / name
        d.mkdir()
        if name in _OPTIONAL_MILESTONES:
            (d / "milestone.toml").write_text(
                'models = ["haiku", "sonnet", "opus"]\noptional = true\n'
            )


def test_round_trip(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "plugin"
    plugin_dir.mkdir()
    _seed_milestones(plugin_dir)
    ctx = RunContext.create(
        project_name="my-project",
        description="test desc",
        output_dir=tmp_path,
        enable_milestones=[],
        plugin_dir=plugin_dir,
    )
    ctx.save()

    context_path = ctx.project_dir / "agent.context.json"
    assert context_path.exists()

    loaded = RunContext.load(context_path)
    assert loaded.project_name == ctx.project_name
    assert loaded.package_name == "my_project"
    assert loaded.project_dir == ctx.project_dir
    assert loaded.plugin_dir == ctx.plugin_dir
    assert loaded.milestones == ctx.milestones
    assert loaded.enabled_milestones == []


def test_enable_milestones_includes_optional(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "plugin"
    plugin_dir.mkdir()
    _seed_milestones(plugin_dir)
    ctx = RunContext.create("aws-proj", "", tmp_path, ["06-aws"], plugin_dir=plugin_dir)
    assert "06-aws" in ctx.enabled_milestones
    assert "06-aws" in ctx.milestones


def test_no_enable_milestones_excludes_optional(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "plugin"
    plugin_dir.mkdir()
    _seed_milestones(plugin_dir)
    ctx = RunContext.create("plain-proj", "", tmp_path, [], plugin_dir=plugin_dir)
    assert "06-aws" not in ctx.milestones


def test_package_name_normalisation(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "plugin"
    plugin_dir.mkdir()
    _seed_milestones(plugin_dir)
    ctx = RunContext.create("my-cool project", "", tmp_path, [], plugin_dir=plugin_dir)
    assert ctx.package_name == "my_cool_project"


def test_load_context_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        RunContext.load(tmp_path / "nonexistent.json")


@pytest.mark.parametrize("name", ["", ".", "..", "a/b", "a\\b", "../etc", "a/../b"])
def test_invalid_project_name(tmp_path: Path, name: str) -> None:
    with pytest.raises(ValueError):
        RunContext.create(name, "", tmp_path, [], plugin_dir=tmp_path)


def test_run_context_is_pydantic_model() -> None:
    assert issubclass(RunContext, object)
    fields = RunContext.model_fields
    assert "project_name" in fields
    assert "milestones" in fields
