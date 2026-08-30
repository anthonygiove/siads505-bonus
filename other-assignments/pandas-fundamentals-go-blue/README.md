# 🏈 Go Blue: A Pandas Data Exploration

**Assignment 1 · Other Assignments · 100 points (10 questions × 10 points)**

A hands-on introduction to `pandas` fundamentals and everyday Python data
manipulation, wrapped around fifteen simulated seasons of Michigan football.
Students work through one notebook, writing ten functions that take them from
`read_csv` to `pivot_table`.

No machine learning, no plotting requirements, no extra libraries. Just the
things that actually get used: loading, cleaning, filtering, grouping,
joining, reshaping.

## What students get

```
assignment.ipynb      the notebook they fill in and hand back
data/games.csv        195 games, 2010-2024
data/opponents.csv    32 teams, with the conference/rival metadata
data/README.md        the data dictionary
requirements.txt
```

Everything else in this folder is **instructor-only** — see
[Handing it out](#handing-it-out).

## The ten questions

| # | Question | What it teaches |
|---|---|---|
| 1 | Kickoff | `read_csv`, `parse_dates`, `set_index` |
| 2 | Scoreboard math | derived columns, `.copy()`, boolean dtypes |
| 3 | Best and worst | `idxmax` / `idxmin`, returning index labels |
| 4 | Follow the money | the `.str` accessor, `pd.to_numeric(errors="coerce")` |
| 5 | Season report card | `groupby`, `.sum()` / `.size()`, assembling a frame |
| 6 | Under the lights | parsing 12-hour times, `np.where`, mean of a boolean |
| 7 | Counting the crowd | missing data, `groupby(...).transform("median")`, `fillna` |
| 8 | Know your enemy | `merge`, why `how="left"` matters, multi-key sorting |
| 9 | The rivalry report | filtering with `.isin()`, multi-column aggregation |
| 10 | Weather or not | `pivot_table`, and leaving a real `NaN` alone |

The notebook closes with an ungraded **victory lap** section: coach-by-coach
records, an attendance-vs-margin correlation, a ticket-price breakdown, a
Maize-and-Blue bar chart, and five open questions students are invited to
answer on their own.

## Grading

Every question is graded twice over.

**Public asserts** ship inside the notebook, directly under each function.
They are worth **zero points** and exist so students can tell whether they are
on track.

**Hidden asserts** live in `grading/hidden_tests.py` and carry the whole
grade — 10 points per question, split across three or four checks so partial
credit is real. Beyond re-checking the answer, they add:

- **structure checks** — return type, column order, index name, dtypes;
- **behaviour checks** — e.g. Question 2 fails if the student mutated the
  DataFrame they were handed;
- **robustness checks** — the same function is re-run on a *different slice of
  the data* and compared against the reference. A student who hard-codes the
  values printed by the public asserts passes the public checks and loses the
  robustness points. Question 9 goes further and hands the student an
  opponents table with different teams flagged as rivals.

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

**The dataset is simulated.** Team names, conferences, stadiums, stadium
capacities and the Michigan coaching timeline (Rodriguez → Hoke → Harbaugh →
Moore) are real. Every score, attendance figure, temperature, weather
condition and ticket price is generated by `tools/generate_data.py` from a
fixed seed (1817, the year the University was founded).

Nothing here should be quoted as a real Michigan football statistic. The
simulated Wolverines go 4–11 against Ohio State over these fifteen seasons,
which is both wrong and rude.

Regenerate at any time — it is deterministic:

```bash
python tools/generate_data.py
```
