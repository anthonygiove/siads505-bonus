# Rubric

**100 points total — 10 points per question.**

Generated from `grading/hidden_tests.py`. If you change the checks there,
regenerate this table so the two do not drift apart.

The **public asserts** inside `assignment.ipynb` are worth **0 points**. They
are a self-check. Everything below is scored by the hidden tests.

Checks labelled *robustness* re-run the student's function on a different slice
of the data and compare against the reference solution. They are the ones that
catch an answer hard-coded from the public asserts.

## Question 1 — Kickoff — load the data  ·  10 pts

`load_games(path)` — read the CSV, parse `date` as datetime, index by `game_id`.

| pts | check |
|----:|-------|
| 3 | returns a DataFrame of the right size |
| 3 | game_id is a unique index |
| 4 | columns, dtypes and spot-checked values |

## Question 2 — Scoreboard math — derived columns  ·  10 pts

`add_result_columns(games)` — add `point_diff`, `total_points`, `won` to a copy.

| pts | check |
|----:|-------|
| 3 | the three new columns exist |
| 5 | the values are right |
| 2 | the input frame was not mutated |

## Question 3 — Best and worst — idxmax / idxmin  ·  10 pts

`best_and_worst(games)` — `(biggest_win_game_id, worst_loss_game_id)`.

| pts | check |
|----:|-------|
| 2 | returns a 2-tuple of game_ids |
| 5 | the right two games |
| 3 | works on a different slice of the schedule |

## Question 4 — Follow the money — string cleaning  ·  10 pts

`ticket_prices(games)` — clean `avg_ticket_price` into a float Series named `ticket_price`.

| pts | check |
|----:|-------|
| 3 | a float Series named ticket_price |
| 3 | unreported prices become NaN |
| 4 | every price converted correctly |

## Question 5 — Season report card — groupby  ·  10 pts

`season_report_card(games)` — wins/losses/points_for/points_against/win_pct per season.

| pts | check |
|----:|-------|
| 3 | shape, column order and season index |
| 4 | the values are right |
| 3 | works on a different set of seasons |

## Question 6 — Under the lights — parsing times  ·  10 pts

`night_game_split(games)` — win pct for kickoffs before vs. from 6:00 PM.

| pts | check |
|----:|-------|
| 3 | a Day/Night Series |
| 4 | the win percentages are right |
| 3 | works on home games only |

## Question 7 — Counting the crowd — missing data  ·  10 pts

`filled_attendance(games)` — fill attendance gaps with the median for that `site`.

| pts | check |
|----:|-------|
| 2 | a complete attendance Series |
| 2 | reported attendance left alone |
| 4 | gaps filled with the right group median |
| 2 | works on a different slice of the schedule |

## Question 8 — Know your enemy — merging  ·  10 pts

`record_by_conference(games, opponents)` — left-merge, then record per conference.

| pts | check |
|----:|-------|
| 3 | shape and a merge that keeps 195 rows |
| 4 | the values and the sort order are right |
| 3 | works when the opponents table changes |

## Question 9 — The rivalry report  ·  10 pts

`rivalry_report(games, opponents)` — one row per team flagged `is_rival`.

| pts | check |
|----:|-------|
| 3 | shape, column order and rival index |
| 4 | the values are right |
| 3 | rivals are read from the opponents table |

## Question 10 — Weather or not — pivot tables  ·  10 pts

`weather_scoring(games)` — pivot mean `michigan_points` by weather × site.

| pts | check |
|----:|-------|
| 2 | a weather-by-site pivot table |
| 4 | the averages are right |
| 1 | the empty cell stays empty |
| 3 | works on a different set of seasons |

---

## Partial credit

Every question splits into three or four independently scored checks, so a
student whose answer is right but whose column order is wrong loses a few
points, not ten.

## Independence

The autograder builds each question's inputs itself, using the reference
loader. Question 1 being wrong does not cascade — a submission that never
gets `load_games` working can still score 90.

## Cells that raise

A code cell that throws (a `NotImplementedError` left in a stub, a failing
public assert, a typo) is caught, logged under "Cells that raised", and
skipped. Later cells still execute, so one broken cell costs only the
questions that depend on it.

## Common deductions

| what happened | typical cost |
|---|---|
| mutated the DataFrame passed in instead of copying it | −2 (Q2) |
| `won` stored as `0`/`1` or `"Yes"`/`"No"` instead of a boolean | −5 (Q2) |
| hard-coded a `game_id` seen in the public asserts | −3 (Q3) |
| dropped the `unavailable` rows instead of coercing them to `NaN` | −3 to −7 (Q4) |
| forgot to round `win_pct` to 3 decimals | −4 (Q5, Q8) |
| read `"12:00 PM"` as midnight | −7 (Q6) |
| filled every attendance gap with one global median | −4 (Q7) |
| used `how="inner"` and changed the row count | −3 (Q8) |
| hard-coded the three rival names | −3 (Q9) |
| filled the empty pivot cell with `0` | −1 (Q10) |

