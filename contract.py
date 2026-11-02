"""Each tool's and task's typed input and output: declarations only."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    SUBMIT = "submit"


class Task(Enum):
    FORMULA_VALIDITY = "formula-validity"


# ── Output dataclasses ─────────────────────────────────────────────────────────

@dataclass
class Constraint(Output):
    id:     Annotated[str,  "The constraint identifier"]
    ok:     Annotated[bool, "True if the constraint passed"]
    detail: Annotated[str,  "Human-readable explanation"]


@dataclass
class SubmitInput(Output):
    expression: Annotated[str, "The expression to judge — may or may not be a well-formed formula"]
    answer:     Annotated[str, 'The agent\'s answer: exactly "yes" (legal) or "no" (not legal)']


@dataclass
class SubmitOutput(Output):
    verdict:     Annotated[str,             '"pass" if the answer is correct, "fail" otherwise']
    score:       Annotated[float,           "1.0 for pass, 0.0 for fail"]
    constraints: Annotated[list[Constraint], "Each constraint checked, in order"]


# ── Registries ─────────────────────────────────────────────────────────────────

TOOLS = {
    Tool.SUBMIT: (SubmitInput, SubmitOutput),
}

TASKS = {
    Task.FORMULA_VALIDITY: (SubmitInput, SubmitOutput),
}
