"""
Generate the simulated "Yost Feed" datasets used by the regex, text and time
assignment.

The datasets are *simulated*. Yost Ice Arena, the opponents and the shape of a
college hockey season are real; every player, every event line and every final
score is randomly generated from a fixed seed. Nothing in here should be
quoted as a real Michigan hockey statistic.

Run from the assignment root:

    python tools/generate_data.py

It rewrites data/events.csv, data/games.csv and data/roster.csv byte-for-byte
identically every time, so the autograder's expected answers stay stable.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 1996  # the year Michigan won its ninth NCAA hockey championship
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

SEASON = 2024
GAMES = 41
PERIOD_SECONDS = 20 * 60
OT_SECONDS = 5 * 60

# opponent -> (code, strength)
OPPONENTS = {
    "Michigan State":   ("MSU", 0.78),
    "Ohio State":       ("OSU", 0.72),
    "Notre Dame":       ("ND", 0.70),
    "Minnesota":        ("MINN", 0.86),
    "Wisconsin":        ("WISC", 0.74),
    "Penn State":       ("PSU", 0.71),
    "Boston College":   ("BC", 0.88),
    "Boston University": ("BU", 0.85),
    "Denver":           ("DU", 0.84),
    "North Dakota":     ("UND", 0.82),
    "Western Michigan": ("WMU", 0.69),
    "Michigan Tech":    ("MTU", 0.58),
    "Lake Superior State": ("LSSU", 0.48),
    "Ferris State":     ("FSU", 0.44),
    "Bowling Green":    ("BGSU", 0.55),
    "Niagara":          ("NIAG", 0.40),
    "Union":            ("UNION", 0.52),
    "Lindenwood":       ("LIN", 0.34),
}

ARENAS = {
    "Michigan State": "Munn Ice Arena", "Ohio State": "Value City Arena",
    "Notre Dame": "Compton Family Ice Arena", "Minnesota": "3M Arena at Mariucci",
    "Wisconsin": "LaBahn Arena", "Penn State": "Pegula Ice Arena",
    "Boston College": "Conte Forum", "Boston University": "Agganis Arena",
    "Denver": "Magness Arena", "North Dakota": "Ralph Engelstad Arena",
    "Western Michigan": "Lawson Ice Arena", "Michigan Tech": "John MacInnes Arena",
    "Lake Superior State": "Taffy Abel Arena", "Ferris State": "Ewigleben Arena",
    "Bowling Green": "Slater Family Ice Arena", "Niagara": "Dwyer Arena",
    "Union": "Messa Rink", "Lindenwood": "Centene Community Ice Center",
}
NEUTRAL_VENUES = ["Little Caesars Arena", "Xcel Energy Center"]

# Names deliberately include an apostrophe, a hyphen and a two-word surname:
# a regex that stops at the first non-letter loses all three.
MICHIGAN_ROSTER = [
    # (jersey, name, position, class, shoots, height, weight, hometown, skill)
    (1,  "N. Kaminski",     "G",  "Jr", "L", "6-2",  190, "Warren, MI", 0.10),
    (31, "A. Sorenson",     "G",  "Fr", "L", "6-3",  198, "Edina, MN", 0.06),
    (2,  "P. Vander-Meer",  "D",  "Sr", "R", "6-4",  212, "Grand Rapids, MI", 0.42),
    (4,  "J. Ferris",       "D",  "So", "L", "6-1",  196, "Barrie, ON", 0.40),
    (6,  "L. O'Halloran",   "D",  "Jr", "L", "5-11", 184, "Dorchester, MA", 0.48),
    (8,  "R. St. Pierre",   "D",  "Fr", "R", "6-0",  188, "Trois-Rivieres, QC", 0.36),
    (14, "C. Wiegand",      "D",  "So", "R", "6-2",  201, "Stockholm, Sweden", 0.34),
    (23, "M. Boychuk",      "D",  "Sr", "L", "6-3",  207, "Sherwood Park, AB", 0.44),
    (27, "T. Ilves",        "D",  "Fr", "L", "5-10", 178, "Tampere, Finland", 0.30),
    (9,  "R. Karr",         "F",  "So", "R", "5-11", 181, "Chicago, IL", 0.82),
    (10, "E. Marchand",     "F",  "Sr", "L", "6-0",  190, "Ottawa, ON", 0.74),
    (11, "D. Ochoa",        "F",  "Jr", "R", "5-9",  172, "Anaheim, CA", 0.70),
    (12, "S. Rutledge",     "F",  "Fr", "L", "6-1",  186, "Ann Arbor, MI", 0.58),
    (16, "K. Nystrom",      "F",  "So", "L", "6-2",  195, "Gothenburg, Sweden", 0.66),
    (17, "T. Brennan",      "F",  "Jr", "R", "6-0",  188, "Toronto, ON", 0.92),
    (18, "H. Okafor",       "F",  "Fr", "R", "6-3",  204, "Houston, TX", 0.54),
    (19, "B. Lindgren",     "F",  "Sr", "L", "5-10", 176, "Duluth, MN", 0.62),
    (20, "G. Pasternak",    "F",  "So", "R", "6-1",  192, "Prague, Czechia", 0.60),
    (21, "W. Achterberg",   "F",  "Jr", "L", "6-2",  198, "Holland, MI", 0.50),
    (22, "F. Delacroix",    "F",  "Fr", "L", "5-11", 180, "Montreal, QC", 0.56),
    (24, "V. Sepp",         "F",  "So", "R", "6-0",  185, "Tallinn, Estonia", 0.46),
    (25, "O. Brightwater",  "F",  "Sr", "L", "6-4",  215, "Calgary, AB", 0.52),
    (26, "A. Quintero",     "F",  "Jr", "R", "5-9",  170, "Miami, FL", 0.64),
    (28, "M. Halloran",     "F",  "Fr", "L", "6-1",  189, "Boston, MA", 0.44),
    (29, "J. Teodoro",      "F",  "So", "R", "5-10", 177, "Manila, Philippines", 0.38),
    (44, "Z. Vandenberg",   "F",  "Sr", "L", "6-5",  221, "Kalamazoo, MI", 0.48),
]

OPP_FIRST = list("ABCDEFGHJKLMNPRSTVW")
OPP_LAST = [
    "Alderson", "Beauchamp", "Cormier", "Doyle", "Eklund", "Fitzpatrick",
    "Gauthier", "Halvorson", "Ives", "Jarvis", "Kuznetsov", "Lachance",
    "Maloney", "Nilsson", "Ostberg", "Peterson", "Quill", "Rasmussen",
    "Savard", "Thibault", "Underwood", "Vasquez", "Whelan", "Yakimov",
]

INFRACTIONS = [
    # (name, minutes, weight)
    ("Tripping", 2, 0.17),
    ("Hooking", 2, 0.13),
    ("Slashing", 2, 0.11),
    ("Interference", 2, 0.10),
    ("Roughing", 2, 0.10),
    ("Cross-checking", 2, 0.09),
    ("High-sticking", 2, 0.08),
    ("Holding", 2, 0.07),
    ("Delay of Game", 2, 0.05),
    ("Too Many Men", 2, 0.04),
    ("Boarding", 5, 0.03),
    ("Contact to the Head", 5, 0.02),
    ("Fighting", 5, 0.01),
]

STRENGTHS = ["EV", "PP", "SH", "EN", "PS"]
STRENGTH_P = [0.72, 0.20, 0.04, 0.03, 0.01]

FILLER_TYPES = ["SHOT", "HIT", "BLOCK", "TAKEAWAY"]
FILLER_P = [0.62, 0.20, 0.13, 0.05]


def clock_string(rng: np.random.Generator, remaining: int) -> str:
    """MM:SS remaining. A third of the sub-ten-minute clocks lose the zero."""
    minutes, seconds = divmod(remaining, 60)
    if minutes < 10 and rng.random() < 0.33:
        return f"{minutes}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def rough_up(rng: np.random.Generator, text: str) -> str:
    """The feed is scraped, and scraped text has stray whitespace in it."""
    roll = rng.random()
    if roll < 0.06:
        return "  " + text
    if roll < 0.12:
        return text + "  "
    if roll < 0.18:
        return text.replace(" #", "  #", 1)
    return text


def opponent_player(rng: np.random.Generator) -> tuple[int, str]:
    jersey = int(rng.integers(1, 40))
    name = (
        OPP_FIRST[int(rng.integers(0, len(OPP_FIRST)))]
        + ". "
        + OPP_LAST[int(rng.integers(0, len(OPP_LAST)))]
    )
    return jersey, name


def simulate() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(SEED)

    skaters = [p for p in MICHIGAN_ROSTER if p[2] != "G"]
    skater_weights = np.array([p[8] for p in skaters], dtype=float)
    skater_weights = skater_weights / skater_weights.sum()

    opponents = list(OPPONENTS)
    schedule = list(rng.choice(opponents, size=GAMES, replace=True))

    start = dt.date(SEASON - 1, 10, 4)
    game_rows: list[dict] = []
    event_rows: list[dict] = []
    event_no = 0

    for game_no, opponent in enumerate(schedule, start=1):
        code, strength = OPPONENTS[opponent]
        date = start + dt.timedelta(days=int(round(155 * (game_no - 1) / (GAMES - 1))))
        site = ["Home", "Away", "Neutral"][int(rng.choice(3, p=[0.55, 0.40, 0.05]))]

        edge = {"Home": 0.10, "Away": -0.08, "Neutral": 0.0}[site]
        mich_lambda = float(np.clip(3.1 + 4.0 * (0.76 + edge - strength), 0.4, 7.0))
        opp_lambda = float(np.clip(3.0 + 3.4 * (strength - 0.76 - edge), 0.5, 7.0))

        # Goal counts are overdispersed relative to a Poisson -- hot goalies
        # are a real thing, and so are 8-1 nights. A negative binomial gives
        # both tails, including the occasional shutout.
        def goals(mean: float, shape: float = 5.0) -> int:
            drawn = int(rng.negative_binomial(shape, shape / (shape + mean)))
            return min(drawn, 9)  # nobody scores ten in a college hockey game

        mich_goals = goals(mich_lambda)
        opp_goals = goals(opp_lambda)

        overtime = 0
        if mich_goals == opp_goals:
            overtime = 1
            if rng.random() < 0.7:  # somebody ends it; otherwise it stays a tie
                if rng.random() < 0.5 + 0.5 * (0.76 + edge - strength):
                    mich_goals += 1
                else:
                    opp_goals += 1

        periods = [1, 2, 3] + ([4] if overtime else [])
        # Spread each side's goals across the periods. An overtime goal, if
        # there was one, belongs to the fourth period by construction.
        reg_mich = mich_goals - (1 if overtime and mich_goals > opp_goals else 0)
        reg_opp = opp_goals - (1 if overtime and opp_goals > mich_goals else 0)
        mich_by_period = list(rng.multinomial(reg_mich, [1 / 3, 1 / 3, 1 / 3]))
        opp_by_period = list(rng.multinomial(reg_opp, [1 / 3, 1 / 3, 1 / 3]))
        if overtime:
            mich_by_period.append(1 if mich_goals > opp_goals else 0)
            opp_by_period.append(1 if opp_goals > mich_goals else 0)

        game_id = f"{SEASON}-G{game_no:02d}"

        for period in periods:
            length = OT_SECONDS if period == 4 else PERIOD_SECONDS
            n_events = int(rng.integers(26, 40)) if period != 4 else int(rng.integers(5, 11))
            n_goals = mich_by_period[period - 1] + opp_by_period[period - 1]
            n_events = max(n_events, n_goals + 2)

            # Distinct second-marks inside the period, in order of play.
            marks = sorted(
                rng.choice(np.arange(5, length - 4), size=n_events, replace=False).tolist()
            )
            goal_slots = sorted(
                rng.choice(len(marks), size=n_goals, replace=False).tolist()
            )
            goal_teams = ["MICH"] * mich_by_period[period - 1] + ["OPP"] * opp_by_period[period - 1]
            rng.shuffle(goal_teams)
            goal_map = dict(zip(goal_slots, goal_teams))

            for slot, elapsed in enumerate(marks):
                remaining = length - int(elapsed)
                clock = clock_string(rng, remaining)
                event_no += 1

                if slot in goal_map:
                    if goal_map[slot] == "MICH":
                        team = "MICH"
                        scorer = skaters[int(rng.choice(len(skaters), p=skater_weights))]
                        jersey, name = scorer[0], scorer[1]
                        n_assists = int(rng.choice([0, 1, 2], p=[0.15, 0.35, 0.50]))
                        pool = [s for s in skaters if s[0] != jersey]
                        weights = np.array([s[8] for s in pool], dtype=float)
                        weights = weights / weights.sum()
                        helpers = (
                            list(rng.choice(len(pool), size=n_assists, replace=False, p=weights))
                            if n_assists
                            else []
                        )
                        if helpers:
                            credit = ", ".join(f"#{pool[i][0]} {pool[i][1]}" for i in helpers)
                            assists = f"(A: {credit})"
                        else:
                            assists = "(unassisted)"
                    else:
                        team = code
                        jersey, name = opponent_player(rng)
                        n_assists = int(rng.choice([0, 1, 2], p=[0.18, 0.36, 0.46]))
                        helpers = [opponent_player(rng) for _ in range(n_assists)]
                        seen = {jersey}
                        helpers = [h for h in helpers if h[0] not in seen and not seen.add(h[0])]
                        assists = (
                            "(A: " + ", ".join(f"#{j} {n}" for j, n in helpers) + ")"
                            if helpers
                            else "(unassisted)"
                        )
                    tag = STRENGTHS[int(rng.choice(len(STRENGTHS), p=STRENGTH_P))]
                    description = f"GOAL {clock} {team} #{jersey} {name} {assists} [{tag}]"

                elif rng.random() < 0.09:
                    is_michigan = rng.random() < 0.5
                    if is_michigan:
                        team = "MICH"
                        offender = skaters[int(rng.integers(0, len(skaters)))]
                        jersey, name = offender[0], offender[1]
                    else:
                        team = code
                        jersey, name = opponent_player(rng)
                    idx = int(rng.choice(len(INFRACTIONS), p=[w for _, _, w in INFRACTIONS]))
                    infraction, minutes, _ = INFRACTIONS[idx]
                    description = (
                        f"PENALTY {clock} {team} #{jersey} {name} ({infraction}, {minutes} min)"
                    )

                else:
                    kind = FILLER_TYPES[int(rng.choice(len(FILLER_TYPES), p=FILLER_P))]
                    if rng.random() < 0.5:
                        team = "MICH"
                        actor = skaters[int(rng.integers(0, len(skaters)))]
                        jersey, name = actor[0], actor[1]
                    else:
                        team = code
                        jersey, name = opponent_player(rng)
                    description = f"{kind} {clock} {team} #{jersey} {name}"

                event_rows.append({
                    "event_id": f"E{event_no:05d}",
                    "game_id": game_id,
                    "period": period,
                    "description": rough_up(rng, description),
                })

        if site == "Home":
            venue, crowd = "Yost Ice Arena", rng.normal(5_800, 300)
        elif site == "Away":
            venue, crowd = ARENAS[opponent], rng.normal(6_400, 2_100)
        else:
            venue = NEUTRAL_VENUES[int(rng.integers(0, len(NEUTRAL_VENUES)))]
            crowd = rng.normal(12_000, 2_500)

        if mich_goals > opp_goals:
            result = "W"
        elif mich_goals < opp_goals:
            result = "L"
        else:
            result = "T"

        game_rows.append({
            "game_id": game_id,
            "season": SEASON,
            "game_no": game_no,
            "date": date.isoformat(),
            "opponent": opponent,
            "opponent_code": code,
            "site": site,
            "venue": venue,
            "michigan_goals": mich_goals,
            "opponent_goals": opp_goals,
            "result": result,
            "overtime": overtime,
            "attendance": int(np.clip(round(crowd), 1_800, 19_500)),
        })

    events = pd.DataFrame.from_records(event_rows)
    games = pd.DataFrame.from_records(game_rows)
    roster = pd.DataFrame(
        [
            {
                "jersey": jersey,
                "player": name,
                "position": position,
                "class": klass,
                "shoots": shoots,
                "height": height,
                "weight_lb": weight,
                "hometown": hometown,
            }
            for jersey, name, position, klass, shoots, height, weight, hometown, _ in MICHIGAN_ROSTER
        ]
    ).sort_values("jersey", ignore_index=True)

    return events, games, roster


def main() -> None:
    events, games, roster = simulate()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    events.to_csv(DATA_DIR / "events.csv", index=False)
    games.to_csv(DATA_DIR / "games.csv", index=False)
    roster.to_csv(DATA_DIR / "roster.csv", index=False)

    record = games["result"].value_counts()
    goals = events["description"].str.strip().str.startswith("GOAL").sum()
    print(f"events.csv {events.shape[0]} rows x {events.shape[1]} cols ({goals} goals)")
    print(f"games.csv  {games.shape[0]} rows x {games.shape[1]} cols")
    print(f"roster.csv {roster.shape[0]} rows x {roster.shape[1]} cols")
    print(
        f"simulated record: {record.get('W', 0)}-{record.get('L', 0)}-{record.get('T', 0)}"
    )


if __name__ == "__main__":
    main()
