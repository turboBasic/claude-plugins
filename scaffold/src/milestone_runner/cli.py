from __future__ import annotations

import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Any

import typer  # pyright: ignore[reportMissingTypeStubs]

from milestone_runner.events.run_log_summary import display_run_log_summary
from milestone_runner.events.run_logger import RunLogger
from milestone_runner.run_context import RunContext
from milestone_runner.runner import MilestoneRunner

app = typer.Typer(add_completion=False)

typer_any: Any = typer
TyperArgument = typer_any.Argument
TyperOption = typer_any.Option

_PLUGIN_DIR = (
    Path(os.environ["MILESTONE_RUNNER_PLUGIN_DIR"])
    if "MILESTONE_RUNNER_PLUGIN_DIR" in os.environ
    else Path(__file__).absolute().parent.parent.parent
)


def _start_run(ctx: RunContext, timeout: int, non_interactive: bool) -> None:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    log_file = ctx.project_dir / f"agent-{timestamp}.log.jsonl"
    symlink = ctx.project_dir / "agent-latest.log.jsonl"
    if symlink.is_symlink():
        symlink.unlink()
    symlink.symlink_to(log_file.name)
    typer.echo(f"Log:        {log_file}")
    event_log = RunLogger(log_file)
    rc = MilestoneRunner(ctx, event_log, timeout, non_interactive).run()
    sys.exit(rc)


@app.command("run")
def cmd_run(
    project_name: Annotated[str, TyperArgument(help="Project name")],
    description: Annotated[str, TyperArgument(help="One-line description")] = "",
    enable_milestones: Annotated[
        str,
        TyperOption(
            "--enable-milestones",
            help="Comma-separated optional milestone names to include",
        ),
    ] = "",
    output_dir: Annotated[
        Path, TyperOption("--output-dir", help="Parent dir for generated project")
    ] = Path("."),
    timeout: Annotated[
        int, TyperOption("--timeout", help="Per-milestone agent timeout in seconds")
    ] = 300,
    non_interactive: Annotated[
        bool,
        TyperOption("--non-interactive", help="Abort on exhaustion without prompting"),
    ] = False,
) -> None:
    existing = output_dir.absolute() / project_name / "agent.context.json"
    if existing.exists():
        typer.echo(
            f"ERROR: {existing} already exists — "
            "this project was already initialised.\n"
            f"Use resume to continue:\n"
            f"  milestone-runner resume {existing}",
            err=True,
        )
        raise typer.Exit(1)
    parsed_enable = [m.strip() for m in enable_milestones.split(",") if m.strip()]
    try:
        ctx = RunContext.create(project_name, description, output_dir, parsed_enable, _PLUGIN_DIR)
    except ValueError as e:
        typer.echo(f"ERROR: {e}", err=True)
        raise typer.Exit(1) from e
    ctx.save()
    _start_run(ctx, timeout, non_interactive)


@app.command("resume")
def cmd_resume(
    context_path: Annotated[Path, TyperArgument(help="Path to agent.context.json")],
    timeout: Annotated[
        int, TyperOption("--timeout", help="Per-milestone agent timeout in seconds")
    ] = 300,
    non_interactive: Annotated[
        bool,
        TyperOption("--non-interactive", help="Abort on exhaustion without prompting"),
    ] = False,
) -> None:
    try:
        ctx = RunContext.load(context_path)
    except FileNotFoundError as e:
        typer.echo(f"ERROR: {e}", err=True)
        raise typer.Exit(1) from e
    _start_run(ctx, timeout, non_interactive)


@app.command("log-summary")
def cmd_log_summary(
    log_file: Annotated[
        Path,
        TyperArgument(help="Path to log file"),
    ] = Path("agent-latest.log.jsonl"),
) -> None:
    if not log_file.exists():
        typer.echo(f"ERROR: {log_file} not found", err=True)
        raise typer.Exit(1)
    rc = display_run_log_summary(log_file)
    sys.exit(rc)
