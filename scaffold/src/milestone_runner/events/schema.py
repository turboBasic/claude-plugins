from __future__ import annotations

import json
import sys
from typing import Annotated, Literal, cast

from pydantic import BaseModel, Field, TypeAdapter


class RunStarted(BaseModel):
    event: Literal["run_started"] = "run_started"
    timestamp: str
    project: str
    milestones: list[str]


class RunCompleted(BaseModel):
    event: Literal["run_completed"] = "run_completed"
    timestamp: str
    project: str


class RunAborted(BaseModel):
    event: Literal["run_aborted"] = "run_aborted"
    timestamp: str
    milestone: str


class MilestoneStarted(BaseModel):
    event: Literal["milestone_started"] = "milestone_started"
    timestamp: str
    milestone: str
    attempt: int
    model: str


class MilestoneCompleted(BaseModel):
    event: Literal["milestone_completed"] = "milestone_completed"
    timestamp: str
    milestone: str
    attempt: int
    notes: list[str] = []


class MilestoneFailed(BaseModel):
    event: Literal["milestone_failed"] = "milestone_failed"
    timestamp: str
    milestone: str
    attempt: int
    failures: list[str] = []


class MilestoneSkipped(BaseModel):
    event: Literal["milestone_skipped"] = "milestone_skipped"
    timestamp: str
    milestone: str
    reason: str | None = None


class MilestoneTimeout(BaseModel):
    event: Literal["milestone_timeout"] = "milestone_timeout"
    timestamp: str
    timeout: int


class MilestoneAgentExhausted(BaseModel):
    event: Literal["milestone_agent_exhausted"] = "milestone_agent_exhausted"
    timestamp: str
    milestone: str


class AgentOutput(BaseModel):
    event: Literal["agent_output"] = "agent_output"
    timestamp: str
    output: str


class VerifyResultEvent(BaseModel):
    event: Literal["verify_result"] = "verify_result"
    timestamp: str
    milestone: str
    exit_code: int
    result: dict[str, object] | None = None


class UnknownEvent(BaseModel):
    event: str
    timestamp: str


KnownLogEvent = Annotated[
    RunStarted
    | RunCompleted
    | RunAborted
    | MilestoneStarted
    | MilestoneCompleted
    | MilestoneFailed
    | MilestoneSkipped
    | MilestoneTimeout
    | MilestoneAgentExhausted
    | AgentOutput
    | VerifyResultEvent,
    Field(discriminator="event"),
]

LogEvent = KnownLogEvent | UnknownEvent

_adapter: TypeAdapter[KnownLogEvent] = TypeAdapter(KnownLogEvent)

_KNOWN_EVENTS = {
    "run_started",
    "run_completed",
    "run_aborted",
    "milestone_started",
    "milestone_completed",
    "milestone_failed",
    "milestone_skipped",
    "milestone_timeout",
    "milestone_agent_exhausted",
    "agent_output",
    "verify_result",
}


def parse_line(line: str) -> LogEvent | None:
    stripped = line.strip()
    if not stripped:
        return None
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    d = cast("dict[str, object]", data)
    event_name = cast("str", d.get("event", ""))
    if event_name in _KNOWN_EVENTS:
        try:
            return _adapter.validate_python(data)
        except Exception as exc:
            print(
                f"warning: malformed {event_name!r} event: {exc}",
                file=sys.stderr,
            )
            return None
    try:
        return UnknownEvent.model_validate(data)
    except Exception:
        return None
