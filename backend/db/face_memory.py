"""
Persistent Face Recognition Database Engine for Otterlook AI.
Stores facial biometric embeddings, analyzed undertones, personalized palettes,
and curated outfit configurations in a persistent local SQLite database.
Recognizes returning clients with high precision and serves their calibrated signature profiles.
"""

import os
import json
import sqlite3
import tempfile
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from backend.vision.face_biometrics import compute_face_similarity, EMBEDDING_DIM
from backend.db import neon_client

logger = logging.getLogger("otterlook.face_memory")


class FaceMemoryDB:
    def __init__(self, db_path: Optional[str] = None):
        self._explicit_sqlite = db_path is not None
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(base_dir, "data")
            try:
                os.makedirs(data_dir, exist_ok=True)
                probe_path = os.path.join(data_dir, ".write_test")
                with open(probe_path, "w") as f:
                    f.write("ok")
                os.remove(probe_path)
                db_path = os.path.join(data_dir, "face_memory.db")
            except OSError:
                # Serverless/read-only filesystem fallback (e.g., Vercel)
                tmp_dir = os.path.join(tempfile.gettempdir(), "otterlook")
                os.makedirs(tmp_dir, exist_ok=True)
                db_path = os.path.join(tmp_dir, "face_memory.db")

        self.db_path = db_path
        self._mem_conn = None
        self._embedding_cache: List[Tuple[str, np.ndarray]] = []
        if self.db_path == ":memory:":
            self._mem_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._mem_conn.row_factory = sqlite3.Row
        self._init_db()

    @property
    def _use_neon(self) -> bool:
        return (not self._explicit_sqlite) and neon_client.is_available()

    def _get_connection(self) -> sqlite3.Connection:
        if self._mem_conn is not None:
            return self._mem_conn
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes SQLite schema for biometric face profiles and warms embedding cache."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                CREATE TABLE IF NOT EXISTS face_profiles (
                    face_id TEXT PRIMARY KEY,
                    embedding BLOB NOT NULL,
                    undertone TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    probabilities TEXT,
                    gender TEXT NOT NULL,
                    skin_hex TEXT NOT NULL,
                    skin_metrics TEXT,
                    palette TEXT NOT NULL,
                    skin_harmonies TEXT,
                    curated_outfits TEXT,
                    detection_count INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                # Safe schema migration for pre-existing databases lacking probabilities column
                cols = {row[1] for row in conn.execute("PRAGMA table_info(face_profiles)").fetchall()}
                if "probabilities" not in cols:
                    conn.execute("ALTER TABLE face_profiles ADD COLUMN probabilities TEXT;")
                conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_face_last_seen ON face_profiles(last_seen_at DESC);
                """)
                conn.commit()
            self._load_embedding_cache()
            logger.info("FaceMemoryDB initialized at %s (%d cached faces)", self.db_path, len(self._embedding_cache))
        except Exception as e:
            logger.error("Failed to initialize FaceMemoryDB: %s", e)

    def _load_embedding_cache(self):
        """Loads all (face_id, embedding) pairs into memory for fast cosine similarity search."""
        cache: List[Tuple[str, np.ndarray]] = []
        if self._use_neon:
            try:
                for item in neon_client.load_face_embeddings():
                    emb = np.array(item["embedding"], dtype=np.float32)
                    if len(emb) == EMBEDDING_DIM:
                        cache.append((item["face_id"], emb))
                self._embedding_cache = cache
                return
            except Exception as e:
                logger.error("Failed to warm embedding cache from Neon: %s", e)
        try:
            with self._get_connection() as conn:
                rows = conn.execute("SELECT face_id, embedding FROM face_profiles ORDER BY last_seen_at DESC").fetchall()
                for row in rows:
                    emb = np.frombuffer(row["embedding"], dtype=np.float32)
                    if len(emb) == EMBEDDING_DIM:
                        cache.append((row["face_id"], emb.copy()))
        except Exception as e:
            logger.error("Failed to warm embedding cache: %s", e)
        self._embedding_cache = cache

    def find_matching_profile(
        self,
        query_embedding: np.ndarray,
        threshold: float = 0.82
    ) -> Optional[Tuple[Dict[str, Any], float]]:
        """
        Compares query_embedding against cached face embeddings using cosine similarity,
        then loads only the matched profile row from Neon or SQLite.
        """
        if query_embedding is None or len(query_embedding) != EMBEDDING_DIM:
            return None

        if self._use_neon:
            self._load_embedding_cache()

        best_face_id = None
        best_similarity = -1.0

        for face_id, stored_emb in self._embedding_cache:
            sim = compute_face_similarity(query_embedding, stored_emb)
            if sim > best_similarity:
                best_similarity = sim
                best_face_id = face_id

        if best_face_id is not None and best_similarity >= threshold:
            if self._use_neon:
                profile_dict = neon_client.get_face_profile(best_face_id)
                if profile_dict is not None:
                    logger.info(
                        "Recognized Neon face profile %s with similarity %.3f (>= %.2f)",
                        profile_dict["face_id"], best_similarity, threshold
                    )
                    return profile_dict, best_similarity
            try:
                with self._get_connection() as conn:
                    row = conn.execute(
                        "SELECT * FROM face_profiles WHERE face_id = ?", (best_face_id,)
                    ).fetchone()
                if row is not None:
                    profile_dict = self._row_to_dict(row)
                    logger.info(
                        "Recognized face profile %s with similarity %.3f (>= %.2f)",
                        profile_dict["face_id"], best_similarity, threshold
                    )
                    return profile_dict, best_similarity
            except Exception as e:
                logger.error("Error fetching matched face profile %s: %s", best_face_id, e)

        return None

    def save_profile(
        self,
        embedding: np.ndarray,
        undertone: str,
        confidence: float,
        palette: List[Dict[str, Any]],
        skin_metrics: Dict[str, Any],
        gender: str = "all",
        skin_hex: str = "#C68B59",
        skin_harmonies: Optional[List[Dict[str, Any]]] = None,
        curated_outfits: Optional[List[Dict[str, Any]]] = None,
        probabilities: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Persists a newly calibrated face profile and its customized palette into the database.
        """
        face_id = f"face_{uuid.uuid4().hex[:12]}"
        emb_f32 = embedding.astype(np.float32)
        emb_bytes = emb_f32.tobytes()

        palette_json = json.dumps(palette)
        metrics_json = json.dumps(skin_metrics)
        harmonies_json = json.dumps(skin_harmonies or [])
        outfits_json = json.dumps(curated_outfits or [])
        probs_json = json.dumps(probabilities) if probabilities else None

        now = datetime.now(timezone.utc).isoformat()

        if self._use_neon:
            neon_client.save_face_profile(
                face_id=face_id,
                embedding=emb_f32.tolist(),
                undertone=undertone,
                confidence=float(confidence),
                probabilities=probabilities,
                gender=gender,
                skin_hex=skin_hex,
                skin_metrics=skin_metrics,
                palette=palette,
                skin_harmonies=skin_harmonies or [],
            )
            self._embedding_cache.insert(0, (face_id, emb_f32.copy()))
            return face_id

        try:
            with self._get_connection() as conn:
                conn.execute("""
                INSERT INTO face_profiles (
                    face_id, embedding, undertone, confidence, probabilities, gender,
                    skin_hex, skin_metrics, palette, skin_harmonies,
                    curated_outfits, detection_count, created_at, last_seen_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?);
                """, (
                    face_id, emb_bytes, undertone, float(confidence), probs_json, gender,
                    skin_hex, metrics_json, palette_json, harmonies_json,
                    outfits_json, now, now
                ))
                conn.commit()
            self._embedding_cache.insert(0, (face_id, emb_f32.copy()))
            logger.info("Saved new face profile %s to database.", face_id)
        except Exception as e:
            logger.error("Failed to save face profile %s: %s", face_id, e)

        return face_id

    def touch_profile(self, face_id: str, new_embedding: Optional[np.ndarray] = None):
        """
        Updates last_seen timestamp, increments detection count, and blends embedding.
        """
        if self._use_neon:
            blended_list: Optional[List[float]] = None
            if new_embedding is not None and len(new_embedding) == EMBEDDING_DIM:
                old_emb = next((emb for fid, emb in self._embedding_cache if fid == face_id), None)
                if old_emb is not None:
                    blended = (0.85 * old_emb + 0.15 * new_embedding).astype(np.float32)
                    norm = np.linalg.norm(blended)
                    if norm > 1e-6:
                        blended = blended / norm
                    blended_list = blended.tolist()
                    self._embedding_cache = [
                        (fid, blended.copy() if fid == face_id else emb)
                        for fid, emb in self._embedding_cache
                    ]
            neon_client.touch_face_profile(face_id, blended_list)
            return

        now = datetime.now(timezone.utc).isoformat()
        try:
            with self._get_connection() as conn:
                if new_embedding is not None and len(new_embedding) == EMBEDDING_DIM:
                    cur = conn.execute("SELECT embedding FROM face_profiles WHERE face_id = ?", (face_id,))
                    row = cur.fetchone()
                    if row:
                        old_emb = np.frombuffer(row["embedding"], dtype=np.float32)
                        # Adaptive moving average: 85% established memory + 15% current view
                        blended = (0.85 * old_emb + 0.15 * new_embedding).astype(np.float32)
                        norm = np.linalg.norm(blended)
                        if norm > 1e-6:
                            blended = blended / norm
                        emb_bytes = blended.tobytes()
                        conn.execute("""
                        UPDATE face_profiles 
                        SET last_seen_at = ?, detection_count = detection_count + 1, embedding = ?
                        WHERE face_id = ?;
                        """, (now, emb_bytes, face_id))
                        self._embedding_cache = [
                            (fid, blended.copy() if fid == face_id else emb)
                            for fid, emb in self._embedding_cache
                        ]
                else:
                    conn.execute("""
                    UPDATE face_profiles 
                    SET last_seen_at = ?, detection_count = detection_count + 1
                    WHERE face_id = ?;
                    """, (now, face_id))
                conn.commit()
        except Exception as e:
            logger.error("Failed to touch profile %s: %s", face_id, e)

    def delete_profile(self, face_id: str) -> bool:
        """Deletes a face profile from the database and in-memory cache."""
        if not face_id:
            return False
        if self._use_neon:
            deleted = neon_client.delete_face_profile(face_id)
            self._embedding_cache = [(fid, emb) for fid, emb in self._embedding_cache if fid != face_id]
            return deleted
        try:
            with self._get_connection() as conn:
                cur = conn.execute("DELETE FROM face_profiles WHERE face_id = ?", (face_id,))
                conn.commit()
                deleted = cur.rowcount > 0
            self._embedding_cache = [(fid, emb) for fid, emb in self._embedding_cache if fid != face_id]
            if deleted:
                logger.info("Deleted face profile %s from database.", face_id)
            return deleted
        except Exception as e:
            logger.error("Failed to delete face profile %s: %s", face_id, e)
            return False

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Converts database row to dictionary with parsed JSON fields."""
        def safe_json(val, default):
            if not val:
                return default
            try:
                return json.loads(val)
            except Exception:
                return default

        probs_raw = row["probabilities"] if "probabilities" in row.keys() else None
        return {
            "face_id": row["face_id"],
            "undertone": row["undertone"],
            "confidence": float(row["confidence"]),
            "probabilities": safe_json(probs_raw, None),
            "gender": row["gender"],
            "skin_hex": row["skin_hex"],
            "skin_metrics": safe_json(row["skin_metrics"], {}),
            "palette": safe_json(row["palette"], []),
            "skin_harmonies": safe_json(row["skin_harmonies"], []),
            "curated_outfits": safe_json(row["curated_outfits"], []),
            "detection_count": int(row["detection_count"]),
            "created_at": row["created_at"],
            "last_seen_at": row["last_seen_at"]
        }

    def get_stats(self) -> Dict[str, Any]:
        """Returns diagnostic counts from the face memory store."""
        if self._use_neon:
            return neon_client.get_face_stats()
        try:
            with self._get_connection() as conn:
                cur = conn.execute("SELECT COUNT(*), SUM(detection_count) FROM face_profiles")
                total_faces, total_recognitions = cur.fetchone()
                return {
                    "total_registered_faces": total_faces or 0,
                    "total_recognitions": total_recognitions or 0
                }
        except Exception as e:
            return {"error": str(e), "total_registered_faces": 0, "total_recognitions": 0}


# Global singleton instance
face_memory_db = FaceMemoryDB()
