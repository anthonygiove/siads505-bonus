# Rubric

**100 points total — 10 points per question.**

Generated from `grading/hidden_tests.py`. If you change the checks there,
regenerate this table so the two do not drift apart.

The **public asserts** inside `assignment.ipynb` are worth **0 points**. They
are a self-check. Everything below is scored by the hidden tests.

## How the two halves are graded

**Questions 1–4 and 9 have right answers.** They are graded the way the other
assignments in this folder are: structure, values, and a *robustness* check
that re-runs the function on seasons 4 and 7 to catch an answer hard-coded from
the public asserts.

**Questions 5–8 and 10 do not.** For those the checks never compare the
student's default against a blessed one. They ask three separate things:

1. **Does the knob work?** The function is called at settings the student did
   not pick — `min_lines` of 1, 3 and 12; all three fill methods; all four
   combinations of the two matching flags; both credit rules. This is most of
   the points, and it is where a student who hard-coded their own choice
   loses them.
2. **Is the declared default defensible?** Read off the function signature with
   `inspect.signature`. `min_lines` must be an integer between 1 and 10;
   `method` must be one of the three named methods; the two flags must be
   actual booleans; `credit` must be `"full"` or `"split"`. A missing default
   fails — the default *is* the answer.
3. **Did they write it down?** `ASSUMPTIONS[<question>]` must be a real
   paragraph: at least 140 characters, no placeholder text.

**A different default, defended, scores exactly what the reference scores.**

## Question 1 — Roll the tape — load three files  ·  10 pts

| pts | check |
|----:|-------|
| 3 | the episodes frame |
| 3 | the lines frame |
| 4 | the character list, and the two frames agree |

## Question 2 — Who said that? — normalising a speaker column  ·  10 pts

| pts | check |
|----:|-------|
| 2 | a speaker_clean Series on the same index |
| 3 | 234 raw variants collapse to 89 speakers |
| 3 | the cleaned names are right |
| 2 | works on a different slice of the run |

## Question 3 — How much did they say? — counting words  ·  10 pts

| pts | check |
|----:|-------|
| 2 | an integer word_count Series |
| 3 | stage directions are not speech |
| 3 | the counts are right |
| 2 | works on a different slice of the run |

## Question 4 — The Big Four — share of the dialogue  ·  10 pts

| pts | check |
|----:|-------|
| 2 | one row per episode, four columns |
| 3 | a character who is not in the season is 0.0 |
| 3 | the shares are right |
| 2 | works on a different slice of the run |

## Question 5 — Who is in this episode? — *you choose the line*  ·  10 pts

| pts | check |
|----:|-------|
| 2 | shape, column order and index |
| 3 | correct at min_lines of 1, 3 and 12 |
| 2 | a defensible default is declared (1 ≤ min_lines ≤ 10) |
| 3 | the choice is written down and defended |

## Question 6 — Fourteen missing numbers — *you choose the fill*  ·  10 pts

| pts | check |
|----:|-------|
| 2 | a complete us_viewers_millions Series |
| 2 | reported episodes are left alone |
| 4 | all three methods compute correctly |
| 2 | a default is declared and defended |

## Question 7 — Catchphrases — *you choose what counts as a match*  ·  10 pts

| pts | check |
|----:|-------|
| 2 | an occurrences Series indexed by phrase |
| 1 | a phrase that never appears counts 0 |
| 5 | all four flag combinations are right |
| 2 | defaults are declared and defended |

## Question 8 — Who wrote it? — *you choose how to split a credit*  ·  10 pts

| pts | check |
|----:|-------|
| 2 | 18 writers, alphabetical, named index |
| 2 | 'split' conserves 180 episodes, 'full' does not |
| 4 | both credit rules compute correctly |
| 2 | a default is declared and defended |

## Question 9 — Who shares a scene with whom?  ·  10 pts

| pts | check |
|----:|-------|
| 2 | a (character_a, character_b) frame of scene counts |
| 2 | each pair once, walk-ons excluded |
| 4 | the counts and the sort order are right |
| 2 | works on a different slice of the run |

## Question 10 — Your own investigation  ·  10 pts

| pts | check |
|----:|-------|
| 3 | the write-up is complete and specific |
| 3 | the function runs and returns a real table |
| 2 | the same data gives the same answer twice |
| 2 | it computes from the data it is handed |

**What the automated checks can and cannot see.** They verify that
`INVESTIGATION` has all four keys filled with substantial, non-placeholder
text; that `question` ends in a question mark; that `my_investigation` returns
a DataFrame of at least 2×1; that two calls on the same input agree; and that
handing it seasons 4 and 7 produces a *different* table from the full corpus,
which is the check a pasted-in answer fails.

They cannot see whether the question is interesting or the reasoning is sound.
**If you want to grade that, grade it separately** — the automated 10 points
measure whether somebody else could check the work, not whether the work was
worth doing. A reasonable scheme is to treat this question's 10 points as the
floor and add a separate participation or discussion mark for the prose.

---

## Partial credit

Every question splits into three or four independently scored checks. A student
whose function is right but whose write-up is missing loses 2–3 points, not 10;
a student who wrote a thoughtful paragraph and got the mechanics wrong keeps
the write-up points.

## Independence

The autograder builds each question's inputs itself, using the reference
loaders. Question 1 being wrong does not cascade — a submission that never gets
`load_lines` working can still score 90.

## Cells that raise

A code cell that throws (a `NotImplementedError` left in a stub, a failing
public assert, a typo) is caught, logged under "Cells that raised", and
skipped. Later cells still execute, so one broken cell costs only the questions
that depend on it. The ungraded exploration cells are no exception — a student
who never defines `clean_speakers` will see Question 5's exploration cell fail,
and nothing else breaks.

## Common deductions

| what happened | typical cost |
|---|---|
| stripped the annotations but did not collapse the leftover double space | −3 (Q2) |
| counted stage directions as spoken words | −3 (Q3) |
| dropped an absent lead to `NaN` instead of `0.0` | −3 (Q4) |
| hard-coded their own `min_lines` instead of using the argument | −3 (Q5) |
| no default on the keyword argument at all | −2 (Q5–Q8) |
| a default outside the defensible range | −2 (Q5, Q6, Q8) |
| flags declared as `0`/`1` rather than `False`/`True` | −2 (Q7) |
| left an `ASSUMPTIONS` entry blank or full of placeholder text | −2 to −3 each |
| implemented only their own fill method | −4 (Q6) |
| implemented only their own credit rule | −4 (Q8) |
| dropped a phrase that never occurs instead of returning 0 | −1 (Q7) |
| let guests or joint credits into the pair table | −2 (Q9) |
| `my_investigation` returns a constant table | −2 (Q10) |
| `INVESTIGATION` filled in with one line per key | −3 (Q10) |
