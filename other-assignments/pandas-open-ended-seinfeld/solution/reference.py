"""
Reference solutions for "Yada Yada Data: Text, Ambiguity and Defensible
Choices".

INSTRUCTORS: keep this file (and this whole `solution/` folder) out of the
copy you hand to students. `grading/build_expected.py` reads it to produce
`grading/expected_values.json`, which is what the hidden tests compare
against, so if you change a question spec, change it here and rebuild.

Five of the ten questions are deliberately underdetermined. For those the
graded thing is not "the answer" but the pair of (a) a function that behaves
correctly for *every* setting of the knob the question exposes, and (b) a
declared default with a written justification. The defaults chosen in this
file are one defensible set among several; a student who picks differently
and defends it should score the same.
"""

from __future__ import annotations

import re
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

EPISODES_CSV = DATA_DIR / "episodes.csv"
LINES_CSV = DATA_DIR / "lines.csv"
CHARACTERS_CSV = DATA_DIR / "characters.csv"

LEADS = ["JERRY", "GEORGE", "ELAINE", "KRAMER"]

# Anything inside round or square brackets is a stage direction, not speech.
STAGE_DIRECTION = re.compile(r"[\(\[][^\)\]]*[\)\]]")
WORD = re.compile(r"[A-Za-z']+")

FILL_METHODS = ("global_median", "season_median", "neighbours")
CREDIT_RULES = ("full", "split")


# The written half of the five underdetermined questions. A student's wording
# will differ; what is graded is that a real choice was made and defended.
ASSUMPTIONS = {
    "episode_cast": (
        "min_lines=3. A character with one or two lines in an episode is a "
        "walk-on -- a waitress taking an order, a doorman saying no. Counting "
        "them as 'in the episode' pushes the typical cast from four people to "
        "nearly seven and buries the four leads in noise. Three lines is the "
        "point where the distribution flattens out: going from 1 to 3 removes "
        "most of the one-line walk-ons, and going from 3 to 12 barely moves "
        "the number at all, which says the remaining people are really in the "
        "episode. The cost is that a genuinely small but real part (a doctor "
        "with two lines that drive the plot) gets dropped, so this threshold "
        "is wrong for any question about guest actors specifically."
    ),
    "filled_viewers": (
        "method='season_median'. Audience size in this corpus climbs steadily "
        "across the nine seasons, so a single global median is biased low for "
        "the late seasons and high for the early ones -- filling a season 9 "
        "gap with the series median understates it by several million. The "
        "season median respects that trend while staying robust to the odd "
        "outlier, which 'neighbours' is not: two adjacent gaps get filled from "
        "the same pair of surrounding points, and a single unusual episode "
        "next to a gap drags the estimate with it. The cost is that a gap at "
        "the very start or end of a season is filled from episodes that aired "
        "months later, so any analysis of within-season trend should exclude "
        "the filled rows rather than trust them."
    ),
    "phrase_counts": (
        "case_sensitive=False, whole_words=True. Case is a transcription "
        "artifact here, not meaning: the corpus contains both 'Giddy up!' and "
        "'giddy up', and no reading of the data treats them as different "
        "events, so folding case recovers roughly a fifth more hits. Whole "
        "words matter in the other direction: without word boundaries a search "
        "for 'her' matches inside 'there', 'other' and 'whether' and returns a "
        "count that has nothing to do with the word. The cost of whole_words "
        "is that a phrase appearing as part of a hyphenated or possessive form "
        "is missed, so a search for a word likely to appear that way should "
        "turn it off deliberately rather than by accident."
    ),
    "writer_credits": (
        "credit='split'. The question this table is usually asked in service "
        "of is 'how much of this show did each writer write', and under 'full' "
        "the credits sum to more than the number of episodes, which makes the "
        "totals uncomparable between a writer who works alone and one who "
        "always works in a pair. Splitting keeps the column summing to 180, so "
        "a share is meaningful. The cost is that it assumes co-writers "
        "contributed equally, which is certainly false in individual cases; "
        "for a question about who was *in the room* rather than how much they "
        "wrote, 'full' is the right rule."
    ),
    "my_investigation": (
        "See INVESTIGATION below -- the assumptions for the open question are "
        "documented there, next to the question they belong to."
    ),
}


# ---------------------------------------------------------------- Question 1
def load_episodes(path=EPISODES_CSV) -> pd.DataFrame:
    episodes = pd.read_csv(path, parse_dates=["air_date"])
    return episodes.set_index("episode_id")


def load_lines(path=LINES_CSV) -> pd.DataFrame:
    lines = pd.read_csv(path)
    return lines.set_index("line_id")


def load_characters(path=CHARACTERS_CSV) -> pd.DataFrame:
    return pd.read_csv(path)


# ---------------------------------------------------------------- Question 2
def clean_speakers(lines: pd.DataFrame) -> pd.Series:
    out = (
        lines["speaker"]
        .astype("object")
        .str.replace(STAGE_DIRECTION, " ", regex=True)
        .str.replace(":", "", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
        .str.upper()
    )
    out.name = "speaker_clean"
    return out


# ---------------------------------------------------------------- Question 3
def line_word_counts(lines: pd.DataFrame) -> pd.Series:
    spoken = lines["dialogue"].astype("object").str.replace(STAGE_DIRECTION, " ", regex=True)
    out = spoken.str.count(r"[A-Za-z']+").astype("int64")
    out.name = "word_count"
    return out


# ---------------------------------------------------------------- Question 4
def speaking_share(lines: pd.DataFrame) -> pd.DataFrame:
    tally = lines.assign(_who=clean_speakers(lines))
    counts = tally.groupby(["episode_id", "_who"]).size().unstack(fill_value=0)
    totals = tally.groupby("episode_id").size()

    out = counts.reindex(columns=LEADS, fill_value=0).div(totals, axis=0).round(3)
    out.index.name = "episode_id"
    out.columns.name = None
    return out.sort_index()


# ---------------------------------------------------------------- Question 5
def episode_cast(lines: pd.DataFrame, min_lines: int = 3) -> pd.DataFrame:
    tally = lines.assign(_who=clean_speakers(lines))
    counts = tally.groupby(["episode_id", "_who"]).size()
    kept = counts[counts >= min_lines].reset_index(name="_n")

    grouped = kept.groupby("episode_id")["_who"]
    out = pd.DataFrame({
        "cast_size": grouped.size().astype("int64"),
        "cast": grouped.apply(lambda names: ", ".join(sorted(names))),
    })
    every_episode = pd.Index(sorted(lines["episode_id"].unique()), name="episode_id")
    out = out.reindex(every_episode)
    out["cast_size"] = out["cast_size"].fillna(0).astype("int64")
    out["cast"] = out["cast"].fillna("")
    return out


# ---------------------------------------------------------------- Question 6
def filled_viewers(episodes: pd.DataFrame, method: str = "season_median") -> pd.Series:
    if method not in FILL_METHODS:
        raise ValueError(f"method should be one of {FILL_METHODS}, got {method!r}")

    reported = episodes["us_viewers_millions"].astype(float)

    if method == "global_median":
        estimate = pd.Series(reported.median(), index=episodes.index)
    elif method == "season_median":
        estimate = episodes.groupby("season")["us_viewers_millions"].transform("median")
    else:
        ordered = episodes.sort_values("episode_overall")["us_viewers_millions"].astype(float)
        neighbours = pd.concat([ordered.ffill(), ordered.bfill()], axis=1)
        estimate = neighbours.mean(axis=1).reindex(episodes.index)

    out = reported.fillna(estimate).round(3)
    out.name = "us_viewers_millions"
    return out


# ---------------------------------------------------------------- Question 7
def phrase_counts(
    lines: pd.DataFrame,
    phrases,
    case_sensitive: bool = False,
    whole_words: bool = True,
) -> pd.Series:
    spoken = lines["dialogue"].astype("object").str.replace(STAGE_DIRECTION, " ", regex=True)
    flags = 0 if case_sensitive else re.IGNORECASE

    tally = []
    for phrase in phrases:
        pattern = re.escape(phrase)
        if whole_words:
            pattern = rf"\b{pattern}\b"
        tally.append(int(spoken.str.count(pattern, flags=flags).sum()))

    out = pd.Series(tally, index=pd.Index(list(phrases), name="phrase"), dtype="int64")
    out.name = "occurrences"
    return out


# ---------------------------------------------------------------- Question 8
def writer_credits(episodes: pd.DataFrame, credit: str = "split") -> pd.Series:
    if credit not in CREDIT_RULES:
        raise ValueError(f"credit should be one of {CREDIT_RULES}, got {credit!r}")

    credited = episodes["writers"].astype("object").str.split("|")
    credited = credited.apply(lambda names: [name.strip() for name in names])

    if credit == "split":
        weight = 1.0 / credited.apply(len)
    else:
        weight = pd.Series(1.0, index=episodes.index)

    exploded = credited.explode().rename("writer").to_frame()
    exploded["weight"] = weight.reindex(exploded.index).to_numpy()

    out = exploded.groupby("writer")["weight"].sum().round(3).sort_index()
    out.name = "credits"
    out.index.name = "writer"
    return out


# ---------------------------------------------------------------- Question 9
def scene_pairs(lines: pd.DataFrame, characters: pd.DataFrame) -> pd.DataFrame:
    named = set(characters.loc[characters["role"].isin(["main", "recurring"]), "character"])

    tally = lines.assign(_who=clean_speakers(lines))
    tally = tally[tally["_who"].isin(named)]
    present = tally[["episode_id", "scene_no", "_who"]].drop_duplicates()

    counter: dict[tuple[str, str], int] = {}
    for _, scene in present.groupby(["episode_id", "scene_no"], sort=False):
        for pair in combinations(sorted(scene["_who"].unique()), 2):
            counter[pair] = counter.get(pair, 0) + 1

    out = pd.DataFrame(
        [{"character_a": a, "character_b": b, "scenes": n} for (a, b), n in counter.items()]
    )
    out = out.sort_values(
        ["scenes", "character_a", "character_b"], ascending=[False, True, True]
    )
    out["scenes"] = out["scenes"].astype("int64")
    return out.set_index(["character_a", "character_b"])


# --------------------------------------------------------------- Question 10
INVESTIGATION = {
    "question": (
        "Does the show get less dependent on Jerry as it goes on, and if so, "
        "who picks up the slack?"
    ),
    "assumptions": (
        "'Dependent on Jerry' is measured as his share of the spoken lines in "
        "an episode, using the cleaned speaker names from Question 2 and "
        "counting every line in the episode in the denominator, including "
        "guest and joint-credited lines. Season 1 is reported but not "
        "interpreted: Elaine is not in it, so the four-way split is not "
        "comparable to the rest. Lines are used rather than words because a "
        "line is the unit the script is organised in; a word-count version of "
        "this table is a reasonable robustness check and is left as an "
        "exercise. Nothing here adjusts for episode length."
    ),
    "method": (
        "Group the cleaned speaker labels by season, take each lead's share of "
        "that season's lines, and report the four shares side by side along "
        "with the share going to everyone else."
    ),
    "finding": (
        "Jerry's share of the dialogue drifts down across the run while the "
        "share going to characters outside the four leads drifts up, so the "
        "series becomes less of a vehicle for one voice and more of an "
        "ensemble. The effect is real but modest -- single-digit percentage "
        "points, not a reinvention -- and the 'everyone else' column moves "
        "more than any individual lead does, which suggests the change is "
        "mostly about a widening recurring cast rather than a redistribution "
        "among the four."
    ),
}


def my_investigation(
    episodes: pd.DataFrame, lines: pd.DataFrame, characters: pd.DataFrame
) -> pd.DataFrame:
    tally = lines.assign(_who=clean_speakers(lines))
    tally = tally.merge(
        episodes[["season"]], left_on="episode_id", right_index=True, how="left"
    )

    per_season = tally.groupby("season").size()
    out = pd.DataFrame(index=per_season.index)
    for lead in LEADS:
        spoken = tally[tally["_who"] == lead].groupby("season").size()
        out[lead] = (spoken.reindex(per_season.index).fillna(0) / per_season).round(3)
    out["everyone_else"] = (1 - out[LEADS].sum(axis=1)).round(3)
    out.index.name = "season"
    return out
