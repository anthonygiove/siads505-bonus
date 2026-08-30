# Rubric

**100 points total — 10 points per question.**

Generated from `grading/hidden_tests.py`. If you change the checks there,
regenerate this table so the two do not drift apart.

The **public asserts** inside `assignment.ipynb` are worth **0 points**. They
are a self-check. Everything below is scored by the hidden tests.

Checks labelled *robustness* re-run the student's function on a different slice
of the data, or with a different keyword argument. They are the ones that catch
an answer hard-coded from the public asserts.

## Question 1 — Tip-off — load the box scores  ·  10 pts

`load_box_scores(path)` and `load_games(path)` — parse dates, build a sorted
`(game_id, player_id)` MultiIndex.

| pts | check |
|----:|-------|
| 3 | returns a DataFrame of the right size |
| 3 | a sorted, unique (game_id, player_id) MultiIndex |
| 4 | columns, dtypes, and the games loader |

## Question 2 — Splitting the line — made-attempted strings  ·  10 pts

`split_shooting(box)` — `"7-13"` into six float columns, DNP rows `NaN`.

| pts | check |
|----:|-------|
| 2 | six float columns in the right order |
| 2 | a DNP is NaN, not zero |
| 4 | every split is right |
| 2 | works on a different slice of the decade |

## Question 3 — Stopping the clock — MM:SS to minutes  ·  10 pts

`minutes_played(box)` — `"26:38"` → `26.63`, `"DNP"` → `NaN`.

| pts | check |
|----:|-------|
| 2 | a float Series named minutes_played |
| 3 | the values are right |
| 3 | the seconds are not thrown away |
| 2 | works on a different season |

## Question 4 — Shooting rates — dividing without blowing up  ·  10 pts

`shooting_rates(box)` — FG%, 3P%, FT% and true shooting; zero denominators are `NaN`.

| pts | check |
|----:|-------|
| 2 | four rate columns on the same index |
| 3 | zero attempts give NaN, never inf or 0 |
| 3 | the rates are right |
| 2 | works on a different slice of the decade |

## Question 5 — Player season totals — named aggregation  ·  10 pts

`player_season_totals(box)` — drop DNP rows, group by `(season, player)`.

| pts | check |
|----:|-------|
| 3 | a (season, player) frame with the right columns |
| 2 | DNP games are not counted as games played |
| 3 | the totals are right |
| 2 | works on a different set of seasons |

## Question 6 — Leading scorer — one row per game  ·  10 pts

`leading_scorer(box)` — top scorer per game, ties broken by minutes then name.

| pts | check |
|----:|-------|
| 2 | exactly one row per game |
| 4 | the right player in each game |
| 2 | ties broken by minutes, then alphabetically |
| 2 | works on a different slice of the decade |

## Question 7 — Rolling form — window functions  ·  10 pts

`rolling_form(games, window=5)` — rolling mean of `team_points` within a season.

| pts | check |
|----:|-------|
| 3 | a rolling_points Series aligned to games |
| 2 | the window restarts each season |
| 3 | the averages are right |
| 2 | honours the window argument |

## Question 8 — Season leaderboard — ranking within groups  ·  10 pts

`season_leaderboard(box, min_games=20)` — qualified scorers ranked per season.

| pts | check |
|----:|-------|
| 2 | shape, column order and index |
| 3 | rank restarts at 1 every season |
| 3 | the leaderboard is right |
| 2 | honours the min_games argument |

## Question 9 — Longest win streak — runs of consecutive results  ·  10 pts

`longest_win_streak(games)` — longest run of wins per season, `0` if there were none.

| pts | check |
|----:|-------|
| 2 | a longest_win_streak Series indexed by season |
| 4 | the streaks are right |
| 2 | a winless season reports 0 |
| 2 | works on a truncated schedule |

## Question 10 — Class and position — merge, then pivot  ·  10 pts

`class_scoring(box, roster)` — two-key merge, then a pivot in academic order.

| pts | check |
|----:|-------|
| 2 | rows and columns in the order asked for |
| 4 | the averages are right |
| 2 | class and position come from the roster |
| 2 | works on a different set of seasons |

---

## Partial credit

Every question splits into three or four independently scored checks, so a
student whose answer is right but whose column order is wrong loses a few
points, not ten.

## Independence

The autograder builds each question's inputs itself, using the reference
loaders. Question 1 being wrong does not cascade — a submission that never
gets `load_box_scores` working can still score 90.

## Cells that raise

A code cell that throws (a `NotImplementedError` left in a stub, a failing
public assert, a typo) is caught, logged under "Cells that raised", and
skipped. Later cells still execute, so one broken cell costs only the
questions that depend on it.

## Common deductions

| what happened | typical cost |
|---|---|
| left `game_id`/`player_id` as columns instead of a MultiIndex | −3 (Q1) |
| forgot `.sort_index()` | −3 (Q1) |
| filled DNP shooting lines with `0` instead of `NaN` | −2 to −6 (Q2) |
| read `"26:38"` as 26 minutes | −3 (Q3) |
| `fg3_made / fg3_att` returned `inf` or `0.0` on zero attempts | −3 (Q4) |
| counted DNP rows as games played | −2 to −5 (Q5) |
| broke a scoring tie by row order instead of minutes | −2 (Q6) |
| let the rolling window run across the season boundary | −2 to −5 (Q7) |
| ranked across the whole decade instead of within each season | −3 (Q8) |
| dropped winless seasons instead of reporting `0` | −2 (Q9) |
| merged on `player_id` alone and multiplied the rows | −4 (Q10) |
| left the pivot in alphabetical order (`Fr, Jr, So, Sr`) | −2 (Q10) |
