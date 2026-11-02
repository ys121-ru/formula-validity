"""
src/plugin/formula_checker.py

Check whether a string is a legal propositional logic formula under the
strict fully-parenthesized grammar:

    formula ::= var
              | ( ¬ formula )
              | ( formula ∨ formula )
              | ( formula ∧ formula )
              | ( formula → formula )
              | ( formula ↔ formula )

    var     ::= [A-Za-z][A-Za-z0-9_]*

Every compound formula must be wrapped in its own parentheses.
  Legal  : A   (A∧B)   ((A∨B)→C)   (¬(A∧B))
  Illegal: A∧B   (A∧B)∨C   A→(B∧C)

Whitespace is stripped before checking, so "( A ∧ B )" is treated the
same as "(A∧B)".
"""

from __future__ import annotations

import re

_OPERATORS = frozenset({'¬', '∨', '∧', '→', '↔'})


def is_valid_formula(s: str) -> bool:
    """
    Return True iff *s* is a legal formula in the strict grammar above.
    """
    s = ''.join(s.split())   # strip all whitespace

    if not s:
        return False

    # ── Atomic: a variable name ───────────────────────────────────────────
    if re.match(r'^[A-Za-z][A-Za-z0-9_]*$', s):
        return True

    # ── Compound: must be wrapped in a matching pair of parentheses ───────
    if s[0] != '(' or s[-1] != ')':
        return False

    inner = s[1:-1]

    # Walk inner tracking bracket depth to find the main connective.
    # The main connective is the last operator found at depth 0.
    depth       = 0
    main_op     = None
    main_op_pos = None

    for i, ch in enumerate(inner):
        if depth < 0:
            return False
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        elif depth == 0 and ch in _OPERATORS:
            main_op     = ch
            main_op_pos = i

    if depth != 0:      # unbalanced parentheses
        return False
    if main_op is None: # no connective found, e.g. "(A)" or "()"
        return False

    # ── Negation: ( ¬ F ) ────────────────────────────────────────────────
    if main_op == '¬':
        if main_op_pos != 0:   # something before ¬ — illegal
            return False
        sub = inner[1:]
        return bool(sub) and is_valid_formula(sub)

    # ── Binary connective: ( F op G ) ────────────────────────────────────
    left  = inner[:main_op_pos]
    right = inner[main_op_pos + 1:]
    return (
        bool(left) and bool(right)
        and is_valid_formula(left)
        and is_valid_formula(right)
    )
