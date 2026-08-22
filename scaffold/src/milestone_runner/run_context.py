from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, field_validator

from milestone_runner.milestone import MilestoneConfig


class RunContext(BaseModel):
    """Immutable project metadata shared across all milestone invocations for a single run."""

    project_name: str
    package_name: str
    description: str
    project_dir: Path
    plugin_dir: Path
    enabled_milestones: list[str]
    milestones: list[str]

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("project_name")
    @classmethod
    def check_project_name(cls, name: str) -> str:
        if not name or name.strip(".") == "":
            raise ValueError(f"invalid project_name: {name!r}")
        if any(c in name for c in ("/", "\\")):
            raise ValueError(f"invalid project_name: {name!r} (must not contain path separators)")
        if ".." in Path(name).parts:
            raise ValueError(f"invalid project_name: {name!r} (must not contain '..')")
        return name

    @classmethod
    def create(
        cls,
        project_name: str,
        description: str,
        output_dir: Path,
        enable_milestones: list[str],
        plugin_dir: Path,
    ) -> RunContext:
        cls.check_project_name(project_name)
        package_name = project_name.replace("-", "_").replace(" ", "_")
        project_dir = output_dir.absolute() / project_name
        cfg = MilestoneConfig.load(plugin_dir)
        milestones = cfg.select(enable_milestones)
        return cls(
            project_name=project_name,
            package_name=package_name,
            description=description,
            project_dir=project_dir,
            plugin_dir=plugin_dir,
            enabled_milestones=enable_milestones,
            milestones=milestones,
        )

    @classmethod
    def load(cls, context_path: Path) -> RunContext:
        if not context_path.exists():
            raise FileNotFoundError(f"context file not found: {context_path}")
        data = json.loads(context_path.read_text())
        return cls.model_validate(data)

    def save(self) -> None:
        self.project_dir.mkdir(parents=True, exist_ok=True)
        path = self.project_dir / "agent.context.json"
        payload = self.model_dump()
        payload["project_dir"] = str(self.project_dir)
        payload["plugin_dir"] = str(self.plugin_dir)
        path.write_text(json.dumps(payload, indent=2) + "\n")
