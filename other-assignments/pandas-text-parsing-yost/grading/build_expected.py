"""
Regenerate grading/expected_values.json from the reference solution.

Run this after changing solution/reference.py or regenerating the data:

    python grading/build_expected.py

run_autograder.py verifies this snapshot before it grades anything, so a
silent change to the dataset or the reference shows up as a loud failure
instead of a room full of wrong grades.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "solution"))
sys.path.insert(0, str(ROOT / "grading"))

import reference as ref  # noqa: E402
from _serialize import to_jsonable  # noqa: E402

SNAPSHOT = ROOT / "grading" / "expected_values.json"


def build() -> dict:
    events = ref.load_events()
    games = ref.load_games()
    roster = ref.load_roster()
    return {
        "q1_events_shape": to_jsonable((events.shape[0], events.shape[1])),
        "q1_games_shape": to_jsonable((games.shape[0], games.shape[1])),
        "q1_roster_shape": to_jsonable((roster.shape[0], roster.shape[1])),
        "q2_parse_events": to_jsonable(ref.parse_events(events).head(8)),
        "q2_type_counts": to_jsonable(
            tuple(sorted(ref.parse_events(events)["event_type"].value_counts().items()))
        ),
        "q3_elapsed_seconds": to_jsonable(ref.elapsed_seconds(events).head(8)),
        "q3_total": to_jsonable(int(ref.elapsed_seconds(events).sum())),
        "q4_assist_credits": to_jsonable(ref.assist_credits(events)),
        "q5_penalty_summary": to_jsonable(ref.penalty_summary(events)),
        "q6_roster_details": to_jsonable(ref.roster_details(roster)),
        "q7_scoring_leaders": to_jsonable(ref.scoring_leaders(events, roster)),
        "q8_strength_breakdown": to_jsonable(ref.strength_breakdown(events)),
        "q9_first_goal_times": to_jsonable(ref.first_goal_times(events, games)),
        "q10_game_winning_goals": to_jsonable(ref.game_winning_goals(events, games)),
    }


def main() -> None:
    SNAPSHOT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
    print(f"wrote {SNAPSHOT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
