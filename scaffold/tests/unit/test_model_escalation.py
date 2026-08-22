from __future__ import annotations

import pytest

from milestone_runner.milestone import MilestoneConfig, MilestoneEntry


def _config(*entries: tuple[str, list[str]]) -> MilestoneConfig:
    return MilestoneConfig(entries=[MilestoneEntry(name=n, models=m) for n, m in entries])


_cfg = _config(
    ("01-scaffold", ["sonnet", "opus"]),
    ("02-pre-commit", ["haiku", "sonnet", "opus"]),
    ("03-ci", ["haiku", "sonnet", "opus"]),
    ("04-config", ["haiku", "sonnet", "opus"]),
    ("05-http", ["haiku", "sonnet", "opus"]),
    ("06-aws", ["haiku", "sonnet", "opus"]),
    ("07-tests", ["sonnet", "opus"]),
)


@pytest.mark.parametrize(
    "milestone,attempt,expected",
    [
        ("01-scaffold", 1, "sonnet"),
        ("01-scaffold", 2, "opus"),
        ("01-scaffold", 3, "opus"),
        ("02-pre-commit", 1, "haiku"),
        ("02-pre-commit", 2, "sonnet"),
        ("02-pre-commit", 3, "opus"),
        ("03-ci", 1, "haiku"),
        ("03-ci", 2, "sonnet"),
        ("04-config", 1, "haiku"),
        ("04-config", 3, "opus"),
        ("07-tests", 1, "sonnet"),
        ("07-tests", 2, "opus"),
        ("07-tests", 3, "opus"),
        ("unknown-milestone", 1, "haiku"),
        ("unknown-milestone", 2, "sonnet"),
        ("unknown-milestone", 3, "opus"),
        ("unknown-milestone", 99, "opus"),
    ],
)
def test_model_for_attempt(milestone: str, attempt: int, expected: str) -> None:
    assert _cfg.model_for_attempt(milestone, attempt) == expected
