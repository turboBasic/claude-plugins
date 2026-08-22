from __future__ import annotations

from unittest.mock import patch

import pytest

from milestone_runner.milestone import Milestone, MilestoneConfig, MilestoneState
from milestone_runner.models import AgentInvocation, AgentResult
from milestone_runner.runner.agent_strategy import AgentMilestoneStrategy

_RESULT = AgentResult(status="done", milestone="04-config", notes=["n1"])
_INV_OK = AgentInvocation(rc=0, output="ok output", result=_RESULT)
_INV_FAIL = AgentInvocation(rc=1, output="err output", result=None)


@pytest.fixture
def strategy(make_run_context) -> AgentMilestoneStrategy:
    ctx = make_run_context()
    config = MilestoneConfig.load(ctx.plugin_dir)
    milestone = Milestone.load("04-config", config, ctx.plugin_dir)
    return AgentMilestoneStrategy(
        milestone=milestone,
        ctx=ctx,
        state=MilestoneState(ctx.project_dir),
        timeout=60,
    )


def test_attempt_label_returns_model_for_attempt(strategy) -> None:
    assert strategy.attempt_label(1) == "haiku"


def test_attempt_dispatch_ok_always_true(strategy) -> None:
    with patch("milestone_runner.runner.agent_strategy.invoke_agent", return_value=_INV_OK):
        result = strategy.attempt(1, prior_failures=None, hint=None)
    assert result.dispatch_ok is True
    assert result.notes == ["n1"]
    assert result.output == "ok output"


def test_attempt_non_zero_rc_still_dispatch_ok(strategy) -> None:
    with patch("milestone_runner.runner.agent_strategy.invoke_agent", return_value=_INV_FAIL):
        result = strategy.attempt(1, prior_failures=None, hint=None)
    assert result.dispatch_ok is True
    assert result.notes == []
    assert result.output == "err output"


def test_attempt_prior_fails_forwarded_without_hint(strategy) -> None:
    captured: list[str] = []

    def _fake_invoke(prompt: str, *_a, **_kw) -> AgentInvocation:
        captured.append(prompt)
        return _INV_OK

    with patch("milestone_runner.runner.agent_strategy.invoke_agent", side_effect=_fake_invoke):
        strategy.attempt(1, prior_failures=["missing file"], hint=None)

    assert any("missing file" in p for p in captured)
    assert not any("User hint:" in p for p in captured)


def test_attempt_injects_hint_into_fails(strategy) -> None:
    captured: list[str] = []

    def _fake_invoke(prompt: str, *_a, **_kw) -> AgentInvocation:
        captured.append(prompt)
        return _INV_OK

    with patch("milestone_runner.runner.agent_strategy.invoke_agent", side_effect=_fake_invoke):
        strategy.attempt(1, prior_failures=["check failed"], hint="use uv sync")

    assert any("User hint: use uv sync" in p for p in captured)


def test_max_attempts_is_three() -> None:
    assert AgentMilestoneStrategy.max_attempts == 3
