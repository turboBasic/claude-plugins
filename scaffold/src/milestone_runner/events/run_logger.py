from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from milestone_runner.events.schema import (
    AgentOutput,
    KnownLogEvent,
    MilestoneAgentExhausted,
    MilestoneCompleted,
    MilestoneFailed,
    MilestoneSkipped,
    MilestoneStarted,
    MilestoneTimeout,
    RunAborted,
    RunCompleted,
    RunStarted,
    VerifyResultEvent,
)


class RunLogger:
    """Appends structured JSONL events to a log file; one method per event type."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def _now(self) -> str:
        return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _write(self, event: KnownLogEvent) -> None:
        with self.path.open("a") as f:
            f.write(event.model_dump_json(exclude_none=True) + "\n")

    def run_started(self, project: str, milestones: list[str]) -> None:
        self._write(RunStarted(timestamp=self._now(), project=project, milestones=milestones))

    def run_completed(self, project: str) -> None:
        self._write(RunCompleted(timestamp=self._now(), project=project))

    def run_aborted(self, milestone: str) -> None:
        self._write(RunAborted(timestamp=self._now(), milestone=milestone))

    def milestone_started(self, milestone: str, attempt: int, model: str) -> None:
        self._write(
            MilestoneStarted(
                timestamp=self._now(), milestone=milestone, attempt=attempt, model=model
            )
        )

    def milestone_completed(self, milestone: str, attempt: int, notes: list[str]) -> None:
        self._write(
            MilestoneCompleted(
                timestamp=self._now(), milestone=milestone, attempt=attempt, notes=notes
            )
        )

    def milestone_failed(self, milestone: str, attempt: int, failures: list[str]) -> None:
        self._write(
            MilestoneFailed(
                timestamp=self._now(), milestone=milestone, attempt=attempt, failures=failures
            )
        )

    def milestone_skipped(self, milestone: str, reason: str | None = None) -> None:
        self._write(MilestoneSkipped(timestamp=self._now(), milestone=milestone, reason=reason))

    def milestone_timeout(self, timeout: int) -> None:
        self._write(MilestoneTimeout(timestamp=self._now(), timeout=timeout))

    def milestone_agent_exhausted(self, milestone: str) -> None:
        self._write(MilestoneAgentExhausted(timestamp=self._now(), milestone=milestone))

    def agent_output(self, output: str) -> None:
        self._write(AgentOutput(timestamp=self._now(), output=output))

    def verify_result(
        self, milestone: str, exit_code: int, result: dict[str, object] | None
    ) -> None:
        self._write(
            VerifyResultEvent(
                timestamp=self._now(),
                milestone=milestone,
                exit_code=exit_code,
                result=result,
            )
        )
