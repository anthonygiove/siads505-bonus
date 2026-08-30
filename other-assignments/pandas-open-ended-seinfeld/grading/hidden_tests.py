"""
HIDDEN TESTS -- do not distribute with the student notebook.

Each of the ten questions is worth 10 points, split across several checks so
that partial credit is possible. Every question is graded against inputs the
autograder builds itself from the reference loaders, so a student who fumbles
Question 1 can still earn full marks on Questions 2-10.

Five of the ten questions are deliberately underdetermined. For those the
checks never compare against one blessed answer. They ask three things
instead: does the function behave correctly at *every* setting of the knob
the question exposes, is the declared default one of the defensible options,
and did the student write down why. A different default, defended, scores the
same as the reference's.

The other five carry the usual "robustness" check -- the same function
re-run on a different slice of the corpus -- to catch answers hard-coded
after peeking at the public asserts.
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



# ------------------------------------------------- helpers for the open half
PLACEHOLDERS = ("todo", "your answer", "fill this in", "tbd", "xxx", "n/a", "..." )


def assumption(ns, key, min_chars=140):
    """Pull one entry out of the student's ASSUMPTIONS dict and sanity-check it."""
    if "ASSUMPTIONS" not in ns:
        raise AssertionError(
            "`ASSUMPTIONS` is not defined. It is the dict near the top of the notebook "
            "where the underdetermined questions get their justification written down."
        )
    book = ns["ASSUMPTIONS"]
    assert isinstance(book, dict), (
        f"`ASSUMPTIONS` should be a dict, got {type(book).__name__}."
    )
    assert key in book, f"`ASSUMPTIONS` has no entry for {key!r}."

    text = book[key]
    assert isinstance(text, str), (
        f"ASSUMPTIONS[{key!r}] should be a string, got {type(text).__name__}."
    )
    stripped = " ".join(text.split())
    assert stripped, f"ASSUMPTIONS[{key!r}] is empty. Write down the choice you made."
    lowered = stripped.lower()
    for placeholder in PLACEHOLDERS:
        assert placeholder not in lowered, (
            f"ASSUMPTIONS[{key!r}] still contains the placeholder text {placeholder!r}."
        )
    assert len(stripped) >= min_chars, (
        f"ASSUMPTIONS[{key!r}] is {len(stripped)} characters; the checks want at least "
        f"{min_chars}. Say what you chose, why it is defensible on this data, and what "
        "it costs you."
    )
    return stripped


def default_of(ns, name, parameter):
    """The default value the student declared for a keyword argument."""
    import inspect

    func = fn(ns, name)
    try:
        signature = inspect.signature(func)
    except (TypeError, ValueError):  # pragma: no cover -- exotic callables
        raise AssertionError(f"`{name}` does not look like an ordinary function.")
    assert parameter in signature.parameters, (
        f"`{name}` should take a `{parameter}=` keyword argument."
    )
    default = signature.parameters[parameter].default
    assert default is not inspect.Parameter.empty, (
        f"`{name}`: give `{parameter}` a default. The default *is* your answer to the "
        "question -- it is the choice you are defending."
    )
    return default


# -------------------------------------------------------------- shared inputs
def episodes():
    return ref.load_episodes()


def lines():
    return ref.load_lines()


def characters():
    return ref.load_characters()


# Seasons 4 and 7 in full: enough episodes to be a real corpus, different
# enough from the whole to catch an answer that was pasted in.
SLICE_SEASONS = [4, 7]


def episodes_slice():
    e = episodes()
    return e[e["season"].isin(SLICE_SEASONS)]


def lines_slice():
    keep = set(episodes_slice().index)
    l = lines()
    return l[l["episode_id"].isin(keep)]


PROBE_PHRASES = ["yada yada", "Giddy up", "her", "Newman", "serenity now", "soup nazi"]


# ------------------------------------------------------------------ Question 1
def q1_episodes(ns):
    out = fn(ns, "load_episodes")()
    assert_is(out, pd.DataFrame, "load_episodes")
    assert out.shape == (180, 10), (
        f"load_episodes: expected a (180, 10) frame once episode_id is the index, got {out.shape}."
    )
    assert out.index.name == "episode_id", (
        f"load_episodes: the index should be named 'episode_id', got {out.index.name!r}."
    )
    assert out.index.is_unique, "load_episodes: episode_id values should be unique."
    assert pd.api.types.is_datetime64_any_dtype(out["air_date"]), (
        f"load_episodes: 'air_date' should be a datetime column, got dtype {out['air_date'].dtype}."
    )


def q1_lines(ns):
    out = fn(ns, "load_lines")()
    assert_is(out, pd.DataFrame, "load_lines")
    assert out.shape == (26389, 6), (
        f"load_lines: expected a (26389, 6) frame once line_id is the index, got {out.shape}."
    )
    assert out.index.name == "line_id", (
        f"load_lines: the index should be named 'line_id', got {out.index.name!r}."
    )
    assert list(out.columns) == [
        "episode_id", "scene_no", "line_no", "location", "speaker", "dialogue"
    ], f"load_lines: columns should keep their original order, got {list(out.columns)}."


def q1_characters_and_join(ns):
    out = fn(ns, "load_characters")()
    assert_is(out, pd.DataFrame, "load_characters")
    assert out.shape == (34, 4), f"load_characters: expected a (34, 4) frame, got {out.shape}."
    assert "character" in out.columns, (
        "load_characters: keep 'character' as a column, not the index."
    )
    assert set(out["role"]) == {"main", "recurring", "guest", "mentioned"}, (
        f"load_characters: unexpected roles {sorted(set(out['role']))}."
    )

    ep = fn(ns, "load_episodes")()
    ln = fn(ns, "load_lines")()
    assert set(ln["episode_id"]) <= set(ep.index), (
        "load_lines / load_episodes: every line should belong to an episode in episodes.csv."
    )


# ------------------------------------------------------------------ Question 2
def q2_structure(ns):
    out = fn(ns, "clean_speakers")(lines())
    assert_is(out, pd.Series, "clean_speakers")
    assert out.name == "speaker_clean", (
        f"clean_speakers: the Series should be named 'speaker_clean', got {out.name!r}."
    )
    assert len(out) == 26389, f"clean_speakers: expected 26389 values, got {len(out)}."
    assert_index(out.index, lines().index, "clean_speakers")


def q2_normalised(ns):
    out = fn(ns, "clean_speakers")(lines())
    assert (out == out.str.upper()).all(), "clean_speakers: the result should be upper case."
    assert not out.str.contains(r"[\(\[\):]").any(), (
        "clean_speakers: annotations like '(V.O.)' and trailing colons should be gone."
    )
    assert (out == out.str.strip()).all(), "clean_speakers: strip the surrounding whitespace."
    assert not out.str.contains("  ").any(), (
        "clean_speakers: collapse runs of whitespace -- \"KRAMER  (cont'd)\" leaves a double "
        "space behind once the annotation is removed."
    )
    assert out.nunique() == 89, (
        f"clean_speakers: expected 89 distinct speakers after cleaning, got {out.nunique()}. "
        "234 raw strings collapse to 89 -- if you have more, some variant is still uncleaned."
    )


def q2_values(ns):
    out = fn(ns, "clean_speakers")(lines())
    assert_series_matches(out, ref.clean_speakers(lines()), "clean_speakers")


def q2_robustness(ns):
    subset = lines_slice()
    out = fn(ns, "clean_speakers")(subset)
    assert_series_matches(out, ref.clean_speakers(subset), "clean_speakers (seasons 4 and 7)")


# ------------------------------------------------------------------ Question 3
def q3_structure(ns):
    out = fn(ns, "line_word_counts")(lines())
    assert_is(out, pd.Series, "line_word_counts")
    assert out.name == "word_count", (
        f"line_word_counts: the Series should be named 'word_count', got {out.name!r}."
    )
    assert pd.api.types.is_integer_dtype(out), (
        f"line_word_counts: a word count is a whole number, got dtype {out.dtype}."
    )
    assert len(out) == 26389, f"line_word_counts: expected 26389 values, got {len(out)}."


def q3_stage_directions(ns):
    """A line that is nothing but '(enters)' contains no spoken words."""
    out = fn(ns, "line_word_counts")(lines())
    want = ref.line_word_counts(lines())
    direction_only = (want == 0).to_numpy()
    assert direction_only.sum() > 300, "internal: the fixture should contain direction-only lines"
    assert int(out[direction_only].sum()) == 0, (
        "line_word_counts: a line that is only a stage direction has a word count of 0 -- "
        "strip anything in round or square brackets before you count."
    )


def q3_values(ns):
    out = fn(ns, "line_word_counts")(lines())
    assert_series_matches(out, ref.line_word_counts(lines()), "line_word_counts")


def q3_robustness(ns):
    subset = lines_slice()
    out = fn(ns, "line_word_counts")(subset)
    assert_series_matches(out, ref.line_word_counts(subset), "line_word_counts (seasons 4 and 7)")


# ------------------------------------------------------------------ Question 4
def q4_structure(ns):
    out = fn(ns, "speaking_share")(lines())
    assert_is(out, pd.DataFrame, "speaking_share")
    assert list(out.columns) == ["JERRY", "GEORGE", "ELAINE", "KRAMER"], (
        f"speaking_share: columns should be the four leads in that order, got {list(out.columns)}."
    )
    assert out.index.name == "episode_id", (
        f"speaking_share: index should be named 'episode_id', got {out.index.name!r}."
    )
    assert len(out) == 180, f"speaking_share: expected one row per episode, got {len(out)}."
    assert list(out.index) == sorted(out.index), "speaking_share: sort the index."


def q4_absent_is_zero(ns):
    """Elaine is not in season 1. Those five rows are 0.0, not NaN."""
    out = fn(ns, "speaking_share")(lines())
    season_one = [i for i in out.index if i.startswith("S01")]
    assert len(season_one) == 5, "internal: season 1 should have five episodes"
    assert out.loc[season_one, "ELAINE"].notna().all(), (
        "speaking_share: Elaine does not appear in season 1. Those rows should read 0.0 -- "
        "a share of nothing is zero, and dropping them to NaN loses five real episodes."
    )
    assert (out.loc[season_one, "ELAINE"] == 0.0).all(), (
        "speaking_share: Elaine's share in the season 1 episodes should be exactly 0.0."
    )


def q4_values(ns):
    out = fn(ns, "speaking_share")(lines())
    assert_frame_matches(out, ref.speaking_share(lines()), "speaking_share", tol=1e-3)


def q4_robustness(ns):
    subset = lines_slice()
    out = fn(ns, "speaking_share")(subset)
    assert_frame_matches(
        out, ref.speaking_share(subset), "speaking_share (seasons 4 and 7)", tol=1e-3
    )


# ------------------------------------------------------------------ Question 5
def q5_structure(ns):
    out = fn(ns, "episode_cast")(lines(), min_lines=3)
    assert_is(out, pd.DataFrame, "episode_cast")
    assert list(out.columns) == ["cast_size", "cast"], (
        f"episode_cast: columns should be ['cast_size', 'cast'], got {list(out.columns)}."
    )
    assert out.index.name == "episode_id", (
        f"episode_cast: index should be named 'episode_id', got {out.index.name!r}."
    )
    assert len(out) == 180, (
        f"episode_cast: every episode gets a row, even at a high threshold -- got {len(out)}."
    )
    assert pd.api.types.is_integer_dtype(out["cast_size"]), (
        f"episode_cast: 'cast_size' should be an integer, got dtype {out['cast_size'].dtype}."
    )


def q5_threshold_works(ns):
    """The knob has to be a knob: three different settings, three right answers."""
    for threshold in (1, 3, 12):
        out = fn(ns, "episode_cast")(lines(), min_lines=threshold)
        want = ref.episode_cast(lines(), min_lines=threshold)
        assert_frame_matches(out, want, f"episode_cast (min_lines={threshold})")


def q5_default_declared(ns):
    default = default_of(ns, "episode_cast", "min_lines")
    assert isinstance(default, (int, np.integer)) and not isinstance(default, bool), (
        f"episode_cast: min_lines should default to a whole number, got {default!r}."
    )
    assert 1 <= int(default) <= 10, (
        f"episode_cast: a default of {default} is hard to defend on this corpus. Below 1 is "
        "meaningless and above 10 throws away characters who are plainly in the episode."
    )


def q5_assumption_written(ns):
    assumption(ns, "episode_cast")


# ------------------------------------------------------------------ Question 6
def q6_structure(ns):
    out = fn(ns, "filled_viewers")(episodes(), method="season_median")
    assert_is(out, pd.Series, "filled_viewers")
    assert out.name == "us_viewers_millions", (
        f"filled_viewers: the Series should be named 'us_viewers_millions', got {out.name!r}."
    )
    assert_index(out.index, episodes().index, "filled_viewers")
    assert pd.api.types.is_float_dtype(out), (
        f"filled_viewers: expected a float Series, got dtype {out.dtype}."
    )
    assert int(out.isna().sum()) == 0, (
        f"filled_viewers: {int(out.isna().sum())} values are still missing."
    )


def q6_reported_untouched(ns):
    out = fn(ns, "filled_viewers")(episodes(), method="season_median")
    reported = episodes()["us_viewers_millions"]
    kept = reported.notna().to_numpy()
    assert_values(
        out[kept], reported[kept].astype(float),
        "filled_viewers (episodes Nielsen actually reported)", tol=1e-6,
    )


def q6_all_three_methods(ns):
    for method in ref.FILL_METHODS:
        out = fn(ns, "filled_viewers")(episodes(), method=method)
        want = ref.filled_viewers(episodes(), method=method)
        assert_series_matches(out, want, f"filled_viewers (method={method!r})", tol=1e-3)


def q6_default_and_assumption(ns):
    default = default_of(ns, "filled_viewers", "method")
    assert default in ref.FILL_METHODS, (
        f"filled_viewers: the default method should be one of {list(ref.FILL_METHODS)}, "
        f"got {default!r}."
    )
    assumption(ns, "filled_viewers")


# ------------------------------------------------------------------ Question 7
def q7_structure(ns):
    out = fn(ns, "phrase_counts")(lines(), PROBE_PHRASES)
    assert_is(out, pd.Series, "phrase_counts")
    assert out.name == "occurrences", (
        f"phrase_counts: the Series should be named 'occurrences', got {out.name!r}."
    )
    assert out.index.name == "phrase", (
        f"phrase_counts: the index should be named 'phrase', got {out.index.name!r}."
    )
    assert list(out.index) == PROBE_PHRASES, (
        "phrase_counts: return the phrases in the order they were handed to you, "
        f"got {list(out.index)}."
    )
    assert pd.api.types.is_integer_dtype(out), (
        f"phrase_counts: counts are whole numbers, got dtype {out.dtype}."
    )


def q7_missing_phrase_is_zero(ns):
    out = fn(ns, "phrase_counts")(lines(), PROBE_PHRASES)
    assert int(out.loc["soup nazi"]) == 0, (
        "phrase_counts: 'soup nazi' never appears in this corpus. That is a count of 0, "
        "and the row still belongs in the result."
    )


def q7_both_flags_work(ns):
    for case_sensitive in (False, True):
        for whole_words in (False, True):
            out = fn(ns, "phrase_counts")(
                lines(), PROBE_PHRASES,
                case_sensitive=case_sensitive, whole_words=whole_words,
            )
            want = ref.phrase_counts(
                lines(), PROBE_PHRASES,
                case_sensitive=case_sensitive, whole_words=whole_words,
            )
            assert_series_matches(
                out, want,
                f"phrase_counts (case_sensitive={case_sensitive}, whole_words={whole_words})",
            )


def q7_defaults_and_assumption(ns):
    for parameter in ("case_sensitive", "whole_words"):
        default = default_of(ns, "phrase_counts", parameter)
        assert isinstance(default, bool), (
            f"phrase_counts: {parameter} should default to True or False, got {default!r}."
        )
    assumption(ns, "phrase_counts")


# ------------------------------------------------------------------ Question 8
def q8_structure(ns):
    out = fn(ns, "writer_credits")(episodes(), credit="full")
    assert_is(out, pd.Series, "writer_credits")
    assert out.name == "credits", (
        f"writer_credits: the Series should be named 'credits', got {out.name!r}."
    )
    assert out.index.name == "writer", (
        f"writer_credits: the index should be named 'writer', got {out.index.name!r}."
    )
    assert list(out.index) == sorted(out.index), (
        "writer_credits: sort the writers alphabetically."
    )
    assert len(out) == 18, (
        f"writer_credits: expected 18 credited writers, got {len(out)}. The `writers` column "
        "holds one or two names separated by ' | ' -- split it before you count."
    )


def q8_split_conserves_episodes(ns):
    out = fn(ns, "writer_credits")(episodes(), credit="split")
    assert abs(float(out.sum()) - 180.0) < 0.01, (
        f"writer_credits: under 'split' the credits should total 180, one per episode, "
        f"got {float(out.sum()):.2f}."
    )
    full = fn(ns, "writer_credits")(episodes(), credit="full")
    assert abs(float(full.sum()) - 245.0) < 0.01, (
        f"writer_credits: under 'full' the credits should total 245 -- 180 episodes, 65 of "
        f"them co-written -- got {float(full.sum()):.2f}."
    )


def q8_both_rules(ns):
    for rule in ref.CREDIT_RULES:
        out = fn(ns, "writer_credits")(episodes(), credit=rule)
        want = ref.writer_credits(episodes(), credit=rule)
        assert_series_matches(out, want, f"writer_credits (credit={rule!r})", tol=1e-3)


def q8_default_and_assumption(ns):
    default = default_of(ns, "writer_credits", "credit")
    assert default in ref.CREDIT_RULES, (
        f"writer_credits: the default should be one of {list(ref.CREDIT_RULES)}, got {default!r}."
    )
    assumption(ns, "writer_credits")


# ------------------------------------------------------------------ Question 9
def q9_structure(ns):
    out = fn(ns, "scene_pairs")(lines(), characters())
    assert_is(out, pd.DataFrame, "scene_pairs")
    assert list(out.columns) == ["scenes"], (
        f"scene_pairs: the only column should be 'scenes', got {list(out.columns)}."
    )
    assert list(out.index.names) == ["character_a", "character_b"], (
        f"scene_pairs: index levels should be ['character_a', 'character_b'], "
        f"got {list(out.index.names)}."
    )
    assert pd.api.types.is_integer_dtype(out["scenes"]), (
        f"scene_pairs: 'scenes' should be a whole number, got dtype {out['scenes'].dtype}."
    )
    assert (out["scenes"] > 0).all(), (
        "scene_pairs: only pairs that actually share a scene belong in the table."
    )


def q9_pairs_are_unordered(ns):
    out = fn(ns, "scene_pairs")(lines(), characters())
    pairs = list(out.index)
    assert all(a < b for a, b in pairs), (
        "scene_pairs: each pair should appear once, with character_a alphabetically before "
        "character_b -- (ELAINE, JERRY) but not also (JERRY, ELAINE)."
    )
    guests = set(characters().loc[characters()["role"] == "guest", "character"])
    flat = {name for pair in pairs for name in pair}
    assert not (flat & guests), (
        f"scene_pairs: walk-on parts should not be in here -- found {sorted(flat & guests)[:3]}. "
        "Restrict to characters whose role is 'main' or 'recurring'."
    )


def q9_values(ns):
    out = fn(ns, "scene_pairs")(lines(), characters())
    assert_frame_matches(out, ref.scene_pairs(lines(), characters()), "scene_pairs")


def q9_robustness(ns):
    subset = lines_slice()
    out = fn(ns, "scene_pairs")(subset, characters())
    assert_frame_matches(
        out, ref.scene_pairs(subset, characters()), "scene_pairs (seasons 4 and 7)"
    )


# ----------------------------------------------------------------- Question 10
INVESTIGATION_KEYS = ("question", "assumptions", "method", "finding")


def q10_writeup(ns):
    assert "INVESTIGATION" in ns, (
        "`INVESTIGATION` is not defined. It is the dict where the open question gets "
        "written down: what you asked, what you assumed, how you did it, what you found."
    )
    book = ns["INVESTIGATION"]
    assert isinstance(book, dict), (
        f"`INVESTIGATION` should be a dict, got {type(book).__name__}."
    )
    missing = [k for k in INVESTIGATION_KEYS if k not in book]
    assert not missing, f"`INVESTIGATION` is missing the key(s) {missing}."

    for key, floor in (("question", 25), ("assumptions", 160), ("method", 60), ("finding", 160)):
        value = book[key]
        assert isinstance(value, str), (
            f"INVESTIGATION[{key!r}] should be a string, got {type(value).__name__}."
        )
        text = " ".join(value.split())
        lowered = text.lower()
        for placeholder in PLACEHOLDERS:
            assert placeholder not in lowered, (
                f"INVESTIGATION[{key!r}] still contains the placeholder {placeholder!r}."
            )
        assert len(text) >= floor, (
            f"INVESTIGATION[{key!r}] is {len(text)} characters; the checks want at least {floor}."
        )
    assert " ".join(book["question"].split()).endswith("?"), (
        "INVESTIGATION['question'] should be an actual question, ending in a question mark."
    )


def q10_runs_and_returns(ns):
    out = fn(ns, "my_investigation")(episodes(), lines(), characters())
    assert_is(out, pd.DataFrame, "my_investigation")
    assert out.shape[0] >= 2 and out.shape[1] >= 1, (
        f"my_investigation: should return a table worth looking at -- got {out.shape}. "
        "Two or more rows, one or more columns."
    )
    assert out.notna().to_numpy().any(), "my_investigation: the result is entirely empty."


def q10_deterministic(ns):
    first = fn(ns, "my_investigation")(episodes(), lines(), characters())
    second = fn(ns, "my_investigation")(episodes(), lines(), characters())
    assert first.shape == second.shape, (
        "my_investigation: two calls on the same data returned different shapes."
    )
    assert first.equals(second), (
        "my_investigation: two calls on the same data returned different answers. Whatever "
        "the finding is, somebody has to be able to reproduce it."
    )


def q10_computes_rather_than_recites(ns):
    """Hand it two seasons instead of nine and it should still answer."""
    whole = fn(ns, "my_investigation")(episodes(), lines(), characters())
    part = fn(ns, "my_investigation")(episodes_slice(), lines_slice(), characters())
    assert_is(part, pd.DataFrame, "my_investigation (seasons 4 and 7)")
    assert part.shape[0] >= 1, (
        "my_investigation: given seasons 4 and 7 it returned an empty table."
    )
    assert not whole.equals(part), (
        "my_investigation: the answer for two seasons is identical to the answer for all "
        "nine, which means the numbers are not being computed from the data you were handed."
    )


# ------------------------------------------------------------------- registry
QUESTIONS = [
    {
        "number": 1,
        "title": "Roll the tape -- load three files",
        "checks": [
            (3, "the episodes frame", q1_episodes),
            (3, "the lines frame", q1_lines),
            (4, "the character list, and the two frames agree", q1_characters_and_join),
        ],
    },
    {
        "number": 2,
        "title": "Who said that? -- normalising a speaker column",
        "checks": [
            (2, "a speaker_clean Series on the same index", q2_structure),
            (3, "234 raw variants collapse to 89 speakers", q2_normalised),
            (3, "the cleaned names are right", q2_values),
            (2, "works on a different slice of the run", q2_robustness),
        ],
    },
    {
        "number": 3,
        "title": "How much did they say? -- counting words",
        "checks": [
            (2, "an integer word_count Series", q3_structure),
            (3, "stage directions are not speech", q3_stage_directions),
            (3, "the counts are right", q3_values),
            (2, "works on a different slice of the run", q3_robustness),
        ],
    },
    {
        "number": 4,
        "title": "The Big Four -- share of the dialogue",
        "checks": [
            (2, "one row per episode, four columns", q4_structure),
            (3, "a character who is not in the season is 0.0", q4_absent_is_zero),
            (3, "the shares are right", q4_values),
            (2, "works on a different slice of the run", q4_robustness),
        ],
    },
    {
        "number": 5,
        "title": "Who is in this episode? -- you choose the line",
        "checks": [
            (2, "shape, column order and index", q5_structure),
            (3, "correct at min_lines of 1, 3 and 12", q5_threshold_works),
            (2, "a defensible default is declared", q5_default_declared),
            (3, "the choice is written down and defended", q5_assumption_written),
        ],
    },
    {
        "number": 6,
        "title": "Fourteen missing numbers -- you choose the fill",
        "checks": [
            (2, "a complete us_viewers_millions Series", q6_structure),
            (2, "reported episodes are left alone", q6_reported_untouched),
            (4, "all three methods compute correctly", q6_all_three_methods),
            (2, "a default is declared and defended", q6_default_and_assumption),
        ],
    },
    {
        "number": 7,
        "title": "Catchphrases -- you choose what counts as a match",
        "checks": [
            (2, "an occurrences Series indexed by phrase", q7_structure),
            (1, "a phrase that never appears counts 0", q7_missing_phrase_is_zero),
            (5, "all four flag combinations are right", q7_both_flags_work),
            (2, "defaults are declared and defended", q7_defaults_and_assumption),
        ],
    },
    {
        "number": 8,
        "title": "Who wrote it? -- you choose how to split a credit",
        "checks": [
            (2, "18 writers, alphabetical, named index", q8_structure),
            (2, "'split' conserves 180 episodes, 'full' does not", q8_split_conserves_episodes),
            (4, "both credit rules compute correctly", q8_both_rules),
            (2, "a default is declared and defended", q8_default_and_assumption),
        ],
    },
    {
        "number": 9,
        "title": "Who shares a scene with whom?",
        "checks": [
            (2, "a (character_a, character_b) frame of scene counts", q9_structure),
            (2, "each pair once, walk-ons excluded", q9_pairs_are_unordered),
            (4, "the counts and the sort order are right", q9_values),
            (2, "works on a different slice of the run", q9_robustness),
        ],
    },
    {
        "number": 10,
        "title": "Your own investigation",
        "checks": [
            (3, "the write-up is complete and specific", q10_writeup),
            (3, "the function runs and returns a real table", q10_runs_and_returns),
            (2, "the same data gives the same answer twice", q10_deterministic),
            (2, "it computes from the data it is handed", q10_computes_rather_than_recites),
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
