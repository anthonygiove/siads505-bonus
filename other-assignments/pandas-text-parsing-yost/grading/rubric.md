# Rubric

**100 points total — 10 points per question.**

Generated from `grading/hidden_tests.py`. If you change the checks there,
regenerate this table so the two do not drift apart.

The **public asserts** inside `assignment.ipynb` are worth **0 points**. They
are a self-check. Everything below is scored by the hidden tests.

Checks labelled *robustness* re-run the student's function on a different slice
of the season — six whole games pulled out of the feed. They are the ones that
catch an answer hard-coded from the public asserts.

## Question 1 — Warm-ups — load the feed  ·  10 pts

`load_events(path)`, `load_games(path)`, `load_roster(path)`.

| pts | check |
|----:|-------|
| 3 | an events frame of the right size, indexed by event_id |
| 3 | the right columns and dtypes |
| 4 | the games and roster loaders |

## Question 2 — Reading the sheet — named capture groups  ·  10 pts

`parse_events(events)` — one `str.extract` for type, clock, team, jersey, player.

| pts | check |
|----:|-------|
| 2 | five columns on the same index |
| 3 | every one of the 4,065 rows parsed |
| 3 | the parsed fields are right |
| 2 | works on a different slice of the season |

## Question 3 — Clock math — a clock that counts down  ·  10 pts

`elapsed_seconds(events)` — seconds since the opening face-off, overtime included.

| pts | check |
|----:|-------|
| 2 | an integer elapsed_seconds Series |
| 3 | regulation times are right |
| 3 | overtime is five minutes, not twenty |
| 2 | works on a different slice of the season |

## Question 4 — Assist credits — findall and explode  ·  10 pts

`assist_credits(events)` — assists per Michigan jersey.

| pts | check |
|----:|-------|
| 2 | an assists Series indexed by jersey |
| 2 | only Michigan goals are counted |
| 4 | the assist totals are right |
| 2 | works on a different slice of the season |

## Question 5 — The penalty box — two fields from one match  ·  10 pts

`penalty_summary(events)` — infraction and minutes out of one parenthesis.

| pts | check |
|----:|-------|
| 2 | shape, column order and index |
| 2 | multi-word infractions survive |
| 4 | the counts and minutes are right |
| 2 | works on a different slice of the season |

## Question 6 — Roster details — three kinds of string surgery  ·  10 pts

`roster_details(roster)` — surname, height in inches, home state/province/country.

| pts | check |
|----:|-------|
| 2 | shape, column order and jersey index |
| 3 | surnames with periods, apostrophes and hyphens |
| 3 | feet-and-inches converted to inches |
| 2 | home state, province or country |

## Question 7 — Scoring leaders — combine, merge, sort  ·  10 pts

`scoring_leaders(events, roster)` — goals, assists, points, named and ranked.

| pts | check |
|----:|-------|
| 2 | shape, column order and player index |
| 4 | goals, assists and points are right |
| 2 | ties on points broken by goals |
| 2 | works on a different slice of the season |

## Question 8 — Special teams — a crosstab with a missing column  ·  10 pts

`strength_breakdown(events)` — goals by team and manpower situation.

| pts | check |
|----:|-------|
| 3 | two rows, five columns, in the order asked for |
| 2 | the strength nobody used is a zero, not a gap |
| 3 | the counts are right |
| 2 | works on a different slice of the season |

## Question 9 — First blood — a genuine missing value  ·  10 pts

`first_goal_times(events, games)` — when Michigan first scored, `NaN` if never.

| pts | check |
|----:|-------|
| 3 | a float Series aligned to games |
| 3 | a shutout is NaN, not zero |
| 2 | the times are right |
| 2 | works on a different slice of the season |

## Question 10 — The game winner — counting inside a group  ·  10 pts

`game_winning_goals(events, games)` — the `(opponent_goals + 1)`-th Michigan goal.

| pts | check |
|----:|-------|
| 3 | one row per win, with the right columns |
| 3 | the right goal in each game |
| 2 | goals are counted in time order |
| 2 | works on a different slice of the season |

---

## Partial credit

Every question splits into three or four independently scored checks, so a
student whose answer is right but whose column order is wrong loses a few
points, not ten.

## Independence

The autograder builds each question's inputs itself, using the reference
loaders. Question 1 being wrong does not cascade — a submission that never
gets `load_events` working can still score 90.

## Cells that raise

A code cell that throws (a `NotImplementedError` left in a stub, a failing
public assert, a typo) is caught, logged under "Cells that raised", and
skipped. Later cells still execute, so one broken cell costs only the
questions that depend on it.

## Common deductions

| what happened | typical cost |
|---|---|
| anchored the pattern with `^` without stripping first | −3 (Q2), cascading |
| matched a literal space instead of `\s+` | −3 (Q2) |
| `\d{2}:\d{2}` missed the clocks with no leading zero | −3 (Q2) |
| read the clock as time elapsed instead of time remaining | −3 to −8 (Q3) |
| treated overtime as a 20-minute period | −3 (Q3) |
| counted assists on the opponent's goals too | −2 to −6 (Q4) |
| used `extract` instead of `findall` and lost the second assist | −4 (Q4) |
| matched one word and lost `Delay of Game` | −2 to −6 (Q5) |
| took "the second word" as the surname (`St.`) | −3 (Q6) |
| took the last two characters as the home state (`en` for Sweden) | −2 (Q6) |
| left `NaN` where a player had goals but no assists | −4 (Q7) |
| dropped the `PS` column because no goal used it | −2 to −5 (Q8) |
| filled a shutout with `0` instead of `NaN` | −3 (Q9) |
| sorted goals by `event_id` or by clock instead of elapsed time | −2 to −5 (Q10) |
