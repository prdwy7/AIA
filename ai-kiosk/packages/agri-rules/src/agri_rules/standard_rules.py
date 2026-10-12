"""Standard rule bundle (WS-RULES v1 starter set).

These rules implement the Phase 0 safety policy minimums. They are
deterministic, versioned, and each ships `test_cases[]`. The full KVK rule
set (per-crop, per-product) is curated by scientists and released through
the governed release pipeline.
"""

from __future__ import annotations

from datetime import date

from canonical_schema.common import BilingualText
from canonical_schema.enums import RuleAction, RuleClass
from canonical_schema.rules import Rule, RuleTestCase

_RULE_VERSION = "1.0.0"
_EFFECTIVE = date(2024, 3, 31)  # PPQS effective date

#: Confidence gates (roadmap §4.2): θ_confirm = 0.80, θ_auto = 0.85.
THETA_CONFIRM = 0.80
THETA_AUTO = 0.85


def standard_rules() -> list[Rule]:
    """The starter deterministic rule bundle (blocking inventory complete)."""
    return [
        # --- Regulatory (PPQS/CIB&RC) -------------------------------------
        Rule(
            rule_version=_RULE_VERSION,
            rule_class=RuleClass.REGULATORY,
            name=BilingualText(te="నిషేధించిన ఉత్పత్తి", en="Banned product (PPQS)"),
            description="Products on the PPQS banned list must never be recommended.",
            condition={"field": "regulatory.status", "op": "eq", "value": "banned"},
            action=RuleAction.BLOCK,
            test_cases=[
                RuleTestCase(
                    input_context={"regulatory": {"status": "banned"}},
                    expected_action=RuleAction.BLOCK,
                ),
                RuleTestCase(
                    input_context={"regulatory": {"status": "permitted"}},
                    expected_action=RuleAction.ALLOWED,
                ),
            ],
            status="active",
            effective_from=_EFFECTIVE,
        ),
        Rule(
            rule_version=_RULE_VERSION,
            rule_class=RuleClass.REGULATORY,
            name=BilingualText(te="నమోదు తిరస్కరించిన ఉత్పత్తి", en="Registration-refused product"),
            description="Products with refused registration must never be recommended.",
            condition={"field": "regulatory.status", "op": "eq", "value": "refused"},
            action=RuleAction.BLOCK,
            test_cases=[
                RuleTestCase(
                    input_context={"regulatory": {"status": "refused"}},
                    expected_action=RuleAction.BLOCK,
                ),
            ],
            status="active",
            effective_from=_EFFECTIVE,
        ),
        Rule(
            rule_version=_RULE_VERSION,
            rule_class=RuleClass.REGULATORY,
            name=BilingualText(te="పరిమిత ఉత్పత్తి", en="Restricted product"),
            description=(
                "Restricted products require scientist review (CONDITION when the "
                "restriction matches the crop — see regulatory.restricted_action)."
            ),
            condition={"field": "regulatory.status", "op": "eq", "value": "restricted"},
            action=RuleAction.REVIEW,
            test_cases=[
                RuleTestCase(
                    input_context={"regulatory": {"status": "restricted"}},
                    expected_action=RuleAction.REVIEW,
                ),
            ],
            status="active",
            effective_from=_EFFECTIVE,
        ),
        # --- Dose (critical numeric — validated independently of the LLM) --
        Rule(
            rule_version=_RULE_VERSION,
            rule_class=RuleClass.DOSE,
            name=BilingualText(te="మోతాదు పరిధి", en="Dose within approved range"),
            description="Dose must lie within [dose_min, dose_max]; out-of-range is blocked.",
            condition={
                "any": [
                    {
                        "all": [
                            {"not": {"field": "decision.dose_value", "op": "is_null"}},
                            {"not": {"field": "decision.dose_min", "op": "is_null"}},
                            {
                                "field": "decision.dose_value",
                                "op": "lt_field",
                                "value": "decision.dose_min",
                            },
                        ]
                    },
                    {
                        "all": [
                            {"not": {"field": "decision.dose_value", "op": "is_null"}},
                            {"not": {"field": "decision.dose_max", "op": "is_null"}},
                            {
                                "field": "decision.dose_value",
                                "op": "gt_field",
                                "value": "decision.dose_max",
                            },
                        ]
                    },
                ]
            },
            action=RuleAction.BLOCK,
            test_cases=[
                RuleTestCase(
                    input_context={
                        "decision": {"dose_value": 100, "dose_min": 200, "dose_max": 500}
                    },
                    expected_action=RuleAction.BLOCK,
                ),
                RuleTestCase(
                    input_context={
                        "decision": {"dose_value": 600, "dose_min": 200, "dose_max": 500}
                    },
                    expected_action=RuleAction.BLOCK,
                ),
                RuleTestCase(
                    input_context={
                        "decision": {"dose_value": 300, "dose_min": 200, "dose_max": 500}
                    },
                    expected_action=RuleAction.ALLOWED,
                ),
            ],
            status="active",
        ),
        # --- PHI / PPE ------------------------------------------------------
        Rule(
            rule_version=_RULE_VERSION,
            rule_class=RuleClass.PHI_PPE,
            name=BilingualText(te="PHI ఉల్లంఘన", en="PHI violation"),
            description="Spraying within the pre-harvest interval of the next harvest is blocked.",
            condition={
                "all": [
                    {"not": {"field": "decision.phi_days", "op": "is_null"}},
                    {"not": {"field": "decision.days_to_harvest", "op": "is_null"}},
                    {
                        "field": "decision.days_to_harvest",
                        "op": "lt_field",
                        "value": "decision.phi_days",
                    },
                ]
            },
            action=RuleAction.BLOCK,
            test_cases=[
                RuleTestCase(
                    input_context={
                        "decision": {"phi_days": 21, "days_to_harvest": 10}
                    },
                    expected_action=RuleAction.BLOCK,
                ),
                RuleTestCase(
                    input_context={
                        "decision": {"phi_days": 21, "days_to_harvest": 30}
                    },
                    expected_action=RuleAction.ALLOWED,
                ),
            ],
            status="active",
        ),
        # --- Weather window --------------------------------------------------
        Rule(
            rule_version=_RULE_VERSION,
            rule_class=RuleClass.WEATHER_WINDOW,
            name=BilingualText(te="వాతావరణం పాతది", en="Stale weather — spray window unknown"),
            description=(
                "STALE weather → spray window UNKNOWN; the system must not assert a "
                "window (confirmation required)."
            ),
            condition={"field": "weather.status", "op": "eq", "value": "STALE"},
            action=RuleAction.REQUIRE_CONFIRMATION,
            test_cases=[
                RuleTestCase(
                    input_context={"weather": {"status": "STALE"}},
                    expected_action=RuleAction.REQUIRE_CONFIRMATION,
                ),
            ],
            status="active",
        ),
        Rule(
            rule_version=_RULE_VERSION,
            rule_class=RuleClass.WEATHER_WINDOW,
            name=BilingualText(te="వర్షంలో పిచికారీ", en="Spraying in heavy rain"),
            description="Spraying when rainfall exceeds 5 mm is unsafe and blocked.",
            condition={
                "all": [
                    {"not": {"field": "weather.rainfall_mm", "op": "is_null"}},
                    {"field": "weather.rainfall_mm", "op": "gt", "value": 5},
                ]
            },
            action=RuleAction.BLOCK,
            test_cases=[
                RuleTestCase(
                    input_context={"weather": {"rainfall_mm": 8.0}},
                    expected_action=RuleAction.BLOCK,
                ),
                RuleTestCase(
                    input_context={"weather": {"rainfall_mm": 1.0}},
                    expected_action=RuleAction.ALLOWED,
                ),
            ],
            status="active",
        ),
        Rule(
            rule_version=_RULE_VERSION,
            rule_class=RuleClass.WEATHER_WINDOW,
            name=BilingualText(te="బలమైన గాలిలో పిచికారీ", en="Spraying in high wind"),
            description="Spraying when wind exceeds 30 km/h (drift risk) is blocked.",
            condition={
                "all": [
                    {"not": {"field": "weather.wind_speed_kmh", "op": "is_null"}},
                    {"field": "weather.wind_speed_kmh", "op": "gt", "value": 30},
                ]
            },
            action=RuleAction.BLOCK,
            test_cases=[
                RuleTestCase(
                    input_context={"weather": {"wind_speed_kmh": 35.0}},
                    expected_action=RuleAction.BLOCK,
                ),
            ],
            status="active",
        ),
        # --- Confidence gate --------------------------------------------------
        Rule(
            rule_version=_RULE_VERSION,
            rule_class=RuleClass.CONFIDENCE_GATE,
            name=BilingualText(te="నిశ్చయత తక్కువ", en="Low decision confidence"),
            description=(
                f"Decision confidence below θ_confirm ({THETA_CONFIRM}) requires "
                "farmer confirmation."
            ),
            condition={
                "all": [
                    {"not": {"field": "decision.confidence", "op": "is_null"}},
                    {"field": "decision.confidence", "op": "lt", "value": THETA_CONFIRM},
                ]
            },
            action=RuleAction.REQUIRE_CONFIRMATION,
            test_cases=[
                RuleTestCase(
                    input_context={"decision": {"confidence": 0.65}},
                    expected_action=RuleAction.REQUIRE_CONFIRMATION,
                ),
                RuleTestCase(
                    input_context={"decision": {"confidence": 0.9}},
                    expected_action=RuleAction.ALLOWED,
                ),
            ],
            status="active",
        ),
    ]
