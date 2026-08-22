from __future__ import annotations

from milestone_runner.agent import invoke_agent
from milestone_runner.milestone import Milestone, MilestoneState
from milestone_runner.models import AttemptResult
from milestone_runner.prompt_builder import PromptBuilder
from milestone_runner.run_context import RunContext

_MAX_RETRIES = 2


class AgentMilestoneStrategy:
    """Runs a milestone by invoking a Claude agent subprocess with per-attempt prompt escalation."""

    max_attempts: int = _MAX_RETRIES + 1
    pass_label: str = "PASSED"

    def __init__(
        self,
        milestone: Milestone,
        ctx: RunContext,
        state: MilestoneState,
        timeout: int,
    ) -> None:
        self._milestone = milestone
        self._ctx = ctx
        self._state = state
        self._timeout = timeout

    def attempt_label(self, n: int) -> str:
        """Return the model name selected for attempt n."""
        return self._milestone.model_for_attempt(n)

    def attempt(
        self,
        n: int,
        prior_failures: list[str] | None,
        hint: str | None,
    ) -> AttemptResult:
        failures = list(prior_failures) if prior_failures else []
        if hint:
            failures.append(f"User hint: {hint}")

        prompt = PromptBuilder(self._ctx).build(
            self._milestone, failures or None, self._state.load_summary()
        )
        model = self.attempt_label(n)
        invocation = invoke_agent(prompt, self._timeout, model, self._ctx.project_dir)
        if invocation.rc != 0:
            print(f"[{self._milestone.name}] agent exited {invocation.rc}")

        return AttemptResult(
            dispatch_ok=True,
            notes=invocation.result.notes if invocation.result else [],
            failures=[],
            output=invocation.output,
        )
