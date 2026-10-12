"""JSON predicate language for rule conditions (roadmap §6.5).

A predicate is a JSON object. Leaf predicates:

    {"field": "case.crop", "op": "eq", "value": "cotton"}

Composite predicates:

    {"all": [pred, pred, ...]}
    {"any": [pred, pred, ...]}
    {"not": pred}

Operators: eq, neq, in, not_in, lt, lte, gt, gte, is_null, contains,
and field-to-field comparisons lt_field, lte_field, gt_field, gte_field
(where `value` is the path of the other field).

Semantics:
- Missing fields evaluate to None (so `is_null` is true for unknowns).
- Comparison operators with a None operand are False (except is_null).
- `contains` works on lists (membership) and strings (substring).
- Evaluation is total and deterministic: no exceptions on bad data — an
  invalid predicate raises `PredicateError` at rule-load time, not at
  evaluation time.
"""

from __future__ import annotations

from typing import Any

LEAF_OPS = {
    "eq", "neq", "in", "not_in", "lt", "lte", "gt", "gte", "is_null", "contains",
    "lt_field", "lte_field", "gt_field", "gte_field",
}
FIELD_CMP_OPS = {"lt_field", "lte_field", "gt_field", "gte_field"}
COMPOSITE_KEYS = {"all", "any", "not"}


class PredicateError(ValueError):
    """Raised when a predicate is structurally invalid."""


def _get_field(context: dict[str, Any], path: str) -> Any:
    """Dot-path lookup; missing → None.

    Tries the literal key first — flat contexts (e.g. `RuleContext.as_flat()`)
    use dot-joined keys such as ``"regulatory.status"`` — then falls back to
    nested dict traversal for structured contexts.
    """
    if path in context:
        return context[path]
    parts = path.split(".")
    current: Any = context
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def _compare(op: str, actual: Any, value: Any, context: dict[str, Any] | None = None) -> bool:
    if op in FIELD_CMP_OPS:
        if context is None:
            raise PredicateError(f"{op} requires a context")
        other = _get_field(context, value)
        if actual is None or other is None:
            return False
        try:
            if op == "lt_field":
                return actual < other
            if op == "lte_field":
                return actual <= other
            if op == "gt_field":
                return actual > other
            return actual >= other
        except TypeError:
            return False
    if op == "eq":
        return actual == value
    if op == "neq":
        return actual != value
    if op == "in":
        if actual is None or not isinstance(value, (list, tuple, set)):
            return False
        return actual in value
    if op == "not_in":
        if actual is None or not isinstance(value, (list, tuple, set)):
            return False
        return actual not in value
    if op in {"lt", "lte", "gt", "gte"}:
        if actual is None or value is None:
            return False
        try:
            if op == "lt":
                return actual < value
            if op == "lte":
                return actual <= value
            if op == "gt":
                return actual > value
            return actual >= value
        except TypeError:
            return False
    if op == "contains":
        if actual is None:
            return False
        if isinstance(actual, (list, tuple, set)):
            return value in actual
        if isinstance(actual, str) and isinstance(value, str):
            return value in actual
        return False
    raise PredicateError(f"unknown operator: {op}")


def validate_predicate(pred: Any) -> None:
    """Structural validation — call at rule load time."""
    if not isinstance(pred, dict):
        raise PredicateError("predicate must be a JSON object")
    keys = set(pred.keys())
    if keys & COMPOSITE_KEYS:
        for key in keys & COMPOSITE_KEYS:
            if key == "not":
                validate_predicate(pred[key])
            else:
                if not isinstance(pred[key], list) or not pred[key]:
                    raise PredicateError(f"{key} requires a non-empty list of predicates")
                for sub in pred[key]:
                    validate_predicate(sub)
        if len(keys & COMPOSITE_KEYS) != 1:
            raise PredicateError("composite predicate must have exactly one of all/any/not")
        return
    if "field" not in keys or "op" not in keys:
        raise PredicateError("leaf predicate requires 'field' and 'op'")
    if pred["op"] not in LEAF_OPS:
        raise PredicateError(f"unknown operator: {pred['op']}")
    if pred["op"] != "is_null" and "value" not in keys:
        raise PredicateError(f"operator {pred['op']} requires 'value'")
    if pred["op"] in FIELD_CMP_OPS and not isinstance(pred["value"], str):
        raise PredicateError(f"operator {pred['op']} requires a field path as 'value'")


def evaluate_predicate(pred: Any, context: dict[str, Any]) -> bool:
    """Evaluate a predicate against a flat context. Deterministic."""
    if not isinstance(pred, dict):
        raise PredicateError("predicate must be a JSON object")
    keys = set(pred.keys())
    if keys & COMPOSITE_KEYS:
        key = next(iter(keys & COMPOSITE_KEYS))
        if key == "all":
            return all(evaluate_predicate(sub, context) for sub in pred[key])
        if key == "any":
            return any(evaluate_predicate(sub, context) for sub in pred[key])
        return not evaluate_predicate(pred[key], context)
    field = pred["field"]
    op = pred["op"]
    actual = _get_field(context, field)
    if op == "is_null":
        return actual is None
    return _compare(op, actual, pred.get("value"), context)
