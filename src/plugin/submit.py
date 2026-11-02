"""Tool implementation: submit a yes/no answer for a formula-validity question."""

from __future__ import annotations

from pathlib import Path

from slimconfig import build_output

from contract import SubmitInput, SubmitOutput


def submit(inp: SubmitInput, workspace: Path) -> SubmitOutput:
    """
    Grade the agent's answer against the formula-validity checker.

    Parameters
    ----------
    inp       : SubmitInput
        The agent's expression and answer, validated by slimconfig.
    workspace : Path
        The plugin's workspace folder (unused — no file I/O needed).

    Returns
    -------
    SubmitOutput
        verdict, score, and the list of constraints checked.
    """
    # Import here so the verifier's sys.path setup does not affect the module
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "verifier"))

    from task import verify
    result = verify(inp.expression, inp.answer)
    return build_output(result, SubmitOutput)
