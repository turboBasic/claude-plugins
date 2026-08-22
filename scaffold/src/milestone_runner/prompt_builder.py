from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from milestone_runner.models import MilestoneSummary
from milestone_runner.run_context import RunContext

if TYPE_CHECKING:
    from milestone_runner.milestone import Milestone

MILESTONES_DIR = "milestones"
MILESTONE_PROMPT_FILE = "PROMPT.md"
RULES_PRE_FILE = "agent-rules-pre.md"
RULES_POST_FILE = "agent-rules-post.md"


class PromptBuilder:
    def __init__(self, ctx: RunContext) -> None:
        self._ctx = ctx

    def build(
        self,
        milestone: Milestone,
        prior_failures: list[str] | None = None,
        prior_summaries: list[MilestoneSummary] | None = None,
    ) -> str:
        parts: list[str] = []

        name = self._ctx.project_name
        parts.append(
            f"Execute milestone `{milestone.name}` for project **{name}** "
            f"at `{self._ctx.project_dir}`.\n"
            f"Project description: {self._ctx.description}\n"
            "Read `agent.context.json` in that directory for full context."
        )
        parts.append(self._prior_summaries_section(prior_summaries))
        parts.append(self._prior_failures_section(prior_failures))
        parts.append(self._rules_pre_section())
        parts.append(self._milestone_section(milestone))
        parts.append(self._rules_post_section())

        return "\n\n".join([part for part in parts if part])

    def _prior_summaries_section(self, prior_summaries: list[MilestoneSummary] | None) -> str:
        if not prior_summaries:
            return ""
        lines: list[str] = ["## Prior milestones", ""]
        for summary in prior_summaries:
            note_str = "; ".join(summary.notes) if summary.notes else "completed, no notes"
            lines.append(f"- **{summary.milestone}**: {note_str}")
        return "\n".join(lines)

    def _prior_failures_section(self, prior_failures: list[str] | None) -> str:
        if not prior_failures:
            return ""
        lines: list[str] = [
            "## Failed checks from previous attempt",
            "",
            "Fix these before proceeding:",
            "",
        ]
        lines.extend([f"- {failure}" for failure in prior_failures])
        return "\n".join(lines)

    def _rules_pre_section(self) -> str:
        return self._read_rules(self._ctx.plugin_dir, RULES_PRE_FILE)

    def _milestone_section(self, milestone: Milestone) -> str:
        milestone_prompt_path = milestone.directory / MILESTONE_PROMPT_FILE
        if milestone_content := milestone_prompt_path.read_text().strip():
            return f"---\n\n{milestone_content}"
        return (
            f"---\n\n## Milestone: {milestone.name}\n\n"
            "No additional instructions provided for this milestone."
        )

    def _rules_post_section(self) -> str:
        if constraints := self._read_rules(self._ctx.plugin_dir, RULES_POST_FILE):
            return f"---\n\n{constraints}"
        return ""

    def _read_rules(self, plugin_dir: Path, filename: str) -> str:
        p = plugin_dir / MILESTONES_DIR / filename
        return p.read_text().strip() if p.exists() else ""
