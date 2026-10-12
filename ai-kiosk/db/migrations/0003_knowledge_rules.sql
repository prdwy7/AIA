-- 0003_knowledge_rules.sql
-- Knowledge base (structured + passages), rules, regulatory products, lexicon.
-- Docs: docs/03-data-model.md §4–§5, §8.

-- ---------------------------------------------------------------------------
-- kb_entries (structured knowledge)
-- ---------------------------------------------------------------------------
CREATE TABLE kb_entries (
    entry_id          CHAR(26) PRIMARY KEY,
    kb_version        TEXT NOT NULL,
    entry_type        TEXT NOT NULL CHECK (entry_type IN (
        'pest', 'disease', 'crop_practice', 'product', 'regulation',
        'weather_rule', 'general'
    )),
    title_te          TEXT NOT NULL,
    title_en          TEXT,
    summary_te        TEXT,
    summary_en        TEXT,
    structured_fields JSONB NOT NULL DEFAULT '{}',
        -- per type: product {active_ingredient, formulation, dose_range, method,
        -- phi_days, ppe[], target_pests[], crop_restrictions[]}, ...
    scope_crops       TEXT[] NOT NULL DEFAULT '{}',
    scope_stages      TEXT[] NOT NULL DEFAULT '{}',
    scope_regions     TEXT[] NOT NULL DEFAULT '{}',
    scope_seasons     TEXT[] NOT NULL DEFAULT '{}',
    authority_level   SMALLINT NOT NULL CHECK (authority_level BETWEEN 1 AND 7),
    source_ref        TEXT,
    effective_from    DATE,
    effective_to      DATE,
    status            TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'retired')),
    superseded_by     CHAR(26),
    test_cases        JSONB NOT NULL DEFAULT '[]',
        -- [{question {te,en}, expected_answer_points[], risk_tier}]
    created_by        TEXT,
    reviewed_by       TEXT,
    reviewed_at       TIMESTAMPTZ,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX kb_entries_type_idx    ON kb_entries (entry_type);
CREATE INDEX kb_entries_version_idx ON kb_entries (kb_version);
CREATE INDEX kb_entries_scope_gin_idx ON kb_entries USING GIN (scope_crops);

-- ---------------------------------------------------------------------------
-- kb_passages (retrieval units, BGE-M3 dense + sparse)
-- ---------------------------------------------------------------------------
CREATE TABLE kb_passages (
    passage_id      CHAR(26) PRIMARY KEY,
    entry_id        CHAR(26) NOT NULL REFERENCES kb_entries (entry_id),
    kb_version      TEXT NOT NULL,
    text_te         TEXT NOT NULL,
    text_en         TEXT,
    chunk_index     INTEGER NOT NULL DEFAULT 0,
    embedding_dense vector(1024),                 -- BGE-M3
    sparse_weights  JSONB,                        -- BGE-M3 lexical weights
    metadata        JSONB NOT NULL DEFAULT '{}',
        -- {crop, stage, region, authority_level, effective_from}
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX kb_passages_entry_idx    ON kb_passages (entry_id);
CREATE INDEX kb_passages_hnsw_idx     ON kb_passages
    USING hnsw (embedding_dense vector_cosine_ops);
CREATE INDEX kb_passages_metadata_gin_idx ON kb_passages USING GIN (metadata jsonb_path_ops);

-- ---------------------------------------------------------------------------
-- rules (deterministic policy; engine: packages/agri-rules)
-- ---------------------------------------------------------------------------
CREATE TABLE rules (
    rule_id          CHAR(26) PRIMARY KEY,
    rule_version     TEXT NOT NULL,
    rule_class       TEXT NOT NULL CHECK (rule_class IN (
        'regulatory', 'crop_target', 'formulation', 'dose', 'method',
        'weather_window', 'phi_ppe', 'environment', 'confidence_gate',
        'clarification_policy'
    )),
    name_te          TEXT NOT NULL,
    name_en          TEXT,
    description      TEXT,
    condition        JSONB NOT NULL,              -- deterministic predicate (agri-rules)
    action           TEXT NOT NULL CHECK (action IN
        ('BLOCK', 'REVIEW', 'CONDITION', 'WARN', 'REQUIRE_CONFIRMATION')),
    scope_crops      TEXT[] NOT NULL DEFAULT '{}',
    scope_regions    TEXT[] NOT NULL DEFAULT '{}',
    scope_products   TEXT[] NOT NULL DEFAULT '{}',
    authority_source CHAR(26),                    -- evidence_ledger.evidence_id
    test_cases       JSONB NOT NULL DEFAULT '[]', -- [{input_context, expected_action}]
    status           TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'retired')),
    effective_from   DATE,
    effective_to     DATE,
    approved_by      TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX rules_class_idx    ON rules (rule_class);
CREATE INDEX rules_status_idx   ON rules (status);
CREATE INDEX rules_scope_gin_idx ON rules USING GIN (scope_crops);

-- ---------------------------------------------------------------------------
-- regulatory_products (PPQS / CIB&RC parsed lists)
-- ---------------------------------------------------------------------------
CREATE TABLE regulatory_products (
    product_id        CHAR(26) PRIMARY KEY,
    active_ingredient TEXT NOT NULL,
    brand_names       TEXT[] NOT NULL DEFAULT '{}',
    status            TEXT NOT NULL CHECK (status IN
        ('banned', 'refused', 'restricted', 'permitted')),
    restrictions      JSONB,                      -- crop/stage/region limits for 'restricted'
    source_ref        TEXT NOT NULL,              -- gazette / PPQS reference
    verified_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    effective_from    DATE,
    effective_to      DATE,
    status_history    JSONB NOT NULL DEFAULT '[]' -- append-only status changes
);

CREATE INDEX regulatory_ingredient_idx ON regulatory_products (active_ingredient);
CREATE INDEX regulatory_status_idx     ON regulatory_products (status);

-- ---------------------------------------------------------------------------
-- lexicon (local terminology mappings; part of SPEECH_VERSION)
-- ---------------------------------------------------------------------------
CREATE TABLE lexicon (
    lexicon_id    CHAR(26) PRIMARY KEY,
    term          TEXT NOT NULL,                  -- local/dialectal term
    normalized    TEXT NOT NULL,                  -- canonical term
    crop          TEXT,
    region        TEXT,
    category      TEXT NOT NULL DEFAULT 'general' CHECK (category IN (
        'crop', 'pest', 'disease', 'product', 'dose', 'location', 'stage', 'general'
    )),
    status        TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'retired')),
    source        TEXT,                           -- correction-derived | curated
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX lexicon_term_idx     ON lexicon (term);
CREATE INDEX lexicon_term_trgm_idx ON lexicon USING GIN (term gin_trgm_ops);
