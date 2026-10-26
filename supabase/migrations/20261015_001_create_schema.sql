-- ===========================================================================
-- Otterlook AI — Supabase Schema Migration
-- Created: 2026-10-15
-- Description: Core tables for storing analysis results, user feedback,
--              and training samples. RLS enabled on all tables with no
--              public policies — backend accesses via service_role key.
-- ===========================================================================

-- Enable the pgcrypto extension for gen_random_uuid() if not already enabled
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ---------------------------------------------------------------------------
-- 1. analyses — stores every undertone analysis result
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS analyses (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at      timestamptz NOT NULL    DEFAULT now(),
    features        jsonb       NOT NULL,
    predicted_undertone text    NOT NULL,
    confidence      real,
    quality_score   int
);

COMMENT ON TABLE analyses IS 'Stores each undertone analysis result with extracted features and ML prediction.';
COMMENT ON COLUMN analyses.features IS 'JSONB of the 22 colorimetric ML features (mean_r, mean_g, ..., rb_ratio).';
COMMENT ON COLUMN analyses.predicted_undertone IS 'ML predicted label: Warm, Cool, or Neutral.';
COMMENT ON COLUMN analyses.confidence IS 'Model confidence score from predict_proba (0.0–1.0).';
COMMENT ON COLUMN analyses.quality_score IS 'Image quality assessment score (0–100).';

-- ---------------------------------------------------------------------------
-- 2. feedback — user corrections on analysis predictions
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS feedback (
    id                  uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id         uuid        NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    corrected_undertone text        NOT NULL,
    created_at          timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE feedback IS 'User-submitted corrections to undertone predictions for active learning.';
COMMENT ON COLUMN feedback.corrected_undertone IS 'User-corrected label: Warm, Cool, or Neutral.';

-- Index for looking up feedback by analysis
CREATE INDEX IF NOT EXISTS idx_feedback_analysis_id ON feedback(analysis_id);

-- ---------------------------------------------------------------------------
-- 3. training_samples — labeled feature rows for model retraining
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS training_samples (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    source          text,
    created_at      timestamptz NOT NULL DEFAULT now(),
    -- Feature columns matching data/training.csv schema
    mean_r          real,
    mean_g          real,
    mean_b          real,
    median_r        real,
    median_g        real,
    median_b        real,
    std_r           real,
    std_g           real,
    std_b           real,
    mean_h          real,
    mean_s          real,
    mean_v          real,
    mean_l          real,
    mean_a          real,
    mean_lab_b      real,
    std_l           real,
    std_a           real,
    std_lab_b       real,
    ita             real,
    b_to_a_ratio    real,
    rg_ratio        real,
    rb_ratio        real,
    undertone       text
);

COMMENT ON TABLE training_samples IS 'Labeled feature vectors for model retraining. Source indicates origin (kaggle, user_feedback, synthetic).';
COMMENT ON COLUMN training_samples.source IS 'Data provenance: kaggle, user_feedback, synthetic, etc.';

-- Index for filtering by source
CREATE INDEX IF NOT EXISTS idx_training_samples_source ON training_samples(source);

-- ---------------------------------------------------------------------------
-- 4. Enable Row Level Security on all tables
--    No public policies — backend uses the service_role key to bypass RLS.
-- ---------------------------------------------------------------------------
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE training_samples ENABLE ROW LEVEL SECURITY;
