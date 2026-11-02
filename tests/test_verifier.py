"""
tests/test_verifier.py

The formula-validity verdict: a correct answer passes all constraints,
and each constraint fails on its own case with its own message.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "plugin"))

import verifier
from slimconfig import build_output
from contract import SubmitInput, SubmitOutput, Task


def _run(expression: str, answer: str) -> dict:
    """Simulate a full task run through the verifier."""
    inp = build_output({"expression": expression, "answer": answer}, SubmitInput)
    out = build_output({"verdict": "?", "score": 0.0, "constraints": []}, SubmitOutput)
    return verifier.verify_task(
        Task.FORMULA_VALIDITY.value, inp, out, None, "/tmp"
    )


def _failed_id(result: dict) -> str:
    """Return the id of the first failing constraint."""
    for c in result["constraints"]:
        if not c["ok"]:
            return c["id"]
    return ""


# ── Correct answers pass ───────────────────────────────────────────────────────

def test_valid_formula_yes_passes():
    result = _run("((A∨B)∧C)", "yes")
    assert result["valid"] and result["score"] == 1.0
    assert all(c["ok"] for c in result["constraints"])


def test_valid_single_variable_passes():
    result = _run("A", "yes")
    assert result["valid"] and result["score"] == 1.0


def test_valid_negation_passes():
    result = _run("(¬A)", "yes")
    assert result["valid"] and result["score"] == 1.0


def test_invalid_formula_no_passes():
    result = _run("(A∧B)∨C", "no")
    assert result["valid"] and result["score"] == 1.0


def test_invalid_unmatched_paren_no_passes():
    result = _run("(((A∨B)∧C)", "no")
    assert result["valid"] and result["score"] == 1.0


# ── Each constraint fails on its own case ─────────────────────────────────────

def test_bad_answer_shape_fails_first():
    result = _run("(A∧B)", "maybe")
    assert not result["valid"] and result["score"] == 0.0
    assert _failed_id(result) == "answer-shape"


def test_wrong_answer_for_valid_fails_validity_correct():
    result = _run("((A↔B)→(¬A))", "no")   # legal formula, wrong answer
    assert not result["valid"] and result["score"] == 0.0
    assert _failed_id(result) == "validity-correct"


def test_wrong_answer_for_invalid_fails_validity_correct():
    result = _run("A∧B", "yes")   # illegal formula, wrong answer
    assert not result["valid"] and result["score"] == 0.0
    assert _failed_id(result) == "validity-correct"


# ── Constraint order ──────────────────────────────────────────────────────────

def test_bad_shape_stops_before_validity_check():
    """A bad shape answer should not reach the validity-correct constraint."""
    result = _run("(A∧B)", "correct")
    ids = [c["id"] for c in result["constraints"]]
    assert "validity-correct" not in ids
