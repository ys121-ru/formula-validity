"""
verifier/task.py

Grade an agent's answer to a yes/no formula-validity question.

Constraints (run in order; first failure stops scoring):
  1. answer-shape     – the agent's answer is exactly "yes" or "no"
  2. validity-correct – the agent's answer matches is_valid_formula()

Scoring:
  All constraints pass  →  verdict "pass",  score 1.0
  Any constraint fails  →  verdict "fail",  score 0.0

Note: there is no "expression-valid" pre-check — the expression being
judged might intentionally be invalid; that is the whole point of the task.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "plugin"))

from formula_checker import is_valid_formula


# ── Constraints ───────────────────────────────────────────────────────────────

def check_answer_shape(answer: str) -> tuple[bool, str]:
    """Constraint 1 — is the answer exactly 'yes' or 'no'?"""
    normalised = answer.strip().lower()
    if normalised in ("yes", "no"):
        return True, f"answer shape OK: {normalised!r}"
    return False, f"expected 'yes' or 'no', got {answer!r}"


def check_validity_correct(expression: str, answer: str) -> tuple[bool, str]:
    """Constraint 2 — does the answer match the checker?"""
    valid    = is_valid_formula(expression)
    expected = "yes" if valid else "no"
    actual   = answer.strip().lower()
    if actual == expected:
        return True, f"answer {actual!r} matches checker ({expected!r})"
    verdict = "a legal formula" if valid else "NOT a legal formula"
    return False, f"answer {actual!r} is wrong — {expression!r} is {verdict}"


# ── Top-level verifier ────────────────────────────────────────────────────────

def verify(expression: str, answer: str) -> dict:
    """
    Run all constraints and return a verdict dict:

      {
        "verdict":     "pass" | "fail",
        "score":       1.0 | 0.0,
        "constraints": [
          {"id": "answer-shape",     "ok": true, "detail": "..."},
          {"id": "validity-correct", "ok": true, "detail": "..."}
        ]
      }
    """
    constraints = []

    def run(cid: str, ok: bool, detail: str) -> bool:
        constraints.append({"id": cid, "ok": ok, "detail": detail})
        return ok

    ok, detail = check_answer_shape(answer)
    if not run("answer-shape", ok, detail):
        return _verdict(False, constraints)

    ok, detail = check_validity_correct(expression, answer)
    run("validity-correct", ok, detail)
    return _verdict(ok, constraints)


def _verdict(passed: bool, constraints: list[dict]) -> dict:
    return {
        "verdict":     "pass" if passed else "fail",
        "score":       1.0   if passed else 0.0,
        "constraints": constraints,
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    """
    Usage:
      python verifier/task.py "<expression>" "<answer>"

    Examples:
      python verifier/task.py "((A∨B)∧C)" "yes"
      python verifier/task.py "(A∧B)∨C"   "no"
    """
    if len(sys.argv) != 3:
        print(main.__doc__)
        sys.exit(1)

    _, expression, answer = sys.argv
    print(json.dumps(verify(expression, answer), indent=2))


if __name__ == "__main__":
    main()
