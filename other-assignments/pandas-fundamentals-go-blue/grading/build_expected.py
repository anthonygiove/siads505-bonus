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
    games = ref.load_games()
    opponents = ref.load_opponents()
    return {
        "q1_load_games": to_jsonable(games.head(3)[["season", "week", "opponent", "site"]]),
        "q1_shape": to_jsonable((games.shape[0], games.shape[1])),
        "q2_add_result_columns": to_jsonable(
            ref.add_result_columns(games)[["point_diff", "total_points", "won"]].head(5)
        ),
        "q3_best_and_worst": to_jsonable(ref.best_and_worst(games)),
        "q4_ticket_prices": to_jsonable(ref.ticket_prices(games).head(5)),
        "q4_mean": to_jsonable(round(float(ref.ticket_prices(games).mean()), 4)),
        "q5_season_report_card": to_jsonable(ref.season_report_card(games)),
        "q6_night_game_split": to_jsonable(ref.night_game_split(games)),
        "q7_filled_attendance_mean": to_jsonable(
            round(float(ref.filled_attendance(games).mean()), 4)
        ),
        "q8_record_by_conference": to_jsonable(ref.record_by_conference(games, opponents)),
        "q9_rivalry_report": to_jsonable(ref.rivalry_report(games, opponents)),
        "q10_weather_scoring": to_jsonable(ref.weather_scoring(games)),
    }


def main() -> None:
    SNAPSHOT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
    print(f"wrote {SNAPSHOT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
