# 📺 Yada Yada Data: Text, Ambiguity & Defensible Choices

**Assignment 4 · Other Assignments · 100 points (10 questions × 10 points)**

The first three assignments in this folder have right answers. **This one is
half open on purpose.**

Students get 26,389 lines of dialogue from a nine-season sitcom, its episode
list, and its character list. Five of the ten questions are ordinary graded
pandas work. **The other five are questions that sound precise and are not** —
*who is in this episode?*, *how many times does someone say that?*, *how do you
fill fourteen missing audience figures?* — because the data contains no column
that answers them and never will.

For those, the assignment is: **look at the data, make a call, expose the call
as an argument, and write down why.**

## The mechanism

This is the part worth stealing for other assignments. An underdetermined
question is graded on three things that have nothing to do with matching a
blessed answer:

1. **Does the knob work?** The hidden checks call the student's function at
   settings they did **not** choose — `min_lines` of 1, 3 and 12; all three
   fill methods; all four combinations of two matching flags; both credit
   rules. A student who hard-codes their own choice fails here.
2. **Is the declared default defensible?** Read straight off the signature with
   `inspect.signature`. The default *is* the answer, so a missing default fails
   and a nonsense one (`min_lines=250`) fails with a message saying why.
3. **Did they write it down?** Each of those questions has an entry in an
   `ASSUMPTIONS` dict at the top of the notebook. The check wants a real
   paragraph — what you chose, why it is defensible *on this data*, and what it
   costs — and rejects placeholders.

**A different default, defended, scores exactly what the reference scores.**

Every one of those questions is preceded by an **ungraded exploration cell**
that shows the student what the choice actually costs before they make it: the
distribution of lines-per-character-per-episode, the audience trend by season,
the same phrase counted four different ways, who among the writers never works
alone.

## What students get

```
assignment.ipynb        the notebook they fill in and hand back
data/lines.csv          26,389 lines of dialogue
data/episodes.csv       180 episodes
data/characters.csv     34 characters
data/README.md          the data dictionary
requirements.txt
```

Everything else in this folder is **instructor-only** — see
[Handing it out](#handing-it-out).

## The ten questions

| # | Question | Kind | What it is about |
|---|---|---|---|
| 1 | Roll the tape | closed | three loaders, three shapes |
| 2 | Who said that? | closed | 234 raw speaker strings → 89 speakers |
| 3 | How much did they say? | closed | words per line, stage directions excluded |
| 4 | The Big Four | closed | share of the dialogue; `0.0` vs `NaN` |
| 5 | **Who is in this episode?** | **open** | *you pick the line-count threshold* |
| 6 | **Fourteen missing numbers** | **open** | *you pick the fill strategy* |
| 7 | **Catchphrases** | **open** | *you pick case and word-boundary rules* |
| 8 | **Who wrote it?** | **open** | *you pick how a co-credit splits* |
| 9 | Who shares a scene with whom? | closed | pairwise scene co-occurrence |
| 10 | **Your own investigation** | **open** | *you write the question* |

Question 10 is the capstone: the student writes their own question, fills in an
`INVESTIGATION` dict (`question` / `assumptions` / `method` / `finding`), and
writes `my_investigation(episodes, lines, characters)` to support it. It is
graded on **checkability, not on being interesting** — the write-up is
complete, the function returns a real table, two calls agree, and handing it
two seasons instead of nine produces a different answer. That last check is what
a pasted-in constant fails.

The notebook closes with an ungraded **victory lap** that reopens six decisions
the assignment made *for* the student — a joint credit counted as a character,
a line as the unit instead of a word, absence encoded as zero, a scene number
standing in for "were they talking to each other", stage directions discarded,
and the fact that the corpus is simulated at all — and invites them to disagree.

## Grading

**Public asserts** ship inside the notebook under each function. They are worth
**zero points** and exist so students can tell whether they are on track. On
the open questions they deliberately check the *mechanism* (call the function
at three thresholds, at all four flag settings) rather than the student's own
default.

**Hidden asserts** live in `grading/hidden_tests.py` and carry the whole grade.
`grading/rubric.md` has the point-by-point split, including a note on what the
automated checks on Question 10 can and cannot see.

### Running the autograder

```bash
pip install -r requirements.txt
python grading/run_autograder.py path/to/submission.ipynb

# a whole class, plus machine-readable output
python grading/run_autograder.py submissions/*.ipynb --json results.json
```

Sanity check, any time:

```bash
python grading/run_autograder.py solution/solution.ipynb   # => 100 / 100
```

Before grading anything it re-runs the reference solution against the pinned
snapshot in `grading/expected_values.json`. Note what the snapshot pins on the
open questions: the answer **at each specific setting of the knob**, never the
reference's own default, which is one defensible choice among several.

## Instructor files

```
solution/reference.py       reference implementations, plus a filled-in ASSUMPTIONS
solution/solution.ipynb     the student notebook, filled in
grading/hidden_tests.py     the 10 x 10 point checks
grading/run_autograder.py   the runner
grading/build_expected.py   regenerates the pinned snapshot
grading/expected_values.json
grading/rubric.md           point-by-point breakdown
tools/generate_data.py      regenerates data/*.csv from a fixed seed
```

The `ASSUMPTIONS` dict in `solution/reference.py` is a **model answer, not a
key**. It is written the way a full-credit justification reads — a concrete
choice, a reason grounded in something visible in the exploration cell, and an
honest statement of the cost. Hand it out after grading if that is useful; it
is more instructive than the code.

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

## About the data

**The corpus is simulated, and this matters more here than in the other three
assignments**, because this one is about drawing conclusions.

Real: the nine-season, 180-episode structure and the per-season episode counts;
the character names and their roles; the writers; the directors.

Simulated: **every line of dialogue**, every title, every air date, every
audience figure and rating, every writing and directing credit, every location.
Dialogue is assembled from templates and word banks by
`tools/generate_data.py`, seeded with 1989. A handful of the show's famous
catchphrases were sprinkled through it so Question 7 has something to find;
nothing else in the dialogue is a quotation.

Any pattern a student finds is therefore a property of a random number
generator, and the last item in the victory lap says so explicitly and asks
them which of their findings they would still expect to hold in a real script
corpus. That is not a disclaimer bolted on at the end — on an assignment about
defensible conclusions it is the last and most important assumption on the
list.

Regenerate at any time — it is deterministic:

```bash
python tools/generate_data.py
```
