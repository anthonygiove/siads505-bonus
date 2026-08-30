"""
Reference solutions for "Hardwood: Grouping, Windows and Reshaping".

INSTRUCTORS: keep this file (and this whole `solution/` folder) out of the
copy you hand to students. `grading/build_expected.py` reads it to produce
`grading/expected_values.json`, which is what the hidden tests compare
against, so if you change a question spec, change it here and rebuild.

Every function here is written the way the assignment asks students to write
it: it takes its inputs as arguments and returns a fresh object rather than
mutating anything in place.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

BOX_CSV = DATA_DIR / "box_scores.csv"
GAMES_CSV = DATA_DIR / "games.csv"
ROSTER_CSV = DATA_DIR / "roster.csv"

CLASS_ORDER = ["Fr", "So", "Jr", "Sr"]
POSITION_ORDER = ["G", "F", "C"]


# ---------------------------------------------------------------- Question 1
def load_box_scores(path=BOX_CSV) -> pd.DataFrame:
    box = pd.read_csv(path, parse_dates=["date"])
    return box.set_index(["game_id", "player_id"]).sort_index()


def load_games(path=GAMES_CSV) -> pd.DataFrame:
    games = pd.read_csv(path, parse_dates=["date"])
    return games.set_index("game_id")


def load_roster(path=ROSTER_CSV) -> pd.DataFrame:
    return pd.read_csv(path)


# ---------------------------------------------------------------- Question 2
def split_shooting(box: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=box.index)
    pairs = [
        ("field_goals", "fg_made", "fg_att"),
        ("three_pointers", "fg3_made", "fg3_att"),
        ("free_throws", "ft_made", "ft_att"),
    ]
    for source, made_col, att_col in pairs:
        parts = box[source].astype("object").str.split("-", expand=True)
        out[made_col] = pd.to_numeric(parts[0], errors="coerce").astype(float)
        out[att_col] = pd.to_numeric(parts[1], errors="coerce").astype(float)
    return out


# ---------------------------------------------------------------- Question 3
def minutes_played(box: pd.DataFrame) -> pd.Series:
    parts = box["minutes"].astype("object").str.split(":", expand=True)
    mins = pd.to_numeric(parts[0], errors="coerce")
    secs = pd.to_numeric(parts[1], errors="coerce")
    out = (mins + secs / 60).astype(float).round(2)
    out.name = "minutes_played"
    return out


# ---------------------------------------------------------------- Question 4
def shooting_rates(box: pd.DataFrame) -> pd.DataFrame:
    shots = split_shooting(box)
    out = pd.DataFrame(index=box.index)
    out["fg_pct"] = (shots["fg_made"] / shots["fg_att"].replace(0, np.nan)).round(3)
    out["fg3_pct"] = (shots["fg3_made"] / shots["fg3_att"].replace(0, np.nan)).round(3)
    out["ft_pct"] = (shots["ft_made"] / shots["ft_att"].replace(0, np.nan)).round(3)
    denominator = 2 * (shots["fg_att"] + 0.44 * shots["ft_att"])
    out["true_shooting"] = (box["points"] / denominator.replace(0, np.nan)).round(3)
    return out


# ---------------------------------------------------------------- Question 5
def player_season_totals(box: pd.DataFrame) -> pd.DataFrame:
    played = box[box["minutes"] != "DNP"].copy()
    played["_minutes"] = minutes_played(played)
    played["_rebounds"] = played["offensive_rebounds"] + played["defensive_rebounds"]

    out = played.groupby(["season", "player"]).agg(
        games_played=("points", "size"),
        minutes=("_minutes", "sum"),
        points=("points", "sum"),
        rebounds=("_rebounds", "sum"),
        assists=("assists", "sum"),
    )
    out["minutes"] = out["minutes"].round(1)
    for col in ("games_played", "points", "rebounds", "assists"):
        out[col] = out[col].astype(int)
    out["ppg"] = (out["points"] / out["games_played"]).round(1)
    return out.sort_index()


# ---------------------------------------------------------------- Question 6
def leading_scorer(box: pd.DataFrame) -> pd.DataFrame:
    played = box[box["minutes"] != "DNP"].copy()
    played["_minutes"] = minutes_played(played)
    played = played.reset_index()
    ordered = played.sort_values(
        ["game_id", "points", "_minutes", "player"],
        ascending=[True, False, False, True],
    )
    best = ordered.groupby("game_id", as_index=False).head(1)
    out = best.set_index("game_id")[["player", "points"]]
    out["points"] = out["points"].astype(int)
    return out.sort_index()


# ---------------------------------------------------------------- Question 7
def rolling_form(games: pd.DataFrame, window: int = 5) -> pd.Series:
    ordered = games.sort_values(["season", "game_no"])
    rolled = ordered.groupby("season")["team_points"].rolling(window).mean()
    rolled = rolled.droplevel("season")
    out = rolled.reindex(games.index).round(2)
    out.name = "rolling_points"
    return out


# ---------------------------------------------------------------- Question 8
def season_leaderboard(box: pd.DataFrame, min_games: int = 20) -> pd.DataFrame:
    totals = player_season_totals(box)
    qualified = totals[totals["games_played"] >= min_games].copy()
    qualified["rank"] = (
        qualified.groupby("season")["ppg"].rank(method="min", ascending=False).astype(int)
    )
    out = qualified[["games_played", "points", "ppg", "rank"]]
    return out.sort_values(["season", "rank", "player"])


# ---------------------------------------------------------------- Question 9
def longest_win_streak(games: pd.DataFrame) -> pd.Series:
    ordered = games.sort_values(["season", "game_no"]).copy()
    ordered["_won"] = ordered["team_points"] > ordered["opponent_points"]
    # Number every run of identical results, then count the wins in each run.
    ordered["_run"] = (
        ordered.groupby("season")["_won"].transform(lambda s: (s != s.shift()).cumsum())
    )
    runs = ordered[ordered["_won"]].groupby(["season", "_run"]).size()
    out = runs.groupby("season").max()
    out = out.reindex(sorted(games["season"].unique()), fill_value=0).astype(int)
    out.name = "longest_win_streak"
    out.index.name = "season"
    return out


# --------------------------------------------------------------- Question 10
def class_scoring(box: pd.DataFrame, roster: pd.DataFrame) -> pd.DataFrame:
    played = box[box["minutes"] != "DNP"].reset_index()
    merged = played.merge(roster, on=["season", "player_id"], how="left")
    table = merged.pivot_table(
        index="class", columns="position", values="points", aggfunc="mean"
    )
    table = table.reindex(index=CLASS_ORDER, columns=POSITION_ORDER).round(2)
    table.index.name = "class"
    table.columns.name = "position"
    return table
