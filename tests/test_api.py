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
    assert "database_connected" in data
    assert data.get("database_provider") == "neon_postgres"


def test_api_auth_config_and_google_validation(client):
    cfg = client.get("/api/auth/config")
    assert cfg.status_code == 200
    cdata = cfg.json()
    assert "google_enabled" in cdata
    assert cdata.get("max_name_chars") == 16

    bad = client.post("/api/auth/google", json={"credential": ""})
    assert bad.status_code in (400, 503)


def test_api_user_progress_persistence(client):
    save_res = client.post(
        "/api/auth/progress",
        json={
            "email": "otter.progress@test.com",
            "name": "Otter User",
            "picture": "https://example.com/avatar.png",
            "progress": {
                "view": "results",
                "selectedGenderMode": "male",
                "currentClothingType": "formal",
                "currentWeather": "winter",
            },
        },
    )
    assert save_res.status_code == 200
    sdata = save_res.json()
    assert sdata["success"] is True
    assert sdata["progress"]["view"] == "results"

    get_res = client.get("/api/auth/progress", params={"email": "otter.progress@test.com"})
    assert get_res.status_code == 200
    gdata = get_res.json()
    assert gdata["success"] is True
    assert gdata["progress"]["selectedGenderMode"] == "male"
    assert gdata["progress"]["currentClothingType"] == "formal"


def test_api_email_auth_and_google_authenticator_2fa(client):
    import time
    from backend.auth_utils import _totp_at

    # Character limits enforced
    short_pw = client.post("/api/auth/register", json={"email": "a@b.com", "password": "123"})
    assert short_pw.status_code == 400
    long_pw = client.post("/api/auth/register", json={"email": "a@b.com", "password": "x" * 17})
    assert long_pw.status_code == 400
    long_email = client.post("/api/auth/register", json={"email": ("a" * 45) + "@test.com", "password": "secret12"})
    assert long_email.status_code == 400

    # Valid registration generates Google Authenticator secret
    reg = client.post("/api/auth/register", json={"email": "otter2fa@test.com", "password": "secret12"})
    assert reg.status_code == 200
    rdata = reg.json()
    assert rdata["success"] is True
    secret = rdata["totp_setup"]["secret"]
    assert "otpauth://totp/" in rdata["totp_setup"]["otpauth_uri"]

    # Enable 2FA with valid 6-digit TOTP code
    code = _totp_at(secret, int(time.time()) // 30)
    v2 = client.post("/api/auth/2fa/verify", json={"email": "otter2fa@test.com", "totp_code": code})
    assert v2.status_code == 200
    assert v2.json()["user"]["totp_enabled"] is True

    # Login without 2FA code prompts for 2FA; login with valid code succeeds
    l1 = client.post("/api/auth/login", json={"email": "otter2fa@test.com", "password": "secret12"})
    assert l1.status_code == 200 and l1.json()["requires_2fa"] is True
    l2 = client.post("/api/auth/login", json={"email": "otter2fa@test.com", "password": "secret12", "totp_code": code})
    assert l2.status_code == 200 and l2.json()["success"] is True


def test_api_feedback_validation(client):
    # Invalid undertone should return 400
    response = client.post("/api/feedback", json={"analysis_id": "test-uuid", "corrected_undertone": "Invalid"})
    assert response.status_code == 400

    # Valid format
    response = client.post("/api/feedback", json={"analysis_id": "test-uuid", "corrected_undertone": "Warm"})
    assert response.status_code == 200
    data = response.json()
    assert "success" in data



def test_api_detect_face_no_face(client):
    import io, cv2, numpy as np
    # Image with no face (solid black and solid color)
    for color in [(0, 0, 0), (34, 139, 34), (255, 255, 255)]:
        no_face_img = np.zeros((300, 300, 3), dtype=np.uint8)
        no_face_img[:, :] = color
        _, encoded = cv2.imencode('.jpg', no_face_img)

        response = client.post(
            '/api/detect-face',
            files={'file': ('no_face.jpg', io.BytesIO(encoded.tobytes()), 'image/jpeg')}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['has_face'] is False
        assert data['face_count'] == 0
        assert "No human face detected" in data['message']

    # Test on floral / beige textured curtain fabric pattern (must NOT detect a face)
    textured_img = np.zeros((400, 400, 3), dtype=np.uint8)
    textured_img[:, :] = (169, 183, 184)  # Beige background (#B8B7A9)
    # Add repetitive floral-like circles
    for cx in range(50, 400, 80):
        for cy in range(50, 400, 80):
            cv2.circle(textured_img, (cx, cy), 25, (120, 140, 160), -1)
            cv2.circle(textured_img, (cx, cy), 10, (80, 100, 120), -1)
    _, enc_text = cv2.imencode('.jpg', textured_img)
    resp_text = client.post(
        '/api/detect-face',
        files={'file': ('curtain_pattern.jpg', io.BytesIO(enc_text.tobytes()), 'image/jpeg')}
    )
    assert resp_text.status_code == 200
    assert resp_text.json()['has_face'] is False
    assert resp_text.json()['face_count'] == 0


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
    assert data.get('stage') == 'face_detection'
    assert 'No human face detected' in data.get('error', '')
    assert 'undertone' not in data
    assert 'palette' not in data
