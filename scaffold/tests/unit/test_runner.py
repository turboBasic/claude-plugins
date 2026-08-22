from __future__ import annotations

from unittest.mock import patch

from milestone_runner.milestone import MilestoneState
from milestone_runner.models import AgentInvocation, AgentResult, VerifyResult
from milestone_runner.run_context import RunContext
from milestone_runner.runner import MilestoneRunner
from milestone_runner.runner.fsm import ExhaustionAction

_AGENT_RESULT = AgentResult(status="done", milestone="04-config", notes=[])
_AGENT_INV = AgentInvocation(rc=0, output="", result=_AGENT_RESULT)
_PASS = VerifyResult(exit_code=0, raw="", failures=[])
_FAIL = VerifyResult(exit_code=1, raw="FAIL: something", failures=["something"])


# ── agent path ───────────────────────────────────────────────────────────────


def test_agent_passed_first_attempt(make_run_context, make_event_log) -> None:
    ctx = make_run_context()
    log = make_event_log()
    with (
        patch(
            "milestone_runner.runner.agent_strategy.invoke_agent",
            return_value=_AGENT_INV,
        ),
        patch("milestone_runner.milestone.core.run_verify", return_value=_PASS),
    ):
        rc = MilestoneRunner(ctx, log, timeout=60, non_interactive=True).run()
    assert rc == 0
    assert "config" in MilestoneState(ctx.project_dir).completed()


def test_agent_passed_on_retry(make_run_context, make_event_log) -> None:
    ctx = make_run_context()
    log = make_event_log()
    verify_results = [_FAIL, _PASS]
    with (
        patch(
            "milestone_runner.runner.agent_strategy.invoke_agent",
            return_value=_AGENT_INV,
        ) as mock_invoke,
        patch(
            "milestone_runner.milestone.core.run_verify",
            side_effect=verify_results,
        ),
    ):
        rc = MilestoneRunner(ctx, log, timeout=60, non_interactive=True).run()
    assert rc == 0
    assert mock_invoke.call_count == 2
    assert "config" in MilestoneState(ctx.project_dir).completed()


def test_agent_exhaustion_abort_non_interactive(make_run_context, make_event_log) -> None:
    ctx = make_run_context()
    log = make_event_log()
    with (
        patch(
            "milestone_runner.runner.agent_strategy.invoke_agent",
            return_value=_AGENT_INV,
        ),
        patch("milestone_runner.milestone.core.run_verify", return_value=_FAIL),
    ):
        rc = MilestoneRunner(ctx, log, timeout=60, non_interactive=True).run()
    assert rc == 1
    assert "config" not in MilestoneState(ctx.project_dir).completed()


def test_agent_exhaustion_skip(make_run_context, make_event_log) -> None:
    ctx = make_run_context()
    log = make_event_log()
    with (
        patch(
            "milestone_runner.runner.agent_strategy.invoke_agent",
            return_value=_AGENT_INV,
        ),
        patch("milestone_runner.milestone.core.run_verify", return_value=_FAIL),
        patch(
            "milestone_runner.runner.exhaustion_policy.ExhaustionPolicy.prompt",
            return_value=(ExhaustionAction.skip, None),
        ),
    ):
        rc = MilestoneRunner(ctx, log, timeout=60, non_interactive=False).run()
    assert rc == 0
    assert "config" in MilestoneState(ctx.project_dir).completed()


def test_agent_exhaustion_retry_hint_passes(make_run_context, make_event_log) -> None:
    ctx = make_run_context()
    log = make_event_log()
    with (
        patch(
            "milestone_runner.runner.agent_strategy.invoke_agent",
            return_value=_AGENT_INV,
        ),
        patch(
            "milestone_runner.milestone.core.run_verify",
            side_effect=[_FAIL, _FAIL, _FAIL, _PASS],
        ),
        patch(
            "milestone_runner.runner.exhaustion_policy.ExhaustionPolicy.prompt",
            return_value=(ExhaustionAction.retry, "fix it"),
        ),
    ):
        rc = MilestoneRunner(ctx, log, timeout=60, non_interactive=False).run()
    assert rc == 0
    assert "config" in MilestoneState(ctx.project_dir).completed()


def test_agent_exhaustion_retry_hint_fails(make_run_context, make_event_log) -> None:
    ctx = make_run_context()
    log = make_event_log()
    with (
        patch(
            "milestone_runner.runner.agent_strategy.invoke_agent",
            return_value=_AGENT_INV,
        ),
        patch("milestone_runner.milestone.core.run_verify", return_value=_FAIL),
        patch(
            "milestone_runner.runner.exhaustion_policy.ExhaustionPolicy.prompt",
            return_value=(ExhaustionAction.retry, "fix it"),
        ),
    ):
        rc = MilestoneRunner(ctx, log, timeout=60, non_interactive=False).run()
    assert rc == 1
    assert "config" not in MilestoneState(ctx.project_dir).completed()


# ── generate path ─────────────────────────────────────────────────────────────


def _add_generate_py(ctx: RunContext, milestone: str, exit_code: int = 0) -> None:
    ms_dir = ctx.plugin_dir / "milestones" / milestone
    payload = f'{{"status":"done","milestone":"{milestone}","notes":[]}}'
    body = f"import sys\nprint({payload!r})\nsys.exit({exit_code})\n"
    (ms_dir / "generate.py").write_text(body)
    (ms_dir / "milestone.toml").write_text('type = "generated"\n')


def test_generate_success(make_run_context, make_event_log) -> None:
    milestone = "01-scaffold"
    ctx = make_run_context(milestone)
    log = make_event_log()
    _add_generate_py(ctx, milestone)
    with patch("milestone_runner.milestone.core.run_verify", return_value=_PASS):
        rc = MilestoneRunner(ctx, log, timeout=60, non_interactive=True).run()
    assert rc == 0
    assert "scaffold" in MilestoneState(ctx.project_dir).completed()


def test_generate_nonzero_exit_aborts(make_run_context, make_event_log) -> None:
    milestone = "01-scaffold"
    ctx = make_run_context(milestone)
    log = make_event_log()
    _add_generate_py(ctx, milestone, exit_code=1)
    rc = MilestoneRunner(ctx, log, timeout=60, non_interactive=True).run()
    assert rc == 1
    assert "scaffold" not in MilestoneState(ctx.project_dir).completed()


def test_generate_failure_abort(make_run_context, make_event_log) -> None:
    milestone = "01-scaffold"
    ctx = make_run_context(milestone)
    log = make_event_log()
    _add_generate_py(ctx, milestone)
    with patch("milestone_runner.milestone.core.run_verify", return_value=_FAIL):
        rc = MilestoneRunner(ctx, log, timeout=60, non_interactive=True).run()
    assert rc == 1
    assert "scaffold" not in MilestoneState(ctx.project_dir).completed()


def test_generate_failure_skip(make_run_context, make_event_log) -> None:
    milestone = "01-scaffold"
    ctx = make_run_context(milestone)
    log = make_event_log()
    _add_generate_py(ctx, milestone)
    with (
        patch("milestone_runner.milestone.core.run_verify", return_value=_FAIL),
        patch(
            "milestone_runner.runner.exhaustion_policy.ExhaustionPolicy.prompt",
            return_value=(ExhaustionAction.skip, None),
        ),
    ):
        rc = MilestoneRunner(ctx, log, timeout=60, non_interactive=False).run()
    assert rc == 0
    assert "scaffold" in MilestoneState(ctx.project_dir).completed()


def test_generate_failure_retry_hint_passes(make_run_context, make_event_log) -> None:
    milestone = "01-scaffold"
    ctx = make_run_context(milestone)
    log = make_event_log()
    _add_generate_py(ctx, milestone)
    with (
        patch(
            "milestone_runner.milestone.core.run_verify",
            side_effect=[_FAIL, _PASS],
        ),
        patch(
            "milestone_runner.runner.exhaustion_policy.ExhaustionPolicy.prompt",
            return_value=(ExhaustionAction.retry, "try again"),
        ),
    ):
        rc = MilestoneRunner(ctx, log, timeout=60, non_interactive=False).run()
    assert rc == 0
    assert "scaffold" in MilestoneState(ctx.project_dir).completed()


def test_generate_failure_retry_hint_fails(make_run_context, make_event_log) -> None:
    milestone = "01-scaffold"
    ctx = make_run_context(milestone)
    log = make_event_log()
    _add_generate_py(ctx, milestone)
    with (
        patch("milestone_runner.milestone.core.run_verify", return_value=_FAIL),
        patch(
            "milestone_runner.runner.exhaustion_policy.ExhaustionPolicy.prompt",
            return_value=(ExhaustionAction.retry, "try again"),
        ),
    ):
        rc = MilestoneRunner(ctx, log, timeout=60, non_interactive=False).run()
    assert rc == 1
    assert "scaffold" not in MilestoneState(ctx.project_dir).completed()


# ── misc paths ────────────────────────────────────────────────────────────────


def test_already_completed_skipped(make_run_context, make_event_log) -> None:
    ctx = make_run_context()
    log = make_event_log()
    (ctx.project_dir / ".milestones.jsonl").write_text('{"milestone": "04-config", "notes": []}\n')
    with patch("milestone_runner.runner.agent_strategy.invoke_agent") as mock_invoke:
        rc = MilestoneRunner(ctx, log, timeout=60, non_interactive=True).run()
    assert rc == 0
    mock_invoke.assert_not_called()


def test_missing_milestone_dir(make_run_context, make_event_log) -> None:
    ctx = make_run_context()
    log = make_event_log()
    import shutil

    shutil.rmtree(ctx.plugin_dir / "milestones" / "04-config")
    rc = MilestoneRunner(ctx, log, timeout=60, non_interactive=True).run()
    assert rc == 1
