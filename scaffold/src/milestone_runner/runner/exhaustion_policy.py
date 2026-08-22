from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from milestone_runner.runner.fsm import ExhaustionAction

if TYPE_CHECKING:
    from milestone_runner.milestone import Milestone


class ExhaustionPolicy:
    """Prompts the user on attempt exhaustion and returns the chosen action and optional hint."""

    def __init__(self, non_interactive: bool) -> None:
        self._non_interactive = non_interactive

    def prompt(
        self,
        milestone: Milestone,
        prior_failures: list[str],
    ) -> tuple[ExhaustionAction, str | None]:
        if self._non_interactive or not sys.stdin.isatty():
            return ExhaustionAction.abort, None

        print(f"\n[{milestone.name}] exhausted all retry attempts.")
        if prior_failures:
            print("Failed checks:")
            for f in prior_failures:
                print(f"  {f}")
        print("\nOptions:")
        print("  s) skip this milestone and continue")
        print("  r) retry with a manual hint")
        print("  a) abort (default)")
        try:
            choice = input("Choice [s/r/a]: ").strip().lower() or "a"
        except EOFError:
            return ExhaustionAction.abort, None

        if choice == "s":
            return ExhaustionAction.skip, None
        if choice == "r":
            try:
                hint = input("Hint: ").strip()
            except EOFError:
                return ExhaustionAction.abort, None
            return ExhaustionAction.retry, hint or None
        return ExhaustionAction.abort, None
