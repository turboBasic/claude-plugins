from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from milestone_runner.models import VerifyPayload, VerifyResult


def run_verify(
    milestone_dir: Path,
    project_dir: Path,
    project_name: str,
    timeout: int | None = None,
) -> VerifyResult:
    try:
        result = subprocess.run(
            ["bash", str(milestone_dir / "verify.sh"), project_name],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raw = f"TIMEOUT: verify.sh did not complete within {timeout}s"
        return VerifyResult(
            exit_code=1,
            raw=raw,
            failures=[raw],
        )
    raw = result.stdout + result.stderr
    return parse_verify_output(result.returncode, raw)


def parse_verify_output(exit_code: int, raw: str) -> VerifyResult:
    parsed: dict[str, object] | None = None
    for line in reversed(raw.splitlines()):
        stripped = line.strip()
        if stripped.startswith("{"):
            try:
                parsed = json.loads(stripped)
                break
            except json.JSONDecodeError:
                pass

    if parsed is not None:
        try:
            payload = VerifyPayload.model_validate(parsed)
        except Exception as exc:
            print(f"warning: verify payload schema error: {exc}", file=sys.stderr)
            payload = VerifyPayload()
        failures = [c.name for c in payload.checks if not c.ok]
        return VerifyResult(
            exit_code=exit_code,
            raw=raw,
            parsed=parsed,
            checks=payload.checks,
            failures=failures,
        )

    # fallback for verify scripts without JSON output
    failures = [line for line in raw.splitlines() if line.startswith("FAIL:")]
    return VerifyResult(exit_code=exit_code, raw=raw, parsed=None, failures=failures)
