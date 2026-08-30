# Other Assignments

Course assignments that live alongside the main project in this repo. Each one
is self-contained: notebook, data, hidden tests, autograder and rubric in a
single folder, with a README explaining how to hand it out and how to grade it.

| # | Assignment | Topic | Points |
|---|---|---|---|
| 1 | [🏈 Go Blue: A Pandas Data Exploration](pandas-fundamentals-go-blue/) | pandas fundamentals & Python data manipulation | 100 |
| 2 | [🏀 Hardwood: Grouping, Windows & Reshaping](pandas-grouping-hardwood/) | MultiIndexes, named aggregation, window functions, ranking, streaks | 100 |
| 3 | [🏒 The Yost Feed: Regex, Text & Time](pandas-text-parsing-yost/) | regular expressions, string extraction, clock arithmetic | 100 |
| 4 | [📺 Yada Yada Data: Text, Ambiguity & Defensible Choices](pandas-open-ended-seinfeld/) | regex on prose, and five questions with no right answer | 100 |

They are meant to be done in order — each one assumes the previous one's
vocabulary and then adds to it — but the data and the autograders are
completely independent, so any of them can be assigned on its own.

Assignment 4 is the odd one out and belongs last: half of its questions have no
right answer, and are graded on whether the student exposed their choice as an
argument, declared a defensible default, and wrote down what it cost them. See
its README for how that is made gradeable.

## How these are built

Every assignment in here follows the same shape, so a student who has done one
knows how to start the next:

- **One notebook, ten questions, ten points each.** Each question asks for one
  function that takes its data as arguments and returns a value.
- **Public asserts** ship in the notebook under each question. They are worth
  **zero points** — they exist so students can tell whether they are on track.
- **Hidden asserts** carry the grade. They re-check the answer, then add
  structure checks (return type, column order, index name) and *robustness*
  checks that re-run the student's function on a different slice of the data.
  Hard-coding the values printed by the public asserts passes the public
  checks and fails the hidden ones.
- **Partial credit is real.** Each question splits into three or four
  separately scored checks.
- **Questions are independent.** The autograder builds each question's inputs
  itself, so fumbling Question 1 does not cascade into a zero.

## Layout

```
<assignment>/
  README.md              what it covers, how to hand it out, how to grade it
  assignment.ipynb       the student notebook
  requirements.txt
  data/                  the dataset, plus a data dictionary
  solution/              reference implementation + filled-in notebook   [instructor]
  grading/               hidden tests, autograder, rubric                [instructor]
  tools/                 dataset generator                              [instructor]
```

Students get `assignment.ipynb`, `data/` and `requirements.txt`. The other
three folders stay with the instructor — each assignment README spells out the
exact copy command.

## Grading any assignment

```bash
cd other-assignments/<assignment>
pip install -r requirements.txt

python grading/run_autograder.py submissions/*.ipynb --json results.json

# sanity check: the reference solution should always score full marks
python grading/run_autograder.py solution/solution.ipynb
```
