"""Blocking-rules inventory (roadmap §4.1 safety policy, §13.2).

The Phase 0 safety policy defines the **minimum** set of blocking rule
classes that must always be present in an active rule bundle. CI verifies
100% coverage on every release (WS-RULES gate): a missing blocking class is a
release blocker, and any rule-coverage gap at runtime surfaces as REVIEW,
never a silent pass.
"""

from __future__ import annotations

from canonical_schema.enums import RuleAction, RuleClass
from canonical_schema.rules import Rule

#: Minimum blocking coverage required in every active rule bundle.
#: (rule_class, description) — at least one active BLOCK rule per entry.
BLOCKING_INVENTORY: list[tuple[RuleClass, str]] = [
    (RuleClass.REGULATORY, "Banned products (PPQS) must be blocked"),
    (RuleClass.REGULATORY, "Registration-refused products must be blocked"),
    (RuleClass.DOSE, "Out-of-range doses must be blocked"),
    (RuleClass.PHI_PPE, "PHI violations (spray within pre-harvest interval) must be blocked"),
    (RuleClass.WEATHER_WINDOW, "Spraying in unsafe weather (heavy rain/high wind) must be blocked"),
]


def verify_inventory(rules: list[Rule]) -> list[str]:
    """Return the list of missing blocking coverage (empty = fully covered).

    A class is covered if at least one active rule of that class has action
    BLOCK.
    """
    covered: set[RuleClass] = set()
    for rule in rules:
        if rule.status == "active" and rule.action == RuleAction.BLOCK:
            covered.add(rule.rule_class)
    missing = []
    for rule_class, description in BLOCKING_INVENTORY:
        if rule_class not in covered:
            missing.append(f"{rule_class.value}: {description}")
    return missing


def inventory_complete(rules: list[Rule]) -> bool:
    return not verify_inventory(rules)
