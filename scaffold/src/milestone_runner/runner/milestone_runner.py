from __future__ import annotations

from dataclasses import dataclass

from milestone_runner.events.run_logger import RunLogger
from milestone_runner.milestone import Milestone, MilestoneConfig, MilestoneState
from milestone_runner.models import AttemptResult, VerifyResult
from milestone_runner.run_context import RunContext
from milestone_runner.runner.exhaustion_policy import ExhaustionPolicy
from milestone_runner.runner.fsm import (
    ExhaustionAction,
    MilestoneEvent,
    MilestonePhase,
    next_phase,
)
from milestone_runner.runner.strategy import MilestoneStrategy, select_strategy


@dataclass
class _AttemptLoopResult:
    phase: MilestonePhase
    prior_failures: list[str]


_ACTION_EVENT: dict[ExhaustionAction, MilestoneEvent] = {
    ExhaustionAction.skip: MilestoneEvent.user_skip,
    ExhaustionAction.retry: MilestoneEvent.user_retry,
    ExhaustionAction.abort: MilestoneEvent.user_abort,
}


class _MilestoneRun:
    """Drives a single milestone: attempt loop, exhaustion handling, finalization."""

    def __init__(
        self,
        milestone: Milestone,
        strategy: MilestoneStrategy,
        log: RunLogger,
        ctx: RunContext,
        state: MilestoneState,
        timeout: int,
        exhaustion_policy: ExhaustionPolicy,
    ) -> None:
        self._milestone = milestone
        self._strategy = strategy
        self._log = log
        self._ctx = ctx
        self._state = state
        self._timeout = timeout
        self._exhaustion_policy = exhaustion_policy

    def execute(self) -> int:
        """Run the attempt loop; handle exhaustion if needed. Returns 0/1."""
        loop = self._run_attempt_loop()
        if loop.phase == MilestonePhase.exhausted:
            return self._handle_exhaustion(loop.prior_failures)
        return 0

    def _run_attempt_loop(self) -> _AttemptLoopResult:
        prior_failures: list[str] = []
        phase = MilestonePhase.pending

        for n in range(1, self._strategy.max_attempts + 1):
            label = self._strategy.attempt_label(n)
            phase = self._log_attempt_started(n, label, phase)

            result = self._strategy.attempt(n, prior_failures or None, hint=None)
            self._log.agent_output(result.output)

            if not result.dispatch_ok:
                prior_failures, phase = self._handle_dispatch_failure(n, result, phase)
                continue

            verify_result = self._verify_and_log()
            passed, prior_failures, phase = self._handle_verify_result(
                n, result, verify_result, phase
            )
            if passed:
                break

        return _AttemptLoopResult(phase=phase, prior_failures=prior_failures)

    def _log_attempt_started(self, n: int, label: str, phase: MilestonePhase) -> MilestonePhase:
        self._log.milestone_started(self._milestone.name, n, label)
        print(f"[{self._milestone.name}] attempt {n} …", flush=True)
        print(f"[{self._milestone.name}] {label}", flush=True)
        return next_phase(phase, MilestoneEvent.started)

    def _handle_dispatch_failure(
        self,
        n: int,
        result: AttemptResult,
        phase: MilestonePhase,
    ) -> tuple[list[str], MilestonePhase]:
        if result.timed_out:
            self._log.milestone_timeout(self._timeout)

        failures = result.failures or ["dispatch failed"]
        self._log.milestone_failed(self._milestone.name, n, failures)
        print(f"[{self._milestone.name}] attempt {n} failed — {len(failures)} check(s)\n")

        event = (
            MilestoneEvent.attempts_exhausted
            if n == self._strategy.max_attempts
            else MilestoneEvent.verify_failed
        )
        return failures, next_phase(phase, event)

    def _handle_verify_result(
        self,
        n: int,
        result: AttemptResult,
        verify_result: VerifyResult,
        phase: MilestonePhase,
    ) -> tuple[bool, list[str], MilestonePhase]:
        if verify_result.exit_code == 0:
            self._finalize_completed(n, result.notes, label=self._strategy.pass_label)
            return True, [], next_phase(phase, MilestoneEvent.verify_passed)

        prior_failures = verify_result.failures
        self._log.milestone_failed(self._milestone.name, n, prior_failures)
        print(f"[{self._milestone.name}] attempt {n} failed — {len(prior_failures)} check(s)\n")
        phase = next_phase(
            phase,
            MilestoneEvent.attempts_exhausted
            if n == self._strategy.max_attempts
            else MilestoneEvent.verify_failed,
        )
        return False, prior_failures, phase

    def _handle_exhaustion(self, prior_failures: list[str]) -> int:
        action, hint = self._exhaustion_policy.prompt(self._milestone, prior_failures)
        phase = next_phase(MilestonePhase.exhausted, _ACTION_EVENT[action])

        if phase == MilestonePhase.skipped:
            self._finalize_skip()
            return 0

        if phase == MilestonePhase.running:
            result = self._run_hint_attempt(prior_failures, hint)
            if result.dispatch_ok and self._verify_and_finalize(result):
                return 0

        self._abort()
        return 1

    def _run_hint_attempt(self, prior_failures: list[str], hint: str | None) -> AttemptResult:
        hint_attempt = self._strategy.max_attempts + 1
        label = self._strategy.attempt_label(hint_attempt)
        self._log.milestone_started(self._milestone.name, hint_attempt, label)
        print(f"[{self._milestone.name}] hint retry …", flush=True)
        result = self._strategy.attempt(hint_attempt, prior_failures, hint)
        self._log.agent_output(result.output)
        return result

    def _verify_and_finalize(self, result: AttemptResult) -> bool:
        hint_attempt = self._strategy.max_attempts + 1
        verify_result = self._verify_and_log()
        event = (
            MilestoneEvent.verify_passed
            if verify_result.exit_code == 0
            else MilestoneEvent.verify_failed
        )
        phase = next_phase(MilestonePhase.exhausted, event)
        if phase == MilestonePhase.passed:
            self._finalize_completed(hint_attempt, result.notes, label=self._strategy.pass_label)
            return True
        return False

    def _abort(self) -> None:
        self._log.milestone_agent_exhausted(self._milestone.name)
        self._log.run_aborted(self._milestone.name)
        print(f"ERROR: milestone {self._milestone.name} failed. Aborting.")

    def _verify_and_log(self) -> VerifyResult:
        verify_result = self._milestone.run_verify(
            self._ctx.project_dir,
            self._ctx.project_name,
            timeout=self._timeout,
        )
        for line in verify_result.raw.splitlines():
            if line.startswith(("PASS:", "FAIL:", "Running:")):
                print(line)
        self._log.verify_result(self._milestone.name, verify_result.exit_code, verify_result.parsed)
        return verify_result

    def _finalize_completed(self, attempt: int, notes: list[str], label: str = "PASSED") -> None:
        self._milestone.record_completion(self._state, notes)
        self._log.milestone_completed(self._milestone.name, attempt, notes)
        print(f"[{self._milestone.name}] {label}\n")

    def _finalize_skip(self) -> None:
        self._milestone.record_completion(self._state, ["skipped by user"])
        self._log.milestone_skipped(self._milestone.name, reason="user decision")
        print(f"[{self._milestone.name}] skipped by user\n")


class MilestoneRunner:
    """Orchestrates the milestone loop: strategy selection, attempt loop, exhaustion handling."""

    def __init__(
        self,
        ctx: RunContext,
        log: RunLogger,
        timeout: int,
        non_interactive: bool,
    ) -> None:
        self._ctx = ctx
        self._log = log
        self._timeout = timeout
        self._state = MilestoneState(ctx.project_dir)
        self._milestone_config = MilestoneConfig.load(ctx.plugin_dir)
        self._exhaustion_policy = ExhaustionPolicy(non_interactive)

    def run(self) -> int:
        """Run all milestones in order; return 0 on success, 1 on first failure."""
        self._log_run_started()
        milestones = [
            Milestone.load(name, self._milestone_config, self._ctx.plugin_dir)
            for name in self._ctx.milestones
        ]

        for milestone in milestones:
            if milestone.is_complete(self._state):
                self._skip_completed(milestone)
                continue

            if not milestone.directory.exists():
                print(f"ERROR: milestone directory not found: {milestone.directory}")
                self._log.run_aborted(milestone.name)
                return 1

            rc = _MilestoneRun(
                milestone,
                select_strategy(milestone, self._ctx, self._state, self._timeout),
                self._log,
                self._ctx,
                self._state,
                self._timeout,
                self._exhaustion_policy,
            ).execute()
            if rc != 0:
                return rc

        self._log_run_completed()
        return 0

    def _log_run_started(self) -> None:
        self._log.run_started(self._ctx.project_name, self._ctx.milestones)
        print(f"Project:    {self._ctx.project_dir}")
        print(f"Milestones: {', '.join(self._ctx.milestones)}")
        print()

    def _log_run_completed(self) -> None:
        self._log.run_completed(self._ctx.project_name)
        print("Done. All milestones complete.")

    def _skip_completed(self, milestone: Milestone) -> None:
        next_phase(MilestonePhase.pending, MilestoneEvent.already_done)
        print(f"[{milestone.name}] skipped (already complete)")
        self._log.milestone_skipped(milestone.name)
