"""
Generate the simulated "Yada Yada Data" corpus used by the open-ended
investigation assignment.

The corpus is *simulated*. The show's structure (nine seasons, 180 episodes),
its characters, its writers and its directors are real; every line of
dialogue, every title, every air date and every audience number in here was
generated from a fixed seed. A handful of the show's famous catchphrases are
sprinkled through the generated dialogue so that Question 7 has something to
find. Nothing else in here should be mistaken for the actual scripts.

Run from the assignment root:

    python tools/generate_data.py

It rewrites data/episodes.csv, data/lines.csv and data/characters.csv
byte-for-byte identically every time, so the autograder's expected answers
stay stable.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 1989  # the year the pilot aired
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Real: nine seasons, 180 episodes, distributed like this.
EPISODES_PER_SEASON = {1: 5, 2: 12, 3: 23, 4: 24, 5: 22, 6: 24, 7: 24, 8: 22, 9: 24}

# Real people. The credits attached to them below are simulated.
WRITERS = [
    ("Larry David", 0.30), ("Jerry Seinfeld", 0.22), ("Peter Mehlman", 0.12),
    ("Larry Charles", 0.10), ("Tom Gammill", 0.08), ("Max Pross", 0.08),
    ("Gregg Kavet", 0.07), ("Andy Robin", 0.07), ("Alec Berg", 0.07),
    ("Jeff Schaffer", 0.07), ("David Mandel", 0.06), ("Spike Feresten", 0.05),
    ("Carol Leifer", 0.05), ("Marjorie Gross", 0.04), ("Steve Koren", 0.04),
    ("Elaine Pope", 0.03), ("Jennifer Crittenden", 0.03), ("Bruce Kirschbaum", 0.02),
]
DIRECTORS_EARLY = ["Tom Cherones", "Tom Cherones", "Tom Cherones", "Joshua White"]
DIRECTORS_LATE = ["Andy Ackerman", "Andy Ackerman", "Andy Ackerman", "David Owen Trainor"]

# character -> (full name, role, first season, share of dialogue)
CHARACTERS = [
    ("JERRY", "Jerry Seinfeld", "main", 1, 0.255),
    ("GEORGE", "George Costanza", "main", 1, 0.225),
    ("ELAINE", "Elaine Benes", "main", 2, 0.185),
    ("KRAMER", "Kramer", "main", 1, 0.150),
    ("NEWMAN", "Newman", "recurring", 3, 0.016),
    ("FRANK", "Frank Costanza", "recurring", 4, 0.014),
    ("ESTELLE", "Estelle Costanza", "recurring", 4, 0.013),
    ("MORTY", "Morty Seinfeld", "recurring", 2, 0.011),
    ("HELEN", "Helen Seinfeld", "recurring", 2, 0.010),
    ("PUDDY", "David Puddy", "recurring", 6, 0.010),
    ("SUSAN", "Susan Ross", "recurring", 4, 0.009),
    ("PETERMAN", "J. Peterman", "recurring", 6, 0.009),
    ("STEINBRENNER", "George Steinbrenner", "recurring", 5, 0.008),
    ("UNCLE LEO", "Uncle Leo", "recurring", 2, 0.008),
    ("JACKIE CHILES", "Jackie Chiles", "recurring", 7, 0.006),
    ("BANIA", "Kenny Bania", "recurring", 6, 0.006),
    ("MICKEY", "Mickey Abbott", "recurring", 6, 0.005),
    ("LLOYD BRAUN", "Lloyd Braun", "recurring", 6, 0.004),
    # Walk-ons. They speak, but nobody is going to build a career on it.
    ("WAITRESS", "", "guest", 1, 0.007),
    ("DOORMAN", "", "guest", 3, 0.005),
    ("CAB DRIVER", "", "guest", 2, 0.005),
    ("DOCTOR", "", "guest", 2, 0.005),
    ("CLERK", "", "guest", 1, 0.005),
    ("NEIGHBOR", "", "guest", 1, 0.005),
    ("MAN", "", "guest", 1, 0.005),
    ("WOMAN", "", "guest", 1, 0.005),
    ("BOSS", "", "guest", 3, 0.004),
    ("MAILMAN", "", "guest", 3, 0.004),
    ("REPORTER", "", "guest", 5, 0.003),
    ("LAWYER", "", "guest", 4, 0.003),
    ("BUS DRIVER", "", "guest", 4, 0.003),
    # On the character list, never given a line. A merge must not invent them.
    ("BOB SACAMANO", "Bob Sacamano", "mentioned", 3, 0.0),
    ("LOMEZ", "Lomez", "mentioned", 4, 0.0),
    ("ART VANDELAY", "Art Vandelay", "mentioned", 2, 0.0),
]

# location -> (first season it is available, last season, weight)
LOCATIONS = [
    ("Jerry's Apartment", 1, 9, 0.30),
    ("Monk's Cafe", 1, 9, 0.22),
    ("The Street", 1, 9, 0.08),
    ("George's Apartment", 1, 9, 0.05),
    ("Elaine's Apartment", 2, 9, 0.05),
    ("Kramer's Apartment", 1, 9, 0.04),
    ("The Hallway", 1, 9, 0.04),
    ("Pendant Publishing", 3, 6, 0.05),
    ("Yankee Stadium", 5, 9, 0.04),
    ("J. Peterman Office", 6, 9, 0.05),
    ("The Subway", 2, 9, 0.03),
    ("Parking Garage", 3, 9, 0.02),
    ("Del Boca Vista", 4, 9, 0.02),
    ("Chinese Restaurant", 2, 9, 0.02),
    ("Movie Theater", 1, 9, 0.02),
    ("Hospital Waiting Room", 3, 9, 0.02),
    ("Coffee Shop Counter", 1, 9, 0.02),
]

TITLE_NOUNS = [
    "Contest", "Puffy Shirt", "Parking Garage", "Chinese Restaurant", "Marine Biologist",
    "Soup", "Fusilli", "Junior Mint", "Opposite", "Boyfriend", "Pothole", "Betrayal",
    "Bizarro Jerry", "Muffin Tops", "Yada Yada", "Millennium", "Voice", "Comeback",
    "Strike", "Bottle Deposit", "Calzone", "Sponge", "Doorman", "Rye", "Cadillac",
    "Wig Master", "Friars Club", "Wait Out", "Invitations", "Foundation", "Soul Mate",
    "Little Kicks", "Package", "Fatigues", "Checks", "Chicken Roaster", "Abstinence",
    "Andrea Doria", "Little Jerry", "Money", "Apology", "Merv Griffin Show", "Slicer",
    "Betrayal Party", "Nap", "Yada", "Reverse Peephole", "Cartoon", "Strongbox",
    "Frogger", "Maid", "Puerto Rican Day", "Burning", "Bookstore", "Wizard",
    "Butter Shave", "Voice Mail", "Serenity", "Blood", "Junk Mail", "Bris",
    "Airport", "Limo", "Good Samaritan", "Letter", "Parking Space", "Keys", "Note",
    "Truth", "Pony Remark", "Jacket", "Phone Message", "Apartment", "Statue", "Revenge",
    "Heart Attack", "Deal", "Baby Shower", "Chaperone", "Big Salad", "Pledge Drive",
    "Chicken", "Couch", "Gymnast", "Soup Nazi", "Secret Code", "Pool Guy", "Diplomat",
    "Face Painter", "Understudy", "Engagement", "Postponement", "Maestro", "Wink",
    "Hot Tub", "Doodle", "Fusilli Jerry", "Diplomat's Club", "Race", "Switch",
    "Label Maker", "Scofflaw", "Highlights", "Beard", "Kiss Hello", "Doorman's Nephew",
    "Jimmy", "Doll", "Friars", "Wife", "Raincoats", "Fire", "Hamptons", "Opera",
    "Virgin", "Contact Lens", "Smelly Car", "Handicap Spot", "Pilot", "Trip", "Pitch",
    "Ticket", "Watch", "Bubble Boy", "Cheever Letters", "Airport Lounge", "Old Man",
    "Implant", "Junior Mints", "Smoke Alarm", "Visa", "Shoes", "Outing", "Seven",
    "Cafe", "Tape", "Nose Job", "Stranded", "Alternate Side", "Red Dot", "Subway",
    "Fix Up", "Boyfriend Part Two", "Suicide", "Fire Truck", "Stall", "Dinner Party",
    "Glasses", "Sniffing Accountant", "Bris Party", "Lip Reader", "Non-Fat Yogurt",
    "Barber", "Masseuse", "Conversion", "Stand-In", "Dog", "Baby", "Pen", "Busboy",
    "Library", "Cafe Owner", "Male Unbonding", "Robbery", "Stock Tip", "Ex-Girlfriend",
    "Seinfeld Chronicles", "Statue Garden", "Jughandle", "Fusilli Contest", "Van Buren",
    "Muffin", "Summer of George", "Yada Yada Yada", "Bottle Return", "Sweater",
    "Kramer Show", "Hot Dog", "Long Weekend", "Diner", "Wallet", "Roommate",
]

# ---------------------------------------------------------------------------
# Word banks. Nothing here is a quotation; the lines are assembled from parts.
NOUNS = [
    "sweater", "muffin", "parking space", "sandwich", "raincoat", "phone message",
    "haircut", "job interview", "answering machine", "coffee table book", "dry cleaner",
    "birthday party", "apartment", "library book", "salad", "date", "bus", "elevator",
    "gym membership", "restaurant reservation", "dinner party", "airport shuttle",
    "soup", "bagel", "rental car", "dentist appointment", "cable guy", "mattress",
    "wallet", "umbrella", "wedding invitation", "grocery list", "movie ticket",
]
PLURALS = [
    "airline peanuts", "car alarms", "waiting rooms", "self-checkout lanes",
    "gym mirrors", "hotel pillows", "parking meters", "return policies",
    "wedding toasts", "vending machines", "office birthdays", "revolving doors",
    "salad bars", "coat checks", "answering machines", "muffin tops",
]
ADJECTIVES = [
    "ridiculous", "unbelievable", "magnificent", "outrageous", "questionable",
    "spectacular", "reasonable", "suspicious", "tremendous", "unacceptable",
    "genius", "borderline", "impossible", "delicate", "fantastic",
]
VERBS_PAST = [
    "returned", "double-dipped", "canceled", "rescheduled", "borrowed", "regifted",
    "forgot", "misplaced", "renegotiated", "confessed", "abandoned", "delivered",
]
VERBS = [
    "return", "cancel", "reschedule", "borrow", "regift", "renegotiate",
    "commit", "explain", "apologize", "handle", "reconsider",
]
NAMES = ["Jerry", "George", "Elaine", "Kramer", "Newman", "Bania", "Puddy", "Susan"]

STAGE_DIRECTIONS = [
    "enters", "exits", "sighs", "the door slams", "long pause", "picks up the phone",
    "pointing", "shrugs", "sliding through the door", "sits down", "stands up",
    "eating", "checking the mail", "looking out the window",
]

# Short, famous catchphrases, sprinkled in so Question 7 has something to find.
CATCHPHRASES = [
    ("KRAMER", "Giddy up!", 0.030),
    ("KRAMER", "giddy up", 0.012),
    ("JERRY", "Hello, Newman.", 0.014),
    ("JERRY", "hello, newman", 0.004),
    ("ELAINE", "Yada yada yada, we were out of there.", 0.010),
    ("GEORGE", "So I yada yada yada'd the whole thing.", 0.008),
    ("JERRY", "And then, yada yada, the check came.", 0.006),
    ("FRANK", "Serenity now!", 0.018),
    ("GEORGE", "serenity now", 0.008),
    ("GEORGE", "I am master of my domain.", 0.010),
    ("KRAMER", "These pretzels are making me thirsty.", 0.010),
    ("JERRY", "No soup for you.", 0.008),
    ("JERRY", "Not that there's anything wrong with that.", 0.012),
    ("GEORGE", "not that there's anything wrong with that", 0.005),
    ("FRANK", "A Festivus for the rest of us.", 0.030),
    ("ELAINE", "A Festivus miracle.", 0.006),
]

TEMPLATES = {
    "JERRY": [
        "What is the deal with {plural}?",
        "So you're telling me you {verb_past} the {noun}?",
        "You know what I like about {plural}? Nothing.",
        "That's a shame.",
        "Who does that? Who {verb_past} a {noun}?",
        "I don't think that's how the {noun} works.",
        "Let me get this straight. You {verb_past} it, and then you told {name}?",
        "This is why nobody wants to {verb} anything with you.",
        "Explain to me, slowly, what happened to the {noun}.",
        "It's a {adj} situation. I'm not saying it isn't.",
    ],
    "GEORGE": [
        "I'm telling you, this is the most {adj} {noun} I have ever seen.",
        "Do you have any idea what I am dealing with here?",
        "It's not a lie if you believe it.",
        "Why does this always happen to me? Why?",
        "I had it. I had the {noun} and I let it go.",
        "You cannot expect a man in my position to {verb} that.",
        "{name}, I need you to back me up on the {noun} thing.",
        "I'm going to {verb} it. I have decided. That's it.",
        "This is a {adj} disaster and it is entirely your fault.",
        "I was in the pool! There was shrinkage!",
    ],
    "ELAINE": [
        "Get OUT!",
        "I cannot believe you {verb_past} my {noun}.",
        "Do you have any idea how {adj} that sounds?",
        "Maybe the dingo ate your {noun}.",
        "{name}, you have to {verb} this. Today.",
        "That is the single most {adj} thing I have ever heard.",
        "No, no, no. We are not doing the {noun} again.",
        "I am done with {plural}. Completely done.",
        "Why would anyone {verb} a {noun} on purpose?",
        "Fine. Fine! I'll handle the {noun} myself.",
    ],
    "KRAMER": [
        "Giddy up!",
        "{name}, I'm telling you, this {noun} is going to be huge.",
        "Oh, you gotta {verb} the {noun}, buddy. You gotta.",
        "I got a guy. He does {plural}. Cash only.",
        "It's a whole {noun} thing, I can't get into it.",
        "You know what your problem is? You don't {verb}.",
        "Boy, that's a {adj} looking {noun}.",
        "I'm out there, {name}, and I'm loving every minute of it.",
        "Listen to me. The {noun} is the future.",
        "Well, I had to {verb} it. What was I supposed to do?",
    ],
    "_OTHER": [
        "I'm going to need you to {verb} that {noun}.",
        "Sir, that is not our policy.",
        "Do you want the {noun} or not?",
        "I've been standing here for twenty minutes.",
        "That will be another {noun}, I'm afraid.",
        "You people are unbelievable.",
        "Look, I just work here.",
        "The {noun} is not available today.",
        "Somebody has to {verb} the {noun}.",
        "That's a {adj} thing to say to a person.",
    ],
}

# How a script supervisor actually types a speaker name at 2 a.m.
SPEAKER_NOISE = [
    (lambda n, rng: n, 0.62),
    (lambda n, rng: n.title(), 0.10),
    (lambda n, rng: n.lower(), 0.05),
    (lambda n, rng: f"{n}:", 0.06),
    (lambda n, rng: f"  {n} ", 0.05),
    (lambda n, rng: f"{n} (V.O.)", 0.04),
    (lambda n, rng: f"{n} (on phone)", 0.03),
    (lambda n, rng: f"{n} [entering]", 0.02),
    (lambda n, rng: f"{n}  (cont'd)", 0.03),
]


def weighted_choice(rng: np.random.Generator, items, weights):
    weights = np.asarray(weights, dtype=float)
    weights = weights / weights.sum()
    return items[int(rng.choice(len(items), p=weights))]


def fill(rng: np.random.Generator, template: str) -> str:
    return template.format(
        noun=NOUNS[int(rng.integers(0, len(NOUNS)))],
        plural=PLURALS[int(rng.integers(0, len(PLURALS)))],
        adj=ADJECTIVES[int(rng.integers(0, len(ADJECTIVES)))],
        verb=VERBS[int(rng.integers(0, len(VERBS)))],
        verb_past=VERBS_PAST[int(rng.integers(0, len(VERBS_PAST)))],
        name=NAMES[int(rng.integers(0, len(NAMES)))],
    )


def air_dates(rng: np.random.Generator) -> dict[int, list[dt.date]]:
    """Thursday nights, September through May, with a winter gap."""
    out = {}
    for season, count in EPISODES_PER_SEASON.items():
        start_year = 1988 + season
        day = dt.date(start_year, 9, 1)
        while day.weekday() != 3:  # Thursday
            day += dt.timedelta(days=1)
        dates = []
        cursor = day
        for i in range(count):
            dates.append(cursor)
            gap = 7 if rng.random() < 0.72 else int(rng.integers(14, 29))
            cursor += dt.timedelta(days=gap)
        out[season] = dates
    return out


def build_speakers(rng, season):
    """Everyone who can speak in this season, with their dialogue weights."""
    available = [
        (name, share) for name, _full, role, first, share in CHARACTERS
        if role != "mentioned" and first <= season and share > 0
    ]
    names = [n for n, _ in available]
    weights = np.array([s for _, s in available], dtype=float)
    return names, weights / weights.sum()


def noisy_speaker(rng, name: str) -> str:
    fn = weighted_choice(rng, [f for f, _ in SPEAKER_NOISE], [w for _, w in SPEAKER_NOISE])
    return fn(name, rng)


def simulate():
    rng = np.random.default_rng(SEED)
    dates = air_dates(rng)
    titles = list(TITLE_NOUNS)
    rng.shuffle(titles)

    writer_names = [w for w, _ in WRITERS]
    writer_weights = np.array([w for _, w in WRITERS], dtype=float)
    writer_weights = writer_weights / writer_weights.sum()

    episode_rows: list[dict] = []
    line_rows: list[dict] = []
    line_no_global = 0
    overall = 0
    title_cursor = 0

    for season, count in EPISODES_PER_SEASON.items():
        speakers, speaker_weights = build_speakers(rng, season)
        locations = [(n, w) for n, first, last, w in LOCATIONS if first <= season <= last]
        loc_names = [n for n, _ in locations]
        loc_weights = np.array([w for _, w in locations], dtype=float)
        loc_weights = loc_weights / loc_weights.sum()

        for index_in_season in range(1, count + 1):
            overall += 1
            episode_id = f"S{season:02d}E{index_in_season:02d}"

            if title_cursor < len(titles):
                title = f"The {titles[title_cursor]}"
                title_cursor += 1
            else:
                title = f"The {NOUNS[int(rng.integers(0, len(NOUNS)))].title()}"

            n_writers = 1 if rng.random() < 0.62 else 2
            credited = list(
                rng.choice(writer_names, size=n_writers, replace=False, p=writer_weights)
            )
            director = (
                DIRECTORS_EARLY[int(rng.integers(0, len(DIRECTORS_EARLY)))]
                if season <= 5
                else DIRECTORS_LATE[int(rng.integers(0, len(DIRECTORS_LATE)))]
            )

            n_scenes = int(rng.integers(14, 23))
            episode_line_no = 0

            for scene_no in range(1, n_scenes + 1):
                location = loc_names[int(rng.choice(len(loc_names), p=loc_weights))]
                n_lines = int(rng.integers(4, 13))

                # A scene has a small cast, drawn once and then talked through.
                cast_size = int(min(len(speakers), rng.integers(2, 5)))
                cast = list(
                    rng.choice(speakers, size=cast_size, replace=False, p=speaker_weights)
                )
                cast_weights = np.array(
                    [speaker_weights[speakers.index(c)] for c in cast], dtype=float
                )
                cast_weights = cast_weights / cast_weights.sum()

                for _ in range(n_lines):
                    episode_line_no += 1
                    line_no_global += 1
                    who = cast[int(rng.choice(len(cast), p=cast_weights))]

                    # Roughly one line in fifty is nothing but a stage direction.
                    if rng.random() < 0.02:
                        dialogue = f"({STAGE_DIRECTIONS[int(rng.integers(0, len(STAGE_DIRECTIONS)))]})"
                    else:
                        catch = None
                        for owner, phrase, rate in CATCHPHRASES:
                            if owner == who and rng.random() < rate:
                                catch = phrase
                                break
                        if catch is not None:
                            dialogue = catch
                        else:
                            bank = TEMPLATES.get(who, TEMPLATES["_OTHER"])
                            dialogue = fill(rng, bank[int(rng.integers(0, len(bank)))])
                        # Sometimes the actor gets a direction mid-line.
                        if rng.random() < 0.08:
                            note = STAGE_DIRECTIONS[int(rng.integers(0, len(STAGE_DIRECTIONS)))]
                            if rng.random() < 0.5:
                                dialogue = f"({note}) {dialogue}"
                            else:
                                dialogue = f"{dialogue} ({note})"

                    # Two characters occasionally get one credited line.
                    raw_speaker = noisy_speaker(rng, who)
                    if rng.random() < 0.006:
                        other = cast[int(rng.integers(0, len(cast)))]
                        if other != who:
                            joiner = " AND " if rng.random() < 0.5 else " & "
                            raw_speaker = f"{who}{joiner}{other}"

                    line_rows.append({
                        "line_id": f"L{line_no_global:05d}",
                        "episode_id": episode_id,
                        "scene_no": scene_no,
                        "line_no": episode_line_no,
                        "location": location,
                        "speaker": raw_speaker,
                        "dialogue": dialogue,
                    })

            base = 11 + 2.4 * season + rng.normal(0, 2.6)
            viewers = float(np.clip(base, 8.0, 40.0))
            rating = float(np.clip(rng.normal(7.6 + 0.11 * season, 0.45), 6.2, 9.6))

            episode_rows.append({
                "episode_id": episode_id,
                "season": season,
                "episode_in_season": index_in_season,
                "episode_overall": overall,
                "title": title,
                "air_date": dates[season][index_in_season - 1].isoformat(),
                "writers": " | ".join(credited),
                "director": director,
                # A couple of the later seasons stretched an episode to an hour.
                "runtime_min": int(
                    rng.choice([22, 22, 22, 23, 23, 44]) if season >= 4
                    else rng.choice([22, 22, 23])
                ),
                "us_viewers_millions": round(viewers, 2),
                "imdb_rating": round(rating, 1),
            })

    episodes = pd.DataFrame.from_records(episode_rows)
    lines = pd.DataFrame.from_records(line_rows)

    # Nielsen never reported a handful of these, and a few never picked up
    # enough votes for a rating. Question 6 is about what to do with them.
    blanks = rng.choice(len(episodes), size=14, replace=False)
    episodes.loc[blanks, "us_viewers_millions"] = np.nan
    blanks = rng.choice(len(episodes), size=6, replace=False)
    episodes.loc[blanks, "imdb_rating"] = np.nan

    characters = pd.DataFrame(
        [
            {"character": name, "full_name": full, "role": role, "first_season": first}
            for name, full, role, first, _share in CHARACTERS
        ]
    ).sort_values("character", ignore_index=True)

    return episodes, lines, characters


def main() -> None:
    episodes, lines, characters = simulate()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    episodes.to_csv(DATA_DIR / "episodes.csv", index=False)
    lines.to_csv(DATA_DIR / "lines.csv", index=False)
    characters.to_csv(DATA_DIR / "characters.csv", index=False)

    print(f"episodes.csv   {episodes.shape[0]} rows x {episodes.shape[1]} cols")
    print(f"lines.csv      {lines.shape[0]} rows x {lines.shape[1]} cols")
    print(f"characters.csv {characters.shape[0]} rows x {characters.shape[1]} cols")
    print(f"distinct raw speaker strings: {lines['speaker'].nunique()}")


if __name__ == "__main__":
    main()
