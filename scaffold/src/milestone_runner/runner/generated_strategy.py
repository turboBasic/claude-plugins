from __future__ import annotations

from milestone_runner.agent import invoke_generate
from milestone_runner.milestone import Milestone
from milestone_runner.models import AttemptResult
from milestone_runner.run_context import RunContext

GENERATE_SCRIPT = "generate.py"


class GeneratedMilestoneStrategy:
    """Runs a milestone by executing a deterministic generate.py script; no LLM involved."""

    max_attempts: int = 1
    pass_label: str = "GENERATED"

    def __init__(
        self,
        milestone: Milestone,
        ctx: RunContext,
        timeout: int,
    ) -> None:
        self._milestone = milestone
        self._generate_py = milestone.directory / GENERATE_SCRIPT
        self._ctx = ctx
        self._timeout = timeout

    def attempt_label(self, n: int) -> str:
        """Always returns 'generate'; generate.py has no model selection."""
        return "generate"

    def attempt(
        self,
        n: int,
        prior_failures: list[str] | None,
        hint: str | None,
    ) -> AttemptResult:
        if hint:
            print(f"[{self._milestone.name}] hint (apply manually, then re-run): {hint}")

        invocation = invoke_generate(self._generate_py, self._ctx.project_dir, self._timeout)

        if invocation.rc != 0:
            timed_out = "TIMEOUT" in invocation.output
            if not timed_out:
                print(invocation.output)
            first_line = (
                invocation.output.splitlines()[0]
                if invocation.output
                else f"{GENERATE_SCRIPT} failed"
            )
            return AttemptResult(
                dispatch_ok=False,
                notes=[],
                failures=[first_line],
                output=invocation.output,
                timed_out=timed_out,
            )

        return AttemptResult(
            dispatch_ok=True,
            notes=invocation.result.notes if invocation.result else [],
            failures=[],
            output=invocation.output,
        )
