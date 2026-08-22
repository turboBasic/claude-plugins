import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from milestone_runner.events.schema import (
    AgentOutput,
    MilestoneAgentExhausted,
    MilestoneCompleted,
    MilestoneFailed,
    MilestoneSkipped,
    MilestoneStarted,
    MilestoneTimeout,
    RunAborted,
    RunCompleted,
    RunStarted,
    UnknownEvent,
    VerifyResultEvent,
    parse_line,
)
from milestone_runner.models import VerifyPayload


def _parse_ts(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)


def _fmt_dur(seconds: float) -> str:
    if seconds < 60:
        return f"{int(seconds)}s"
    return f"{int(seconds // 60)}m{int(seconds % 60)}s"


@dataclass
class AttemptRecord:
    start: str
    end: str | None = None
    result: str | None = None
    failures: list[str] = field(default_factory=list[str])
    agent_output: str | None = None
    timeout: bool = False


@dataclass
class MilestoneRecord:
    attempts: list[AttemptRecord] = field(default_factory=list[AttemptRecord])
    skipped: bool = False
    final: str = "incomplete"


def display_run_log_summary(log_path: Path) -> int:
    events = [e for line in log_path.read_text().splitlines() if (e := parse_line(line))]

    run_start: RunStarted | None = next((e for e in events if isinstance(e, RunStarted)), None)
    run_end: RunCompleted | RunAborted | None = next(
        (e for e in events if isinstance(e, (RunCompleted, RunAborted))), None
    )

    project = run_start.project if run_start else "unknown"
    milestones_planned = run_start.milestones if run_start else []
    run_ts = run_start.timestamp if run_start else "?"
    run_end_ts = run_end.timestamp if run_end else None
    run_status = run_end.event if run_end else "incomplete"

    total_dur = "?"
    if run_start and run_end_ts:
        total_dur = _fmt_dur((_parse_ts(run_end_ts) - _parse_ts(run_ts)).total_seconds())

    end_str = run_end_ts or "?"
    print(f"Run: {project}  started {run_ts}  {run_status} {end_str}  ({total_dur})")
    print("─" * 68)

    milestone_data: dict[str, MilestoneRecord] = {m: MilestoneRecord() for m in milestones_planned}
    current: str | None = None

    for e in events:
        match e:
            case MilestoneSkipped(milestone=m):
                if m in milestone_data:
                    milestone_data[m].skipped = True

            case MilestoneStarted(milestone=m, timestamp=ts):
                current = m
                if m in milestone_data:
                    milestone_data[m].attempts.append(AttemptRecord(start=ts))

            case AgentOutput(output=out):
                if current and current in milestone_data:
                    attempts = milestone_data[current].attempts
                    if attempts:
                        attempts[-1].agent_output = out

            case VerifyResultEvent(milestone=m, result=result):
                if m and m in milestone_data:
                    attempts = milestone_data[m].attempts
                    if attempts and isinstance(result, dict):
                        try:
                            payload = VerifyPayload.model_validate(result)
                        except Exception as exc:
                            print(
                                f"warning: verify payload schema error: {exc}",
                                file=sys.stderr,
                            )
                            payload = VerifyPayload()
                        attempts[-1].failures = [c.name for c in payload.checks if not c.ok]

            case MilestoneCompleted(milestone=m, timestamp=ts):
                if m in milestone_data:
                    attempts = milestone_data[m].attempts
                    if attempts:
                        attempts[-1].end = ts
                        attempts[-1].result = "passed"
                    milestone_data[m].final = "PASSED"

            case MilestoneFailed(milestone=m, timestamp=ts):
                if m in milestone_data:
                    attempts = milestone_data[m].attempts
                    if attempts:
                        attempts[-1].end = ts
                        attempts[-1].result = "failed"

            case MilestoneTimeout():
                if current and current in milestone_data:
                    attempts = milestone_data[current].attempts
                    if attempts:
                        attempts[-1].timeout = True

            case RunAborted(milestone=m):
                if m in milestone_data:
                    milestone_data[m].final = "FAILED"

            case RunStarted() | RunCompleted() | MilestoneAgentExhausted() | UnknownEvent():
                pass

    passed = failed = skipped = 0

    for m in milestones_planned:
        d = milestone_data.get(m)
        if d is None:
            print(f"  {m:<22} NOT STARTED")
            continue

        if d.skipped:
            print(f"  {m:<22} SKIPPED")
            skipped += 1
            continue

        if not d.attempts:
            print(f"  {m:<22} NOT STARTED")
            continue

        last_end = d.attempts[-1].end or run_end_ts or ""
        dur = "?"
        if last_end:
            dur = _fmt_dur((_parse_ts(last_end) - _parse_ts(d.attempts[0].start)).total_seconds())
        n = len(d.attempts)
        attempt_str = "1 attempt" if n == 1 else f"{n} attempts"

        print(f"  {m:<22} {d.final:<8} {attempt_str}  {dur}")

        for i, a in enumerate(d.attempts, 1):
            if a.timeout and a.result != "passed":
                print(f"    attempt {i}: TIMEOUT")
            elif a.failures and a.result != "passed":
                for fl in a.failures:
                    print(f"    attempt {i}: {fl}")

        if d.final == "PASSED":
            passed += 1
        else:
            failed += 1
            output = d.attempts[-1].agent_output or ""
            excerpt = next((ln for ln in output.splitlines() if ln.strip()), "")
            if excerpt:
                print(f"    agent: {excerpt[:80]}")

    print("─" * 68)
    parts: list[str] = []
    if passed:
        parts.append(f"{passed} passed")
    if failed:
        parts.append(f"{failed} failed")
    if skipped:
        parts.append(f"{skipped} skipped")
    print("Summary: " + ", ".join(parts))
    return 0 if failed == 0 else 1
