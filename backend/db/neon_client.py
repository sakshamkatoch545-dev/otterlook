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
_shared_conn = None


def _get_connection_url() -> str:
    return (
        os.environ.get("DATABASE_URL", "").strip()
        or os.environ.get("POSTGRES_URL", "").strip()
        or os.environ.get("STORAGE_URL", "").strip()
        or os.environ.get("STORAGE_POSTGRES_URL", "").strip()
    )


def _open_connection():
    """Return a reusable Neon Postgres connection, reconnecting if closed."""
    global _shared_conn
    db_url = _get_connection_url()
    if not db_url:
        return None

    try:
        import pg8000.native as pg
    except ImportError:
        logger.warning("pg8000 package not installed. Run: pip install pg8000>=1.31.0")
        return None

    if _shared_conn is not None:
        try:
            _shared_conn.run("SELECT 1")
            return _shared_conn
        except Exception:
            try:
                _shared_conn.close()
            except Exception:
                pass
            _shared_conn = None

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
        _shared_conn = conn
        return conn
    except Exception as exc:
        logger.error("Failed to connect to Neon Postgres: %s", exc)
        return None


def _close_if_not_shared(conn) -> None:
    if conn is not None and conn is not _shared_conn:
        try:
            conn.close()
        except Exception:
            pass


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
    conn.run(
        """
        CREATE TABLE IF NOT EXISTS face_profiles (
            face_id TEXT PRIMARY KEY,
            embedding JSONB NOT NULL,
            undertone TEXT NOT NULL,
            confidence REAL NOT NULL,
            probabilities JSONB,
            gender TEXT NOT NULL,
            skin_hex TEXT NOT NULL,
            skin_metrics JSONB,
            palette JSONB NOT NULL,
            skin_harmonies JSONB,
            detection_count INT NOT NULL DEFAULT 1,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now()
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
        _close_if_not_shared(conn)


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
        _close_if_not_shared(conn)


# ---------------------------------------------------------------------------
# Biometric Face Profiles persistence in Neon Postgres
# ---------------------------------------------------------------------------
def load_face_embeddings() -> List[Dict[str, Any]]:
    """Load all (face_id, embedding) pairs ordered by most recently seen."""
    conn = _open_connection()
    if conn is None:
        return []
    try:
        rows = conn.run(
            "SELECT face_id, embedding FROM face_profiles ORDER BY last_seen_at DESC"
        )
        results: List[Dict[str, Any]] = []
        for face_id, emb in rows:
            if isinstance(emb, str):
                emb = json.loads(emb)
            results.append({"face_id": face_id, "embedding": emb})
        return results
    except Exception as exc:
        logger.error("Failed to load face embeddings from Neon: %s", exc)
        return []
    finally:
        _close_if_not_shared(conn)


def get_face_profile(face_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a single calibrated face profile from Neon by face_id."""
    conn = _open_connection()
    if conn is None:
        return None
    try:
        rows = conn.run(
            """
            SELECT face_id, undertone, confidence, probabilities, gender,
                   skin_hex, skin_metrics, palette, skin_harmonies,
                   detection_count, created_at, last_seen_at
            FROM face_profiles
            WHERE face_id = :face_id
            """,
            face_id=face_id,
        )
        if not rows:
            return None
        r = rows[0]

        def _parse(val, default):
            if val is None:
                return default
            if isinstance(val, str):
                try:
                    return json.loads(val)
                except Exception:
                    return default
            return val

        return {
            "face_id": r[0],
            "undertone": r[1],
            "confidence": float(r[2]),
            "probabilities": _parse(r[3], None),
            "gender": r[4],
            "skin_hex": r[5],
            "skin_metrics": _parse(r[6], {}),
            "palette": _parse(r[7], []),
            "skin_harmonies": _parse(r[8], []),
            "curated_outfits": [],
            "detection_count": int(r[9]),
            "created_at": str(r[10]),
            "last_seen_at": str(r[11]),
        }
    except Exception as exc:
        logger.error("Failed to fetch face profile %s from Neon: %s", face_id, exc)
        return None
    finally:
        _close_if_not_shared(conn)


def save_face_profile(
    face_id: str,
    embedding: List[float],
    undertone: str,
    confidence: float,
    probabilities: Optional[Dict[str, float]],
    gender: str,
    skin_hex: str,
    skin_metrics: Dict[str, Any],
    palette: List[Dict[str, Any]],
    skin_harmonies: List[Dict[str, Any]],
) -> bool:
    """Insert a newly calibrated face profile into Neon Postgres."""
    conn = _open_connection()
    if conn is None:
        return False
    try:
        conn.run(
            """
            INSERT INTO face_profiles (
                face_id, embedding, undertone, confidence, probabilities,
                gender, skin_hex, skin_metrics, palette, skin_harmonies
            ) VALUES (
                :face_id, CAST(:embedding AS JSONB), :undertone, :confidence,
                CAST(:probabilities AS JSONB), :gender, :skin_hex,
                CAST(:skin_metrics AS JSONB), CAST(:palette AS JSONB),
                CAST(:skin_harmonies AS JSONB)
            )
            ON CONFLICT (face_id) DO NOTHING
            """,
            face_id=face_id,
            embedding=json.dumps(embedding),
            undertone=undertone,
            confidence=float(confidence),
            probabilities=json.dumps(probabilities) if probabilities else None,
            gender=gender,
            skin_hex=skin_hex,
            skin_metrics=json.dumps(skin_metrics),
            palette=json.dumps(palette),
            skin_harmonies=json.dumps(skin_harmonies),
        )
        logger.info("Saved face profile %s to Neon Postgres.", face_id)
        return True
    except Exception as exc:
        logger.error("Failed to save face profile %s to Neon: %s", face_id, exc)
        return False
    finally:
        _close_if_not_shared(conn)


def touch_face_profile(face_id: str, blended_embedding: Optional[List[float]] = None) -> None:
    """Update last_seen_at, detection_count, and blended embedding in Neon."""
    conn = _open_connection()
    if conn is None:
        return
    try:
        if blended_embedding is not None:
            conn.run(
                """
                UPDATE face_profiles
                SET last_seen_at = now(),
                    detection_count = detection_count + 1,
                    embedding = CAST(:embedding AS JSONB)
                WHERE face_id = :face_id
                """,
                face_id=face_id,
                embedding=json.dumps(blended_embedding),
            )
        else:
            conn.run(
                """
                UPDATE face_profiles
                SET last_seen_at = now(),
                    detection_count = detection_count + 1
                WHERE face_id = :face_id
                """,
                face_id=face_id,
            )
    except Exception as exc:
        logger.error("Failed to touch face profile %s in Neon: %s", face_id, exc)
    finally:
        _close_if_not_shared(conn)


def delete_face_profile(face_id: str) -> bool:
    """Delete a face profile from Neon Postgres."""
    conn = _open_connection()
    if conn is None:
        return False
    try:
        rows = conn.run(
            "DELETE FROM face_profiles WHERE face_id = :face_id RETURNING face_id",
            face_id=face_id,
        )
        return len(rows) > 0
    except Exception as exc:
        logger.error("Failed to delete face profile %s from Neon: %s", face_id, exc)
        return False
    finally:
        _close_if_not_shared(conn)


def get_face_stats() -> Dict[str, Any]:
    """Return total registered faces and total recognitions from Neon."""
    conn = _open_connection()
    if conn is None:
        return {"total_registered_faces": 0, "total_recognitions": 0}
    try:
        rows = conn.run(
            "SELECT COUNT(*), COALESCE(SUM(detection_count), 0) FROM face_profiles"
        )
        total_faces, total_recognitions = rows[0]
        return {
            "total_registered_faces": int(total_faces or 0),
            "total_recognitions": int(total_recognitions or 0),
        }
    except Exception as exc:
        return {"error": str(exc), "total_registered_faces": 0, "total_recognitions": 0}
    finally:
        _close_if_not_shared(conn)
