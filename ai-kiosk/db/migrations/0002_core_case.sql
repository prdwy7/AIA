-- 0002_core_case.sql
-- Case graph (Case-to-Solution Tree), media, decisions, decision deltas,
-- evidence ledger. Docs: docs/03-data-model.md §1–§3, §8.
--
-- Invariants:
--   * All IDs are ULIDs (26-char Crockford base32); all timestamps UTC.
--   * case_nodes is APPEND-ONLY: no UPDATE except status transitions
--     (active -> superseded | rejected), no DELETE. Enforced by trigger.
--   * Nothing is ever overwritten — corrections append new nodes.

-- ---------------------------------------------------------------------------
-- cases (case headers)
-- ---------------------------------------------------------------------------
CREATE TABLE cases (
    case_id                CHAR(26) PRIMARY KEY,
    short_code             TEXT NOT NULL UNIQUE,              -- e.g. "BNV-4F7K2"
    qr_payload             TEXT NOT NULL,
    channel                TEXT NOT NULL
        CHECK (channel IN ('kiosk', 'whatsapp', 'web', 'operator')),
    channel_ref            TEXT,                              -- e.g. WhatsApp thread ID
    farmer_ref             TEXT,                              -- pseudonymous; NULL until opt-in
    consent_ref            TEXT,
    kiosk_id               CHAR(26),
    location_state         TEXT,
    location_district      TEXT,
    location_mandal        TEXT,
    location_village       TEXT,
    location_lat           DOUBLE PRECISION,
    location_lon           DOUBLE PRECISION,
    location_accuracy_m    DOUBLE PRECISION,
    language               TEXT NOT NULL CHECK (language IN ('te', 'en', 'te-en')),
    crop                   TEXT,
    variety                TEXT,
    stage                  TEXT,
    severity               TEXT,
    media_refs             TEXT[] NOT NULL DEFAULT '{}',
    weather_snapshot_id    CHAR(26),
    soil_snapshot_id       CHAR(26),
    previous_interventions JSONB NOT NULL DEFAULT '[]',
    version_tuple          JSONB NOT NULL,
        -- {model, knowledge, rules, prompt_policy, speech, schema}
    status                 TEXT NOT NULL DEFAULT 'open',
    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at              TIMESTAMPTZ,
    close_reason           TEXT
);

CREATE INDEX cases_farmer_ref_idx  ON cases (farmer_ref);
CREATE INDEX cases_status_idx      ON cases (status);
CREATE INDEX cases_created_at_idx  ON cases (created_at DESC);

-- ---------------------------------------------------------------------------
-- case_nodes (append-only Case-to-Solution Tree)
-- ---------------------------------------------------------------------------
CREATE TABLE case_nodes (
    node_id          CHAR(26) PRIMARY KEY,
    case_id          CHAR(26) NOT NULL REFERENCES cases (case_id),
    parent_node_id   CHAR(26) REFERENCES case_nodes (node_id),
    node_type        TEXT NOT NULL CHECK (node_type IN (
        'input', 'interpretation', 'correction', 'observation', 'hypothesis',
        'question', 'answer', 'evidence', 'contradiction', 'decision',
        'intervention', 'outcome', 'escalation', 'scientist_feedback',
        'similar_case_ref'
    )),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by       TEXT NOT NULL,        -- farmer | system | scientist:<id> | operator
    source_channel   TEXT NOT NULL,
    source_modality  TEXT NOT NULL CHECK (source_modality IN
        ('voice', 'touch', 'text', 'picture', 'system')),
    confidence       DOUBLE PRECISION
        CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),
    status           TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'superseded', 'rejected')),
    evidence_refs    TEXT[] NOT NULL DEFAULT '{}',
    payload          JSONB NOT NULL        -- typed per node_type (canonical-schema)
);

CREATE INDEX case_nodes_case_type_idx    ON case_nodes (case_id, node_type);
CREATE INDEX case_nodes_case_created_idx ON case_nodes (case_id, created_at);
CREATE INDEX case_nodes_payload_gin_idx  ON case_nodes USING GIN (payload jsonb_path_ops);

-- Append-only enforcement: reject UPDATE/DELETE except status transitions.
CREATE OR REPLACE FUNCTION case_nodes_append_only() RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'case_nodes is append-only: DELETE rejected (node %)', OLD.node_id;
    END IF;
    IF TG_OP = 'UPDATE' THEN
        IF NEW.node_id          IS DISTINCT FROM OLD.node_id
           OR NEW.case_id       IS DISTINCT FROM OLD.case_id
           OR NEW.parent_node_id IS DISTINCT FROM OLD.parent_node_id
           OR NEW.node_type     IS DISTINCT FROM OLD.node_type
           OR NEW.created_at    IS DISTINCT FROM OLD.created_at
           OR NEW.created_by    IS DISTINCT FROM OLD.created_by
           OR NEW.source_channel IS DISTINCT FROM OLD.source_channel
           OR NEW.source_modality IS DISTINCT FROM OLD.source_modality
           OR NEW.confidence    IS DISTINCT FROM OLD.confidence
           OR NEW.evidence_refs IS DISTINCT FROM OLD.evidence_refs
           OR NEW.payload       IS DISTINCT FROM OLD.payload
        THEN
            RAISE EXCEPTION
                'case_nodes is append-only: only status transitions allowed (node %)',
                OLD.node_id;
        END IF;
        IF OLD.status <> 'active' THEN
            RAISE EXCEPTION
                'case_nodes: status % cannot be transitioned (node %)',
                OLD.status, OLD.node_id;
        END IF;
        IF NEW.status = 'active' THEN
            RAISE EXCEPTION
                'case_nodes: status transition must move away from active (node %)',
                OLD.node_id;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER case_nodes_append_only_trg
    BEFORE UPDATE OR DELETE ON case_nodes
    FOR EACH ROW EXECUTE FUNCTION case_nodes_append_only();

-- ---------------------------------------------------------------------------
-- media (audio/image metadata + MinIO refs)
-- ---------------------------------------------------------------------------
CREATE TABLE media (
    media_id      CHAR(26) PRIMARY KEY,
    case_id       CHAR(26) NOT NULL REFERENCES cases (case_id),
    media_type    TEXT NOT NULL CHECK (media_type IN ('audio', 'image', 'video', 'document')),
    modality      TEXT NOT NULL CHECK (modality IN ('voice', 'touch', 'text', 'picture')),
    minio_key     TEXT NOT NULL,
    content_hash  TEXT,                        -- SHA-256; media dedup
    size_bytes    BIGINT,
    duration_ms   INTEGER,
    width         INTEGER,
    height        INTEGER,
    faces_blurred BOOLEAN NOT NULL DEFAULT TRUE,  -- faces blurred by default (policy)
    quality       JSONB,                       -- {usable: bool, reasons[]}
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX media_case_idx ON media (case_id);
CREATE INDEX media_type_idx ON media (media_type);

-- ---------------------------------------------------------------------------
-- decisions (denormalized from decision nodes for querying)
-- ---------------------------------------------------------------------------
CREATE TABLE decisions (
    decision_node_id    CHAR(26) PRIMARY KEY REFERENCES case_nodes (node_id),
    case_id             CHAR(26) NOT NULL REFERENCES cases (case_id),
    intent              TEXT NOT NULL CHECK (intent IN
        ('information', 'diagnosis', 'advisory', 'prescription')),
    selected_diagnosis  TEXT,
    diagnoses           JSONB NOT NULL DEFAULT '[]',
    interventions       JSONB NOT NULL DEFAULT '[]',
    warnings            JSONB NOT NULL DEFAULT '[]',
    evidence_refs       TEXT[] NOT NULL DEFAULT '{}',
    rules_evaluated     JSONB NOT NULL DEFAULT '[]',
    confidence          DOUBLE PRECISION,
    model_version       TEXT,
    knowledge_version   TEXT,
    rule_version        TEXT,
    prompt_policy_version TEXT,
    status              TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'approved', 'corrected', 'rejected', 'locked')),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX decisions_case_idx     ON decisions (case_id);
CREATE INDEX decisions_status_idx   ON decisions (status);
CREATE INDEX decisions_versions_idx ON decisions (model_version, knowledge_version, rule_version);

-- ---------------------------------------------------------------------------
-- decision_deltas (learning objects)
-- ---------------------------------------------------------------------------
CREATE TABLE decision_deltas (
    delta_id             CHAR(26) PRIMARY KEY,
    decision_node_id     CHAR(26) NOT NULL,
    case_id              CHAR(26) NOT NULL,
    scientist_id         TEXT NOT NULL,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    changed_fields       JSONB NOT NULL DEFAULT '[]',   -- [{field, old_value, new_value}]
    correction_type      TEXT NOT NULL CHECK (correction_type IN (
        'PRODUCT_SELECTION', 'DOSAGE', 'FORMULATION', 'TIMING', 'DIAGNOSIS',
        'MISSING_CONTEXT', 'OUTDATED_KNOWLEDGE', 'LOCAL_CONDITION',
        'EXPERT_PREFERENCE', 'EXPLANATION'
    )),
    reason               TEXT,
    evidence_refs        TEXT[] NOT NULL DEFAULT '{}',
    evidence_status      TEXT NOT NULL DEFAULT 'EXPERT_PREFERENCE'
        CHECK (evidence_status IN ('EVIDENCE_BACKED', 'LOCALLY_VALIDATED', 'EXPERT_PREFERENCE')),
    context_snapshot_ref TEXT NOT NULL,
    approval_status      TEXT NOT NULL DEFAULT 'pending'
        CHECK (approval_status IN ('pending', 'approved_for_learning', 'rejected')),
    learning_channel     TEXT NOT NULL DEFAULT 'none'
        CHECK (learning_channel IN ('knowledge', 'rule', 'training', 'case_memory', 'language', 'none')),
    released_version     TEXT
);

CREATE INDEX deltas_correction_type_idx ON decision_deltas (correction_type);
CREATE INDEX deltas_approval_idx        ON decision_deltas (approval_status);
CREATE INDEX deltas_channel_idx         ON decision_deltas (learning_channel);

-- ---------------------------------------------------------------------------
-- evidence_ledger (claims -> sources)
-- ---------------------------------------------------------------------------
CREATE TABLE evidence_ledger (
    evidence_id      CHAR(26) PRIMARY KEY,
    claim            TEXT NOT NULL,
    source_type      TEXT NOT NULL CHECK (source_type IN (
        'law', 'institutional', 'kvc_sa', 'weather', 'research',
        'local_validated', 'secondary'
    )),
    source_name      TEXT NOT NULL,
    source_ref       TEXT,
    source_version   TEXT,
    published_date   DATE,
    retrieved_date   DATE,
    authority_level  SMALLINT NOT NULL CHECK (authority_level BETWEEN 1 AND 7),
    effective_from   DATE,
    effective_to     DATE,
    superseded_by    CHAR(26),
    confidence       DOUBLE PRECISION
        CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),
    scope_crops      TEXT[] NOT NULL DEFAULT '{}',
    scope_regions    TEXT[] NOT NULL DEFAULT '{}',
    scope_seasons    TEXT[] NOT NULL DEFAULT '{}',
    verified_by      TEXT,
    verified_at      TIMESTAMPTZ
);

CREATE INDEX evidence_authority_idx   ON evidence_ledger (authority_level);
CREATE INDEX evidence_effective_idx   ON evidence_ledger (effective_from);
CREATE INDEX evidence_scope_gin_idx   ON evidence_ledger USING GIN (scope_crops);
