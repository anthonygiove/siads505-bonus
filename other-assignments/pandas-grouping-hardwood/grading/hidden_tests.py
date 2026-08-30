"""
HIDDEN TESTS -- do not distribute with the student notebook.

Each of the ten questions is worth 10 points, split across several checks so
that partial credit is possible. Every question is graded against inputs the
autograder builds itself from the reference loaders, so a student who fumbles
Question 1 can still earn full marks on Questions 2-10.

Most questions also carry a "robustness" check that re-runs the student's
function on a *different* slice of the data, or with a different keyword
argument. Those checks exist to catch answers that were hard-coded after
peeking at the public asserts.
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
def box():
    return ref.load_box_scores()


def games():
    return ref.load_games()


def roster():
    return ref.load_roster()


def season_slice(frame, seasons):
    return frame[frame["season"].isin(seasons)]


# ------------------------------------------------------------------ Question 1
def q1_box_shape(ns):
    out = fn(ns, "load_box_scores")()
    assert_is(out, pd.DataFrame, "load_box_scores")
    assert out.shape == (4160, 17), (
        f"load_box_scores: expected a (4160, 17) frame once game_id and player_id "
        f"are the index, got {out.shape}."
    )


def q1_box_index(ns):
    out = fn(ns, "load_box_scores")()
    assert isinstance(out.index, pd.MultiIndex), (
        f"load_box_scores: the index should be a MultiIndex of (game_id, player_id), "
        f"got a plain {type(out.index).__name__}."
    )
    assert list(out.index.names) == ["game_id", "player_id"], (
        f"load_box_scores: index levels should be ['game_id', 'player_id'], "
        f"got {list(out.index.names)}."
    )
    assert out.index.is_unique, (
        "load_box_scores: (game_id, player_id) should be unique -- one row per player per game."
    )
    assert out.index.is_monotonic_increasing, (
        "load_box_scores: sort the index (`.sort_index()`) so the rows come back in order."
    )
    for col in ("game_id", "player_id"):
        assert col not in out.columns, (
            f"load_box_scores: {col!r} should be in the index, not also a column."
        )


def q1_dtypes_and_games(ns):
    out = fn(ns, "load_box_scores")()
    want = box()
    assert list(out.columns) == list(want.columns), (
        f"load_box_scores: columns should be {list(want.columns)}, got {list(out.columns)}."
    )
    assert pd.api.types.is_datetime64_any_dtype(out["date"]), (
        f"load_box_scores: 'date' should be a datetime column, got dtype {out['date'].dtype}."
    )
    assert out.loc[("2015-G01", "P001"), "player"] == want.loc[("2015-G01", "P001"), "player"]

    g = fn(ns, "load_games")()
    assert_is(g, pd.DataFrame, "load_games")
    assert g.shape == (320, 11), (
        f"load_games: expected a (320, 11) frame once game_id is the index, got {g.shape}."
    )
    assert g.index.name == "game_id", (
        f"load_games: the index should be named 'game_id', got {g.index.name!r}."
    )
    assert pd.api.types.is_datetime64_any_dtype(g["date"]), (
        f"load_games: 'date' should be a datetime column, got dtype {g['date'].dtype}."
    )


# ------------------------------------------------------------------ Question 2
COLS_Q2 = ["fg_made", "fg_att", "fg3_made", "fg3_att", "ft_made", "ft_att"]


def q2_structure(ns):
    out = fn(ns, "split_shooting")(box())
    assert_is(out, pd.DataFrame, "split_shooting")
    assert list(out.columns) == COLS_Q2, (
        f"split_shooting: columns should be {COLS_Q2} in that order, got {list(out.columns)}."
    )
    assert len(out) == 4160, f"split_shooting: expected 4160 rows, got {len(out)}."
    assert_index(out.index, box().index, "split_shooting")
    for col in COLS_Q2:
        assert pd.api.types.is_float_dtype(out[col]), (
            f"split_shooting: {col!r} should be a float column (a DNP has no number), "
            f"got dtype {out[col].dtype}."
        )


def q2_dnp_is_nan(ns):
    out = fn(ns, "split_shooting")(box())
    dnp = box()["minutes"] == "DNP"
    assert int(out.loc[dnp, "fg_att"].isna().sum()) == int(dnp.sum()) == 1134, (
        "split_shooting: every DNP row should be NaN across all six columns -- "
        "a player who did not play did not attempt zero shots, they attempted none."
    )
    assert int(out.loc[~dnp].isna().sum().sum()) == 0, (
        "split_shooting: rows where the player did play should never be NaN."
    )


def q2_values(ns):
    out = fn(ns, "split_shooting")(box())
    assert_frame_matches(out, ref.split_shooting(box()), "split_shooting", tol=1e-9)


def q2_robustness(ns):
    subset = season_slice(box(), [2019, 2020])
    out = fn(ns, "split_shooting")(subset)
    assert_frame_matches(out, ref.split_shooting(subset), "split_shooting (2019-2020)", tol=1e-9)


# ------------------------------------------------------------------ Question 3
def q3_structure(ns):
    out = fn(ns, "minutes_played")(box())
    assert_is(out, pd.Series, "minutes_played")
    assert out.name == "minutes_played", (
        f"minutes_played: the Series should be named 'minutes_played', got {out.name!r}."
    )
    assert pd.api.types.is_float_dtype(out), (
        f"minutes_played: expected a float Series, got dtype {out.dtype}."
    )
    assert len(out) == 4160, f"minutes_played: expected 4160 values, got {len(out)}."
    assert int(out.isna().sum()) == 1134, (
        f"minutes_played: the 1134 'DNP' rows should be NaN, got {int(out.isna().sum())} NaN values."
    )


def q3_values(ns):
    out = fn(ns, "minutes_played")(box())
    assert_series_matches(out, ref.minutes_played(box()), "minutes_played", tol=1e-6)


def q3_seconds_not_dropped(ns):
    """A student who reads only the part before the colon loses the seconds."""
    out = fn(ns, "minutes_played")(box())
    want = ref.minutes_played(box())
    fractional = want.dropna() % 1 != 0
    assert fractional.sum() > 100, "internal: the fixture should contain partial minutes"
    assert_values(
        out.dropna()[fractional.to_numpy()],
        want.dropna()[fractional.to_numpy()],
        "minutes_played (rows with seconds on the clock)",
        tol=1e-6,
    )


def q3_robustness(ns):
    subset = season_slice(box(), [2022])
    out = fn(ns, "minutes_played")(subset)
    assert_series_matches(out, ref.minutes_played(subset), "minutes_played (2022)", tol=1e-6)


# ------------------------------------------------------------------ Question 4
COLS_Q4 = ["fg_pct", "fg3_pct", "ft_pct", "true_shooting"]


def q4_structure(ns):
    out = fn(ns, "shooting_rates")(box())
    assert_is(out, pd.DataFrame, "shooting_rates")
    assert list(out.columns) == COLS_Q4, (
        f"shooting_rates: columns should be {COLS_Q4} in that order, got {list(out.columns)}."
    )
    assert len(out) == 4160, f"shooting_rates: expected 4160 rows, got {len(out)}."
    assert_index(out.index, box().index, "shooting_rates")


def q4_no_division_blowups(ns):
    out = fn(ns, "shooting_rates")(box())
    numeric = out[COLS_Q4].to_numpy(dtype=float)
    assert not np.isinf(numeric).any(), (
        "shooting_rates: dividing by zero attempts produced inf. A player who took no "
        "threes has no three-point percentage -- that cell should be NaN."
    )
    shots = ref.split_shooting(box())
    no_threes = shots["fg3_att"] == 0
    assert bool(out.loc[no_threes, "fg3_pct"].isna().all()), (
        "shooting_rates: rows with zero three-point attempts should be NaN, not 0.0."
    )
    assert bool(out.loc[shots["ft_att"] == 0, "ft_pct"].isna().all()), (
        "shooting_rates: rows with zero free-throw attempts should be NaN, not 0.0."
    )


def q4_values(ns):
    out = fn(ns, "shooting_rates")(box())
    assert_frame_matches(out, ref.shooting_rates(box()), "shooting_rates", tol=1e-6)


def q4_robustness(ns):
    subset = season_slice(box(), [2016, 2023])
    out = fn(ns, "shooting_rates")(subset)
    assert_frame_matches(out, ref.shooting_rates(subset), "shooting_rates (2016 & 2023)", tol=1e-6)


# ------------------------------------------------------------------ Question 5
COLS_Q5 = ["games_played", "minutes", "points", "rebounds", "assists", "ppg"]


def q5_structure(ns):
    out = fn(ns, "player_season_totals")(box())
    assert_is(out, pd.DataFrame, "player_season_totals")
    assert list(out.columns) == COLS_Q5, (
        f"player_season_totals: columns should be {COLS_Q5} in that order, got {list(out.columns)}."
    )
    assert isinstance(out.index, pd.MultiIndex), (
        "player_season_totals: the index should be a (season, player) MultiIndex."
    )
    assert list(out.index.names) == ["season", "player"], (
        f"player_season_totals: index levels should be ['season', 'player'], "
        f"got {list(out.index.names)}."
    )
    want = ref.player_season_totals(box())
    assert len(out) == len(want), (
        f"player_season_totals: expected {len(want)} rows (one per player per season they "
        f"actually appeared in a game), got {len(out)}."
    )


def q5_drops_dnp(ns):
    out = fn(ns, "player_season_totals")(box())
    want = ref.player_season_totals(box())
    assert_values(
        out["games_played"].reindex(want.index),
        want["games_played"],
        "player_season_totals ['games_played'] -- a DNP is not a game played",
    )


def q5_values(ns):
    out = fn(ns, "player_season_totals")(box())
    assert_frame_matches(out, ref.player_season_totals(box()), "player_season_totals", tol=1e-6)


def q5_robustness(ns):
    subset = season_slice(box(), [2017, 2018, 2019])
    out = fn(ns, "player_season_totals")(subset)
    assert_frame_matches(
        out, ref.player_season_totals(subset), "player_season_totals (2017-2019)", tol=1e-6
    )


# ------------------------------------------------------------------ Question 6
def q6_structure(ns):
    out = fn(ns, "leading_scorer")(box())
    assert_is(out, pd.DataFrame, "leading_scorer")
    assert list(out.columns) == ["player", "points"], (
        f"leading_scorer: columns should be ['player', 'points'], got {list(out.columns)}."
    )
    assert out.index.name == "game_id", (
        f"leading_scorer: index should be named 'game_id', got {out.index.name!r}."
    )
    assert len(out) == 320, (
        f"leading_scorer: expected exactly one row per game (320), got {len(out)}."
    )
    assert out.index.is_unique, "leading_scorer: one row per game -- game_id must be unique."


def q6_values(ns):
    out = fn(ns, "leading_scorer")(box())
    assert_frame_matches(out, ref.leading_scorer(box()), "leading_scorer", tol=1e-6)


def q6_tiebreak(ns):
    """When two players tie on points the one who played more minutes wins."""
    out = fn(ns, "leading_scorer")(box())
    want = ref.leading_scorer(box())
    played = box()[box()["minutes"] != "DNP"]
    top = played.groupby("game_id")["points"].transform("max")
    tied = played[played["points"] == top].groupby("game_id").size() > 1
    contested = list(tied.index[tied])
    assert len(contested) > 10, "internal: the fixture should contain tied games"
    assert_frame_matches(
        out.loc[contested], want.loc[contested], "leading_scorer (games with a tie at the top)"
    )


def q6_robustness(ns):
    subset = season_slice(box(), [2021, 2024])
    out = fn(ns, "leading_scorer")(subset)
    assert_frame_matches(out, ref.leading_scorer(subset), "leading_scorer (2021 & 2024)", tol=1e-6)


# ------------------------------------------------------------------ Question 7
def q7_structure(ns):
    out = fn(ns, "rolling_form")(games())
    assert_is(out, pd.Series, "rolling_form")
    assert out.name == "rolling_points", (
        f"rolling_form: the Series should be named 'rolling_points', got {out.name!r}."
    )
    assert len(out) == 320, f"rolling_form: expected 320 values, got {len(out)}."
    assert_index(out.index, games().index, "rolling_form")
    assert int(out.isna().sum()) == 40, (
        f"rolling_form: the first four games of each of the ten seasons have no "
        f"five-game window yet, so 40 values should be NaN -- got {int(out.isna().sum())}."
    )


def q7_no_season_bleed(ns):
    """Game 1 of a new season must not average in the end of the last one."""
    out = fn(ns, "rolling_form")(games())
    openers = games().index[games()["game_no"] <= 4]
    assert bool(out.loc[openers].isna().all()), (
        "rolling_form: the window has to restart every season. Games 1-4 of a season "
        "cannot borrow scores from the previous one."
    )


def q7_values(ns):
    out = fn(ns, "rolling_form")(games())
    assert_series_matches(out, ref.rolling_form(games()), "rolling_form", tol=1e-6)


def q7_window_argument(ns):
    out = fn(ns, "rolling_form")(games(), window=10)
    assert_series_matches(out, ref.rolling_form(games(), window=10), "rolling_form (window=10)", tol=1e-6)


# ------------------------------------------------------------------ Question 8
COLS_Q8 = ["games_played", "points", "ppg", "rank"]


def q8_structure(ns):
    out = fn(ns, "season_leaderboard")(box())
    assert_is(out, pd.DataFrame, "season_leaderboard")
    assert list(out.columns) == COLS_Q8, (
        f"season_leaderboard: columns should be {COLS_Q8} in that order, got {list(out.columns)}."
    )
    assert list(out.index.names) == ["season", "player"], (
        f"season_leaderboard: index levels should be ['season', 'player'], "
        f"got {list(out.index.names)}."
    )
    want = ref.season_leaderboard(box())
    assert len(out) == len(want), (
        f"season_leaderboard: expected {len(want)} qualified player-seasons, got {len(out)}."
    )


def q8_ranks_restart(ns):
    out = fn(ns, "season_leaderboard")(box())
    want = ref.season_leaderboard(box())
    firsts = out.reset_index().groupby("season")["rank"].min()
    assert (firsts == 1).all(), (
        "season_leaderboard: rank should restart at 1 in every season, not run 1..N "
        "across the whole decade."
    )
    assert_values(
        out["rank"].reindex(want.index).astype(float),
        want["rank"].astype(float),
        "season_leaderboard ['rank']",
    )


def q8_values(ns):
    out = fn(ns, "season_leaderboard")(box())
    assert_frame_matches(out, ref.season_leaderboard(box()), "season_leaderboard", tol=1e-6)


def q8_min_games_argument(ns):
    out = fn(ns, "season_leaderboard")(box(), min_games=28)
    want = ref.season_leaderboard(box(), min_games=28)
    assert_frame_matches(out, want, "season_leaderboard (min_games=28)", tol=1e-6)


# ------------------------------------------------------------------ Question 9
def q9_structure(ns):
    out = fn(ns, "longest_win_streak")(games())
    assert_is(out, pd.Series, "longest_win_streak")
    assert out.name == "longest_win_streak", (
        f"longest_win_streak: the Series should be named 'longest_win_streak', got {out.name!r}."
    )
    assert out.index.name == "season", (
        f"longest_win_streak: the index should be named 'season', got {out.index.name!r}."
    )
    assert list(out.index) == list(range(2015, 2025)), (
        "longest_win_streak: one row per season, 2015..2024 ascending."
    )


def q9_values(ns):
    out = fn(ns, "longest_win_streak")(games())
    assert_series_matches(out, ref.longest_win_streak(games()), "longest_win_streak")


def q9_winless_season(ns):
    """A season with no wins at all is a streak of zero, not a missing row."""
    losses = pd.DataFrame(
        {
            "season": [2015, 2015, 2015, 2016, 2016],
            "game_no": [1, 2, 3, 1, 2],
            "team_points": [60, 61, 62, 80, 81],
            "opponent_points": [70, 71, 72, 70, 90],
        },
        index=pd.Index(["a", "b", "c", "d", "e"], name="game_id"),
    )
    out = fn(ns, "longest_win_streak")(losses)
    assert_series_matches(out, ref.longest_win_streak(losses), "longest_win_streak (a winless season)")


def q9_robustness(ns):
    subset = games()[games()["game_no"] <= 14]
    out = fn(ns, "longest_win_streak")(subset)
    assert_series_matches(
        out, ref.longest_win_streak(subset), "longest_win_streak (first 14 games only)"
    )


# ----------------------------------------------------------------- Question 10
def q10_structure(ns):
    out = fn(ns, "class_scoring")(box(), roster())
    assert_is(out, pd.DataFrame, "class_scoring")
    assert list(out.index) == ["Fr", "So", "Jr", "Sr"], (
        f"class_scoring: rows should be ['Fr', 'So', 'Jr', 'Sr'] in academic order, "
        f"not alphabetical -- got {list(out.index)}."
    )
    assert list(out.columns) == ["G", "F", "C"], (
        f"class_scoring: columns should be ['G', 'F', 'C'] in that order, got {list(out.columns)}."
    )


def q10_values(ns):
    out = fn(ns, "class_scoring")(box(), roster())
    assert_frame_matches(out, ref.class_scoring(box(), roster()), "class_scoring", tol=1e-2)


def q10_reads_the_roster(ns):
    """Class and position have to come from the roster, not from memory."""
    shuffled = roster().copy()
    swap = {"Fr": "Sr", "So": "Jr", "Jr": "So", "Sr": "Fr"}
    shuffled["class"] = shuffled["class"].map(swap)
    out = fn(ns, "class_scoring")(box(), shuffled)
    assert_frame_matches(
        out, ref.class_scoring(box(), shuffled), "class_scoring (classes swapped)", tol=1e-2
    )


def q10_robustness(ns):
    subset = season_slice(box(), [2018, 2019, 2020])
    out = fn(ns, "class_scoring")(subset, roster())
    assert_frame_matches(
        out, ref.class_scoring(subset, roster()), "class_scoring (2018-2020)", tol=1e-2
    )


# ------------------------------------------------------------------- registry
QUESTIONS = [
    {
        "number": 1,
        "title": "Tip-off -- load the box scores",
        "checks": [
            (3, "returns a DataFrame of the right size", q1_box_shape),
            (3, "a sorted, unique (game_id, player_id) MultiIndex", q1_box_index),
            (4, "columns, dtypes, and the games loader", q1_dtypes_and_games),
        ],
    },
    {
        "number": 2,
        "title": "Splitting the line -- made-attempted strings",
        "checks": [
            (2, "six float columns in the right order", q2_structure),
            (2, "a DNP is NaN, not zero", q2_dnp_is_nan),
            (4, "every split is right", q2_values),
            (2, "works on a different slice of the decade", q2_robustness),
        ],
    },
    {
        "number": 3,
        "title": "Stopping the clock -- MM:SS to minutes",
        "checks": [
            (2, "a float Series named minutes_played", q3_structure),
            (3, "the values are right", q3_values),
            (3, "the seconds are not thrown away", q3_seconds_not_dropped),
            (2, "works on a different season", q3_robustness),
        ],
    },
    {
        "number": 4,
        "title": "Shooting rates -- dividing without blowing up",
        "checks": [
            (2, "four rate columns on the same index", q4_structure),
            (3, "zero attempts give NaN, never inf or 0", q4_no_division_blowups),
            (3, "the rates are right", q4_values),
            (2, "works on a different slice of the decade", q4_robustness),
        ],
    },
    {
        "number": 5,
        "title": "Player season totals -- named aggregation",
        "checks": [
            (3, "a (season, player) frame with the right columns", q5_structure),
            (2, "DNP games are not counted as games played", q5_drops_dnp),
            (3, "the totals are right", q5_values),
            (2, "works on a different set of seasons", q5_robustness),
        ],
    },
    {
        "number": 6,
        "title": "Leading scorer -- one row per game",
        "checks": [
            (2, "exactly one row per game", q6_structure),
            (4, "the right player in each game", q6_values),
            (2, "ties broken by minutes, then alphabetically", q6_tiebreak),
            (2, "works on a different slice of the decade", q6_robustness),
        ],
    },
    {
        "number": 7,
        "title": "Rolling form -- window functions",
        "checks": [
            (3, "a rolling_points Series aligned to games", q7_structure),
            (2, "the window restarts each season", q7_no_season_bleed),
            (3, "the averages are right", q7_values),
            (2, "honours the window argument", q7_window_argument),
        ],
    },
    {
        "number": 8,
        "title": "Season leaderboard -- ranking within groups",
        "checks": [
            (2, "shape, column order and index", q8_structure),
            (3, "rank restarts at 1 every season", q8_ranks_restart),
            (3, "the leaderboard is right", q8_values),
            (2, "honours the min_games argument", q8_min_games_argument),
        ],
    },
    {
        "number": 9,
        "title": "Longest win streak -- runs of consecutive results",
        "checks": [
            (2, "a longest_win_streak Series indexed by season", q9_structure),
            (4, "the streaks are right", q9_values),
            (2, "a winless season reports 0", q9_winless_season),
            (2, "works on a truncated schedule", q9_robustness),
        ],
    },
    {
        "number": 10,
        "title": "Class and position -- merge, then pivot",
        "checks": [
            (2, "rows and columns in the order asked for", q10_structure),
            (4, "the averages are right", q10_values),
            (2, "class and position come from the roster", q10_reads_the_roster),
            (2, "works on a different set of seasons", q10_robustness),
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
