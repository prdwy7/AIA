-- 0006_weather_similarity.sql
-- Weather snapshots (IMD cache) and similar-case index.
-- Docs: docs/03-data-model.md §8.

-- ---------------------------------------------------------------------------
-- weather_snapshots (cached IMD data; 90-day retention)
-- ---------------------------------------------------------------------------
CREATE TABLE weather_snapshots (
    snapshot_id   CHAR(26) PRIMARY KEY,
    station_id    TEXT NOT NULL,
    location      JSONB NOT NULL,                  -- {state, district, mandal, lat, lon}
    snapshot_type TEXT NOT NULL CHECK (snapshot_type IN
        ('forecast', 'nowcast', 'current', 'warning', 'rainfall', 'agromet')),
    observed_at   TIMESTAMPTZ NOT NULL,
    valid_from    TIMESTAMPTZ NOT NULL,
    valid_to      TIMESTAMPTZ,
    data          JSONB NOT NULL,                  -- normalized units
    source_ref    TEXT NOT NULL,                   -- IMD endpoint + request id
    fetched_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    staleness     TEXT NOT NULL DEFAULT 'FRESH' CHECK (staleness IN ('FRESH', 'STALE')),
    UNIQUE (station_id, snapshot_type, valid_from)
);

CREATE INDEX weather_station_date_idx ON weather_snapshots (station_id, valid_from DESC);
CREATE INDEX weather_staleness_idx    ON weather_snapshots (staleness);

-- ---------------------------------------------------------------------------
-- similar_case_index (case embeddings for similarity search)
-- ---------------------------------------------------------------------------
CREATE TABLE similar_case_index (
    case_id    CHAR(26) PRIMARY KEY REFERENCES cases (case_id),
    embedding  vector(1024),                       -- case embedding (BGE-M3)
    crop       TEXT,
    stage      TEXT,
    region     TEXT,
    season     TEXT,
    outcome    TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX similar_case_hnsw_idx ON similar_case_index
    USING hnsw (embedding vector_cosine_ops);
CREATE INDEX similar_case_crop_idx ON similar_case_index (crop, stage);
