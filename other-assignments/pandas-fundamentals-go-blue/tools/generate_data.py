"""
Generate the simulated "Go Blue" datasets used by the pandas fundamentals
assignment.

The datasets are *simulated*. Team names, conferences, stadiums and the
coaching timeline are real, but every score, attendance figure, temperature
and ticket price is randomly generated from a fixed seed. Nothing in here
should be quoted as a real Michigan football statistic.

Run from the assignment root:

    python tools/generate_data.py

It rewrites data/games.csv and data/opponents.csv byte-for-byte identically
every time, so the autograder's expected answers stay stable.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 1817  # the year the University of Michigan was founded
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

SEASONS = list(range(2010, 2025))

# Real coaching timeline for Michigan football.
COACHES = {
    **{y: "Rich Rodriguez" for y in [2010]},
    **{y: "Brady Hoke" for y in range(2011, 2015)},
    **{y: "Jim Harbaugh" for y in range(2015, 2024)},
    **{y: "Sherrone Moore" for y in [2024]},
}

# opponent -> (conference, mascot, home_state, stadium, capacity, founded, strength)
# "strength" only drives the simulation; it is not written to disk.
OPPONENTS = {
    "Ohio State":        ("Big Ten", "Buckeyes", "OH", "Ohio Stadium", 102780, 1870, 0.93),
    "Michigan State":    ("Big Ten", "Spartans", "MI", "Spartan Stadium", 75005, 1855, 0.74),
    "Penn State":        ("Big Ten", "Nittany Lions", "PA", "Beaver Stadium", 106572, 1855, 0.82),
    "Wisconsin":         ("Big Ten", "Badgers", "WI", "Camp Randall Stadium", 75822, 1848, 0.78),
    "Iowa":              ("Big Ten", "Hawkeyes", "IA", "Kinnick Stadium", 69250, 1847, 0.70),
    "Minnesota":         ("Big Ten", "Golden Gophers", "MN", "Huntington Bank Stadium", 50805, 1851, 0.60),
    "Nebraska":          ("Big Ten", "Cornhuskers", "NE", "Memorial Stadium", 85458, 1869, 0.66),
    "Illinois":          ("Big Ten", "Fighting Illini", "IL", "Memorial Stadium", 60670, 1867, 0.52),
    "Indiana":           ("Big Ten", "Hoosiers", "IN", "Memorial Stadium", 52626, 1820, 0.50),
    "Purdue":            ("Big Ten", "Boilermakers", "IN", "Ross-Ade Stadium", 57236, 1869, 0.54),
    "Northwestern":      ("Big Ten", "Wildcats", "IL", "Ryan Field", 47330, 1851, 0.55),
    "Maryland":          ("Big Ten", "Terrapins", "MD", "SECU Stadium", 51802, 1856, 0.53),
    "Rutgers":           ("Big Ten", "Scarlet Knights", "NJ", "SHI Stadium", 52454, 1766, 0.45),
    "Notre Dame":        ("Independent", "Fighting Irish", "IN", "Notre Dame Stadium", 77622, 1842, 0.84),
    "Western Michigan":  ("MAC", "Broncos", "MI", "Waldo Stadium", 30200, 1903, 0.30),
    "Central Michigan":  ("MAC", "Chippewas", "MI", "Kelly/Shorts Stadium", 30255, 1892, 0.27),
    "Eastern Michigan":  ("MAC", "Eagles", "MI", "Rynearson Stadium", 30200, 1849, 0.22),
    "Bowling Green":     ("MAC", "Falcons", "OH", "Doyt Perry Stadium", 24000, 1910, 0.25),
    "Akron":             ("MAC", "Zips", "OH", "InfoCision Stadium", 30000, 1870, 0.20),
    "Miami (OH)":        ("MAC", "RedHawks", "OH", "Yager Stadium", 24286, 1809, 0.26),
    "Air Force":         ("Mountain West", "Falcons", "CO", "Falcon Stadium", 46692, 1954, 0.44),
    "UNLV":              ("Mountain West", "Rebels", "NV", "Allegiant Stadium", 65000, 1957, 0.33),
    "Hawaii":            ("Mountain West", "Rainbow Warriors", "HI", "Ching Complex", 15000, 1907, 0.31),
    "Colorado":          ("Pac-12", "Buffaloes", "CO", "Folsom Field", 50183, 1876, 0.48),
    "Washington":        ("Pac-12", "Huskies", "WA", "Husky Stadium", 70138, 1861, 0.76),
    "Utah":              ("Pac-12", "Utes", "UT", "Rice-Eccles Stadium", 51444, 1850, 0.72),
    "Alabama":           ("SEC", "Crimson Tide", "AL", "Bryant-Denny Stadium", 100077, 1831, 0.95),
    "Florida":           ("SEC", "Gators", "FL", "Ben Hill Griffin Stadium", 88548, 1853, 0.79),
    "Virginia Tech":     ("ACC", "Hokies", "VA", "Lane Stadium", 65632, 1872, 0.62),
    "Appalachian State": ("Sun Belt", "Mountaineers", "NC", "Kidd Brewer Stadium", 30000, 1899, 0.40),
    # These two never show up on the schedule below -- they exist so that a
    # merge has to prove it does not invent rows.
    "Boston College":    ("ACC", "Eagles", "MA", "Alumni Stadium", 44500, 1863, 0.56),
    "Oregon":            ("Pac-12", "Ducks", "OR", "Autzen Stadium", 54000, 1876, 0.83),
}

RIVALS = {"Ohio State", "Michigan State", "Notre Dame"}

BIG_TEN_POOL = [t for t, v in OPPONENTS.items() if v[0] == "Big Ten"]
NONCON_POOL = [
    "Notre Dame", "Western Michigan", "Central Michigan", "Eastern Michigan",
    "Bowling Green", "Akron", "Miami (OH)", "Air Force", "UNLV", "Hawaii",
    "Colorado", "Washington", "Utah", "Alabama", "Florida", "Virginia Tech",
    "Appalachian State",
]

NEUTRAL_SITES = ["Ford Field", "AT&T Stadium", "Mercedes-Benz Stadium", "Lucas Oil Stadium"]

KICKOFFS = ["12:00 PM", "12:00 PM", "3:30 PM", "3:30 PM", "4:00 PM",
            "7:00 PM", "7:30 PM", "8:00 PM", "9:00 PM"]

WEATHER = ["Sunny", "Cloudy", "Overcast", "Rain", "Snow", "Windy"]
WEATHER_P = [0.34, 0.26, 0.16, 0.13, 0.05, 0.06]

# How good Michigan is in a given season (drives the simulated scores).
TEAM_RATING = {
    2010: 0.55, 2011: 0.72, 2012: 0.70, 2013: 0.62, 2014: 0.55,
    2015: 0.76, 2016: 0.88, 2017: 0.70, 2018: 0.85, 2019: 0.78,
    2020: 0.52, 2021: 0.87, 2022: 0.92, 2023: 0.95, 2024: 0.66,
}


def first_saturday_of_september(year: int) -> dt.date:
    d = dt.date(year, 9, 1)
    while d.weekday() != 5:  # 5 == Saturday
        d += dt.timedelta(days=1)
    return d


def build_schedule(rng: np.random.Generator, season: int) -> list[dict]:
    """Thirteen games: 4 non-conference, 9 Big Ten, Ohio State always last."""
    noncon = list(rng.choice(NONCON_POOL, size=4, replace=False))
    big_ten = [t for t in BIG_TEN_POOL if t != "Ohio State"]
    conf = list(rng.choice(big_ten, size=8, replace=False))

    opponents = noncon + conf
    rng.shuffle(opponents)
    opponents.append("Ohio State")  # The Game closes every season.

    # 7 home, 5 away, 1 neutral. The Game alternates like it does in real life.
    sites = ["Home"] * 7 + ["Away"] * 5
    rng.shuffle(sites)
    sites.append("Home" if season % 2 == 0 else "Away")
    # Turn one early non-conference game into a neutral-site kickoff classic.
    neutral_slot = int(rng.integers(0, 3))
    sites[neutral_slot] = "Neutral"

    start = first_saturday_of_september(season)
    rows = []
    for week, (opp, site) in enumerate(zip(opponents, sites), start=1):
        date = start + dt.timedelta(days=7 * (week - 1))
        rows.append({"week": week, "date": date, "opponent": opp, "site": site})
    return rows


def simulate() -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(SEED)
    records = []

    for season in SEASONS:
        um = TEAM_RATING[season]
        for game in build_schedule(rng, season):
            opp = game["opponent"]
            conference, mascot, state, stadium, capacity, founded, opp_rating = OPPONENTS[opp]
            site = game["site"]
            date = game["date"]

            home_edge = {"Home": 0.06, "Away": -0.06, "Neutral": 0.0}[site]
            edge = (um + home_edge) - opp_rating

            um_pts = 24 + 42 * edge + rng.normal(0, 8)
            op_pts = 24 - 30 * edge + rng.normal(0, 8)
            um_pts = int(np.clip(round(um_pts / 3.0) * 3 + rng.integers(0, 2), 0, 77))
            op_pts = int(np.clip(round(op_pts / 3.0) * 3 + rng.integers(0, 2), 0, 77))
            if um_pts == op_pts:  # no ties in college football
                um_pts += 3 if rng.random() < 0.55 else -3
                um_pts = max(um_pts, 0)

            if site == "Home":
                venue = "Michigan Stadium"
                crowd = rng.normal(109_500, 2_400)
            elif site == "Away":
                venue = stadium
                crowd = capacity * rng.uniform(0.88, 1.02)
            else:
                venue = NEUTRAL_SITES[int(rng.integers(0, len(NEUTRAL_SITES)))]
                crowd = rng.normal(62_000, 6_500)
            attendance = int(np.clip(round(crowd), 12_000, 115_109))

            month = date.month
            base_temp = {8: 78, 9: 71, 10: 58, 11: 43, 12: 34}.get(month, 50)
            temperature = round(float(rng.normal(base_temp, 9)), 1)

            weather = WEATHER[int(rng.choice(len(WEATHER), p=WEATHER_P))]
            if temperature > 45 and weather == "Snow":
                weather = "Cloudy"

            kickoff = KICKOFFS[int(rng.integers(0, len(KICKOFFS)))]

            # Students only buy tickets to home games.
            students = int(rng.normal(19_500, 1_800)) if site == "Home" else np.nan

            price = 55 + 180 * opp_rating + rng.normal(0, 18)
            if opp in RIVALS:
                price *= 1.9
            if site != "Home":
                price *= 0.75
            price = max(round(float(price), 2), 18.0)

            records.append({
                "game_id": f"{season}-W{game['week']:02d}",
                "season": season,
                "week": game["week"],
                "date": date.isoformat(),
                "kickoff": kickoff,
                "opponent": opp,
                "site": site,
                "stadium": venue,
                "michigan_points": um_pts,
                "opponent_points": op_pts,
                "attendance": attendance,
                "temperature_f": temperature,
                "weather": weather,
                "student_tickets_sold": students,
                "avg_ticket_price": f"${price:,.2f}",
                "head_coach": COACHES[season],
            })

    games = pd.DataFrame.from_records(records)

    # Punch holes in the data so students have to deal with missing values.
    holes = rng.choice(len(games), size=int(len(games) * 0.07), replace=False)
    games.loc[holes, "attendance"] = np.nan
    holes = rng.choice(len(games), size=int(len(games) * 0.04), replace=False)
    games.loc[holes, "temperature_f"] = np.nan

    # Rough up the ticket prices the way a real export from a ticketing system
    # would be rough: stray whitespace, and a few rows the box office never
    # reported at all. Note that "unavailable" is not one of the strings
    # read_csv treats as missing, so it survives the round trip to disk.
    messy = rng.choice(len(games), size=8, replace=False)
    games.loc[messy, "avg_ticket_price"] = (
        "  " + games.loc[messy, "avg_ticket_price"].astype(str) + " "
    )
    missing = rng.choice(len(games), size=5, replace=False)
    games.loc[missing, "avg_ticket_price"] = "unavailable"

    opponents = pd.DataFrame(
        [
            {
                "opponent": name,
                "conference": meta[0],
                "mascot": meta[1],
                "home_state": meta[2],
                "home_stadium": meta[3],
                "stadium_capacity": meta[4],
                "founded": meta[5],
                "is_rival": name in RIVALS,
            }
            for name, meta in OPPONENTS.items()
        ]
    ).sort_values("opponent", ignore_index=True)

    return games, opponents


def main() -> None:
    games, opponents = simulate()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    games.to_csv(DATA_DIR / "games.csv", index=False)
    opponents.to_csv(DATA_DIR / "opponents.csv", index=False)

    wins = (games["michigan_points"] > games["opponent_points"]).sum()
    print(f"games.csv      {games.shape[0]} rows x {games.shape[1]} cols")
    print(f"opponents.csv  {opponents.shape[0]} rows x {opponents.shape[1]} cols")
    print(f"simulated record: {wins}-{len(games) - wins}")


if __name__ == "__main__":
    main()
