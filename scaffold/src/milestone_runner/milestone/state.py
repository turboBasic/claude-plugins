from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from milestone_runner.models import MilestoneSummary

_MILESTONES_STATE_FILE = ".milestones.jsonl"


class MilestoneState:
    """Reads and writes the .milestones.jsonl state file in the project directory."""

    def __init__(self, project_dir: Path) -> None:
        self._file = project_dir / _MILESTONES_STATE_FILE

    def completed(self) -> list[str]:
        if not self._file.exists():
            return []
        result: list[str] = []
        for line in self._file.read_text().splitlines():
            line = line.strip()
            if line:
                entry: dict[str, object] = json.loads(line)
                milestone = str(entry.get("milestone", ""))
                if milestone:
                    result.append(milestone.split("-", 1)[1])
        return result

    def record(self, milestone: str, notes: list[str]) -> None:
        entry = {"milestone": milestone, "notes": notes}
        with self._file.open("a") as f:
            f.write(json.dumps(entry) + "\n")

    def load_summary(self) -> list[MilestoneSummary]:
        if not self._file.exists():
            return []
        result: list[MilestoneSummary] = []
        for line in self._file.read_text().splitlines():
            line = line.strip()
            if line:
                entry: dict[str, object] = json.loads(line)
                raw_notes = entry.get("notes")
                notes = (
                    [str(n) for n in cast("list[object]", raw_notes)]
                    if isinstance(raw_notes, list)
                    else []
                )
                result.append(
                    MilestoneSummary(
                        milestone=str(entry.get("milestone", "")),
                        notes=notes,
                    )
                )
        return result
