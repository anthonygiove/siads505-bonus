"""
HIDDEN TESTS -- do not distribute with the student notebook.

Each of the ten questions is worth 10 points, split across several checks so
that partial credit is possible. Every question is graded against inputs the
autograder builds itself from the reference loader, so a student who fumbles
Question 1 can still earn full marks on Questions 2-10.

Most questions also carry a "robustness" check that re-runs the student's
function on a *different* slice of the data. Those checks exist to catch
answers that were hard-coded after peeking at the public asserts.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "solution"))

import reference as ref  # noqa: E402


# --------------------------------------------------------------- test helpers
class Missing(AssertionError):
    """Raised when the student never defined the function at all."""


def fn(ns, name):
    if name not in ns:
        raise Missing(f"`{name}` is not defined in the notebook.")
    func = ns[name]
    if not callable(func):
        raise Missing(f"`{name}` exists but is not a function.")
    return func


def _close(a, b, tol=1e-6):
    a_nan = a is None or (isinstance(a, float) and math.isnan(a))
    b_nan = b is None or (isinstance(b, float) and math.isnan(b))
    if a_nan or b_nan:
        return a_nan and b_nan
    if isinstance(a, (bool, np.bool_)) or isinstance(b, (bool, np.bool_)):
        return bool(a) == bool(b)
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return a == b


def assert_is(obj, kind, what):
    assert isinstance(obj, kind), (
        f"{what} should return a {kind.__name__}, got {type(obj).__name__}."
    )


def assert_index(actual, expected, what):
    got = [str(v) for v in actual]
    want = [str(v) for v in expected]
    assert got == want, f"{what}: index should be {want}, got {got}."


def assert_series_matches(actual, expected, what, tol=1e-6):
    assert_is(actual, pd.Series, what)
    assert len(actual) == len(expected), (
        f"{what}: expected {len(expected)} values, got {len(actual)}."
    )
    assert_index(actual.index, expected.index, what)
    for key, want in expected.items():
        got = actual.loc[key]
        assert _close(got, want, tol), (
            f"{what}: value at {key!r} should be {want!r}, got {got!r}."
        )


def assert_frame_matches(actual, expected, what, tol=1e-6, ordered_columns=True):
    assert_is(actual, pd.DataFrame, what)
    got_cols, want_cols = list(actual.columns), list(expected.columns)
    if ordered_columns:
        assert got_cols == want_cols, (
            f"{what}: columns should be {want_cols} in that order, got {got_cols}."
        )
    else:
        missing = [c for c in want_cols if c not in got_cols]
        assert not missing, f"{what}: missing column(s) {missing}."
    assert len(actual) == len(expected), (
        f"{what}: expected {len(expected)} rows, got {len(actual)}."
    )
    assert_index(actual.index, expected.index, what)
    for col in want_cols:
        for key in expected.index:
            want, got = expected.at[key, col], actual.at[key, col]
            assert _close(got, want, tol), (
                f"{what}: [{key!r}, {col!r}] should be {want!r}, got {got!r}."
            )


# -------------------------------------------------------------- shared inputs
def games():
    return ref.load_games()


def opponents():
    return ref.load_opponents()


# ------------------------------------------------------------------ Question 1
def q1_type_and_shape(ns):
    out = fn(ns, "load_games")()
    assert_is(out, pd.DataFrame, "load_games")
    assert out.shape == (195, 15), (
        f"load_games: expected a (195, 15) frame once game_id is the index, got {out.shape}."
    )


def q1_index(ns):
    out = fn(ns, "load_games")()
    assert out.index.name == "game_id", (
        f"load_games: the index should be named 'game_id', got {out.index.name!r}."
    )
    assert out.index.is_unique, "load_games: game_id values should be unique."
    assert "game_id" not in out.columns, (
        "load_games: game_id should be the index, not also a column."
    )


def q1_dtypes_and_values(ns):
    out = fn(ns, "load_games")()
    assert pd.api.types.is_datetime64_any_dtype(out["date"]), (
        f"load_games: 'date' should be a datetime column, got dtype {out['date'].dtype}."
    )
    want = games()
    assert list(out.columns) == list(want.columns), (
        f"load_games: columns should be {list(want.columns)}, got {list(out.columns)}."
    )
    assert out.loc["2010-W01", "opponent"] == "Appalachian State"
    assert out.loc["2023-W13", "season"] == 2023
    assert out["date"].min() == pd.Timestamp("2010-09-04")


# ------------------------------------------------------------------ Question 2
def q2_columns_present(ns):
    out = fn(ns, "add_result_columns")(games())
    assert_is(out, pd.DataFrame, "add_result_columns")
    for col in ("point_diff", "total_points", "won"):
        assert col in out.columns, f"add_result_columns: missing column {col!r}."
    assert len(out) == 195, f"add_result_columns: expected 195 rows, got {len(out)}."


def q2_values(ns):
    out = fn(ns, "add_result_columns")(games())
    want = ref.add_result_columns(games())
    assert_frame_matches(
        out[["point_diff", "total_points", "won"]],
        want[["point_diff", "total_points", "won"]],
        "add_result_columns",
    )
    assert out["won"].dtype == bool, (
        f"add_result_columns: 'won' should hold True/False, got dtype {out['won'].dtype}."
    )


def q2_does_not_mutate(ns):
    original = games()
    before = list(original.columns)
    fn(ns, "add_result_columns")(original)
    assert list(original.columns) == before, (
        "add_result_columns: the DataFrame you were handed was modified in place. "
        "Work on a .copy() and return the copy."
    )


# ------------------------------------------------------------------ Question 3
def q3_shape(ns):
    out = fn(ns, "best_and_worst")(games())
    assert isinstance(out, tuple), (
        f"best_and_worst should return a tuple, got {type(out).__name__}."
    )
    assert len(out) == 2, f"best_and_worst should return 2 items, got {len(out)}."
    assert all(isinstance(v, str) for v in out), (
        f"best_and_worst should return game_id strings, got {out!r}."
    )


def q3_values(ns):
    out = fn(ns, "best_and_worst")(games())
    want = ref.best_and_worst(games())
    assert out == want, f"best_and_worst: expected {want}, got {out}."


def q3_robustness(ns):
    subset = games().head(60)
    out = fn(ns, "best_and_worst")(subset)
    want = ref.best_and_worst(subset)
    assert out == want, (
        f"best_and_worst: on the first 60 games expected {want}, got {out}. "
        "Compute the answer from the DataFrame you are given."
    )


# ------------------------------------------------------------------ Question 4
def q4_type(ns):
    out = fn(ns, "ticket_prices")(games())
    assert_is(out, pd.Series, "ticket_prices")
    assert out.name == "ticket_price", (
        f"ticket_prices: the Series should be named 'ticket_price', got {out.name!r}."
    )
    assert pd.api.types.is_float_dtype(out), (
        f"ticket_prices: expected a float Series, got dtype {out.dtype}."
    )
    assert len(out) == 195, f"ticket_prices: expected 195 values, got {len(out)}."


def q4_missing_handled(ns):
    out = fn(ns, "ticket_prices")(games())
    want = ref.ticket_prices(games())
    assert out.isna().sum() == want.isna().sum() == 5, (
        f"ticket_prices: the 5 'unavailable' rows should become NaN, "
        f"got {int(out.isna().sum())} NaN values."
    )
    assert list(out.index[out.isna()]) == list(want.index[want.isna()]), (
        "ticket_prices: the NaN values are not on the rows marked 'unavailable'."
    )


def q4_values(ns):
    out = fn(ns, "ticket_prices")(games())
    want = ref.ticket_prices(games())
    assert_series_matches(out, want, "ticket_prices", tol=1e-4)


# ------------------------------------------------------------------ Question 5
def q5_structure(ns):
    out = fn(ns, "season_report_card")(games())
    assert_is(out, pd.DataFrame, "season_report_card")
    assert list(out.columns) == ["wins", "losses", "points_for", "points_against", "win_pct"], (
        f"season_report_card: columns should be ['wins', 'losses', 'points_for', "
        f"'points_against', 'win_pct'], got {list(out.columns)}."
    )
    assert out.index.name == "season", (
        f"season_report_card: index should be named 'season', got {out.index.name!r}."
    )
    assert list(out.index) == list(range(2010, 2025)), (
        "season_report_card: index should be seasons 2010..2024 in ascending order."
    )


def q5_values(ns):
    out = fn(ns, "season_report_card")(games())
    assert_frame_matches(out, ref.season_report_card(games()), "season_report_card", tol=1e-3)


def q5_robustness(ns):
    subset = games()[games()["season"] >= 2018]
    out = fn(ns, "season_report_card")(subset)
    want = ref.season_report_card(subset)
    assert_frame_matches(out, want, "season_report_card (2018 onward)", tol=1e-3)


# ------------------------------------------------------------------ Question 6
def q6_structure(ns):
    out = fn(ns, "night_game_split")(games())
    assert_is(out, pd.Series, "night_game_split")
    assert list(out.index) == ["Day", "Night"], (
        f"night_game_split: index should be ['Day', 'Night'], got {list(out.index)}."
    )


def q6_values(ns):
    out = fn(ns, "night_game_split")(games())
    assert_series_matches(out, ref.night_game_split(games()), "night_game_split", tol=1e-3)


def q6_robustness(ns):
    subset = games()[games()["site"] == "Home"]
    out = fn(ns, "night_game_split")(subset)
    want = ref.night_game_split(subset)
    assert_series_matches(out, want, "night_game_split (home games only)", tol=1e-3)


# ------------------------------------------------------------------ Question 7
def q7_no_missing(ns):
    out = fn(ns, "filled_attendance")(games())
    assert_is(out, pd.Series, "filled_attendance")
    assert out.name == "attendance", (
        f"filled_attendance: the Series should be named 'attendance', got {out.name!r}."
    )
    assert len(out) == 195, f"filled_attendance: expected 195 values, got {len(out)}."
    assert out.isna().sum() == 0, (
        f"filled_attendance: {int(out.isna().sum())} values are still missing."
    )


def q7_untouched_rows(ns):
    out = fn(ns, "filled_attendance")(games())
    original = games()["attendance"]
    kept = original.notna()
    assert_series_matches(out[kept], original[kept], "filled_attendance (rows that were not missing)")


def q7_values(ns):
    out = fn(ns, "filled_attendance")(games())
    assert_series_matches(out, ref.filled_attendance(games()), "filled_attendance", tol=1e-4)


def q7_robustness(ns):
    subset = games().iloc[::2]
    out = fn(ns, "filled_attendance")(subset)
    want = ref.filled_attendance(subset)
    assert_series_matches(out, want, "filled_attendance (every other game)", tol=1e-4)


# ------------------------------------------------------------------ Question 8
def q8_structure(ns):
    out = fn(ns, "record_by_conference")(games(), opponents())
    assert_is(out, pd.DataFrame, "record_by_conference")
    assert list(out.columns) == ["games", "wins", "win_pct"], (
        f"record_by_conference: columns should be ['games', 'wins', 'win_pct'], "
        f"got {list(out.columns)}."
    )
    assert out.index.name == "conference", (
        f"record_by_conference: index should be named 'conference', got {out.index.name!r}."
    )
    assert int(out["games"].sum()) == 195, (
        f"record_by_conference: the games column should total 195 (the merge must not "
        f"add or drop rows), got {int(out['games'].sum())}."
    )


def q8_values(ns):
    out = fn(ns, "record_by_conference")(games(), opponents())
    assert_frame_matches(
        out, ref.record_by_conference(games(), opponents()), "record_by_conference", tol=1e-3
    )


def q8_robustness(ns):
    opp = opponents()
    trimmed = opp[opp["conference"] != "MAC"].reset_index(drop=True)
    out = fn(ns, "record_by_conference")(games(), trimmed)
    want = ref.record_by_conference(games(), trimmed)
    assert_frame_matches(out, want, "record_by_conference (MAC removed from opponents)", tol=1e-3)


# ------------------------------------------------------------------ Question 9
def q9_structure(ns):
    out = fn(ns, "rivalry_report")(games(), opponents())
    assert_is(out, pd.DataFrame, "rivalry_report")
    assert list(out.columns) == ["games", "wins", "losses", "win_pct", "avg_point_diff"], (
        f"rivalry_report: columns should be ['games', 'wins', 'losses', 'win_pct', "
        f"'avg_point_diff'], got {list(out.columns)}."
    )
    assert list(out.index) == ["Michigan State", "Notre Dame", "Ohio State"], (
        f"rivalry_report: index should be the three rivals in alphabetical order, "
        f"got {list(out.index)}."
    )


def q9_values(ns):
    out = fn(ns, "rivalry_report")(games(), opponents())
    assert_frame_matches(
        out, ref.rivalry_report(games(), opponents()), "rivalry_report", tol=1e-2
    )


def q9_robustness(ns):
    """The rival list must come from the opponents table, not from memory."""
    opp = opponents().copy()
    opp["is_rival"] = opp["opponent"].isin(["Wisconsin", "Iowa"])
    out = fn(ns, "rivalry_report")(games(), opp)
    want = ref.rivalry_report(games(), opp)
    assert_frame_matches(
        out, want, "rivalry_report (rivals redefined as Iowa and Wisconsin)", tol=1e-2
    )


# ----------------------------------------------------------------- Question 10
def q10_structure(ns):
    out = fn(ns, "weather_scoring")(games())
    assert_is(out, pd.DataFrame, "weather_scoring")
    assert list(out.index) == ["Cloudy", "Overcast", "Rain", "Snow", "Sunny", "Windy"], (
        f"weather_scoring: index should be the six weather values in alphabetical "
        f"order, got {list(out.index)}."
    )
    assert list(out.columns) == ["Away", "Home", "Neutral"], (
        f"weather_scoring: columns should be ['Away', 'Home', 'Neutral'], got {list(out.columns)}."
    )


def q10_values(ns):
    out = fn(ns, "weather_scoring")(games())
    assert_frame_matches(out, ref.weather_scoring(games()), "weather_scoring", tol=1e-2)


def q10_keeps_the_gap(ns):
    out = fn(ns, "weather_scoring")(games())
    assert pd.isna(out.at["Snow", "Neutral"]), (
        "weather_scoring: Michigan never played a neutral-site game in the snow, so "
        "that cell should stay NaN -- do not fill it in."
    )


def q10_robustness(ns):
    subset = games()[games()["season"] < 2018]
    out = fn(ns, "weather_scoring")(subset)
    want = ref.weather_scoring(subset)
    assert_frame_matches(out, want, "weather_scoring (2010-2017)", tol=1e-2)


# ------------------------------------------------------------------- registry
QUESTIONS = [
    {
        "number": 1,
        "title": "Kickoff -- load the data",
        "checks": [
            (3, "returns a DataFrame of the right size", q1_type_and_shape),
            (3, "game_id is a unique index", q1_index),
            (4, "columns, dtypes and spot-checked values", q1_dtypes_and_values),
        ],
    },
    {
        "number": 2,
        "title": "Scoreboard math -- derived columns",
        "checks": [
            (3, "the three new columns exist", q2_columns_present),
            (5, "the values are right", q2_values),
            (2, "the input frame was not mutated", q2_does_not_mutate),
        ],
    },
    {
        "number": 3,
        "title": "Best and worst -- idxmax / idxmin",
        "checks": [
            (2, "returns a 2-tuple of game_ids", q3_shape),
            (5, "the right two games", q3_values),
            (3, "works on a different slice of the schedule", q3_robustness),
        ],
    },
    {
        "number": 4,
        "title": "Follow the money -- string cleaning",
        "checks": [
            (3, "a float Series named ticket_price", q4_type),
            (3, "unreported prices become NaN", q4_missing_handled),
            (4, "every price converted correctly", q4_values),
        ],
    },
    {
        "number": 5,
        "title": "Season report card -- groupby",
        "checks": [
            (3, "shape, column order and season index", q5_structure),
            (4, "the values are right", q5_values),
            (3, "works on a different set of seasons", q5_robustness),
        ],
    },
    {
        "number": 6,
        "title": "Under the lights -- parsing times",
        "checks": [
            (3, "a Day/Night Series", q6_structure),
            (4, "the win percentages are right", q6_values),
            (3, "works on home games only", q6_robustness),
        ],
    },
    {
        "number": 7,
        "title": "Counting the crowd -- missing data",
        "checks": [
            (2, "a complete attendance Series", q7_no_missing),
            (2, "reported attendance left alone", q7_untouched_rows),
            (4, "gaps filled with the right group median", q7_values),
            (2, "works on a different slice of the schedule", q7_robustness),
        ],
    },
    {
        "number": 8,
        "title": "Know your enemy -- merging",
        "checks": [
            (3, "shape and a merge that keeps 195 rows", q8_structure),
            (4, "the values and the sort order are right", q8_values),
            (3, "works when the opponents table changes", q8_robustness),
        ],
    },
    {
        "number": 9,
        "title": "The rivalry report",
        "checks": [
            (3, "shape, column order and rival index", q9_structure),
            (4, "the values are right", q9_values),
            (3, "rivals are read from the opponents table", q9_robustness),
        ],
    },
    {
        "number": 10,
        "title": "Weather or not -- pivot tables",
        "checks": [
            (2, "a weather-by-site pivot table", q10_structure),
            (4, "the averages are right", q10_values),
            (1, "the empty cell stays empty", q10_keeps_the_gap),
            (3, "works on a different set of seasons", q10_robustness),
        ],
    },
]

POINTS_PER_QUESTION = 10

assert len(QUESTIONS) == 10
for _q in QUESTIONS:
    _total = sum(w for w, _, _ in _q["checks"])
    assert _total == POINTS_PER_QUESTION, (
        f"Question {_q['number']} checks sum to {_total}, not {POINTS_PER_QUESTION}."
    )
