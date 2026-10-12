"""agri-rules — deterministic agricultural rules engine.

The LLM is a language/reasoning assistant, never the authority (roadmap §1.2).
Regulatory/dose/PHI/weather rules are deterministic and the LLM cannot
override them (defense layer 4, roadmap §14.5).

- `engine.evaluate(rules, context)` → `EvaluationReport`
- `predicates` — JSON predicate language (eq/neq/in/not_in/lt/lte/gt/gte/
  is_null/contains + field-to-field comparisons)
- `regulatory` — PPQS/CIB&RC mapping (banned→BLOCK, refused→BLOCK,
  restricted→REVIEW/CONDITION)
- `inventory` — blocking-rules inventory (100% coverage required)
- `standard_rules` — WS-RULES v1 starter bundle
"""

from .context import (
    CaseContext,
    DecisionContext,
    RegulatoryContext,
    RuleContext,
    WeatherContext,
)
from .engine import evaluate
from .inventory import BLOCKING_INVENTORY, inventory_complete, verify_inventory
from .predicates import PredicateError, evaluate_predicate, validate_predicate
from .regulatory import regulatory_action, regulatory_block_reason
from .result import EvaluationReport, RuleResult
from .standard_rules import THETA_AUTO, THETA_CONFIRM, standard_rules

__version__ = "1.0.0"

__all__ = [
    "__version__",
    "BLOCKING_INVENTORY",
    "CaseContext",
    "DecisionContext",
    "EvaluationReport",
    "PredicateError",
    "RegulatoryContext",
    "RuleContext",
    "RuleResult",
    "THETA_AUTO",
    "THETA_CONFIRM",
    "WeatherContext",
    "evaluate",
    "evaluate_predicate",
    "inventory_complete",
    "regulatory_action",
    "regulatory_block_reason",
    "standard_rules",
    "validate_predicate",
    "verify_inventory",
]
