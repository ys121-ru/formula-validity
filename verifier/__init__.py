"""The deterministic verifier: checks the agent's submitted answer against the formula-validity rules."""

from contract import Task, Tool

from . import task as _task

# tool → its verifier module
TOOLS = {
    Tool.SUBMIT: _task,
}

# task → its verify_task function
TASKS = {
    Task.FORMULA_VALIDITY: _task.verify_task,
}


def verify_input(tool: str, value) -> list[dict]:
    return TOOLS[Tool(tool)].verify_input(value)


def verify_output(tool: str, input_value, output_value, workspace: str) -> dict:
    return TOOLS[Tool(tool)].verify_output(input_value, output_value, workspace)


def verify_task(task: str, arguments, output, reference, workspace: str) -> dict:
    return TASKS[Task(task)](arguments, output, reference, workspace)
