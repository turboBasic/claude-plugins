from __future__ import annotations

import pytest

from milestone_runner.runner.fsm import MilestoneEvent, MilestonePhase, next_phase

P = MilestonePhase
E = MilestoneEvent


@pytest.mark.parametrize(
    "phase,event,expected",
    [
        (P.pending, E.already_done, P.skipped),
        (P.pending, E.started, P.running),
        (P.running, E.started, P.running),
        (P.running, E.verify_passed, P.passed),
        (P.running, E.verify_failed, P.running),
        (P.running, E.attempts_exhausted, P.exhausted),
        (P.exhausted, E.user_skip, P.skipped),
        (P.exhausted, E.user_retry, P.running),
        (P.exhausted, E.user_abort, P.aborted),
        (P.exhausted, E.verify_passed, P.passed),
        (P.exhausted, E.verify_failed, P.aborted),
    ],
)
def test_transitions(
    phase: MilestonePhase, event: MilestoneEvent, expected: MilestonePhase
) -> None:
    assert next_phase(phase, event) == expected


def test_invalid_transition_raises() -> None:
    with pytest.raises(ValueError, match="invalid transition"):
        next_phase(P.passed, E.started)
