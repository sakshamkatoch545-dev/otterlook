"""
Neon Serverless Postgres Client Module for Otterlook AI.

Replaces Supabase so the database never pauses after 7 days of inactivity
and auto-wakes on demand. Uses pure-Python `pg8000.native` for zero-friction
Vercel serverless and local compatibility.

Environment Variables Supported:
    DATABASE_URL  - Neon Postgres connection string (preferred)
    POSTGRES_URL  - Vercel Postgres/Neon integration connection string
"""

import json
import logging
import os
import ssl
import uuid
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, unquote, urlparse

logger = logging.getLogger("otterlook.neon")

_schema_initialized = False


def _get_connection_url() -> str:
    return (
        os.environ.get("DATABASE_URL", "").strip()
        or os.environ.get("POSTGRES_URL", "").strip()
    )


def _open_connection():
    """Open a short-lived Neon Postgres connection (serverless-safe)."""
    db_url = _get_connection_url()
    if not db_url:
        return None

    try:
        import pg8000.native as pg
    except ImportError:
        logger.warning("pg8000 package not installed. Run: pip install pg8000>=1.31.0")
        return None

    try:
        parsed = urlparse(db_url)
        user = unquote(parsed.username or "")
        password = unquote(parsed.password or "")
        host = parsed.hostname or ""
        port = parsed.port or 5432
        database = (parsed.path or "/neondb").lstrip("/") or "neondb"
        qs = parse_qs(parsed.query)
        sslmode = (qs.get("sslmode", ["require"])[0] or "require").lower()

        ssl_ctx = None
        if sslmode != "disable" and host not in ("localhost", "127.0.0.1"):
            ssl_ctx = ssl.create_default_context()

        conn = pg.Connection(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database,
            ssl_context=ssl_ctx,
            timeout=10,
        )
        _ensure_schema(conn)
        return conn
    except Exception as exc:
        logger.error("Failed to connect to Neon Postgres: %s", exc)
        return None


def _ensure_schema(conn) -> None:
    """Create core tables automatically if they do not yet exist."""
    global _schema_initialized
    if _schema_initialized:
        return

    conn.run(
        """
        CREATE TABLE IF NOT EXISTS analyses (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            features JSONB NOT NULL,
            predicted_undertone TEXT NOT NULL,
            confidence REAL,
            quality_score INT
        )
        """
    )
    conn.run(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id TEXT PRIMARY KEY,
            analysis_id TEXT NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
            corrected_undertone TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    _schema_initialized = True


def is_available() -> bool:
    """Check whether Neon Postgres URL is configured (and driver is installed)."""
    if not _get_connection_url():
        return False
    try:
        import pg8000.native  # noqa: F401
        return True
    except ImportError:
        return False


def save_analysis(
    features: Dict[str, float],
    predicted_undertone: str,
    confidence: float,
    quality_score: int,
    analysis_id: Optional[str] = None,
) -> Optional[str]:
    """Persist an analysis result to the `analyses` table."""
    conn = _open_connection()
    if conn is None:
        return None

    row_id = analysis_id or str(uuid.uuid4())
    try:
        conn.run(
            """
            INSERT INTO analyses (id, features, predicted_undertone, confidence, quality_score)
            VALUES (:id, CAST(:features AS JSONB), :undertone, :confidence, :quality)
            ON CONFLICT (id) DO NOTHING
            """,
            id=row_id,
            features=json.dumps(features),
            undertone=predicted_undertone,
            confidence=float(confidence),
            quality=int(quality_score),
        )
        logger.info("Saved analysis %s to Neon (undertone=%s)", row_id, predicted_undertone)
        return row_id
    except Exception as exc:
        logger.error("Failed to save analysis to Neon: %s", exc)
        return None
    finally:
        try:
            conn.close()
        except Exception:
            pass


def save_feedback(
    analysis_id: str,
    corrected_undertone: str,
) -> Optional[str]:
    """Persist user undertone feedback to the `feedback` table."""
    if corrected_undertone not in ("Warm", "Cool", "Neutral"):
        logger.warning("Invalid corrected_undertone: %s", corrected_undertone)
        return None

    conn = _open_connection()
    if conn is None:
        return None

    feedback_id = str(uuid.uuid4())
    try:
        conn.run(
            """
            INSERT INTO feedback (id, analysis_id, corrected_undertone)
            VALUES (:id, :analysis_id, :corrected)
            """,
            id=feedback_id,
            analysis_id=analysis_id,
            corrected=corrected_undertone,
        )
        logger.info(
            "Saved feedback %s for analysis %s (corrected=%s)",
            feedback_id,
            analysis_id,
            corrected_undertone,
        )
        return feedback_id
    except Exception as exc:
        logger.error("Failed to save feedback to Neon: %s", exc)
        return None
    finally:
        try:
            conn.close()
        except Exception:
            pass
