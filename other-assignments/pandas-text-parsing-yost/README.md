# 🏒 The Yost Feed: Regex, Text & Time

**Assignment 3 · Other Assignments · 100 points (10 questions × 10 points)**

An assignment about the data you actually get: a **feed**. One row per event,
and the whole event crammed into a single string a scraper pulled off a
scoreboard.

```
GOAL 12:34 MICH #17 T. Brennan (A: #9 R. Karr, #22 D. Ochoa) [EV]
PENALTY 05:11 MICH #4 J. Ferris (Tripping, 2 min)
SHOT 8:45 OSU #22 P. Kuznetsov
```

Everything you want is in there. None of it is in a column. Students spend ten
questions getting it out, using **regular expressions with named groups**,
`.str.extract`, `.str.findall`, `.explode`, clock arithmetic on a clock that
counts *down*, and the joins and group-wise counting that turn 4,065 lines of
play-by-play into a scoring leaderboard.

Still no machine learning, no plotting requirement, no libraries beyond
`pandas` and `numpy`.

## What students get

```
assignment.ipynb        the notebook they fill in and hand back
data/events.csv         4,065 play-by-play events, one simulated season
data/games.csv          41 games
data/roster.csv         26 players
data/README.md          the data dictionary
requirements.txt
```

Everything else in this folder is **instructor-only** — see
[Handing it out](#handing-it-out).

## The ten questions

| # | Question | What it teaches |
|---|---|---|
| 1 | Warm-ups | `read_csv`, `set_index`, `parse_dates`, dtypes |
| 2 | Reading the sheet | `str.extract` with named groups; whitespace and `\s+` |
| 3 | Clock math | a clock that counts down, and a 5-minute overtime |
| 4 | Assist credits | `str.findall`, `explode`, `value_counts` |
| 5 | The penalty box | two named groups from one match; multi-word labels |
| 6 | Roster details | surnames with punctuation, `"6-1"` → inches, `rsplit` |
| 7 | Scoring leaders | aligning two Series, `fillna(0)`, merge, multi-key sort |
| 8 | Special teams | `crosstab`, then `reindex(..., fill_value=0)` |
| 9 | First blood | `reindex` to turn a missing group into an honest `NaN` |
| 10 | The game winner | `cumcount` in time order, and a definition worth reading twice |

The notebook closes with an ungraded **victory lap**: one assembled frame of
the whole feed, goals by five-minute bucket, a crude shooting percentage,
penalty minutes against results, a matplotlib histogram of goal times, and six
open questions students are invited to answer on their own.

## Grading

Every question is graded twice over.

**Public asserts** ship inside the notebook, directly under each function.
They are worth **zero points** and exist so students can tell whether they are
on track.

**Hidden asserts** live in `grading/hidden_tests.py` and carry the whole
grade — 10 points per question, split across three or four checks so partial
credit is real. Beyond re-checking the answer, they add:

- **structure checks** — return type, column order, index names, dtypes;
- **behaviour checks** — Question 2 fails if any of the 4,065 rows came back
  unparsed; Question 3 scores overtime separately from regulation; Question 4
  fails if an opponent's jersey shows up in a Michigan assist count; Question 8
  fails if the strength nobody used disappeared instead of reporting zero;
  Question 9 fails if a shutout became a `0`;
- **robustness checks** — the same function is re-run on a *different six
  games* pulled out of the feed. A student who hard-codes the values printed by
  the public asserts passes the public checks and loses the robustness points.

Each question is graded against inputs the autograder builds itself, so a
student who never gets Question 1 working can still score 90.

### Running the autograder

```bash
pip install -r requirements.txt
python grading/run_autograder.py path/to/submission.ipynb

# a whole class, plus machine-readable output
python grading/run_autograder.py submissions/*.ipynb --json results.json
```

It executes the notebook's code cells one at a time in a fresh namespace. A
cell that raises — including a failing public assert — is reported and
skipped, so one broken cell does not zero out the submission.

Before grading anything it re-runs the reference solution and compares it to
the pinned snapshot in `grading/expected_values.json`. If the dataset or the
reference has drifted, it stops with an error rather than grading a room full
of students against stale answers.

Sanity check, any time:

```bash
python grading/run_autograder.py solution/solution.ipynb   # => 100 / 100
```

## Instructor files

```
solution/reference.py       reference implementations (source of truth)
solution/solution.ipynb     the student notebook, filled in
grading/hidden_tests.py     the 10 x 10 point checks
grading/run_autograder.py   the runner
grading/build_expected.py   regenerates the pinned snapshot
grading/expected_values.json
grading/rubric.md           point-by-point breakdown
tools/generate_data.py      regenerates data/*.csv from a fixed seed
```

### Handing it out

Give students `assignment.ipynb`, `data/`, and `requirements.txt`. Withhold
`solution/`, `grading/`, and `tools/`:

```bash
mkdir -p handout && cp -r assignment.ipynb data requirements.txt handout/
```

### Changing a question

1. Edit the spec in the notebook **and** the implementation in
   `solution/reference.py`.
2. Update the matching checks in `grading/hidden_tests.py`.
3. `python grading/build_expected.py`
4. `python grading/run_autograder.py solution/solution.ipynb` — expect 100/100.

If you regenerate the data, the answers in the notebook's public asserts change
too. Re-run the reference to get the new values before you republish.

## About the messiness

The whitespace in `events.csv` is deliberate and load-bearing. 487 descriptions
carry stray leading or trailing spaces and 231 have a doubled space in the
middle, so a pattern anchored with `^` and written with literal spaces returns
`NaN` for those rows **without raising anything**. Students who test their
regex on `.head()` and move on lose points at Question 2 and again everywhere
downstream; the hidden check names the problem explicitly when it fires.

The other traps are the same shape: clocks with no leading zero, goals with two
assists rather than one, infractions with spaces in them, surnames containing a
period, an apostrophe or a hyphen, and opponent jersey numbers that collide
with Michigan's.

## About the data

**The dataset is simulated.** Yost Ice Arena, the opponents, their arenas and
the format of a play-by-play feed are real. Every player, every name, every
event and every score is generated by `tools/generate_data.py` from a fixed
seed (1996, the year Michigan won its ninth NCAA hockey championship).

Nothing here should be quoted as a real Michigan hockey statistic. The
simulated Wolverines go 23–18 and get shut out five times, which is both wrong
and unkind.

Regenerate at any time — it is deterministic:

```bash
python tools/generate_data.py
```
