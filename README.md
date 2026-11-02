# formula-validity

A [NanoAgent](https://github.com/RUSH-LAB/nanoagent) plugin.
Given an expression, the agent decides whether it is a legal propositional
logic formula under the strict fully-parenthesized grammar and answers
**"yes"** or **"no"**.

---

## Grammar

```
formula ::= var
          | ( ¬ formula )
          | ( formula ∨ formula )
          | ( formula ∧ formula )
          | ( formula → formula )
          | ( formula ↔ formula )

var ::= [A-Za-z][A-Za-z0-9_]*
```

Every compound formula must be wrapped in its own parentheses.

| Expression | Legal? | Reason |
|---|---|---|
| `A` | ✅ | single variable |
| `(A∧B)` | ✅ | binary connective, fully parenthesized |
| `((A∨B)→C)` | ✅ | nested, fully parenthesized |
| `(¬(A∧B))` | ✅ | negation of a compound formula |
| `A∧B` | ❌ | missing outer parentheses |
| `(A∧B)∨C` | ❌ | outer `∨` not parenthesized |
| `A→(B∧C)` | ❌ | outer `→` not parenthesized |
| `((∨A)∧B)` | ❌ | `∨` has no left operand |

---

## Install

```bash
pip install mcp slimconfig
# or, with uv (recommended by NanoAgent):
uv sync
```

---

## Run the tests

```bash
pytest tests/
```

---

## Project structure

```
formula-validity/
│
├── contract.py              # Tool/Task enums, Input/Output dataclasses, TOOLS/TASKS registries
├── pyproject.toml           # Package metadata and dependencies
├── nanoagent.yaml           # Plugin manifest — runtime, tools, task instructions
│
├── src/plugin/
│   ├── __init__.py          # Re-exports submit()
│   ├── __main__.py          # MCP stdio server — NanoAgent runs this as a subprocess
│   ├── formula_checker.py   # is_valid_formula() — the strict grammar checker
│   └── submit.py            # Tool implementation: SubmitInput → SubmitOutput
│
├── verifier/
│   └── task.py              # Two constraints → verdict JSON
│
└── tests/
    ├── cases/               # One .json file per scripted test case
    ├── conftest.py          # Path setup and case loader
    └── test_cases.py        # Parametrised pytest runner
```

---

## How it works

NanoAgent starts the plugin as a subprocess and communicates over MCP stdio:

```
NanoAgent  ──(MCP stdio)──▶  src/plugin/__main__.py
                                      │
                              builds SubmitInput
                              via contract.py
                                      │
                              calls submit.py
                                      │
                              calls verifier/task.py
                                      │
                              returns SubmitOutput
```

`contract.py` is the schema layer — it declares the typed input and output
for every tool using `slimconfig.Output` dataclasses. NanoAgent uses these
to validate what goes in and comes out of each tool call.

---

## Tool

### `submit`

Submit a yes/no answer for a formula-validity question.

**Input**

| Field | Type | Description |
|---|---|---|
| `expression` | string | The expression to judge |
| `answer` | string | `"yes"` or `"no"` |

**Output**

| Field | Type | Description |
|---|---|---|
| `verdict` | string | `"pass"` or `"fail"` |
| `score` | float | `1.0` for pass, `0.0` for fail |
| `constraints` | list | Each constraint checked, in order |

**Constraints checked (in order)**

| # | id | Checks |
|---|---|---|
| 1 | `answer-shape` | Answer is exactly `"yes"` or `"no"` |
| 2 | `validity-correct` | Answer matches `is_valid_formula(expression)` |

The first failing constraint stops evaluation.

---

## Verifier output example

```json
{
  "verdict": "pass",
  "score": 1.0,
  "constraints": [
    {"id": "answer-shape",     "ok": true, "detail": "answer shape OK: 'yes'"},
    {"id": "validity-correct", "ok": true, "detail": "answer 'yes' matches checker ('yes')"}
  ]
}
```

---

## Adding a new test case

Drop a `.json` file into `tests/cases/`:

```json
{
  "description": "((A↔B)→(¬A)) is a legal formula — agent says yes",
  "expression":   "((A↔B)→(¬A))",
  "agent_answer": "yes",
  "expect": { "verdict": "pass", "score": 1.0 }
}
```

Then run `pytest tests/` — no code changes needed.
