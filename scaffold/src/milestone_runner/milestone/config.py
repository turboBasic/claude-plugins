from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel, model_validator

DEFAULT_MODELS: list[str] = ["haiku", "sonnet", "opus"]
_DEFAULT_TYPE: str = "agent"
_MILESTONE_CONFIG_FILE: str = "milestone.toml"


class MilestoneEntry(BaseModel):
    """Per-milestone configuration loaded from milestone.toml."""

    name: str
    models: list[str] = DEFAULT_MODELS
    type: str = _DEFAULT_TYPE
    optional: bool = False

    @model_validator(mode="after")
    def _non_empty_models(self) -> MilestoneEntry:
        if not self.models:
            raise ValueError(f"milestone {self.name!r}: models must not be empty")
        return self


class MilestoneConfig(BaseModel):
    """Aggregated configuration for all milestones under the plugin's milestones/ directory."""

    entries: list[MilestoneEntry]

    @classmethod
    def load(cls, plugin_dir: Path) -> MilestoneConfig:
        milestones_dir = plugin_dir / "milestones"
        entries: list[MilestoneEntry] = []
        for d in sorted(milestones_dir.iterdir()):
            if not d.is_dir():
                continue
            toml_path = d / _MILESTONE_CONFIG_FILE
            raw = tomllib.loads(toml_path.read_text()) if toml_path.exists() else {}
            entries.append(
                MilestoneEntry(
                    name=d.name,
                    models=raw.get("models", DEFAULT_MODELS),
                    type=raw.get("type", _DEFAULT_TYPE),
                    optional=raw.get("optional", False),
                )
            )
        return cls(entries=entries)

    def entry(self, milestone: str) -> MilestoneEntry | None:
        return next((e for e in self.entries if e.name == milestone), None)

    def optional_milestones(self) -> list[str]:
        return [e.name for e in self.entries if e.optional]

    def select(self, enabled_milestones: list[str]) -> list[str]:
        return [e.name for e in self.entries if not e.optional or e.name in enabled_milestones]

    def model_for_attempt(self, milestone: str, attempt: int) -> str:
        e = self.entry(milestone)
        ladder = e.models if e else DEFAULT_MODELS
        return ladder[min(attempt - 1, len(ladder) - 1)]
