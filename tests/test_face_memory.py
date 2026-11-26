"""
Unit tests for Facial Biometrics, Persistent Face Database Memory,
and Differentiated Palette Generation.
"""

import os
import sys
import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.vision.face_biometrics import extract_face_embedding, compute_face_similarity, EMBEDDING_DIM
from backend.db.face_memory import FaceMemoryDB
from backend.recommendations.palette_generator import PaletteGenerator


def test_face_embedding_dimensions_and_norm():
    """Verify embedding shape is (128,) with unit L2 norm."""
    dummy_img = np.full((200, 200, 3), 160, dtype=np.uint8)
    dummy_img[50:150, 50:150] = [140, 180, 210]  # simulated face area
    bbox = [50, 50, 100, 100]

    emb = extract_face_embedding(dummy_img, bbox)
    assert emb.shape == (EMBEDDING_DIM,)
    assert emb.dtype == np.float32
    norm = np.linalg.norm(emb)
    assert np.isclose(norm, 1.0, atol=1e-4)


def test_face_similarity_same_vs_different():
    """Verify high similarity for near-identical faces and low similarity for different faces."""
    img_a = np.full((200, 200, 3), 160, dtype=np.uint8)
    img_a[50:150, 50:150] = [120, 140, 190]
    bbox_a = [50, 50, 100, 100]
    emb_a = extract_face_embedding(img_a, bbox_a)

    # Near-identical face (minor sensor noise)
    img_a_noisy = img_a.copy()
    img_a_noisy[50:150, 50:150] = np.clip(img_a_noisy[50:150, 50:150].astype(int) + 3, 0, 255).astype(np.uint8)
    emb_a_noisy = extract_face_embedding(img_a_noisy, bbox_a)

    # Completely different face with different structure and color
    img_b = np.full((200, 200, 3), 40, dtype=np.uint8)
    img_b[30:170, 40:140] = [50, 80, 120]  # different aspect ratio and tone
    bbox_b = [40, 30, 100, 140]
    emb_b = extract_face_embedding(img_b, bbox_b)

    sim_same = compute_face_similarity(emb_a, emb_a_noisy)
    sim_diff = compute_face_similarity(emb_a, emb_b)

    assert sim_same >= 0.85, f"Expected high similarity for same face, got {sim_same}"
    assert sim_diff < 0.70, f"Expected low similarity for different face, got {sim_diff}"


def test_face_memory_database_crud_and_matching():
    """Verify SQLite face memory persistence, cosine similarity matching, and retrieval."""
    db = FaceMemoryDB(":memory:")
    
    # Register Person 1
    emb_person1 = np.random.randn(128).astype(np.float32)
    emb_person1 /= np.linalg.norm(emb_person1)
    palette_person1 = [
        {"name": "Terracotta", "hex": "#E07A5F"},
        {"name": "Warm Amber", "hex": "#D4A373"}
    ]
    
    fid = db.save_profile(
        embedding=emb_person1,
        undertone="Warm",
        confidence=0.96,
        palette=palette_person1,
        skin_metrics={"cielab": {"L": 62.0, "a": 14.0, "b": 18.0}},
        gender="male",
        skin_hex="#D4A373"
    )
    assert fid.startswith("face_")

    # Match returning Person 1
    matched = db.find_matching_profile(emb_person1, threshold=0.82)
    assert matched is not None
    profile, sim = matched
    assert profile["face_id"] == fid
    assert profile["undertone"] == "Warm"
    assert profile["palette"][0]["name"] == "Terracotta"
    assert sim >= 0.99

    # Try matching Person 2 (completely different embedding)
    emb_person2 = np.random.randn(128).astype(np.float32)
    emb_person2 /= np.linalg.norm(emb_person2)
    
    no_match = db.find_matching_profile(emb_person2, threshold=0.82)
    assert no_match is None


def test_palette_differentiation_for_different_faces():
    """Verify that different faces receive different, customized color palettes."""
    pg = PaletteGenerator()

    # Face A: Warm, high melanin, deeper skin (Type IV)
    metrics_a = {
        "cielab": {"L": 46.0, "a": 13.5, "b": 21.0},
        "ita_angle": -5.0,
        "representative_hex": "#8D5524",
        "phototype_estimate": "Type IV — Olive / Rich"
    }
    emb_a = np.zeros(128, dtype=np.float32)
    emb_a[:32] = 0.5

    # Face B: Warm, fair/light golden skin (Type II)
    metrics_b = {
        "cielab": {"L": 74.0, "a": 9.5, "b": 14.0},
        "ita_angle": 42.0,
        "representative_hex": "#F4D0B8",
        "phototype_estimate": "Type II — Fair Warm"
    }
    emb_b = np.zeros(128, dtype=np.float32)
    emb_b[32:64] = 0.5

    recs_a = pg.generate_recommendations(undertone="Warm", skin_metrics=metrics_a, face_embedding=emb_a)
    recs_b = pg.generate_recommendations(undertone="Warm", skin_metrics=metrics_b, face_embedding=emb_b)

    palette_a = [c["name"] for c in recs_a["palette"]]
    palette_b = [c["name"] for c in recs_b["palette"]]
    hexes_a = [c["hex"] for c in recs_a["palette"]]
    hexes_b = [c["hex"] for c in recs_b["palette"]]

    # They should NOT be identical!
    assert palette_a != palette_b or hexes_a != hexes_b, "Expected different palettes for distinct faces"


def test_deterministic_palette_for_same_face():
    """Verify that the exact same face receives a deterministic identical palette."""
    pg = PaletteGenerator()
    metrics = {
        "cielab": {"L": 64.0, "a": 11.0, "b": 16.5},
        "ita_angle": 24.0,
        "representative_hex": "#C68B59"
    }
    emb = np.random.randn(128).astype(np.float32)
    emb /= np.linalg.norm(emb)

    recs1 = pg.generate_recommendations(undertone="Warm", skin_metrics=metrics, face_embedding=emb)
    recs2 = pg.generate_recommendations(undertone="Warm", skin_metrics=metrics, face_embedding=emb)

    hexes1 = [c["hex"] for c in recs1["palette"]]
    hexes2 = [c["hex"] for c in recs2["palette"]]
    assert hexes1 == hexes2, "Expected identical palettes for the same face"


def test_face_memory_probabilities_and_delete():
    """Verify full 3-class probabilities persistence and profile deletion."""
    db = FaceMemoryDB(":memory:")
    emb = np.ones(128, dtype=np.float32)
    emb /= np.linalg.norm(emb)

    probs = {"Warm": 0.72, "Neutral": 0.18, "Cool": 0.10}
    fid = db.save_profile(
        embedding=emb,
        undertone="Warm",
        confidence=0.72,
        palette=[{"name": "Amber", "hex": "#D4A373"}],
        skin_metrics={"cielab": {"L": 60.0, "a": 12.0, "b": 17.0}},
        probabilities=probs,
    )

    matched = db.find_matching_profile(emb, threshold=0.82)
    assert matched is not None
    profile, _ = matched
    assert profile["probabilities"] == probs

    assert db.delete_profile(fid) is True
    assert db.delete_profile(fid) is False
    assert db.find_matching_profile(emb, threshold=0.82) is None


def test_skin_extractor_illumination_normalization():
    """Verify illumination normalizer softens strong color casts without altering neutral images."""
    from backend.vision.skin_detection import SkinExtractor
    extractor = SkinExtractor()

    # Neutral gray image should remain unchanged
    neutral = np.full((64, 64, 3), 128, dtype=np.uint8)
    out_neutral = extractor._normalize_illumination(neutral)
    assert np.array_equal(out_neutral, neutral)

    # Strong warm/yellow tungsten cast (low B, high R) should be softened toward neutral
    cast = np.zeros((64, 64, 3), dtype=np.uint8)
    cast[:, :] = [70, 140, 210]  # BGR
    out_cast = extractor._normalize_illumination(cast)
    assert float(out_cast[:, :, 0].mean()) > 70.0
    assert float(out_cast[:, :, 2].mean()) < 210.0


def test_delete_face_profile_endpoint():
    """Verify DELETE /api/face-profile/{face_id} returns 404 for unknown and 200 for existing."""
    from fastapi.testclient import TestClient
    from backend.main import app, face_memory_db

    client = TestClient(app)
    res_missing = client.delete("/api/face-profile/face_does_not_exist")
    assert res_missing.status_code == 404

    emb = np.random.randn(128).astype(np.float32)
    emb /= np.linalg.norm(emb)
    fid = face_memory_db.save_profile(
        embedding=emb,
        undertone="Neutral",
        confidence=0.85,
        palette=[{"name": "Sage", "hex": "#8A9A5B"}],
        skin_metrics={},
    )
    res_ok = client.delete(f"/api/face-profile/{fid}")
    assert res_ok.status_code == 200
    assert res_ok.json()["deleted_face_id"] == fid
