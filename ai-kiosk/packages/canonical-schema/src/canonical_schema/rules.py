"""Rules and regulatory product data (roadmap §6.5).

Rules are deterministic: the LLM cannot override them. The machine-readable
engine lives in `packages/agri-rules/`.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from .common import BilingualText, new_ulid
from .enums import RegulatoryStatus, RuleAction, RuleClass


class RuleScope(BaseModel):
    model_config = ConfigDict(frozen=True)

    crops: list[str] = Field(default_factory=list)
    regions: list[str] = Field(default_factory=list)
    products: list[str] = Field(default_factory=list)


class RuleTestCase(BaseModel):
    """Each rule ships test cases; CI runs the full rule suite (roadmap §6.5,
    §13.2). 100% of blocking rules must be covered."""

    model_config = ConfigDict(frozen=True)

    input_context: dict = Field(description="Case/decision/weather context to evaluate")
    expected_action: RuleAction


class Rule(BaseModel):
    """Deterministic rule (roadmap §6.5)."""

    model_config = ConfigDict(frozen=True)

    rule_id: str = Field(default_factory=new_ulid, min_length=26, max_length=26)
    rule_version: str
    rule_class: RuleClass
    name: BilingualText
    description: str | None = None

    condition: dict = Field(
        description=(
            "JSON deterministic predicate over case/decision/weather context "
            "(agri-rules predicate language: eq/neq/in/not_in/lt/lte/gt/gte/"
            "is_null/contains/all/any/not)"
        )
    )
    action: RuleAction
    scope: RuleScope = Field(default_factory=RuleScope)
    authority_source: str | None = Field(default=None, description="evidence_ledger ULID")
    test_cases: list[RuleTestCase] = Field(default_factory=list)
    status: str = Field(default="active", description="active | retired")
    effective_from: date | None = None
    effective_to: date | None = None
    approved_by: str | None = None


class RegulatoryProduct(BaseModel):
    """PPQS/CIB&RC parsed product record (roadmap §6.5 regulatory_products).

    PPQS effective 31 Mar 2024 + gazette updates; re-verified before each
    release (risk R07)."""

    model_config = ConfigDict(frozen=True)

    product_id: str = Field(default_factory=new_ulid, min_length=26, max_length=26)
    active_ingredient: str
    trade_names: list[str] = Field(default_factory=list)
    status: RegulatoryStatus
    restrictions: str | None = Field(
        default=None, description="For restricted: crop/region/dose limits"
    )
    source_ref: str | None = Field(default=None, description="Gazette/evidence reference")
    effective_from: date | None = None
    effective_to: date | None = None
    verified_at: datetime | None = None
