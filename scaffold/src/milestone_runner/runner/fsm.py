from __future__ import annotations

import enum


class ExhaustionAction(enum.Enum):
    """User decision after all retry attempts are consumed."""

    skip = "skip"
    retry = "retry"
    abort = "abort"


class MilestonePhase(enum.Enum):
    """States of the per-milestone FSM."""

    pending = "pending"  # not yet started
    running = "running"  # attempt in progress
    passed = "passed"  # verify succeeded → terminal
    skipped = "skipped"  # already done or user-skipped → terminal
    exhausted = "exhausted"  # all attempts failed, awaiting user decision
    aborted = "aborted"  # terminal failure


class MilestoneEvent(enum.Enum):
    """Events that drive the per-milestone FSM."""

    already_done = "already_done"  # milestone found in completed set
    started = "started"  # attempt dispatched
    verify_passed = "verify_passed"  # verify.sh exited 0
    verify_failed = "verify_failed"  # verify.sh exited non-0, retries remain
    attempts_exhausted = "attempts_exhausted"  # all retries consumed
    user_skip = "user_skip"  # user chose skip at exhaustion prompt
    user_retry = "user_retry"  # user chose retry-with-hint
    user_abort = "user_abort"  # user chose abort (or non-interactive)


_TRANSITIONS: dict[tuple[MilestonePhase, MilestoneEvent], MilestonePhase] = {
    (MilestonePhase.pending, MilestoneEvent.already_done): MilestonePhase.skipped,
    (MilestonePhase.pending, MilestoneEvent.started): MilestonePhase.running,
    (MilestonePhase.running, MilestoneEvent.started): MilestonePhase.running,
    (MilestonePhase.running, MilestoneEvent.verify_passed): MilestonePhase.passed,
    (MilestonePhase.running, MilestoneEvent.verify_failed): MilestonePhase.running,
    (MilestonePhase.running, MilestoneEvent.attempts_exhausted): MilestonePhase.exhausted,
    (MilestonePhase.exhausted, MilestoneEvent.user_skip): MilestonePhase.skipped,
    (MilestonePhase.exhausted, MilestoneEvent.user_retry): MilestonePhase.running,
    (MilestonePhase.exhausted, MilestoneEvent.user_abort): MilestonePhase.aborted,
    (MilestonePhase.exhausted, MilestoneEvent.verify_passed): MilestonePhase.passed,
    (MilestonePhase.exhausted, MilestoneEvent.verify_failed): MilestonePhase.aborted,
}


def next_phase(phase: MilestonePhase, event: MilestoneEvent) -> MilestonePhase:
    """Pure transition function — no side effects."""
    try:
        return _TRANSITIONS[(phase, event)]
    except KeyError:
        raise ValueError(f"invalid transition: {phase} + {event}") from None
