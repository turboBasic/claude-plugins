from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from milestone_runner.models import AttemptResult

if TYPE_CHECKING:
    from milestone_runner.milestone import Milestone, MilestoneState
    from milestone_runner.run_context import RunContext


class MilestoneStrategy(Protocol):
    """Protocol for milestone execution strategies; defines how attempts are dispatched."""

    max_attempts: int
    pass_label: str

    def attempt_label(self, n: int) -> str:
        """Return the label logged for attempt n (e.g. model name or 'generate')."""
        ...

    def attempt(
        self,
        n: int,
        prior_failures: list[str] | None,
        hint: str | None,
    ) -> AttemptResult: ...


def select_strategy(
    milestone: Milestone,
    ctx: RunContext,
    state: MilestoneState,
    timeout: int,
) -> MilestoneStrategy:
    """Return the appropriate strategy for the milestone type (generated vs agent)."""
    from milestone_runner.runner.agent_strategy import AgentMilestoneStrategy
    from milestone_runner.runner.generated_strategy import GeneratedMilestoneStrategy

    if milestone.entry.type == "generated":
        return GeneratedMilestoneStrategy(milestone=milestone, ctx=ctx, timeout=timeout)
    return AgentMilestoneStrategy(milestone=milestone, ctx=ctx, state=state, timeout=timeout)
