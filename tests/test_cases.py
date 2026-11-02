"""
tests/test_cases.py

Iterate over every .json file in tests/cases/ and assert the verifier
result matches the expected verdict and score.

Run with:
  pytest tests/
"""

import pytest
from conftest import load_cases

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "plugin"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from slimconfig import build_output
from contract import SubmitInput, SubmitOutput, Task
import verifier


def _run(case: dict) -> dict:
    inp = build_output(
        {"expression": case["expression"], "answer": case["agent_answer"]},
        SubmitInput,
    )
    out = build_output({"verdict": "?", "score": 0.0, "constraints": []}, SubmitOutput)
    return verifier.verify_task(Task.FORMULA_VALIDITY.value, inp, out, None, "/tmp")


@pytest.mark.parametrize("fname,case", load_cases(), ids=[c for c, _ in load_cases()])
def test_case(fname: str, case: dict) -> None:
    result = _run(case)
    expect = case["expect"]

    detail = "\n".join(
        f"  [{c['id']}] {'ok' if c['ok'] else 'FAIL'}  {c['detail']}"
        for c in result["constraints"]
    )

    assert result["verdict"] == expect["verdict"], (
        f"\n{fname}: expected verdict={expect['verdict']!r}, "
        f"got {result['verdict']!r}\n{detail}"
    )
    assert result["score"] == expect["score"], (
        f"\n{fname}: expected score={expect['score']}, "
        f"got {result['score']}\n{detail}"
    )
