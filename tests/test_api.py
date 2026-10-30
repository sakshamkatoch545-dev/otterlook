"""
Unit tests for recommendations palette generator and FastAPI integration.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from recommendations.palette_generator import PaletteGenerator
from main import app

@pytest.fixture
def palette_gen():
    return PaletteGenerator()

@pytest.fixture
def client():
    return TestClient(app)

def test_palette_generation_warm(palette_gen):
    res = palette_gen.generate_recommendations("Warm")
    assert res["undertone"] == "Warm"
    assert len(res["palette"]) > 0
    assert len(res["recommendations"]["clothing"]) > 0
    assert len(res["recommendations"]["makeup"]) > 0
    assert len(res["less_recommended"]) > 0

def test_palette_generation_cool(palette_gen):
    res = palette_gen.generate_recommendations("Cool")
    assert res["undertone"] == "Cool"
    assert any("Blue" in item["name"] or "Plum" in item["name"] or "Lavender" in item["name"] for item in res["palette"])

def test_api_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True

def test_api_analyze_sample(client):
    sample_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "assets", "samples", "sample_warm.jpg")
    assert os.path.exists(sample_path)
    
    with open(sample_path, "rb") as f:
        response = client.post("/api/analyze", files={"file": ("sample_warm.jpg", f, "image/jpeg")})
        
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert "undertone" in res_data
    assert "palette" in res_data
    assert "recommendations" in res_data
    assert "analysis_id" in res_data

def test_api_db_status(client):
    response = client.get("/api/db-status")
    assert response.status_code == 200
    data = response.json()
    assert "supabase_connected" in data


def test_api_feedback_validation(client):
    # Invalid undertone should return 400
    response = client.post("/api/feedback", json={"analysis_id": "test-uuid", "corrected_undertone": "Invalid"})
    assert response.status_code == 400

    # Valid format
    response = client.post("/api/feedback", json={"analysis_id": "test-uuid", "corrected_undertone": "Warm"})
    assert response.status_code == 200
    data = response.json()
    assert "success" in data



def test_api_analyze_no_face_gives_no_output(client):
    import io, cv2, numpy as np
    # Image with no face
    no_face_img = np.zeros((300, 300, 3), dtype=np.uint8)
    no_face_img[:, :] = (34, 139, 34)
    _, encoded = cv2.imencode('.jpg', no_face_img)

    response = client.post(
        '/api/analyze',
        files={'file': ('no_face.jpg', io.BytesIO(encoded.tobytes()), 'image/jpeg')}
    )
    # Must not give output if no face is shown!
    assert response.status_code == 422
    data = response.json()
    assert data['success'] is False
    assert data.get('stage') in ('face_detection', 'quality_check')
    assert 'undertone' not in data
    assert 'palette' not in data
