"""Verifier for the formula-validity task and submit tool."""

from __future__ import annotations

from pathlib import Path

from contract import SubmitInput, SubmitOutput
from formula_checker import is_valid_formula


# ── Constraint helpers ────────────────────────────────────────────────────────

def _constraint(cid: str, ok: bool, detail: str) -> dict:
    return {"id": cid, "ok": ok, "detail": detail}


def _verdict(passed: bool, constraints: list[dict]) -> dict:
    return {
        "valid":       passed,
        "verdict":     "pass" if passed else "fail",
        "score":       1.0 if passed else 0.0,
        "constraints": constraints,
    }


# ── Per-call checks ───────────────────────────────────────────────────────────

def verify_input(inp: SubmitInput) -> list[dict]:
    """Validate the tool's input (called before the tool runs)."""
    # Input is already type-checked by slimconfig; nothing extra to verify.
    return []


def verify_output(inp: SubmitInput, out: SubmitOutput, workspace: Path) -> dict:
    """
    Grade the tool's output against the formula-validity checker.

    Constraints (in order):
      1. answer-shape     — answer is exactly "yes" or "no"
      2. validity-correct — answer matches is_valid_formula(expression)
    """
    constraints = []

    # Constraint 1 — answer shape
    normalised = inp.answer.strip().lower()
    if normalised not in ("yes", "no"):
        constraints.append(_constraint(
            "answer-shape", False,
            f"expected 'yes' or 'no', got {inp.answer!r}",
        ))
        return _verdict(False, constraints)
    constraints.append(_constraint(
        "answer-shape", True, f"answer shape OK: {normalised!r}",
    ))

    # Constraint 2 — correctness
    valid    = is_valid_formula(inp.expression)
    expected = "yes" if valid else "no"
    if normalised == expected:
        constraints.append(_constraint(
            "validity-correct", True,
            f"answer {normalised!r} matches checker ({expected!r})",
        ))
        return _verdict(True, constraints)

    label = "a legal formula" if valid else "NOT a legal formula"
    constraints.append(_constraint(
        "validity-correct", False,
        f"answer {normalised!r} is wrong — {inp.expression!r} is {label}",
    ))
    return _verdict(False, constraints)


def verify_task(arguments: SubmitInput, output: SubmitOutput,
                reference, workspace: str) -> dict:
    """Top-level task verifier called by NanoAgent after the agent submits."""
    return verify_output(arguments, output, Path(workspace))
