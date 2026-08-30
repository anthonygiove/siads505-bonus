"""
Regenerate grading/expected_values.json from the reference solution.

Run this after changing solution/reference.py or regenerating the data:

    python grading/build_expected.py

run_autograder.py verifies this snapshot before it grades anything, so a
silent change to the corpus or the reference shows up as a loud failure
instead of a room full of wrong grades.

Note what is *not* in here. Five of the ten questions are deliberately
underdetermined, and for those the snapshot pins the answer at each specific
setting of the knob -- not at the reference's default, which is only one
defensible choice among several.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "solution"))
sys.path.insert(0, str(ROOT / "grading"))

import reference as ref  # noqa: E402
from _serialize import to_jsonable  # noqa: E402

SNAPSHOT = ROOT / "grading" / "expected_values.json"

PROBE_PHRASES = ["yada yada", "Giddy up", "her", "Newman", "serenity now", "soup nazi"]


def build() -> dict:
    episodes = ref.load_episodes()
    lines = ref.load_lines()
    characters = ref.load_characters()

    out = {
        "q1_episodes_shape": to_jsonable((episodes.shape[0], episodes.shape[1])),
        "q1_lines_shape": to_jsonable((lines.shape[0], lines.shape[1])),
        "q1_characters_shape": to_jsonable((characters.shape[0], characters.shape[1])),
        "q2_clean_speakers": to_jsonable(ref.clean_speakers(lines).head(8)),
        "q2_distinct": to_jsonable(int(ref.clean_speakers(lines).nunique())),
        "q3_word_counts": to_jsonable(ref.line_word_counts(lines).head(8)),
        "q3_total": to_jsonable(int(ref.line_word_counts(lines).sum())),
        "q4_speaking_share": to_jsonable(ref.speaking_share(lines).head(8)),
        "q9_scene_pairs": to_jsonable(ref.scene_pairs(lines, characters).head(12)),
    }
    for threshold in (1, 3, 12):
        out[f"q5_episode_cast_{threshold}"] = to_jsonable(
            ref.episode_cast(lines, min_lines=threshold).head(6)
        )
    for method in ref.FILL_METHODS:
        out[f"q6_filled_viewers_{method}"] = to_jsonable(
            round(float(ref.filled_viewers(episodes, method=method).sum()), 4)
        )
    for case_sensitive in (False, True):
        for whole_words in (False, True):
            key = f"q7_phrase_counts_cs{int(case_sensitive)}_ww{int(whole_words)}"
            out[key] = to_jsonable(
                ref.phrase_counts(
                    lines, PROBE_PHRASES,
                    case_sensitive=case_sensitive, whole_words=whole_words,
                )
            )
    for rule in ref.CREDIT_RULES:
        out[f"q8_writer_credits_{rule}"] = to_jsonable(ref.writer_credits(episodes, credit=rule))
    return out


def main() -> None:
    SNAPSHOT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
    print(f"wrote {SNAPSHOT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
