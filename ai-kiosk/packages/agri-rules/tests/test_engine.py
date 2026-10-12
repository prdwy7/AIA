"""Rules engine tests (roadmap §13.2).

Covers: regulatory (PPQS) mapping, dose range, PHI, weather STALE→UNKNOWN,
confidence gates, blocking inventory, and the key property test:
**no blocked intervention can reach printable state**.
"""

from __future__ import annotations

from datetime import date

import pytest
from agri_rules import (
    CaseContext,
    DecisionContext,
    EvaluationReport,
    RegulatoryContext,
    RuleContext,
    WeatherContext,
    evaluate,
    evaluate_predicate,
    inventory_complete,
    regulatory_action,
    standard_rules,
    validate_predicate,
)
from agri_rules.predicates import PredicateError
from canonical_schema.enums import RuleAction
from pydantic import ValidationError

TODAY = date(2026, 10, 1)
RULES = standard_rules()


def _ctx(
    *,
    crop: str | None = "cotton",
    regulatory_status: str = "permitted",
    restrictions: str | None = None,
    dose_value: float | None = None,
    dose_min: float | None = None,
    dose_max: float | None = None,
    phi_days: int | None = None,
    days_to_harvest: int | None = None,
    weather_status: str = "FRESH",
    rainfall: float | None = None,
    wind: float | None = None,
    confidence: float | None = None,
) -> RuleContext:
    return RuleContext(
        case=CaseContext(crop=crop),
        decision=DecisionContext(
            dose_value=dose_value,
            dose_min=dose_min,
            dose_max=dose_max,
            phi_days=phi_days,
            days_to_harvest=days_to_harvest,
            confidence=confidence,
        ),
        weather=WeatherContext(status=weather_status, rainfall_mm=rainfall, wind_speed_kmh=wind),
        regulatory=RegulatoryContext(status=regulatory_status, restrictions=restrictions),
    )


# ---------------------------------------------------------------------------
# Regulatory (PPQS)
# ---------------------------------------------------------------------------


def test_banned_product_blocked():
    report = evaluate(RULES, _ctx(regulatory_status="banned"), today=TODAY)
    assert report.blocked
    assert not report.printable


def test_refused_product_blocked():
    report = evaluate(RULES, _ctx(regulatory_status="refused"), today=TODAY)
    assert report.blocked
    assert not report.printable


def test_restricted_product_review():
    report = evaluate(RULES, _ctx(regulatory_status="restricted"), today=TODAY)
    assert not report.blocked
    assert report.requires_review


def test_restricted_action_mapping():
    assert regulatory_action(_ctx(regulatory_status="banned")) == RuleAction.BLOCK
    assert regulatory_action(_ctx(regulatory_status="refused")) == RuleAction.BLOCK
    assert regulatory_action(_ctx(regulatory_status="restricted")) == RuleAction.REVIEW
    assert (
        regulatory_action(_ctx(regulatory_status="restricted", restrictions="not for cotton"))
        == RuleAction.CONDITION
    )
    assert regulatory_action(_ctx(regulatory_status="permitted")) == RuleAction.ALLOWED


def test_permitted_product_passes():
    report = evaluate(RULES, _ctx(), today=TODAY)
    assert not report.blocked
    assert report.printable


# ---------------------------------------------------------------------------
# Dose range (critical numeric — independent of the LLM)
# ---------------------------------------------------------------------------


def test_dose_below_min_blocked():
    report = evaluate(RULES, _ctx(dose_value=100, dose_min=200, dose_max=500), today=TODAY)
    assert report.blocked
    assert not report.printable


def test_dose_above_max_blocked():
    report = evaluate(RULES, _ctx(dose_value=600, dose_min=200, dose_max=500), today=TODAY)
    assert report.blocked


def test_dose_in_range_passes():
    report = evaluate(RULES, _ctx(dose_value=300, dose_min=200, dose_max=500), today=TODAY)
    assert not report.blocked
    assert report.printable


def test_llm_out_of_range_dose_never_passes():
    """Property (roadmap §13.2): an LLM output proposing an out-of-range dose
    is corrected/blocked by rules, never passed through."""
    for dose in (0, 1, 199, 501, 5000, 100000):
        report = evaluate(RULES, _ctx(dose_value=dose, dose_min=200, dose_max=500), today=TODAY)
        assert report.blocked, f"dose {dose} must be blocked"


# ---------------------------------------------------------------------------
# PHI
# ---------------------------------------------------------------------------


def test_phi_violation_blocked():
    report = evaluate(RULES, _ctx(phi_days=21, days_to_harvest=10), today=TODAY)
    assert report.blocked


def test_phi_respected_passes():
    report = evaluate(RULES, _ctx(phi_days=21, days_to_harvest=30), today=TODAY)
    assert not report.blocked
    assert report.printable


# ---------------------------------------------------------------------------
# Weather
# ---------------------------------------------------------------------------


def test_stale_weather_requires_confirmation():
    """STALE weather → spray window UNKNOWN → confirmation required."""
    report = evaluate(RULES, _ctx(weather_status="STALE"), today=TODAY)
    assert not report.blocked
    assert report.requires_confirmation
    assert not report.printable


def test_heavy_rain_blocked():
    report = evaluate(RULES, _ctx(rainfall=8.0), today=TODAY)
    assert report.blocked


def test_high_wind_blocked():
    report = evaluate(RULES, _ctx(wind=35.0), today=TODAY)
    assert report.blocked


def test_fresh_weather_passes():
    report = evaluate(RULES, _ctx(weather_status="FRESH", rainfall=0.0, wind=10.0), today=TODAY)
    assert report.printable


# ---------------------------------------------------------------------------
# Confidence gate
# ---------------------------------------------------------------------------


def test_low_confidence_requires_confirmation():
    report = evaluate(RULES, _ctx(confidence=0.65), today=TODAY)
    assert report.requires_confirmation


def test_high_confidence_passes():
    report = evaluate(RULES, _ctx(confidence=0.9), today=TODAY)
    assert report.printable


# ---------------------------------------------------------------------------
# Property test: blocked never reaches printable
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "ctx_kwargs",
    [
        {"regulatory_status": "banned"},
        {"regulatory_status": "refused"},
        {"dose_value": 5000, "dose_min": 200, "dose_max": 500},
        {"dose_value": 10, "dose_min": 200, "dose_max": 500},
        {"phi_days": 21, "days_to_harvest": 5},
        {"rainfall": 10.0},
        {"wind": 40.0},
        {"regulatory_status": "banned", "rainfall": 10.0, "phi_days": 30, "days_to_harvest": 10},
    ],
)
def test_blocked_never_printable(ctx_kwargs: dict):
    """Fuzz-style property: any context that triggers a BLOCK rule yields a
    report that is not printable — no combination of other factors can
    override a block (LLM cannot override)."""
    report = evaluate(RULES, _ctx(**ctx_kwargs), today=TODAY)
    assert report.blocked
    assert not report.printable
    assert report.blocking_rule_ids()


# ---------------------------------------------------------------------------
# Blocking inventory
# ---------------------------------------------------------------------------


def test_standard_bundle_has_complete_blocking_inventory():
    assert inventory_complete(RULES)


def test_inventory_detects_missing_coverage():
    from agri_rules import verify_inventory

    # Remove all dose rules → dose coverage missing.
    from canonical_schema.enums import RuleClass

    no_dose = [r for r in RULES if r.rule_class != RuleClass.DOSE]
    missing = verify_inventory(no_dose)
    assert any("dose" in m.lower() for m in missing)


# ---------------------------------------------------------------------------
# Predicate language
# ---------------------------------------------------------------------------


def test_predicate_ops():
    ctx = {"case": {"crop": "cotton"}, "decision": {"dose_value": 300, "dose_min": 200}}
    assert evaluate_predicate({"field": "case.crop", "op": "eq", "value": "cotton"}, ctx)
    assert evaluate_predicate({"field": "case.crop", "op": "neq", "value": "paddy"}, ctx)
    assert evaluate_predicate({"field": "case.crop", "op": "in", "value": ["cotton", "maize"]}, ctx)
    assert evaluate_predicate({"field": "case.crop", "op": "not_in", "value": ["paddy"]}, ctx)
    assert evaluate_predicate({"field": "decision.dose_value", "op": "lt", "value": 400}, ctx)
    assert evaluate_predicate({"field": "decision.dose_value", "op": "gt", "value": 200}, ctx)
    assert evaluate_predicate({"field": "decision.dose_value", "op": "lte", "value": 300}, ctx)
    assert evaluate_predicate({"field": "decision.dose_value", "op": "gte", "value": 300}, ctx)
    assert evaluate_predicate({"field": "case.missing", "op": "is_null"}, ctx)
    assert not evaluate_predicate({"field": "case.crop", "op": "is_null"}, ctx)
    assert evaluate_predicate({"field": "case.crop", "op": "contains", "value": "cot"}, ctx)


def test_predicate_field_to_field():
    ctx = {"decision": {"dose_value": 100, "dose_min": 200}}
    assert evaluate_predicate(
        {"field": "decision.dose_value", "op": "lt_field", "value": "decision.dose_min"}, ctx
    )
    assert not evaluate_predicate(
        {"field": "decision.dose_value", "op": "gt_field", "value": "decision.dose_min"}, ctx
    )


def test_predicate_composites():
    ctx = {"case": {"crop": "cotton"}, "weather": {"status": "FRESH"}}
    assert evaluate_predicate(
        {"all": [
            {"field": "case.crop", "op": "eq", "value": "cotton"},
            {"field": "weather.status", "op": "eq", "value": "FRESH"},
        ]},
        ctx,
    )
    assert evaluate_predicate(
        {"any": [
            {"field": "case.crop", "op": "eq", "value": "paddy"},
            {"field": "weather.status", "op": "eq", "value": "FRESH"},
        ]},
        ctx,
    )
    assert not evaluate_predicate(
        {"not": {"field": "case.crop", "op": "eq", "value": "cotton"}}, ctx
    )


def test_predicate_missing_field_is_null():
    assert evaluate_predicate({"field": "case.nonexistent", "op": "is_null"}, {})
    # Comparison with missing operand is False (fail-safe).
    assert not evaluate_predicate({"field": "case.nonexistent", "op": "eq", "value": "x"}, {})


def test_invalid_predicate_rejected():
    with pytest.raises(PredicateError):
        validate_predicate({"field": "x", "op": "bogus"})
    with pytest.raises(PredicateError):
        validate_predicate({"op": "eq"})
    with pytest.raises(PredicateError):
        validate_predicate({"all": []})
    with pytest.raises(PredicateError):
        validate_predicate("not a dict")


def test_all_standard_rule_conditions_are_valid():
    for rule in RULES:
        validate_predicate(rule.condition)  # raises if invalid


def test_rule_test_cases_pass():
    """Every rule's shipped test cases evaluate as expected (CI rule suite)."""
    for rule in RULES:
        for tc in rule.test_cases:
            ctx = RuleContext.model_validate(tc.input_context)
            report = evaluate([rule], ctx, today=TODAY)
            matched = any(
                r.rule_id == rule.rule_id and r.result.value != "pass" for r in report.results
            )
            if tc.expected_action == RuleAction.ALLOWED:
                assert not matched or report.printable, f"rule {rule.rule_id} test case failed"
            else:
                assert matched, f"rule {rule.rule_id} test case should match"
                expected_result = {
                    RuleAction.BLOCK: "block",
                    RuleAction.REVIEW: "review",
                    RuleAction.CONDITION: "condition",
                    RuleAction.WARN: "warn",
                    RuleAction.REQUIRE_CONFIRMATION: "require_confirmation",
                }[tc.expected_action]
                assert any(r.result.value == expected_result for r in report.results)


def test_report_is_frozen():
    report = evaluate(RULES, _ctx(), today=TODAY)
    assert isinstance(report, EvaluationReport)
    with pytest.raises(ValidationError):
        report.blocked = True  # type: ignore[misc]
