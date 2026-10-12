"""Deterministic rules engine (roadmap §6.5).

`evaluate(rules, context)` runs every active rule whose condition matches the
context and aggregates the results. The engine is pure: same rules + same
context → same report, always. The LLM cannot override these results —
downstream services treat `blocked=True` as absolute.
"""

from __future__ import annotations

from datetime import date

from canonical_schema.enums import RuleAction
from canonical_schema.enums import RuleResult as RuleResultEnum
from canonical_schema.rules import Rule

from .context import RuleContext
from .predicates import evaluate_predicate, validate_predicate
from .result import EvaluationReport, RuleResult

_ACTION_TO_RESULT: dict[RuleAction, RuleResultEnum] = {
    RuleAction.BLOCK: RuleResultEnum.BLOCK,
    RuleAction.REVIEW: RuleResultEnum.REVIEW,
    RuleAction.CONDITION: RuleResultEnum.CONDITION,
    RuleAction.WARN: RuleResultEnum.WARN,
    RuleAction.REQUIRE_CONFIRMATION: RuleResultEnum.REQUIRE_CONFIRMATION,
    RuleAction.ALLOWED: RuleResultEnum.PASS,
}


def _is_active(rule: Rule, today: date) -> bool:
    if rule.status != "active":
        return False
    if rule.effective_from is not None and today < rule.effective_from:
        return False
    if rule.effective_to is not None and today > rule.effective_to:
        return False
    return True


def _in_scope(rule: Rule, context: RuleContext) -> bool:
    """Scope filtering: empty scope list = applies to all."""
    scope = rule.scope
    if scope.crops and context.case.crop is not None and context.case.crop not in scope.crops:
        return False
    if (
        scope.regions
        and context.case.region is not None
        and context.case.region not in scope.regions
    ):
        return False
    if (
        scope.products
        and context.decision.product_id is not None
        and context.decision.product_id not in scope.products
    ):
        return False
    return True


def evaluate(
    rules: list[Rule], context: RuleContext, today: date | None = None
) -> EvaluationReport:
    """Evaluate all rules against the context.

    Every active, in-scope rule is recorded in the report (pass or action) so
    the decision node's `rules_evaluated[]` is a complete audit trail.
    """
    today = today or date.today()
    flat = context.as_flat()
    results: list[RuleResult] = []
    warnings: list[str] = []
    conditions: list[str] = []

    for rule in rules:
        if not _is_active(rule, today):
            continue
        if not _in_scope(rule, context):
            continue
        try:
            validate_predicate(rule.condition)
            matched = evaluate_predicate(rule.condition, flat)
        except Exception as e:  # noqa: BLE001 — engine must not crash on bad rules
            results.append(
                RuleResult(
                    rule_id=rule.rule_id,
                    rule_class=rule.rule_class.value,
                    result=RuleResultEnum.REVIEW,
                    details=f"rule evaluation error (fail-safe REVIEW): {e}",
                )
            )
            continue
        if not matched:
            results.append(
                RuleResult(
                    rule_id=rule.rule_id,
                    rule_class=rule.rule_class.value,
                    result=RuleResultEnum.PASS,
                )
            )
            continue
        result = _ACTION_TO_RESULT[rule.action]
        results.append(
            RuleResult(
                rule_id=rule.rule_id,
                rule_class=rule.rule_class.value,
                result=result,
                action=rule.action,
                details=rule.description,
            )
        )
        if result == RuleResultEnum.WARN:
            warnings.append(rule.name.en or rule.name.te)
        elif result == RuleResultEnum.CONDITION:
            conditions.append(rule.name.en or rule.name.te)

    return EvaluationReport(
        results=results,
        blocked=any(r.result == RuleResultEnum.BLOCK for r in results),
        requires_review=any(r.result == RuleResultEnum.REVIEW for r in results),
        requires_confirmation=any(r.result == RuleResultEnum.REQUIRE_CONFIRMATION for r in results),
        warnings=warnings,
        conditions=conditions,
    )
