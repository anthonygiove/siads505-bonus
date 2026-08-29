"""
Grade a submitted notebook against the hidden tests.

    python grading/run_autograder.py assignment.ipynb
    python grading/run_autograder.py submissions/*.ipynb --json results.json

What it does, in order:

1. Re-runs the reference solution and compares it to the pinned snapshot in
   expected_values.json. If the data or the reference has drifted, it stops
   before grading anyone.
2. Executes the notebook's code cells one at a time in a fresh namespace. A
   cell that raises (including a failing public assert) is recorded and
   skipped -- the remaining cells still run, so one broken cell does not
   zero out the submission.
3. Runs the hidden checks for all ten questions and prints a scorecard.

Every question is graded on inputs the autograder builds itself, so the
questions are independent of one another.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "grading"))
sys.path.insert(0, str(ROOT / "solution"))

import hidden_tests  # noqa: E402
from _serialize import to_jsonable  # noqa: E402


def verify_snapshot() -> None:
    import build_expected

    snapshot_path = ROOT / "grading" / "expected_values.json"
    if not snapshot_path.exists():
        raise SystemExit(
            "grading/expected_values.json is missing. Run: python grading/build_expected.py"
        )
    pinned = json.loads(snapshot_path.read_text())
    current = json.loads(json.dumps(build_expected.build()))
    drifted = sorted(k for k in set(pinned) | set(current) if pinned.get(k) != current.get(k))
    if drifted:
        raise SystemExit(
            "The reference answers no longer match the pinned snapshot for: "
            + ", ".join(drifted)
            + "\nEither the dataset or solution/reference.py changed. If that was "
            "deliberate, rerun: python grading/build_expected.py"
        )


def load_notebook_namespace(path: Path) -> tuple[dict, list[str]]:
    import nbformat

    nb = nbformat.read(path, as_version=4)
    # `display` is an IPython builtin inside Jupyter but not out here, and
    # exploratory cells legitimately use it.
    namespace: dict = {"__name__": "__student__", "display": print}
    errors: list[str] = []

    for i, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        # Drop IPython magics and shell escapes; they are not valid Python.
        source = "\n".join(
            line for line in cell.source.splitlines()
            if not line.lstrip().startswith(("%", "!"))
        )
        if not source.strip():
            continue
        try:
            exec(compile(source, f"<cell {i}>", "exec"), namespace)
        except BaseException as exc:  # noqa: BLE001 -- a student cell can raise anything
            errors.append(f"cell {i}: {type(exc).__name__}: {exc}")
    return namespace, errors


def grade(namespace: dict) -> dict:
    results = []
    for question in hidden_tests.QUESTIONS:
        checks = []
        earned = 0.0
        for weight, label, check in question["checks"]:
            try:
                check(namespace)
            except BaseException as exc:  # noqa: BLE001
                detail = str(exc).strip()
                if isinstance(exc, NotImplementedError):
                    message = "not implemented yet"
                elif isinstance(exc, AssertionError):
                    message = detail or "assertion failed"
                elif detail:
                    message = f"{type(exc).__name__}: {detail}"
                else:
                    message = type(exc).__name__
                checks.append(
                    {"label": label, "points": 0.0, "possible": weight, "message": message}
                )
            else:
                earned += weight
                checks.append({"label": label, "points": float(weight), "possible": weight})
        results.append(
            {
                "number": question["number"],
                "title": question["title"],
                "points": earned,
                "possible": hidden_tests.POINTS_PER_QUESTION,
                "checks": checks,
            }
        )
    return {
        "questions": results,
        "score": sum(q["points"] for q in results),
        "possible": sum(q["possible"] for q in results),
    }


def print_report(notebook: Path, report: dict, cell_errors: list[str]) -> None:
    print()
    print("=" * 68)
    print(f"  GO BLUE PANDAS AUTOGRADER  --  {notebook.name}")
    print("=" * 68)
    for question in report["questions"]:
        mark = "PASS" if question["points"] == question["possible"] else "----"
        print(
            f"\n[{mark}] Q{question['number']:>2}  {question['title']}"
            f"   {question['points']:g}/{question['possible']} pts"
        )
        for check in question["checks"]:
            bullet = "  ok  " if check["points"] == check["possible"] else "  X   "
            print(f"    {bullet}({check['points']:g}/{check['possible']}) {check['label']}")
            if "message" in check:
                for line in str(check["message"]).splitlines():
                    print(f"          {line}")
    if cell_errors:
        print("\nCells that raised while the notebook was executed:")
        for err in cell_errors:
            print(f"    - {err}")
    print()
    print("-" * 68)
    print(f"  TOTAL: {report['score']:g} / {report['possible']} points")
    print("-" * 68)
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebooks", nargs="+", type=Path)
    parser.add_argument("--json", type=Path, help="write machine-readable results here")
    parser.add_argument(
        "--skip-snapshot-check", action="store_true",
        help="grade even if the reference answers have drifted from the snapshot",
    )
    args = parser.parse_args()

    os.chdir(ROOT)  # so a student's relative "data/games.csv" resolves
    if not args.skip_snapshot_check:
        verify_snapshot()

    all_results = []
    for notebook in args.notebooks:
        if not notebook.exists():
            print(f"skipping {notebook}: file not found", file=sys.stderr)
            continue
        try:
            namespace, cell_errors = load_notebook_namespace(notebook)
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            print(f"skipping {notebook}: could not be read as a notebook", file=sys.stderr)
            continue
        report = grade(namespace)
        report["notebook"] = str(notebook)
        report["cell_errors"] = cell_errors
        print_report(notebook, report, cell_errors)
        all_results.append(report)

    if args.json:
        args.json.write_text(json.dumps(all_results, indent=2) + "\n")
        print(f"wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
