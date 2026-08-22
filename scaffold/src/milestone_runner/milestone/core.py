from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from milestone_runner.milestone.config import DEFAULT_MODELS, MilestoneConfig, MilestoneEntry
from milestone_runner.milestone.state import MilestoneState
from milestone_runner.milestone.verify import run_verify
from milestone_runner.models import VerifyResult


@dataclass
class Milestone:
    """Identity and config for a single milestone: path derivation, verification, and state ops."""

    name: str
    entry: MilestoneEntry
    directory: Path

    @property
    def short_name(self) -> str:
        return self.name.split("-", 1)[1]

    def model_for_attempt(self, n: int) -> str:
        ladder = self.entry.models
        return ladder[min(n - 1, len(ladder) - 1)]

    def is_complete(self, state: MilestoneState) -> bool:
        return self.short_name in state.completed()

    def record_completion(self, state: MilestoneState, notes: list[str]) -> None:
        state.record(self.name, notes)

    def run_verify(self, project_dir: Path, project_name: str, timeout: int) -> VerifyResult:
        return run_verify(self.directory, project_dir, project_name, timeout)

    @classmethod
    def load(cls, name: str, config: MilestoneConfig, plugin_dir: Path) -> Milestone:
        entry = config.entry(name) or MilestoneEntry(
            name=name, models=DEFAULT_MODELS, type="agent", optional=False
        )
        return cls(name=name, entry=entry, directory=plugin_dir / "milestones" / name)
