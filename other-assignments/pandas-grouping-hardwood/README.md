# 🏀 Hardwood: Grouping, Windows & Reshaping

**Assignment 2 · Other Assignments · 100 points (10 questions × 10 points)**

The second half of pandas, wrapped around ten simulated seasons of Michigan
basketball. Assignment 1 got students to `groupby` and `pivot_table`. This one
keeps going: **MultiIndexes**, **named aggregation**, **window functions**,
**ranking inside groups**, **runs and streaks**, and the string surgery that
turns a box score into numbers you can add up.

Still no machine learning, no plotting requirement, no libraries beyond
`pandas` and `numpy`.

## What students get

```
assignment.ipynb        the notebook they fill in and hand back
data/box_scores.csv     4,160 player-games, 2015-2024
data/games.csv          320 games
data/roster.csv         150 player-seasons
data/README.md          the data dictionary
requirements.txt
```

Everything else in this folder is **instructor-only** — see
[Handing it out](#handing-it-out).

## The ten questions

| # | Question | What it teaches |
|---|---|---|
| 1 | Tip-off | `set_index` with two keys, `sort_index`, `parse_dates` |
| 2 | Splitting the line | `.str.split(expand=True)`, `to_numeric(errors="coerce")` |
| 3 | Stopping the clock | `MM:SS` → float, and why the seconds matter |
| 4 | Shooting rates | division by zero: `NaN`, never `inf`, never `0` |
| 5 | The season totals | `groupby().agg(name=(col, how))`, MultiIndex output |
| 6 | Who led the team tonight | multi-key `sort_values` + `groupby().head(1)` |
| 7 | Rolling form | `groupby().rolling()`, `droplevel`, `reindex` |
| 8 | The leaderboard | `groupby().rank(method="min")` inside a group |
| 9 | The longest streak | the `(s != s.shift()).cumsum()` run-labelling trick |
| 10 | Class and position | a two-key merge, then a pivot in a non-alphabetical order |

The notebook closes with an ungraded **victory lap**: season-by-season splits,
whether hot form carries into the next game, career arcs by player, an
efficiency-versus-volume table, a matplotlib chart of every season's rolling
scoring, and six open questions students are invited to answer on their own.

## Grading

Every question is graded twice over.

**Public asserts** ship inside the notebook, directly under each function.
They are worth **zero points** and exist so students can tell whether they are
on track.

**Hidden asserts** live in `grading/hidden_tests.py` and carry the whole
grade — 10 points per question, split across three or four checks so partial
credit is real. Beyond re-checking the answer, they add:

- **structure checks** — return type, column order, index names, dtypes;
- **behaviour checks** — Question 2 fails if a DNP became a zero; Question 7
  fails if the rolling window bleeds across a season boundary; Question 9
  fails if a winless season vanishes instead of reporting `0`;
- **robustness checks** — the same function is re-run on a *different slice of
  the data*, or with a different keyword argument (`window=10`,
  `min_games=28`). A student who hard-codes the values printed by the public
  asserts passes the public checks and loses the robustness points. Question
  10 goes further and hands the student a roster with every class label
  swapped.

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

## About the data

**The dataset is simulated.** The arenas, the conferences and the shape of a
Big Ten schedule are real. Every player, every name, every box-score line,
every final score and every attendance figure is generated by
`tools/generate_data.py` from a fixed seed (1989, the year Michigan won the
men's basketball national championship).

Nothing here should be quoted as a real Michigan basketball statistic. The
simulated Wolverines go 193–127 over these ten seasons and their best team is
a 2019 side that does not resemble any actual Michigan team.

Regenerate at any time — it is deterministic:

```bash
python tools/generate_data.py
```
