"""Rule evaluation results (roadmap §6.5).

Result classes: ALLOWED / BLOCKED / REVIEW / CONDITION / WARN /
REQUIRE_CONFIRMATION. BLOCKED is absolute — a blocked decision can never
reach printable state (enforced by the advisory/prescription services and
property-tested in `tests/test_invariants.py`).
"""

from __future__ import annotations

from canonical_schema.enums import RuleAction
from canonical_schema.enums import RuleResult as RuleResultEnum
from pydantic import BaseModel, ConfigDict, Field


class RuleResult(BaseModel):
    """Per-rule evaluation outcome (recorded on the decision node)."""

    model_config = ConfigDict(frozen=True)

    rule_id: str
    rule_class: str
    result: RuleResultEnum
    action: RuleAction | None = Field(
        default=None, description="The rule's action when its condition matched"
    )
    details: str | None = None


class EvaluationReport(BaseModel):
    """Aggregate report for a decision draft (roadmap §7 /v1/rules/evaluate)."""

    model_config = ConfigDict(frozen=True)

    results: list[RuleResult] = Field(default_factory=list)
    blocked: bool = False
    requires_review: bool = False
    requires_confirmation: bool = False
    warnings: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)

    @property
    def printable(self) -> bool:
        """A decision is printable only if not blocked and no unresolved
        review/confirmation is required."""
        return not (self.blocked or self.requires_review or self.requires_confirmation)

    def blocking_rule_ids(self) -> list[str]:
        return [r.rule_id for r in self.results if r.result == RuleResultEnum.BLOCK]
