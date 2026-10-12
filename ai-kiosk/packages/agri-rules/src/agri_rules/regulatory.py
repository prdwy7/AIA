"""PPQS/CIB&RC regulatory logic (roadmap §6.5, risk R07).

PPQS effective 31 Mar 2024 + gazette updates. Mapping:

- **banned** → BLOCK (absolute)
- **refused** (registration refused) → BLOCK (absolute)
- **restricted** → CONDITION when the restriction applies to the current
  context (e.g., crop restriction matches), otherwise REVIEW
- **permitted** → ALLOWED

Regulatory tables are versioned and re-verified before each release
(quarterly audit). The LLM never sees raw regulatory data as instructions —
only this engine consumes it.
"""

from __future__ import annotations

from canonical_schema.enums import RegulatoryStatus, RuleAction

from .context import RuleContext


def regulatory_action(context: RuleContext) -> RuleAction:
    """Determine the regulatory action for the product under evaluation."""
    status = RegulatoryStatus(context.regulatory.status)
    if status == RegulatoryStatus.BANNED:
        return RuleAction.BLOCK
    if status == RegulatoryStatus.REFUSED:
        return RuleAction.BLOCK
    if status == RegulatoryStatus.RESTRICTED:
        return _restricted_action(context)
    return RuleAction.ALLOWED


def _restricted_action(context: RuleContext) -> RuleAction:
    """Restricted products: CONDITION if the restriction applies to this
    context (crop match), otherwise REVIEW (scientist must check)."""
    restrictions = (context.regulatory.restrictions or "").strip().lower()
    if not restrictions:
        return RuleAction.REVIEW
    crop = (context.case.crop or "").lower()
    # Restriction strings list affected crops, e.g. "not for cotton; max 2 applications".
    if crop and crop in restrictions:
        return RuleAction.CONDITION
    return RuleAction.REVIEW


def regulatory_block_reason(context: RuleContext) -> str | None:
    """Human-readable block reason for audit/farmer-facing transparency."""
    status = RegulatoryStatus(context.regulatory.status)
    if status == RegulatoryStatus.BANNED:
        return "This product is banned under PPQS and must not be recommended."
    if status == RegulatoryStatus.REFUSED:
        return "Registration for this product has been refused; it must not be recommended."
    return None
