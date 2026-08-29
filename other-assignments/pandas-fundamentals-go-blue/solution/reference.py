"""
Reference solutions for the "Go Blue: A Pandas Data Exploration" assignment.

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

GAMES_CSV = DATA_DIR / "games.csv"
OPPONENTS_CSV = DATA_DIR / "opponents.csv"


# ---------------------------------------------------------------- Question 1
def load_games(path=GAMES_CSV) -> pd.DataFrame:
    games = pd.read_csv(path, parse_dates=["date"])
    return games.set_index("game_id")


def load_opponents(path=OPPONENTS_CSV) -> pd.DataFrame:
    return pd.read_csv(path)


# ---------------------------------------------------------------- Question 2
def add_result_columns(games: pd.DataFrame) -> pd.DataFrame:
    out = games.copy()
    out["point_diff"] = out["michigan_points"] - out["opponent_points"]
    out["total_points"] = out["michigan_points"] + out["opponent_points"]
    out["won"] = out["michigan_points"] > out["opponent_points"]
    return out


# ---------------------------------------------------------------- Question 3
def best_and_worst(games: pd.DataFrame) -> tuple[str, str]:
    diff = games["michigan_points"] - games["opponent_points"]
    return (diff.idxmax(), diff.idxmin())


# ---------------------------------------------------------------- Question 4
def ticket_prices(games: pd.DataFrame) -> pd.Series:
    cleaned = games["avg_ticket_price"].astype(str).str.strip().str.replace(
        "$", "", regex=False
    ).str.replace(",", "", regex=False)
    prices = pd.to_numeric(cleaned, errors="coerce")
    prices.name = "ticket_price"
    return prices


# ---------------------------------------------------------------- Question 5
def season_report_card(games: pd.DataFrame) -> pd.DataFrame:
    won = games["michigan_points"] > games["opponent_points"]
    grouped = games.assign(_won=won).groupby("season")
    out = pd.DataFrame(
        {
            "wins": grouped["_won"].sum().astype(int),
            "losses": (grouped.size() - grouped["_won"].sum()).astype(int),
            "points_for": grouped["michigan_points"].sum().astype(int),
            "points_against": grouped["opponent_points"].sum().astype(int),
        }
    )
    out["win_pct"] = (out["wins"] / (out["wins"] + out["losses"])).round(3)
    return out.sort_index()


# ---------------------------------------------------------------- Question 6
def night_game_split(games: pd.DataFrame) -> pd.Series:
    hour = pd.to_datetime(games["kickoff"], format="%I:%M %p").dt.hour
    label = np.where(hour >= 18, "Night", "Day")
    won = games["michigan_points"] > games["opponent_points"]
    pct = won.groupby(label).mean().round(3)
    pct = pct.reindex(["Day", "Night"])
    pct.name = "win_pct"
    pct.index.name = "time_of_day"
    return pct


# ---------------------------------------------------------------- Question 7
def filled_attendance(games: pd.DataFrame) -> pd.Series:
    medians = games.groupby("site")["attendance"].transform("median")
    filled = games["attendance"].fillna(medians).astype(float)
    filled.name = "attendance"
    return filled


# ---------------------------------------------------------------- Question 8
def record_by_conference(games: pd.DataFrame, opponents: pd.DataFrame) -> pd.DataFrame:
    merged = games.merge(opponents, on="opponent", how="left")
    merged["_won"] = merged["michigan_points"] > merged["opponent_points"]
    grouped = merged.groupby("conference")
    out = pd.DataFrame(
        {
            "games": grouped.size().astype(int),
            "wins": grouped["_won"].sum().astype(int),
        }
    )
    out["win_pct"] = (out["wins"] / out["games"]).round(3)
    out = out.sort_values(
        ["win_pct", "conference"], ascending=[False, True]
    )
    return out


# ---------------------------------------------------------------- Question 9
def rivalry_report(games: pd.DataFrame, opponents: pd.DataFrame) -> pd.DataFrame:
    rivals = opponents.loc[opponents["is_rival"], "opponent"]
    played = games[games["opponent"].isin(rivals)].copy()
    played["_won"] = played["michigan_points"] > played["opponent_points"]
    played["_diff"] = played["michigan_points"] - played["opponent_points"]
    grouped = played.groupby("opponent")
    out = pd.DataFrame(
        {
            "games": grouped.size().astype(int),
            "wins": grouped["_won"].sum().astype(int),
        }
    )
    out["losses"] = (out["games"] - out["wins"]).astype(int)
    out["win_pct"] = (out["wins"] / out["games"]).round(3)
    out["avg_point_diff"] = grouped["_diff"].mean().round(2)
    out = out[["games", "wins", "losses", "win_pct", "avg_point_diff"]]
    return out.sort_index()


# --------------------------------------------------------------- Question 10
def weather_scoring(games: pd.DataFrame) -> pd.DataFrame:
    table = games.pivot_table(
        index="weather",
        columns="site",
        values="michigan_points",
        aggfunc="mean",
    ).round(2)
    return table.sort_index()
