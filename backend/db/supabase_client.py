"""
Supabase Client Module for Otterlook AI.

Provides functions to persist analysis results, user feedback, and
export labeled training data. Gracefully degrades if Supabase env vars
are not configured — the app continues to work without persistence.

Environment Variables Required:
    SUPABASE_URL         - Project URL (e.g. https://xxxxx.supabase.co)
    SUPABASE_SERVICE_KEY - service_role key (bypasses RLS)
"""

import os
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger("otterlook.supabase")

# ---------------------------------------------------------------------------
# Lazy-initialized Supabase client singleton
# ---------------------------------------------------------------------------
_supabase_client = None
_init_attempted = False


def _get_client():
    """
    Returns the Supabase client, initializing on first call.
    Returns None if env vars are missing or connection fails.
    """
    global _supabase_client, _init_attempted

    if _init_attempted:
        return _supabase_client

    _init_attempted = True

    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_SERVICE_KEY", "").strip()

    if not url or not key:
        logger.warning(
            "SUPABASE_URL and/or SUPABASE_SERVICE_KEY not set. "
            "Supabase persistence is disabled. The app will run without "
            "database storage."
        )
        return None

    try:
        from supabase import create_client, Client
        _supabase_client = create_client(url, key)
        logger.info("Supabase client initialized successfully for %s", url)
    except ImportError:
        logger.warning(
            "supabase package not installed. Run: pip install supabase>=2.0.0"
        )
    except Exception as e:
        logger.error("Failed to initialize Supabase client: %s", e)

    return _supabase_client


def is_available() -> bool:
    """Check whether the Supabase client is configured and connected."""
    return _get_client() is not None


# ---------------------------------------------------------------------------
# save_analysis — persists analysis results
# ---------------------------------------------------------------------------
def save_analysis(
    features: Dict[str, float],
    predicted_undertone: str,
    confidence: float,
    quality_score: int
) -> Optional[str]:
    """
    Saves an analysis result to the `analyses` table.

    Args:
        features: Dict of 22 ML feature values.
        predicted_undertone: "Warm", "Cool", or "Neutral".
        confidence: Model confidence (0.0–1.0).
        quality_score: Image quality score (0–100).

    Returns:
        The UUID of the inserted row, or None if Supabase is unavailable.
    """
    client = _get_client()
    if client is None:
        logger.debug("Supabase unavailable — skipping analysis save.")
        return None

    try:
        row = {
            "features": features,
            "predicted_undertone": predicted_undertone,
            "confidence": confidence,
            "quality_score": quality_score,
        }
        result = client.table("analyses").insert(row).execute()

        if result.data and len(result.data) > 0:
            analysis_id = result.data[0]["id"]
            logger.info("Saved analysis %s (undertone=%s)", analysis_id, predicted_undertone)
            return analysis_id
        else:
            logger.warning("Analysis insert returned no data.")
            return None

    except Exception as e:
        logger.error("Failed to save analysis: %s", e)
        return None


# ---------------------------------------------------------------------------
# save_feedback — persists user feedback/corrections
# ---------------------------------------------------------------------------
def save_feedback(
    analysis_id: str,
    corrected_undertone: str
) -> Optional[str]:
    """
    Saves user feedback (correction) to the `feedback` table.

    Args:
        analysis_id: UUID of the original analysis.
        corrected_undertone: User's corrected label ("Warm", "Cool", "Neutral").

    Returns:
        The UUID of the inserted feedback row, or None if unavailable.
    """
    client = _get_client()
    if client is None:
        logger.debug("Supabase unavailable — skipping feedback save.")
        return None

    if corrected_undertone not in ("Warm", "Cool", "Neutral"):
        logger.warning("Invalid corrected_undertone: %s", corrected_undertone)
        return None

    try:
        row = {
            "analysis_id": analysis_id,
            "corrected_undertone": corrected_undertone,
        }
        result = client.table("feedback").insert(row).execute()

        if result.data and len(result.data) > 0:
            feedback_id = result.data[0]["id"]
            logger.info(
                "Saved feedback %s for analysis %s (corrected=%s)",
                feedback_id, analysis_id, corrected_undertone
            )
            return feedback_id
        else:
            logger.warning("Feedback insert returned no data.")
            return None

    except Exception as e:
        logger.error("Failed to save feedback: %s", e)
        return None


# ---------------------------------------------------------------------------
# export_labeled_data — retrieves labeled training data
# ---------------------------------------------------------------------------
def export_labeled_data(
    source: Optional[str] = None,
    limit: int = 10000
) -> List[Dict[str, Any]]:
    """
    Exports labeled rows from the `training_samples` table.

    Args:
        source: Optional filter by source (e.g. 'kaggle', 'user_feedback').
        limit: Maximum rows to return.

    Returns:
        List of dicts with feature columns and undertone label.
    """
    client = _get_client()
    if client is None:
        logger.debug("Supabase unavailable — cannot export training data.")
        return []

    try:
        query = client.table("training_samples").select("*").limit(limit)
        if source:
            query = query.eq("source", source)

        result = query.execute()
        rows = result.data if result.data else []
        logger.info("Exported %d training samples (source=%s)", len(rows), source or "all")
        return rows

    except Exception as e:
        logger.error("Failed to export training data: %s", e)
        return []


# ---------------------------------------------------------------------------
# insert_training_samples — bulk insert training data
# ---------------------------------------------------------------------------
def insert_training_samples(
    rows: List[Dict[str, Any]],
    batch_size: int = 500
) -> int:
    """
    Bulk inserts training sample rows into the `training_samples` table.

    Args:
        rows: List of dicts matching the training_samples columns.
        batch_size: Number of rows per insert batch.

    Returns:
        Total number of rows successfully inserted.
    """
    client = _get_client()
    if client is None:
        logger.debug("Supabase unavailable — skipping training sample insert.")
        return 0

    total_inserted = 0
    try:
        for i in range(0, len(rows), batch_size):
            batch = rows[i : i + batch_size]
            result = client.table("training_samples").insert(batch).execute()
            inserted = len(result.data) if result.data else 0
            total_inserted += inserted

        logger.info("Inserted %d training samples total.", total_inserted)
    except Exception as e:
        logger.error("Failed to insert training samples (inserted %d so far): %s", total_inserted, e)

    return total_inserted
