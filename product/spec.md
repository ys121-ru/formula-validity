# Formula Validity — Product Spec

## What it does

The agent is shown an expression and answers **yes** (legal formula) or **no** (not legal).

The grammar is the strict fully-parenthesized grammar taught in formal logic courses:
every compound formula must be wrapped in its own pair of parentheses.

## Who it is for

Students in a logic or discrete mathematics course learning the formal syntax of
propositional logic. The task tests whether they can correctly identify whether
a given expression is well-formed.

## Inputs

| Field | Description |
|---|---|
| `expression` | An arbitrary string that may or may not be a legal formula |

## Output

| Field | Description |
|---|---|
| `answer` | `"yes"` or `"no"` |

## Grading

The agent's answer is checked against `is_valid_formula(expression)`.
Score is **1.0** for a correct answer and **0.0** otherwise. No partial credit.

## Non-goals

- This plugin does not evaluate the truth value of a formula.
- It does not accept flexible syntax (operator precedence, no-parens style).
- It does not parse LaTeX or natural language descriptions.
