-- 0005_devices_sync.sql
-- Device fleet, sync events/manifests, users/roles, audit log.
-- Docs: docs/03-data-model.md §7, §8.

-- ---------------------------------------------------------------------------
-- devices (kiosk fleet)
-- ---------------------------------------------------------------------------
CREATE TABLE devices (
    device_id            CHAR(26) PRIMARY KEY,
    name                 TEXT NOT NULL,
    location             JSONB,
    hardware_profile     TEXT,
    cert_fingerprint     TEXT,
    status               TEXT NOT NULL DEFAULT 'offline' CHECK (status IN
        ('online', 'offline', 'degraded', 'decommissioned')),
    last_seen_at         TIMESTAMPTZ,
    active_version_tuple JSONB,
    sync_state           JSONB NOT NULL DEFAULT '{}',
        -- {last_event_seq, pending_events, last_sync_at}
    health               JSONB,
        -- latest snapshot {cpu, mem, gpu, disk, temp, printer_ok, network}
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- sync_events (append-only, edge -> central)
-- ---------------------------------------------------------------------------
CREATE TABLE sync_events (
    event_id        CHAR(26) PRIMARY KEY,
    device_id       CHAR(26) NOT NULL REFERENCES devices (device_id),
    seq             BIGINT NOT NULL,
    case_id         CHAR(26),
    event_type      TEXT NOT NULL CHECK (event_type IN
        ('input', 'interpretation', 'correction', 'decision', 'outcome',
         'escalation', 'telemetry', 'print_job')),
    payload         JSONB NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    ack_status      TEXT NOT NULL DEFAULT 'pending' CHECK (ack_status IN
        ('pending', 'acked', 'failed')),
    idempotency_key TEXT NOT NULL UNIQUE,          -- = event_id; retries safe
    UNIQUE (device_id, seq)
);

CREATE INDEX sync_events_device_seq_idx ON sync_events (device_id, seq);
CREATE INDEX sync_events_ack_idx        ON sync_events (ack_status);

-- ---------------------------------------------------------------------------
-- sync_manifests (central -> edge)
-- ---------------------------------------------------------------------------
CREATE TABLE sync_manifests (
    manifest_id   CHAR(26) PRIMARY KEY,
    device_id     CHAR(26) NOT NULL REFERENCES devices (device_id),
    issued_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    artifacts     JSONB NOT NULL DEFAULT '[]',
        -- [{class, version, sha256, signature, minio_key, size}]
    applied_state JSONB,                           -- edge reports back
    applied_at    TIMESTAMPTZ
);

CREATE INDEX manifests_device_idx ON sync_manifests (device_id, issued_at DESC);

-- ---------------------------------------------------------------------------
-- users / roles (Keycloak-synced)
-- ---------------------------------------------------------------------------
CREATE TABLE users (
    user_id      CHAR(26) PRIMARY KEY,
    keycloak_id  TEXT NOT NULL UNIQUE,
    display_name TEXT,
    email        TEXT,
    role         TEXT NOT NULL CHECK (role IN ('operator', 'scientist', 'admin', 'auditor')),
    mfa_enabled  BOOLEAN NOT NULL DEFAULT FALSE,
    active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX users_role_idx ON users (role);

-- ---------------------------------------------------------------------------
-- audit_log (append-only: who/what/when/version)
-- ---------------------------------------------------------------------------
CREATE TABLE audit_log (
    audit_id      BIGSERIAL PRIMARY KEY,
    entity_type   TEXT NOT NULL,
    entity_id     TEXT NOT NULL,
    actor         TEXT NOT NULL,
    action        TEXT NOT NULL,
    version_tuple JSONB,
    details       JSONB NOT NULL DEFAULT '{}',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX audit_entity_idx  ON audit_log (entity_type, entity_id);
CREATE INDEX audit_created_idx ON audit_log (created_at DESC);

CREATE OR REPLACE FUNCTION audit_log_append_only() RETURNS trigger AS $$
BEGIN
    IF TG_OP IN ('UPDATE', 'DELETE') THEN
        RAISE EXCEPTION 'audit_log is append-only: % rejected', TG_OP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_log_append_only_trg
    BEFORE UPDATE OR DELETE ON audit_log
    FOR EACH ROW EXECUTE FUNCTION audit_log_append_only();
