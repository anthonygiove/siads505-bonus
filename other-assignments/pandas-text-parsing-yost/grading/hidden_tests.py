"""
HIDDEN TESTS -- do not distribute with the student notebook.

Each of the ten questions is worth 10 points, split across several checks so
that partial credit is possible. Every question is graded against inputs the
autograder builds itself from the reference loaders, so a student who fumbles
Question 1 can still earn full marks on Questions 2-10.

Most questions also carry a "robustness" check that re-runs the student's
function on a *different* slice of the season -- a handful of whole games
pulled out of the feed. Those checks exist to catch answers that were
hard-coded after peeking at the public asserts.
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


def _label(value):
    return str(tuple(value)) if isinstance(value, tuple) else str(value)


def assert_index(actual, expected, what):
    got = [_label(v) for v in actual]
    want = [_label(v) for v in expected]
    if got == want:
        return
    if len(got) != len(want):
        raise AssertionError(
            f"{what}: expected {len(want)} rows, got {len(got)}."
        )
    first = next(i for i in range(len(got)) if got[i] != want[i])
    raise AssertionError(
        f"{what}: the index does not match. Row {first} should be "
        f"{want[first]}, got {got[first]}."
    )


def _first_mismatch(actual: pd.Series, expected: pd.Series, tol: float):
    """Index of the first differing value, or None. NaN == NaN here."""
    got, want = actual.to_numpy(), expected.to_numpy()
    if got.dtype.kind in "fiub" and want.dtype.kind in "fiub":
        a, b = got.astype(float), want.astype(float)
        bad = ~((np.abs(a - b) <= tol) | (np.isnan(a) & np.isnan(b)))
    else:
        bad = np.array(
            [not _close(x, y, tol) for x, y in zip(got.tolist(), want.tolist())],
            dtype=bool,
        )
    hits = np.flatnonzero(bad)
    return int(hits[0]) if len(hits) else None


def assert_values(actual: pd.Series, expected: pd.Series, what: str, tol=1e-6):
    where = _first_mismatch(actual, expected, tol)
    if where is None:
        return
    key = _label(expected.index[where])
    raise AssertionError(
        f"{what}: value at {key} should be {expected.iloc[where]!r}, "
        f"got {actual.iloc[where]!r}."
    )


def assert_series_matches(actual, expected, what, tol=1e-6):
    assert_is(actual, pd.Series, what)
    assert len(actual) == len(expected), (
        f"{what}: expected {len(expected)} values, got {len(actual)}."
    )
    assert_index(actual.index, expected.index, what)
    assert_values(actual, expected, what, tol)


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
        assert_values(actual[col], expected[col], f"{what} [{col!r}]", tol)



# -------------------------------------------------------------- shared inputs
MICHIGAN_JERSEYS = {
    1, 2, 4, 6, 8, 9, 10, 11, 12, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
    26, 27, 28, 29, 31, 44,
}

# Six whole games pulled out of the middle of the season. Whole games, because
# half a game log answers half of these questions wrongly on purpose.
SLICE_GAMES = ["2024-G07", "2024-G12", "2024-G20", "2024-G26", "2024-G33", "2024-G40"]


def events():
    return ref.load_events()


def games():
    return ref.load_games()


def roster():
    return ref.load_roster()


def events_slice():
    e = events()
    return e[e["game_id"].isin(SLICE_GAMES)]


def games_slice():
    return games().loc[SLICE_GAMES]


# ------------------------------------------------------------------ Question 1
def q1_events_shape(ns):
    out = fn(ns, "load_events")()
    assert_is(out, pd.DataFrame, "load_events")
    assert out.shape == (4065, 3), (
        f"load_events: expected a (4065, 3) frame once event_id is the index, got {out.shape}."
    )
    assert out.index.name == "event_id", (
        f"load_events: the index should be named 'event_id', got {out.index.name!r}."
    )
    assert out.index.is_unique, "load_events: event_id values should be unique."


def q1_events_columns(ns):
    out = fn(ns, "load_events")()
    assert list(out.columns) == ["game_id", "period", "description"], (
        f"load_events: columns should be ['game_id', 'period', 'description'], "
        f"got {list(out.columns)}."
    )
    assert "event_id" not in out.columns, (
        "load_events: event_id should be the index, not also a column."
    )
    assert pd.api.types.is_integer_dtype(out["period"]), (
        f"load_events: 'period' should be an integer column, got dtype {out['period'].dtype}."
    )
    assert sorted(out["period"].unique().tolist()) == [1, 2, 3, 4], (
        "load_events: periods should be 1, 2, 3 and 4 (overtime)."
    )


def q1_games_and_roster(ns):
    g = fn(ns, "load_games")()
    assert_is(g, pd.DataFrame, "load_games")
    assert g.shape == (41, 12), (
        f"load_games: expected a (41, 12) frame once game_id is the index, got {g.shape}."
    )
    assert g.index.name == "game_id", (
        f"load_games: the index should be named 'game_id', got {g.index.name!r}."
    )
    assert pd.api.types.is_datetime64_any_dtype(g["date"]), (
        f"load_games: 'date' should be a datetime column, got dtype {g['date'].dtype}."
    )

    r = fn(ns, "load_roster")()
    assert_is(r, pd.DataFrame, "load_roster")
    assert r.shape == (26, 8), f"load_roster: expected a (26, 8) frame, got {r.shape}."
    assert "jersey" in r.columns, "load_roster: keep 'jersey' as a column, not the index."


# ------------------------------------------------------------------ Question 2
COLS_Q2 = ["event_type", "clock", "team", "jersey", "player"]


def q2_structure(ns):
    out = fn(ns, "parse_events")(events())
    assert_is(out, pd.DataFrame, "parse_events")
    assert list(out.columns) == COLS_Q2, (
        f"parse_events: columns should be {COLS_Q2} in that order, got {list(out.columns)}."
    )
    assert len(out) == 4065, f"parse_events: expected 4065 rows, got {len(out)}."
    assert_index(out.index, events().index, "parse_events")
    assert pd.api.types.is_integer_dtype(out["jersey"]), (
        f"parse_events: 'jersey' should be an integer column, got dtype {out['jersey'].dtype}."
    )


def q2_every_row_parsed(ns):
    """Anchoring to ^ without stripping loses every row the scraper padded."""
    out = fn(ns, "parse_events")(events())
    unparsed = out["event_type"].isna().sum()
    assert int(unparsed) == 0, (
        f"parse_events: {int(unparsed)} rows came back empty. Some descriptions carry "
        "leading or trailing whitespace and doubled spaces -- strip first, and match "
        "runs of whitespace with \\s+ rather than a single space."
    )
    assert not out["player"].str.startswith(" ").any(), (
        "parse_events: 'player' still has leading whitespace on some rows."
    )
    assert not out["player"].str.endswith(" ").any(), (
        "parse_events: 'player' still has trailing whitespace on some rows."
    )


def q2_values(ns):
    out = fn(ns, "parse_events")(events())
    assert_frame_matches(out, ref.parse_events(events()), "parse_events")


def q2_robustness(ns):
    subset = events_slice()
    out = fn(ns, "parse_events")(subset)
    assert_frame_matches(out, ref.parse_events(subset), "parse_events (six games)")


# ------------------------------------------------------------------ Question 3
def q3_structure(ns):
    out = fn(ns, "elapsed_seconds")(events())
    assert_is(out, pd.Series, "elapsed_seconds")
    assert out.name == "elapsed_seconds", (
        f"elapsed_seconds: the Series should be named 'elapsed_seconds', got {out.name!r}."
    )
    assert pd.api.types.is_integer_dtype(out), (
        f"elapsed_seconds: expected whole seconds, got dtype {out.dtype}."
    )
    assert len(out) == 4065, f"elapsed_seconds: expected 4065 values, got {len(out)}."
    assert out.min() > 0, (
        "elapsed_seconds: the clock counts *down*. An event at 19:16 of the first "
        "period happened 44 seconds in, not 1,156."
    )


def q3_regulation(ns):
    out = fn(ns, "elapsed_seconds")(events())
    want = ref.elapsed_seconds(events())
    regulation = events()["period"] != 4
    assert_series_matches(
        out[regulation.to_numpy()],
        want[regulation.to_numpy()],
        "elapsed_seconds (regulation)",
    )


def q3_overtime(ns):
    """Overtime is five minutes long, not twenty."""
    out = fn(ns, "elapsed_seconds")(events())
    want = ref.elapsed_seconds(events())
    overtime = (events()["period"] == 4).to_numpy()
    assert overtime.sum() > 20, "internal: the fixture should contain overtime events"
    assert_series_matches(out[overtime], want[overtime], "elapsed_seconds (overtime)")


def q3_robustness(ns):
    subset = events_slice()
    out = fn(ns, "elapsed_seconds")(subset)
    assert_series_matches(out, ref.elapsed_seconds(subset), "elapsed_seconds (six games)")


# ------------------------------------------------------------------ Question 4
def q4_structure(ns):
    out = fn(ns, "assist_credits")(events())
    assert_is(out, pd.Series, "assist_credits")
    assert out.name == "assists", (
        f"assist_credits: the Series should be named 'assists', got {out.name!r}."
    )
    assert out.index.name == "jersey", (
        f"assist_credits: the index should be named 'jersey', got {out.index.name!r}."
    )
    assert pd.api.types.is_integer_dtype(out), (
        f"assist_credits: assists are whole numbers, got dtype {out.dtype}."
    )
    assert list(out.index) == sorted(out.index), (
        "assist_credits: sort the index by jersey number, ascending."
    )


def q4_michigan_only(ns):
    out = fn(ns, "assist_credits")(events())
    strays = sorted(set(int(j) for j in out.index) - MICHIGAN_JERSEYS)
    assert not strays, (
        f"assist_credits: jersey numbers {strays} are not on the Michigan roster -- "
        "you are counting assists on the other team's goals too."
    )


def q4_values(ns):
    out = fn(ns, "assist_credits")(events())
    assert_series_matches(out, ref.assist_credits(events()), "assist_credits")


def q4_robustness(ns):
    subset = events_slice()
    out = fn(ns, "assist_credits")(subset)
    assert_series_matches(out, ref.assist_credits(subset), "assist_credits (six games)")


# ------------------------------------------------------------------ Question 5
def q5_structure(ns):
    out = fn(ns, "penalty_summary")(events())
    assert_is(out, pd.DataFrame, "penalty_summary")
    assert list(out.columns) == ["count", "minutes"], (
        f"penalty_summary: columns should be ['count', 'minutes'], got {list(out.columns)}."
    )
    assert out.index.name == "infraction", (
        f"penalty_summary: the index should be named 'infraction', got {out.index.name!r}."
    )
    want = ref.penalty_summary(events())
    assert set(out.index) == set(want.index), (
        f"penalty_summary: expected these infractions: {sorted(want.index)}, "
        f"got {sorted(out.index)}."
    )


def q5_multiword_infractions(ns):
    """'Delay of Game' and 'Cross-checking' break a naive one-word pattern."""
    out = fn(ns, "penalty_summary")(events())
    for label in ("Delay of Game", "Too Many Men", "Cross-checking", "Contact to the Head"):
        assert label in out.index, (
            f"penalty_summary: {label!r} is missing. Infraction names contain spaces "
            "and hyphens -- match everything up to the comma, not a single word."
        )


def q5_values(ns):
    out = fn(ns, "penalty_summary")(events())
    assert_frame_matches(out, ref.penalty_summary(events()), "penalty_summary")


def q5_robustness(ns):
    subset = events_slice()
    out = fn(ns, "penalty_summary")(subset)
    assert_frame_matches(out, ref.penalty_summary(subset), "penalty_summary (six games)")


# ------------------------------------------------------------------ Question 6
def q6_structure(ns):
    out = fn(ns, "roster_details")(roster())
    assert_is(out, pd.DataFrame, "roster_details")
    assert list(out.columns) == ["last_name", "height_in", "home_region"], (
        f"roster_details: columns should be ['last_name', 'height_in', 'home_region'], "
        f"got {list(out.columns)}."
    )
    assert out.index.name == "jersey", (
        f"roster_details: the index should be named 'jersey', got {out.index.name!r}."
    )
    assert len(out) == 26, f"roster_details: expected 26 rows, got {len(out)}."


def q6_last_names(ns):
    out = fn(ns, "roster_details")(roster())
    tricky = {8: "St. Pierre", 6: "O'Halloran", 2: "Vander-Meer"}
    for jersey, want in tricky.items():
        got = out.at[jersey, "last_name"]
        assert got == want, (
            f"roster_details: #{jersey} should be {want!r}, got {got!r}. A surname can "
            "contain a period, an apostrophe or a hyphen -- take everything after the "
            "first initial rather than the next word."
        )


def q6_heights(ns):
    out = fn(ns, "roster_details")(roster())
    assert pd.api.types.is_integer_dtype(out["height_in"]), (
        f"roster_details: 'height_in' should be whole inches, got dtype {out['height_in'].dtype}."
    )
    assert_values(
        out["height_in"], ref.roster_details(roster())["height_in"], "roster_details ['height_in']"
    )


def q6_regions(ns):
    out = fn(ns, "roster_details")(roster())
    assert_values(
        out["home_region"], ref.roster_details(roster())["home_region"],
        "roster_details ['home_region']",
    )


# ------------------------------------------------------------------ Question 7
COLS_Q7 = ["jersey", "goals", "assists", "points"]


def q7_structure(ns):
    out = fn(ns, "scoring_leaders")(events(), roster())
    assert_is(out, pd.DataFrame, "scoring_leaders")
    assert list(out.columns) == COLS_Q7, (
        f"scoring_leaders: columns should be {COLS_Q7} in that order, got {list(out.columns)}."
    )
    assert out.index.name == "player", (
        f"scoring_leaders: the index should be named 'player', got {out.index.name!r}."
    )
    want = ref.scoring_leaders(events(), roster())
    assert len(out) == len(want), (
        f"scoring_leaders: expected {len(want)} players with at least one point, got {len(out)}."
    )
    assert (out["points"] == out["goals"] + out["assists"]).all(), (
        "scoring_leaders: points should be goals plus assists."
    )


def q7_values(ns):
    out = fn(ns, "scoring_leaders")(events(), roster())
    assert_frame_matches(out, ref.scoring_leaders(events(), roster()), "scoring_leaders")


def q7_tiebreak(ns):
    """Level on points, the player with more goals is listed first."""
    out = fn(ns, "scoring_leaders")(events(), roster())
    want = ref.scoring_leaders(events(), roster())
    tied = want["points"].duplicated(keep=False)
    assert tied.sum() > 4, "internal: the fixture should contain players tied on points"
    assert_index(
        out.index[tied.to_numpy()], want.index[tied.to_numpy()],
        "scoring_leaders (players tied on points)",
    )


def q7_robustness(ns):
    subset = events_slice()
    out = fn(ns, "scoring_leaders")(subset, roster())
    assert_frame_matches(
        out, ref.scoring_leaders(subset, roster()), "scoring_leaders (six games)"
    )


# ------------------------------------------------------------------ Question 8
def q8_structure(ns):
    out = fn(ns, "strength_breakdown")(events())
    assert_is(out, pd.DataFrame, "strength_breakdown")
    assert list(out.index) == ["Michigan", "Opponent"], (
        f"strength_breakdown: rows should be ['Michigan', 'Opponent'], got {list(out.index)}."
    )
    assert list(out.columns) == ["EV", "PP", "SH", "EN", "PS"], (
        f"strength_breakdown: columns should be ['EV', 'PP', 'SH', 'EN', 'PS'] in that "
        f"order, got {list(out.columns)}."
    )
    assert pd.api.types.is_integer_dtype(out.to_numpy().dtype), (
        "strength_breakdown: these are counts of goals -- keep them whole numbers."
    )


def q8_empty_column(ns):
    """No penalty-shot goals happened. The column still has to be there, at 0."""
    out = fn(ns, "strength_breakdown")(events())
    assert int(out["PS"].sum()) == 0, "strength_breakdown: 'PS' should total 0 this season."
    assert (out["PS"] == 0).all(), (
        "strength_breakdown: nobody scored on a penalty shot, so the PS column is a "
        "column of zeroes -- a count of zero, not a missing value."
    )


def q8_values(ns):
    out = fn(ns, "strength_breakdown")(events())
    assert_frame_matches(out, ref.strength_breakdown(events()), "strength_breakdown")


def q8_robustness(ns):
    subset = events_slice()
    out = fn(ns, "strength_breakdown")(subset)
    assert_frame_matches(out, ref.strength_breakdown(subset), "strength_breakdown (six games)")


# ------------------------------------------------------------------ Question 9
def q9_structure(ns):
    out = fn(ns, "first_goal_times")(events(), games())
    assert_is(out, pd.Series, "first_goal_times")
    assert out.name == "first_goal_second", (
        f"first_goal_times: the Series should be named 'first_goal_second', got {out.name!r}."
    )
    assert pd.api.types.is_float_dtype(out), (
        f"first_goal_times: expected a float Series (a shutout has no value), "
        f"got dtype {out.dtype}."
    )
    assert_index(out.index, games().index, "first_goal_times")


def q9_shutouts_are_nan(ns):
    out = fn(ns, "first_goal_times")(events(), games())
    blanked = games()[games()["michigan_goals"] == 0].index
    assert len(blanked) == 5, "internal: the fixture should contain five shutouts"
    assert bool(out.loc[blanked].isna().all()), (
        "first_goal_times: Michigan was shut out five times. Those games have no first "
        "goal -- the answer is NaN, not 0 and not a dropped row."
    )
    assert int(out.isna().sum()) == 5, (
        f"first_goal_times: expected exactly 5 NaN values, got {int(out.isna().sum())}."
    )


def q9_values(ns):
    out = fn(ns, "first_goal_times")(events(), games())
    assert_series_matches(out, ref.first_goal_times(events(), games()), "first_goal_times")


def q9_robustness(ns):
    out = fn(ns, "first_goal_times")(events_slice(), games_slice())
    want = ref.first_goal_times(events_slice(), games_slice())
    assert_series_matches(out, want, "first_goal_times (six games)")


# ----------------------------------------------------------------- Question 10
COLS_Q10 = ["period", "clock", "jersey", "player"]


def q10_structure(ns):
    out = fn(ns, "game_winning_goals")(events(), games())
    assert_is(out, pd.DataFrame, "game_winning_goals")
    assert list(out.columns) == COLS_Q10, (
        f"game_winning_goals: columns should be {COLS_Q10} in that order, got {list(out.columns)}."
    )
    assert out.index.name == "game_id", (
        f"game_winning_goals: the index should be named 'game_id', got {out.index.name!r}."
    )
    wins = games()[games()["michigan_goals"] > games()["opponent_goals"]]
    assert len(out) == len(wins) == 23, (
        f"game_winning_goals: one row for each of the 23 wins and nothing else, got {len(out)}."
    )
    assert set(out.index) <= set(wins.index), (
        "game_winning_goals: a game Michigan did not win has no game-winning goal."
    )


def q10_values(ns):
    out = fn(ns, "game_winning_goals")(events(), games())
    assert_frame_matches(out, ref.game_winning_goals(events(), games()), "game_winning_goals")


def q10_counts_in_order(ns):
    """The winner is the Nth Michigan goal in *time* order, not row order."""
    out = fn(ns, "game_winning_goals")(events(), games())
    want = ref.game_winning_goals(events(), games())
    late = want[want["period"] >= 3].index
    assert len(late) > 3, "internal: the fixture should contain late game-winners"
    assert_frame_matches(
        out.loc[late], want.loc[late], "game_winning_goals (winners scored in the third or later)"
    )


def q10_robustness(ns):
    out = fn(ns, "game_winning_goals")(events_slice(), games_slice())
    want = ref.game_winning_goals(events_slice(), games_slice())
    assert_frame_matches(out, want, "game_winning_goals (six games)")


# ------------------------------------------------------------------- registry
QUESTIONS = [
    {
        "number": 1,
        "title": "Warm-ups -- load the feed",
        "checks": [
            (3, "an events frame of the right size, indexed by event_id", q1_events_shape),
            (3, "the right columns and dtypes", q1_events_columns),
            (4, "the games and roster loaders", q1_games_and_roster),
        ],
    },
    {
        "number": 2,
        "title": "Reading the sheet -- named capture groups",
        "checks": [
            (2, "five columns on the same index", q2_structure),
            (3, "every one of the 4,065 rows parsed", q2_every_row_parsed),
            (3, "the parsed fields are right", q2_values),
            (2, "works on a different slice of the season", q2_robustness),
        ],
    },
    {
        "number": 3,
        "title": "Clock math -- a clock that counts down",
        "checks": [
            (2, "an integer elapsed_seconds Series", q3_structure),
            (3, "regulation times are right", q3_regulation),
            (3, "overtime is five minutes, not twenty", q3_overtime),
            (2, "works on a different slice of the season", q3_robustness),
        ],
    },
    {
        "number": 4,
        "title": "Assist credits -- findall and explode",
        "checks": [
            (2, "an assists Series indexed by jersey", q4_structure),
            (2, "only Michigan goals are counted", q4_michigan_only),
            (4, "the assist totals are right", q4_values),
            (2, "works on a different slice of the season", q4_robustness),
        ],
    },
    {
        "number": 5,
        "title": "The penalty box -- two fields from one match",
        "checks": [
            (2, "shape, column order and index", q5_structure),
            (2, "multi-word infractions survive", q5_multiword_infractions),
            (4, "the counts and minutes are right", q5_values),
            (2, "works on a different slice of the season", q5_robustness),
        ],
    },
    {
        "number": 6,
        "title": "Roster details -- three kinds of string surgery",
        "checks": [
            (2, "shape, column order and jersey index", q6_structure),
            (3, "surnames with periods, apostrophes and hyphens", q6_last_names),
            (3, "feet-and-inches converted to inches", q6_heights),
            (2, "home state, province or country", q6_regions),
        ],
    },
    {
        "number": 7,
        "title": "Scoring leaders -- combine, merge, sort",
        "checks": [
            (2, "shape, column order and player index", q7_structure),
            (4, "goals, assists and points are right", q7_values),
            (2, "ties on points broken by goals", q7_tiebreak),
            (2, "works on a different slice of the season", q7_robustness),
        ],
    },
    {
        "number": 8,
        "title": "Special teams -- a crosstab with a missing column",
        "checks": [
            (3, "two rows, five columns, in the order asked for", q8_structure),
            (2, "the strength nobody used is a zero, not a gap", q8_empty_column),
            (3, "the counts are right", q8_values),
            (2, "works on a different slice of the season", q8_robustness),
        ],
    },
    {
        "number": 9,
        "title": "First blood -- a genuine missing value",
        "checks": [
            (3, "a float Series aligned to games", q9_structure),
            (3, "a shutout is NaN, not zero", q9_shutouts_are_nan),
            (2, "the times are right", q9_values),
            (2, "works on a different slice of the season", q9_robustness),
        ],
    },
    {
        "number": 10,
        "title": "The game winner -- counting inside a group",
        "checks": [
            (3, "one row per win, with the right columns", q10_structure),
            (3, "the right goal in each game", q10_values),
            (2, "goals are counted in time order", q10_counts_in_order),
            (2, "works on a different slice of the season", q10_robustness),
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
