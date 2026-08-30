"""
Generate the simulated "Hardwood" datasets used by the grouping, windows and
reshaping assignment.

The datasets are *simulated*. Conference names, arena names and the shape of a
Big Ten basketball season are real; every player, every box-score line and
every final score is randomly generated from a fixed seed. Nothing in here
should be quoted as a real Michigan basketball statistic.

Run from the assignment root:

    python tools/generate_data.py

It rewrites data/box_scores.csv, data/games.csv and data/roster.csv
byte-for-byte identically every time, so the autograder's expected answers
stay stable.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 1989  # the year Michigan won the men's basketball national championship
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# `season` is the year the season *ends*: 2024 means the 2023-24 season.
SEASONS = list(range(2015, 2025))
GAMES_PER_SEASON = 32
ROSTER_SIZE = 13          # players who dress
REDSHIRTS_PER_SEASON = 2  # on the roster, never in a box score

CLASSES = ["Fr", "So", "Jr", "Sr"]
POSITIONS = ["G", "G", "G", "G", "F", "F", "F", "C"]

# opponent -> (conference, site_bias, strength)
OPPONENTS = {
    "Ohio State":       ("Big Ten", 0.74),
    "Michigan State":   ("Big Ten", 0.80),
    "Purdue":           ("Big Ten", 0.82),
    "Wisconsin":        ("Big Ten", 0.76),
    "Indiana":          ("Big Ten", 0.68),
    "Illinois":         ("Big Ten", 0.72),
    "Iowa":             ("Big Ten", 0.70),
    "Maryland":         ("Big Ten", 0.71),
    "Penn State":       ("Big Ten", 0.63),
    "Rutgers":          ("Big Ten", 0.58),
    "Northwestern":     ("Big Ten", 0.57),
    "Minnesota":        ("Big Ten", 0.55),
    "Nebraska":         ("Big Ten", 0.54),
    "Duke":             ("ACC", 0.90),
    "North Carolina":   ("ACC", 0.86),
    "Villanova":        ("Big East", 0.84),
    "Creighton":        ("Big East", 0.72),
    "Xavier":           ("Big East", 0.66),
    "Gonzaga":          ("WCC", 0.88),
    "Kansas":           ("Big 12", 0.89),
    "Texas":            ("Big 12", 0.75),
    "Oregon":           ("Pac-12", 0.73),
    "UCLA":             ("Pac-12", 0.78),
    "Kentucky":         ("SEC", 0.85),
    "Detroit Mercy":    ("Horizon", 0.28),
    "Oakland":          ("Horizon", 0.34),
    "Youngstown State": ("Horizon", 0.30),
    "Central Michigan": ("MAC", 0.33),
    "Western Michigan": ("MAC", 0.31),
    "Toledo":           ("MAC", 0.42),
    "Chicago State":    ("Independent", 0.18),
    "Presbyterian":     ("Big South", 0.22),
    "South Carolina State": ("MEAC", 0.20),
    "Elon":             ("CAA", 0.26),
    "UMass Lowell":     ("America East", 0.24),
}

BIG_TEN = [t for t, meta in OPPONENTS.items() if meta[0] == "Big Ten"]
NONCON = [t for t, meta in OPPONENTS.items() if meta[0] != "Big Ten"]

NEUTRAL_VENUES = [
    "Barclays Center", "T-Mobile Arena", "Mohegan Sun Arena", "Little Caesars Arena",
]
OPPONENT_ARENAS = {
    "Ohio State": "Value City Arena", "Michigan State": "Breslin Center",
    "Purdue": "Mackey Arena", "Wisconsin": "Kohl Center",
    "Indiana": "Simon Skjodt Assembly Hall", "Illinois": "State Farm Center",
    "Iowa": "Carver-Hawkeye Arena", "Maryland": "Xfinity Center",
    "Penn State": "Bryce Jordan Center", "Rutgers": "Jersey Mike's Arena",
    "Northwestern": "Welsh-Ryan Arena", "Minnesota": "Williams Arena",
    "Nebraska": "Pinnacle Bank Arena",
}

# How good Michigan is in a given season (drives the simulated results).
TEAM_RATING = {
    2015: 0.58, 2016: 0.66, 2017: 0.74, 2018: 0.84, 2019: 0.86,
    2020: 0.68, 2021: 0.88, 2022: 0.64, 2023: 0.62, 2024: 0.48,
}

FIRST_NAMES = [
    "Duncan", "Zavier", "Caleb", "Isaiah", "Moussa", "Terrance", "Jaden", "Eli",
    "Franz", "Hunter", "Brandon", "Nolan", "Adrien", "Kobe", "Marcus", "Rowan",
    "Devin", "Micah", "Julian", "Trey", "Owen", "Sebastian", "Grant", "Amir",
    "Cole", "Tobias", "Malachi", "Emmett", "Rafael", "Desmond", "Lucas", "Xavi",
    "Quentin", "Bennett", "Ronan", "Silas", "Tariq", "Vaughn", "Wesley", "Yusuf",
]
LAST_NAMES = [
    "Abrams", "Beaudry", "Castellano", "Danforth", "Ellsworth", "Farrier",
    "Gundersen", "Halvorsen", "Ibarra", "Jankowski", "Kalinowski", "Lindqvist",
    "Marchetti", "Novotny", "Okonkwo", "Pellegrini", "Quintero", "Rasmussen",
    "Stankovic", "Thibodeaux", "Ustinov", "Vandermeer", "Whitcomb", "Xiong",
    "Yamamoto", "Zielinski", "Baptiste", "Cavanaugh", "Delacroix", "Eskridge",
    "Fontaine", "Grzelak", "Hollenbeck", "Iversen", "Janssen", "Kowalczyk",
    "Larsson", "Montoya", "Nakamura", "Ostrowski", "Petrov", "Rendon",
]
HOMETOWNS = [
    "Ann Arbor, MI", "Detroit, MI", "Chicago, IL", "Indianapolis, IN",
    "Columbus, OH", "Toronto, ON", "Brooklyn, NY", "Philadelphia, PA",
    "Atlanta, GA", "Houston, TX", "Los Angeles, CA", "Phoenix, AZ",
    "Minneapolis, MN", "St. Louis, MO", "Nashville, TN", "Milwaukee, WI",
    "Grand Rapids, MI", "Cleveland, OH", "Louisville, KY", "Boston, MA",
]


def season_dates(season: int) -> list[dt.date]:
    """Thirty-two dates from early November to early March, four days apart."""
    start = dt.date(season - 1, 11, 6)
    return [start + dt.timedelta(days=4 * i) for i in range(GAMES_PER_SEASON)]


def build_schedule(rng: np.random.Generator, season: int) -> list[dict]:
    """12 non-conference games, then 20 Big Ten games."""
    noncon = list(rng.choice(NONCON, size=12, replace=False))
    conf = list(rng.choice(BIG_TEN, size=13, replace=False))
    conf = conf + list(rng.choice(conf, size=7, replace=False))  # home-and-home repeats
    rng.shuffle(conf)

    rows = []
    for i, (opp, date) in enumerate(zip(noncon + conf, season_dates(season)), start=1):
        if i <= 12:
            # Non-conference: mostly home, a few neutral-site tournament games.
            site = "Neutral" if 6 <= i <= 8 else "Home"
        else:
            site = "Home" if rng.random() < 0.5 else "Away"
        rows.append({"game_no": i, "date": date, "opponent": opp, "site": site})
    return rows


class Player:
    __slots__ = ("player_id", "name", "jersey", "position", "years",
                 "height_in", "hometown", "skill", "usage", "three_rate")

    def __init__(self, rng, player_id, used_names, used_jerseys):
        while True:
            name = (
                FIRST_NAMES[int(rng.integers(0, len(FIRST_NAMES)))]
                + " "
                + LAST_NAMES[int(rng.integers(0, len(LAST_NAMES)))]
            )
            if name not in used_names:
                used_names.add(name)
                break
        while True:
            jersey = int(rng.integers(0, 56))
            if jersey not in used_jerseys:
                used_jerseys.add(jersey)
                break
        self.player_id = player_id
        self.name = name
        self.jersey = jersey
        self.position = POSITIONS[int(rng.integers(0, len(POSITIONS)))]
        self.years = 1
        self.height_in = int(
            {"G": rng.integers(71, 78), "F": rng.integers(77, 82), "C": rng.integers(80, 85)}[
                self.position
            ]
        )
        self.hometown = HOMETOWNS[int(rng.integers(0, len(HOMETOWNS)))]
        self.skill = float(rng.uniform(0.25, 0.95))
        self.usage = float(rng.uniform(0.12, 0.32))
        self.three_rate = float(
            {"G": rng.uniform(0.35, 0.62), "F": rng.uniform(0.18, 0.45), "C": rng.uniform(0.02, 0.18)}[
                self.position
            ]
        )

    @property
    def klass(self) -> str:
        return CLASSES[min(self.years - 1, 3)]

    def advance(self) -> None:
        self.years += 1
        self.skill = min(self.skill + 0.06, 0.98)


def mmss(minutes: float) -> str:
    total = int(round(minutes * 60))
    return f"{total // 60}:{total % 60:02d}"


def simulate() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(SEED)

    used_names: set[str] = set()
    next_id = 1
    squad: list[Player] = []
    redshirts: list[Player] = []

    # Seed the 2015 roster with a realistic mix of classes rather than
    # thirteen freshmen. `years` is one behind because the season loop calls
    # advance() before it writes anything out.
    _used_jerseys: set[int] = set()
    for _years in [0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3]:
        starter = Player(rng, f"P{next_id:03d}", used_names, _used_jerseys)
        starter.years = _years
        starter.skill = min(starter.skill + 0.06 * _years, 0.98)
        next_id += 1
        squad.append(starter)

    box_rows: list[dict] = []
    game_rows: list[dict] = []
    roster_rows: list[dict] = []

    for season in SEASONS:
        # ---- roster churn: seniors graduate, a few transfer, everyone else
        #      moves up a class, and freshmen fill the gaps.
        for p in squad + redshirts:
            p.advance()
        squad = [p for p in squad if p.years <= 4 and rng.random() > 0.12]
        # A redshirt either joins the rotation the next year or moves on.
        promoted = [p for p in redshirts if p.years <= 4 and rng.random() < 0.5]
        squad.extend(promoted)
        redshirts = []

        used_jerseys = {p.jersey for p in squad}
        while len(squad) < ROSTER_SIZE:
            squad.append(Player(rng, f"P{next_id:03d}", used_names, used_jerseys))
            next_id += 1
        squad = squad[:ROSTER_SIZE]
        used_jerseys = {p.jersey for p in squad}
        while len(redshirts) < REDSHIRTS_PER_SEASON:
            redshirts.append(Player(rng, f"P{next_id:03d}", used_names, used_jerseys))
            next_id += 1

        for p in squad + redshirts:
            roster_rows.append({
                "season": season,
                "player_id": p.player_id,
                "player": p.name,
                "jersey": p.jersey,
                "position": p.position,
                "class": p.klass,
                "height_in": p.height_in,
                "hometown": p.hometown,
                "dressed": p in squad,
            })

        rating = TEAM_RATING[season]
        order = sorted(squad, key=lambda p: -p.skill)

        for game in build_schedule(rng, season):
            game_id = f"{season}-G{game['game_no']:02d}"
            opponent = game["opponent"]
            conference, opp_strength = OPPONENTS[opponent]
            site = game["site"]

            overtime = 1 if rng.random() < 0.06 else 0
            team_minutes = 200 + 25 * overtime

            # ---- who plays tonight
            available = list(order)
            n_dnp = int(rng.integers(2, 6))
            bench_pool = available[5:]
            # The end of the bench sits far more often than the sixth man does.
            bench_weights = np.array([(1.0 - pl.skill) ** 2 + 0.04 for pl in bench_pool])
            bench_weights = bench_weights / bench_weights.sum()
            dnp = set(
                rng.choice(
                    [p.player_id for p in bench_pool],
                    size=n_dnp,
                    replace=False,
                    p=bench_weights,
                )
            )
            playing = [p for p in available if p.player_id not in dnp]

            weights = np.array([p.skill ** 2 for p in playing], dtype=float)
            weights = weights / weights.sum()
            weights = weights * rng.uniform(0.85, 1.15, size=len(playing))
            weights = weights / weights.sum()
            minutes = np.clip(weights * team_minutes, 2.0, 38.0)
            minutes = minutes * (team_minutes / minutes.sum())
            starters = {p.player_id for p in playing[:5]}

            # A college team takes roughly 56 shots a night; hand them out in
            # proportion to minutes played and how much a player likes to shoot.
            team_fga = int(round(rng.normal(56, 4.5))) + 6 * overtime
            shares = np.array([m * pl.usage for pl, m in zip(playing, minutes)])
            shares = shares / shares.sum()

            game_box: list[dict] = []
            for p, mins, share in zip(playing, minutes, shares):
                pace = mins / 40.0
                fga = max(0, int(round(share * team_fga + rng.normal(0, 1.2))))
                fg3a = int(round(fga * p.three_rate * rng.uniform(0.7, 1.3)))
                fg3a = int(np.clip(fg3a, 0, fga))
                fg2a = fga - fg3a

                two_pct = np.clip(rng.normal(0.30 + 0.34 * p.skill, 0.11), 0.05, 0.85)
                three_pct = np.clip(rng.normal(0.18 + 0.28 * p.skill, 0.13), 0.0, 0.75)
                fg2m = int(rng.binomial(fg2a, two_pct)) if fg2a else 0
                fg3m = int(rng.binomial(fg3a, three_pct)) if fg3a else 0
                fgm, fg3m = fg2m + fg3m, fg3m

                fta = max(0, int(round(rng.normal(fga * 0.30, 1.4))))
                ft_pct = np.clip(rng.normal(0.55 + 0.28 * p.skill, 0.10), 0.25, 0.98)
                ftm = int(rng.binomial(fta, ft_pct)) if fta else 0

                big = {"G": 0.5, "F": 1.0, "C": 1.4}[p.position]
                oreb = int(rng.poisson(1.1 * big * pace * 2))
                dreb = int(rng.poisson(2.4 * big * pace * 2))
                assists = int(rng.poisson((3.4 if p.position == "G" else 1.2) * pace * 1.6))
                turnovers = int(rng.poisson(1.6 * pace * 1.6))
                steals = int(rng.poisson(0.9 * pace * 1.4))
                blocks = int(rng.poisson((1.3 if p.position == "C" else 0.4) * pace * 1.4))
                fouls = int(np.clip(rng.poisson(2.0 * pace * 1.5), 0, 5))
                points = 2 * fgm + fg3m + ftm

                game_box.append({
                    "game_id": game_id,
                    "season": season,
                    "game_no": game["game_no"],
                    "date": game["date"].isoformat(),
                    "player_id": p.player_id,
                    "player": p.name,
                    "started": p.player_id in starters,
                    "minutes": mmss(mins),
                    "field_goals": f"{fgm}-{fga}",
                    "three_pointers": f"{fg3m}-{fg3a}",
                    "free_throws": f"{ftm}-{fta}",
                    "offensive_rebounds": oreb,
                    "defensive_rebounds": dreb,
                    "assists": assists,
                    "turnovers": turnovers,
                    "steals": steals,
                    "blocks": blocks,
                    "fouls": fouls,
                    "points": points,
                })

            for p in order:
                if p.player_id in dnp:
                    game_box.append({
                        "game_id": game_id,
                        "season": season,
                        "game_no": game["game_no"],
                        "date": game["date"].isoformat(),
                        "player_id": p.player_id,
                        "player": p.name,
                        "started": False,
                        "minutes": "DNP",
                        "field_goals": np.nan,
                        "three_pointers": np.nan,
                        "free_throws": np.nan,
                        "offensive_rebounds": np.nan,
                        "defensive_rebounds": np.nan,
                        "assists": np.nan,
                        "turnovers": np.nan,
                        "steals": np.nan,
                        "blocks": np.nan,
                        "fouls": np.nan,
                        "points": np.nan,
                    })

            game_box.sort(key=lambda r: r["player_id"])
            box_rows.extend(game_box)

            team_points = int(sum(r["points"] for r in game_box if r["minutes"] != "DNP"))

            home_edge = {"Home": 0.05, "Away": -0.05, "Neutral": 0.0}[site]
            edge = (rating + home_edge) - opp_strength
            opp_points = team_points - int(round(rng.normal(26 * edge, 10)))
            opp_points = int(np.clip(opp_points, 38, 112))
            if opp_points == team_points:
                opp_points += 2 if rng.random() < 0.5 else -2
            if overtime:
                # An overtime game was tied at the end of regulation, so the
                # final margin has to be small.
                if abs(team_points - opp_points) > 9:
                    opp_points = team_points - int(np.sign(team_points - opp_points)) * int(
                        rng.integers(1, 8)
                    )

            if site == "Home":
                venue = "Crisler Center"
                crowd = rng.normal(11_800, 1_500)
            elif site == "Away":
                venue = OPPONENT_ARENAS.get(opponent, f"{opponent} Arena")
                crowd = rng.normal(13_500, 3_400)
            else:
                venue = NEUTRAL_VENUES[int(rng.integers(0, len(NEUTRAL_VENUES)))]
                crowd = rng.normal(9_800, 2_900)

            game_rows.append({
                "game_id": game_id,
                "season": season,
                "game_no": game["game_no"],
                "date": game["date"].isoformat(),
                "opponent": opponent,
                "conference": conference,
                "site": site,
                "venue": venue,
                "team_points": team_points,
                "opponent_points": opp_points,
                "overtime": overtime,
                "attendance": int(np.clip(round(crowd), 3_500, 22_000)),
            })

    box = pd.DataFrame.from_records(box_rows)
    games = pd.DataFrame.from_records(game_rows)
    roster = pd.DataFrame.from_records(roster_rows)

    # A handful of games were never charted by the SID's office, so their
    # attendance is missing. Students meet that gap in the victory lap.
    holes = rng.choice(len(games), size=9, replace=False)
    games.loc[holes, "attendance"] = np.nan

    roster = roster.sort_values(["season", "player_id"], ignore_index=True)
    return box, games, roster


def main() -> None:
    box, games, roster = simulate()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    box.to_csv(DATA_DIR / "box_scores.csv", index=False)
    games.to_csv(DATA_DIR / "games.csv", index=False)
    roster.to_csv(DATA_DIR / "roster.csv", index=False)

    wins = (games["team_points"] > games["opponent_points"]).sum()
    dnp = (box["minutes"] == "DNP").sum()
    print(f"box_scores.csv {box.shape[0]} rows x {box.shape[1]} cols ({dnp} DNP rows)")
    print(f"games.csv      {games.shape[0]} rows x {games.shape[1]} cols")
    print(f"roster.csv     {roster.shape[0]} rows x {roster.shape[1]} cols")
    print(f"simulated record: {wins}-{len(games) - wins}")


if __name__ == "__main__":
    main()
