from __future__ import annotations

from unittest.mock import patch

import pytest

from milestone_runner.milestone import Milestone, MilestoneConfig
from milestone_runner.models import AgentInvocation, AgentResult
from milestone_runner.runner.generated_strategy import GeneratedMilestoneStrategy

_RESULT = AgentResult(status="done", milestone="01-scaffold", notes=["scaffolded"])
_INV_OK = AgentInvocation(
    rc=0,
    output='{"status":"done","milestone":"01-scaffold","notes":["scaffolded"]}',
    result=_RESULT,
)
_INV_FAIL = AgentInvocation(rc=1, output="something went wrong", result=None)
_INV_TIMEOUT = AgentInvocation(
    rc=1, output="TIMEOUT: generate.py did not complete within 60s", result=None
)


@pytest.fixture
def strategy(make_run_context) -> GeneratedMilestoneStrategy:
    ctx = make_run_context("01-scaffold")
    config = MilestoneConfig.load(ctx.plugin_dir)
    milestone = Milestone.load("01-scaffold", config, ctx.plugin_dir)
    return GeneratedMilestoneStrategy(milestone=milestone, ctx=ctx, timeout=60)


def test_attempt_dispatch_ok_on_success(strategy) -> None:
    with patch(
        "milestone_runner.runner.generated_strategy.invoke_generate",
        return_value=_INV_OK,
    ):
        result = strategy.attempt(1, prior_failures=None, hint=None)
    assert result.dispatch_ok is True
    assert result.notes == ["scaffolded"]
    assert result.timed_out is False


def test_attempt_dispatch_not_ok_on_nonzero_exit(strategy) -> None:
    with patch(
        "milestone_runner.runner.generated_strategy.invoke_generate",
        return_value=_INV_FAIL,
    ):
        result = strategy.attempt(1, prior_failures=None, hint=None)
    assert result.dispatch_ok is False
    assert result.timed_out is False
    assert result.failures == ["something went wrong"]
    assert result.output == "something went wrong"


def test_attempt_timed_out_flag(strategy) -> None:
    with patch(
        "milestone_runner.runner.generated_strategy.invoke_generate",
        return_value=_INV_TIMEOUT,
    ):
        result = strategy.attempt(1, prior_failures=None, hint=None)
    assert result.dispatch_ok is False
    assert result.timed_out is True
    assert result.failures == ["TIMEOUT: generate.py did not complete within 60s"]


def test_attempt_label_always_generate(strategy) -> None:
    assert strategy.attempt_label(1) == "generate"
    assert strategy.attempt_label(99) == "generate"


def test_max_attempts_is_one() -> None:
    assert GeneratedMilestoneStrategy.max_attempts == 1


def test_hint_printed_not_injected(strategy, capsys) -> None:
    with patch(
        "milestone_runner.runner.generated_strategy.invoke_generate",
        return_value=_INV_OK,
    ):
        strategy.attempt(1, prior_failures=None, hint="run uv sync")
    out = capsys.readouterr().out
    assert "run uv sync" in out
