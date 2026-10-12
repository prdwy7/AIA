# agri-rules

Deterministic agricultural rules engine — regulatory (PPQS/CIB&RC), dose,
PHI/PPE, weather-window and confidence gates.

**Purpose:** the LLM is a language/reasoning assistant, never the authority
(roadmap §1.2). This engine is defense layer 4 (roadmap §14.5):
regulatory/dose/PHI/weather rules are deterministic and **the LLM cannot
override them**. A blocked intervention can never reach printable state.

**Responsibilities:**
- `engine.evaluate(rules, context) → EvaluationReport` — pure, deterministic
- `predicates` — JSON predicate language: `eq/neq/in/not_in/lt/lte/gt/gte/
  is_null/contains` + field-to-field `lt_field/lte_field/gt_field/gte_field`,
  composites `all/any/not`
- `regulatory` — PPQS mapping: banned→BLOCK, refused→BLOCK,
  restricted→REVIEW/CONDITION (PPQS effective 31 Mar 2024 + gazette updates)
- `inventory` — blocking-rules inventory; 100% coverage is a release gate
- `standard_rules` — WS-RULES v1 starter bundle (blocking inventory complete)

**Tech:** Python 3.12, Pydantic v2, `canonical-schema` (Rule models). No I/O.

**Interfaces:** consumed by `rules-service` (`POST /v1/rules/evaluate`),
`advisory-service` (gate orchestration), and the CI rule suite (every rule
ships `test_cases[]`; property test: no blocked intervention reaches
printable state).

**Dependencies:** `canonical-schema`.

**Scaling:** stateless library; versioned in the version registry (`rules`
artifact class). Released per regulatory update + quarterly audit (risk R07).

**Built-in phase:** Phase 1 (WS-RULES start: regulatory data parsing first).

**Key invariants:**
- Deterministic: same rules + context → same report, always.
- BLOCK is absolute: `EvaluationReport.printable` is False when blocked,
  requires review, or requires confirmation.
- Missing data fails safe: rule evaluation errors → REVIEW, never silent pass.
- STALE weather → spray window UNKNOWN (never guess a window).
- Confidence gates: θ_confirm = 0.80, θ_auto = 0.85.

**Spec:** [docs/02-modules.md](../../docs/02-modules.md) (S9 rules-service),
roadmap §6.5, §13.2, §14.5.
