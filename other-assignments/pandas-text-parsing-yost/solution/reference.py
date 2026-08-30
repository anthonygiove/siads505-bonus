"""
Reference solutions for "The Yost Feed: Regex, Text and Time".

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

EVENTS_CSV = DATA_DIR / "events.csv"
GAMES_CSV = DATA_DIR / "games.csv"
ROSTER_CSV = DATA_DIR / "roster.csv"

PERIOD_SECONDS = 20 * 60
OT_SECONDS = 5 * 60

EVENT_PATTERN = (
    r"^(?P<event_type>[A-Z]+)\s+"
    r"(?P<clock>\d{1,2}:\d{2})\s+"
    r"(?P<team>[A-Z]+)\s+"
    r"#(?P<jersey>\d+)\s+"
    r"(?P<player>[^(]+)"
)

STRENGTHS = ["EV", "PP", "SH", "EN", "PS"]


def _clean(events: pd.DataFrame) -> pd.Series:
    """The feed is scraped; strip before anchoring a pattern to the start."""
    return events["description"].astype("object").str.strip()


# ---------------------------------------------------------------- Question 1
def load_events(path=EVENTS_CSV) -> pd.DataFrame:
    events = pd.read_csv(path)
    return events.set_index("event_id")


def load_games(path=GAMES_CSV) -> pd.DataFrame:
    games = pd.read_csv(path, parse_dates=["date"])
    return games.set_index("game_id")


def load_roster(path=ROSTER_CSV) -> pd.DataFrame:
    return pd.read_csv(path)


# ---------------------------------------------------------------- Question 2
def parse_events(events: pd.DataFrame) -> pd.DataFrame:
    out = _clean(events).str.extract(EVENT_PATTERN)
    out["jersey"] = pd.to_numeric(out["jersey"]).astype("int64")
    out["player"] = out["player"].str.strip()
    return out[["event_type", "clock", "team", "jersey", "player"]]


# ---------------------------------------------------------------- Question 3
def elapsed_seconds(events: pd.DataFrame) -> pd.Series:
    clock = parse_events(events)["clock"]
    parts = clock.str.split(":", expand=True)
    remaining = pd.to_numeric(parts[0]) * 60 + pd.to_numeric(parts[1])

    period = events["period"].astype("int64")
    length = np.where(period == 4, OT_SECONDS, PERIOD_SECONDS)
    out = ((period - 1) * PERIOD_SECONDS + (length - remaining)).astype("int64")
    out.name = "elapsed_seconds"
    return out


# ---------------------------------------------------------------- Question 4
def assist_credits(events: pd.DataFrame) -> pd.Series:
    parsed = parse_events(events)
    michigan_goals = (parsed["event_type"] == "GOAL") & (parsed["team"] == "MICH")

    credits = _clean(events)[michigan_goals].str.extract(r"\(A:([^)]*)\)")[0]
    jerseys = credits.dropna().str.findall(r"#(\d+)").explode()

    out = jerseys.astype("int64").value_counts().sort_index().astype("int64")
    out.name = "assists"
    out.index.name = "jersey"
    return out


# ---------------------------------------------------------------- Question 5
def penalty_summary(events: pd.DataFrame) -> pd.DataFrame:
    parsed = parse_events(events)
    taken = (parsed["event_type"] == "PENALTY") & (parsed["team"] == "MICH")

    detail = _clean(events)[taken].str.extract(
        r"\((?P<infraction>[^,]+),\s*(?P<minutes>\d+)\s*min\)"
    )
    detail["minutes"] = pd.to_numeric(detail["minutes"])

    out = detail.groupby("infraction").agg(
        count=("minutes", "size"), minutes=("minutes", "sum")
    )
    out = out.astype("int64").reset_index()
    out = out.sort_values(["minutes", "infraction"], ascending=[False, True])
    return out.set_index("infraction")


# ---------------------------------------------------------------- Question 6
def roster_details(roster: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=pd.Index(roster["jersey"].astype("int64"), name="jersey"))

    out["last_name"] = roster["player"].str.extract(r"^\S+\s+(.+)$")[0].to_numpy()

    height = roster["height"].str.split("-", expand=True)
    feet = pd.to_numeric(height[0])
    inches = pd.to_numeric(height[1])
    out["height_in"] = (feet * 12 + inches).astype("int64").to_numpy()

    out["home_region"] = (
        roster["hometown"].str.rsplit(",", n=1).str[1].str.strip().to_numpy()
    )
    return out.sort_index()


# ---------------------------------------------------------------- Question 7
def scoring_leaders(events: pd.DataFrame, roster: pd.DataFrame) -> pd.DataFrame:
    parsed = parse_events(events)
    michigan_goals = (parsed["event_type"] == "GOAL") & (parsed["team"] == "MICH")

    goals = parsed.loc[michigan_goals, "jersey"].value_counts()
    assists = assist_credits(events)

    tally = pd.DataFrame({"goals": goals, "assists": assists}).fillna(0).astype("int64")
    tally.index.name = "jersey"
    tally["points"] = tally["goals"] + tally["assists"]
    tally = tally[tally["points"] > 0].reset_index()

    merged = tally.merge(roster[["jersey", "player"]], on="jersey", how="left")
    merged = merged.sort_values(
        ["points", "goals", "player"], ascending=[False, False, True]
    )
    return merged.set_index("player")[["jersey", "goals", "assists", "points"]]


# ---------------------------------------------------------------- Question 8
def strength_breakdown(events: pd.DataFrame) -> pd.DataFrame:
    parsed = parse_events(events)
    goals = parsed["event_type"] == "GOAL"

    tag = _clean(events)[goals].str.extract(r"\[(\w+)\]")[0]
    tag.name = "strength"
    side = pd.Series(
        np.where(parsed.loc[goals, "team"] == "MICH", "Michigan", "Opponent"),
        index=tag.index,
        name="team",
    )

    table = pd.crosstab(side, tag)
    table = table.reindex(
        index=["Michigan", "Opponent"], columns=STRENGTHS, fill_value=0
    ).astype("int64")
    table.index.name = "team"
    table.columns.name = "strength"
    return table


# ---------------------------------------------------------------- Question 9
def first_goal_times(events: pd.DataFrame, games: pd.DataFrame) -> pd.Series:
    parsed = parse_events(events)
    michigan_goals = (parsed["event_type"] == "GOAL") & (parsed["team"] == "MICH")

    elapsed = elapsed_seconds(events)[michigan_goals]
    first = elapsed.groupby(events.loc[michigan_goals, "game_id"]).min()

    out = first.reindex(games.index).astype(float)
    out.name = "first_goal_second"
    out.index.name = "game_id"
    return out


# --------------------------------------------------------------- Question 10
def game_winning_goals(events: pd.DataFrame, games: pd.DataFrame) -> pd.DataFrame:
    parsed = parse_events(events)
    michigan_goals = (parsed["event_type"] == "GOAL") & (parsed["team"] == "MICH")

    scored = parsed.loc[michigan_goals, ["clock", "jersey", "player"]].copy()
    scored["game_id"] = events.loc[michigan_goals, "game_id"]
    scored["period"] = events.loc[michigan_goals, "period"].astype("int64")
    scored["_elapsed"] = elapsed_seconds(events)[michigan_goals]

    scored = scored.sort_values(["game_id", "_elapsed"])
    scored["_goal_no"] = scored.groupby("game_id").cumcount() + 1

    wins = games[games["michigan_goals"] > games["opponent_goals"]]
    target = (wins["opponent_goals"] + 1).rename("_target").to_frame()

    merged = scored.merge(target, left_on="game_id", right_index=True, how="inner")
    winners = merged[merged["_goal_no"] == merged["_target"]]

    out = winners.set_index("game_id")[["period", "clock", "jersey", "player"]]
    return out.sort_index()
