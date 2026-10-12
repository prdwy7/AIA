-- 0004_learning_versions.sql
-- Learning candidates, version registry, prescriptions, outcomes, escalations,
-- follow-ups. Docs: docs/03-data-model.md §6, §8.

-- ---------------------------------------------------------------------------
-- learning_candidates (governed learning)
-- ---------------------------------------------------------------------------
CREATE TABLE learning_candidates (
    candidate_id      CHAR(26) PRIMARY KEY,
    channel           TEXT NOT NULL CHECK (channel IN
        ('knowledge', 'rule', 'training', 'language', 'case_memory')),
    source_refs       JSONB NOT NULL DEFAULT '[]',  -- delta/outcome/case IDs
    payload           JSONB NOT NULL,               -- proposed KB entry / rule / example / mapping
    status            TEXT NOT NULL DEFAULT 'draft' CHECK (status IN
        ('draft', 'in_validation', 'expert_review', 'approved', 'rejected', 'released')),
    validation_report JSONB,
        -- {data_quality, regression, safety, counterexample, holdout}
    provenance        JSONB NOT NULL,
        -- 11 fields: who, what_observed, when, channel, evidence, ai_original,
        -- corrected, independently_verified, outcome_support, approved_for_learning,
        -- used_in_version
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    reviewed_by       TEXT,
    decided_at        TIMESTAMPTZ
);

CREATE INDEX candidates_channel_idx ON learning_candidates (channel);
CREATE INDEX candidates_status_idx  ON learning_candidates (status);

-- ---------------------------------------------------------------------------
-- version_registry (artifact versions; content-addressed)
-- ---------------------------------------------------------------------------
CREATE TABLE version_registry (
    artifact_class    TEXT NOT NULL CHECK (artifact_class IN
        ('model', 'knowledge', 'rules', 'prompt_policy', 'speech', 'schema')),
    version           TEXT NOT NULL,               -- semver
    artifact_ref      TEXT NOT NULL,               -- MinIO key
    sha256            TEXT NOT NULL,
    signature         TEXT,
    status            TEXT NOT NULL DEFAULT 'candidate' CHECK (status IN
        ('candidate', 'shadow', 'canary', 'production', 'retired')),
    environment       TEXT NOT NULL DEFAULT 'central' CHECK (environment IN ('edge', 'central')),
    promoted_at       TIMESTAMPTZ,
    promoted_by       TEXT,
    retired_at        TIMESTAMPTZ,
    retirement_reason TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (artifact_class, version)
);

CREATE INDEX version_registry_status_idx ON version_registry (status);

-- ---------------------------------------------------------------------------
-- prescriptions (locked output)
-- ---------------------------------------------------------------------------
CREATE TABLE prescriptions (
    prescription_id  CHAR(26) PRIMARY KEY,
    decision_node_id CHAR(26) NOT NULL,
    case_id          CHAR(26) NOT NULL,
    status           TEXT NOT NULL DEFAULT 'draft' CHECK (status IN
        ('draft', 'approved', 'locked', 'printed', 'void')),
    content          JSONB NOT NULL,
        -- {diagnosis, product, formulation, dose, method, timing, phi, ppe[],
        -- warnings[], explanation {te, en}, safety_notes}
    version_tuple    JSONB NOT NULL,
    scientist_id     TEXT,
    approved_at      TIMESTAMPTZ,
    locked_at        TIMESTAMPTZ,
    print_id         TEXT UNIQUE,                  -- idempotent print
    qr_payload       TEXT NOT NULL,                -- prescription_id + verification URL
    verification     JSONB NOT NULL DEFAULT '{}',  -- {verified_at, verified_by, result}
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX prescriptions_case_idx   ON prescriptions (case_id);
CREATE INDEX prescriptions_status_idx ON prescriptions (status);

-- ---------------------------------------------------------------------------
-- outcomes (closed loop)
-- ---------------------------------------------------------------------------
CREATE TABLE outcomes (
    outcome_id          CHAR(26) PRIMARY KEY,
    case_id             CHAR(26) NOT NULL,
    intervention_id     CHAR(26) NOT NULL,
    reported_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    reported_by         TEXT NOT NULL CHECK (reported_by IN ('farmer', 'worker', 'scientist')),
    result              TEXT NOT NULL CHECK (result IN
        ('worked', 'partial', 'failed', 'worsened', 'unknown')),
    farmer_report       TEXT,
    farmer_report_media TEXT[],
    supporting_media    TEXT[] NOT NULL DEFAULT '{}',
    days_after          INTEGER,
    weather_context_ref TEXT,
    verified_by         TEXT,
    failure_class       TEXT,
    escalation_id       CHAR(26),
    learning_status     TEXT NOT NULL DEFAULT 'pending'
        CHECK (learning_status IN ('pending', 'captured', 'rejected')),
    expected_result     TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX outcomes_case_idx     ON outcomes (case_id);
CREATE INDEX outcomes_result_idx   ON outcomes (result);
CREATE INDEX outcomes_reported_idx ON outcomes (reported_at DESC);

-- ---------------------------------------------------------------------------
-- escalations (human handoff workflow)
-- ---------------------------------------------------------------------------
CREATE TABLE escalations (
    escalation_id    CHAR(26) PRIMARY KEY,
    case_id          CHAR(26) NOT NULL,
    level            TEXT NOT NULL CHECK (level IN ('L1', 'L2', 'L3', 'L4')),
    trigger_type     TEXT NOT NULL,
    trigger_evidence TEXT[] NOT NULL DEFAULT '{}',
    status           TEXT NOT NULL DEFAULT 'OPEN' CHECK (status IN
        ('OPEN', 'ASSIGNED', 'INVESTIGATING', 'RESOLVED', 'LEARNING_CAPTURED')),
    assigned_to      TEXT,
    assigned_at      TIMESTAMPTZ,
    resolved_at      TIMESTAMPTZ,
    resolution_note  TEXT,
    packet_ref       TEXT,                         -- compact case packet for scientist
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX escalations_status_idx   ON escalations (status);
CREATE INDEX escalations_level_idx    ON escalations (level);
CREATE INDEX escalations_assigned_idx ON escalations (assigned_to);

-- ---------------------------------------------------------------------------
-- followups (protocol-based outcome follow-ups)
-- ---------------------------------------------------------------------------
CREATE TABLE followups (
    followup_id     CHAR(26) PRIMARY KEY,
    case_id         CHAR(26) NOT NULL,
    intervention_id CHAR(26) NOT NULL,
    followup_due_at TIMESTAMPTZ NOT NULL,
    channel         TEXT NOT NULL CHECK (channel IN ('kiosk', 'whatsapp', 'web', 'operator')),
    status          TEXT NOT NULL DEFAULT 'scheduled' CHECK (status IN
        ('scheduled', 'sent', 'answered', 'expired', 'cancelled')),
    sent_at         TIMESTAMPTZ,
    answered_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX followups_due_idx    ON followups (followup_due_at) WHERE status = 'scheduled';
CREATE INDEX followups_status_idx ON followups (status);
