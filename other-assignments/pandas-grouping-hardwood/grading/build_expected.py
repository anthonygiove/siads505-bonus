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
    box = ref.load_box_scores()
    games = ref.load_games()
    roster = ref.load_roster()
    return {
        "q1_box_head": to_jsonable(box.head(4)[["season", "player", "minutes", "points"]]),
        "q1_box_shape": to_jsonable((box.shape[0], box.shape[1])),
        "q1_games_shape": to_jsonable((games.shape[0], games.shape[1])),
        "q2_split_shooting": to_jsonable(ref.split_shooting(box).head(6)),
        "q2_totals": to_jsonable(
            tuple(round(float(v), 4) for v in ref.split_shooting(box).sum().tolist())
        ),
        "q3_minutes_played": to_jsonable(ref.minutes_played(box).head(6)),
        "q3_total": to_jsonable(round(float(ref.minutes_played(box).sum()), 4)),
        "q4_shooting_rates": to_jsonable(ref.shooting_rates(box).head(6)),
        "q4_means": to_jsonable(
            tuple(round(float(v), 6) for v in ref.shooting_rates(box).mean().tolist())
        ),
        "q5_player_season_totals": to_jsonable(ref.player_season_totals(box).head(12)),
        "q5_shape": to_jsonable(
            (ref.player_season_totals(box).shape[0], ref.player_season_totals(box).shape[1])
        ),
        "q6_leading_scorer": to_jsonable(ref.leading_scorer(box).head(10)),
        "q7_rolling_form": to_jsonable(ref.rolling_form(games).head(10)),
        "q7_mean": to_jsonable(round(float(ref.rolling_form(games).mean()), 6)),
        "q8_season_leaderboard": to_jsonable(ref.season_leaderboard(box).head(12)),
        "q9_longest_win_streak": to_jsonable(ref.longest_win_streak(games)),
        "q10_class_scoring": to_jsonable(ref.class_scoring(box, roster)),
    }


def main() -> None:
    SNAPSHOT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
    print(f"wrote {SNAPSHOT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
