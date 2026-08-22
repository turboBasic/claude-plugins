from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from milestone_runner.models import AgentInvocation, AgentResult


def _remove_fence(raw: str, fence: str = "json") -> str:
    start_token = f"```{fence}"
    start = raw.rfind(start_token)
    if start == -1:
        return raw
    end = raw.find("```", start + len(start_token))
    if end == -1:
        return raw
    return raw[start + len(start_token) : end].strip()


def _agent_result(raw: str) -> AgentResult | None:
    try:
        data: object = json.loads(raw.strip())
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    try:
        return AgentResult.model_validate(data)
    except Exception:
        return None


def _parse_agent_output(raw: str) -> AgentResult | None:
    raw = _remove_fence(raw.strip(), "json")

    if result := _agent_result(raw):
        return result

    for line in reversed(raw.splitlines()):
        if result := _agent_result(line):
            return result
    return None


def _run_subprocess(
    cmd: list[str],
    cwd: Path,
    timeout: int,
    timeout_label: str = "process",
) -> AgentInvocation:
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout + result.stderr
        return AgentInvocation(
            rc=result.returncode, output=output, result=_parse_agent_output(output)
        )
    except subprocess.TimeoutExpired:
        output = f"TIMEOUT: {timeout_label} did not complete within {timeout}s"
        return AgentInvocation(rc=1, output=output, result=None)


def invoke_agent(
    prompt: str,
    timeout: int,
    model: str | None = None,
    project_dir: Path | None = None,
) -> AgentInvocation:
    cmd = [
        "claude",
        "--print",
        "-p",
        prompt,
        "--allowedTools",
        "Read,Write,Edit,Bash,Glob,Grep",
    ]
    if model:
        cmd += ["--model", model]
    return _run_subprocess(cmd, project_dir or Path("."), timeout, timeout_label="agent")


def invoke_generate(
    generate_py: Path,
    project_dir: Path,
    timeout: int,
) -> AgentInvocation:
    context_path = project_dir / "agent.context.json"
    cmd = [sys.executable, str(generate_py), str(project_dir), str(context_path)]
    return _run_subprocess(cmd, project_dir, timeout, timeout_label="generate.py")
