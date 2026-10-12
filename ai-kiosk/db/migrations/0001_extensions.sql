-- 0001_extensions.sql
-- AI Kiosk — central PostgreSQL extensions (docs/03-data-model.md §8).
-- Requires: PostgreSQL 17, pgvector 0.8.2 (vector), pg_trgm (contrib, built-in).

CREATE EXTENSION IF NOT EXISTS vector;   -- pgvector 0.8.2: HNSW vector similarity
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- trigram similarity for fuzzy term search
