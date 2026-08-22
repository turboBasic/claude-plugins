from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel


class CheckResult(BaseModel):
    """A single named check and its pass/fail outcome from verify.sh JSON output."""

    name: str
    ok: bool


class VerifyPayload(BaseModel):
    """Parsed JSON body emitted by verify.sh on stdout."""

    milestone: str = ""
    passed: bool = False
    checks: list[CheckResult] = []


@dataclass
class VerifyResult:
    """Full result of a verify.sh invocation: raw output, parsed checks, and derived fail list."""

    exit_code: int
    raw: str
    parsed: dict[str, object] | None = None
    checks: list[CheckResult] = field(default_factory=list[CheckResult])
    failures: list[str] = field(default_factory=list[str])


class AgentResult(BaseModel):
    """JSON result object emitted by the agent at the end of its response."""

    status: Literal["done"] = "done"
    milestone: str = ""
    notes: list[str] = []


@dataclass
class AgentInvocation:
    """Raw result of a claude or generate.py subprocess call."""

    rc: int
    output: str
    result: AgentResult | None


@dataclass
class AttemptResult:
    """Outcome of a single strategy attempt, before verify is called."""

    dispatch_ok: bool  # True: subprocess ran OK, proceed to verify. False: subprocess failed.
    notes: list[str]
    failures: list[str]
    output: str
    timed_out: bool = False  # timed_out=True implies dispatch_ok=False


@dataclass
class MilestoneSummary:
    """Accumulated notes for a completed milestone; passed as context to subsequent milestones."""

    milestone: str
    notes: list[str]
