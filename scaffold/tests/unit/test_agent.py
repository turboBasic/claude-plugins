from __future__ import annotations

from pathlib import Path

from milestone_runner.milestone import Milestone, MilestoneConfig
from milestone_runner.models import MilestoneSummary
from milestone_runner.prompt_builder import (
    MILESTONE_PROMPT_FILE,
    MILESTONES_DIR,
    RULES_POST_FILE,
    RULES_PRE_FILE,
    PromptBuilder,
)
from milestone_runner.run_context import RunContext


def _make_ctx(tmp_path: Path) -> RunContext:
    plugin_dir = tmp_path / "plugin"
    milestones_dir = plugin_dir / MILESTONES_DIR
    (milestones_dir / "01-scaffold").mkdir(parents=True)
    (milestones_dir / "01-scaffold" / MILESTONE_PROMPT_FILE).write_text(
        "# scaffold\n\nDo the thing.\n"
    )
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    return RunContext(
        project_name="myapp",
        package_name="myapp",
        description="A test app",
        project_dir=project_dir,
        plugin_dir=plugin_dir,
        enabled_milestones=[],
        milestones=["01-scaffold"],
    )


def _make_milestone(ctx: RunContext) -> Milestone:
    config = MilestoneConfig.load(ctx.plugin_dir)
    return Milestone.load("01-scaffold", config, ctx.plugin_dir)


def test_build_prompt_contains_milestone_content(tmp_path: Path) -> None:
    ctx = _make_ctx(tmp_path)
    prompt = PromptBuilder(ctx).build(_make_milestone(ctx))
    assert "# scaffold" in prompt
    assert "Do the thing." in prompt


def test_build_prompt_contains_project_description(tmp_path: Path) -> None:
    ctx = _make_ctx(tmp_path)
    prompt = PromptBuilder(ctx).build(_make_milestone(ctx))
    assert "Project description: A test app" in prompt


def test_build_prompt_contains_project_name(tmp_path: Path) -> None:
    ctx = _make_ctx(tmp_path)
    prompt = PromptBuilder(ctx).build(_make_milestone(ctx))
    assert "**myapp**" in prompt


def test_build_prompt_prior_fails_included(tmp_path: Path) -> None:
    ctx = _make_ctx(tmp_path)
    prompt = PromptBuilder(ctx).build(_make_milestone(ctx), prior_failures=["uv.lock missing"])
    assert "uv.lock missing" in prompt
    assert "## Failed checks from previous attempt" in prompt


def test_build_prompt_prior_summaries_included(tmp_path: Path) -> None:
    ctx = _make_ctx(tmp_path)
    prompt = PromptBuilder(ctx).build(
        _make_milestone(ctx),
        prior_summaries=[MilestoneSummary(milestone="00-init", notes=["did stuff"])],
    )
    assert "## Prior milestones" in prompt
    assert "**00-init**" in prompt
    assert "did stuff" in prompt


def test_build_prompt_injects_agent_rules_pre_and_post(tmp_path: Path) -> None:
    ctx = _make_ctx(tmp_path)
    rules_dir = ctx.plugin_dir / MILESTONES_DIR
    (rules_dir / RULES_PRE_FILE).write_text("## Global Rules\n\n- Be good.\n")
    (rules_dir / RULES_POST_FILE).write_text(
        "## Before outputting the result, verify\n\n- Check stuff.\n"
    )
    prompt = PromptBuilder(ctx).build(_make_milestone(ctx))
    assert "## Global Rules" in prompt
    assert "Be good." in prompt
    assert "## Before outputting the result, verify" in prompt
    assert "Check stuff." in prompt
    pre_idx = prompt.index("## Global Rules")
    scaffold_idx = prompt.index("# scaffold")
    post_idx = prompt.index("## Before outputting the result, verify")
    assert pre_idx < scaffold_idx < post_idx


def test_build_prompt_separator_before_milestone(tmp_path: Path) -> None:
    ctx = _make_ctx(tmp_path)
    prompt = PromptBuilder(ctx).build(_make_milestone(ctx))
    lines = prompt.splitlines()
    scaffold_idx = next(i for i, line in enumerate(lines) if line.startswith("# scaffold"))
    preceding = [line for line in lines[:scaffold_idx] if line.strip() == "---"]
    assert len(preceding) == 1
