"""
Unit tests for Outfit Synthesizer engine and endpoints.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from recommendations.outfit_synthesizer import (
    generate_curated_outfits,
    CLOTHING_TYPES,
    WEATHER_TYPES,
)
from main import app

@pytest.fixture
def client():
    return TestClient(app)

MOCK_PALETTE = [
    {"name": "Terracotta", "hex": "#E07A5F", "role": "Primary Warm Accent"},
    {"name": "Warm Amber", "hex": "#D4A373", "role": "Secondary Accent"},
    {"name": "Rich Camel", "hex": "#C59B6D", "role": "Neutral Foundation"},
    {"name": "Cream Linen", "hex": "#F4EBD9", "role": "Light Contrast / Upper"},
    {"name": "Deep Bronze", "hex": "#6F4E37", "role": "Grounding Shadow / Lower"},
    {"name": "Golden Olive", "hex": "#8A8154", "role": "Subtle Depth"},
    {"name": "Champagne Gold", "hex": "#E8D8A6", "role": "Lustre Accent / Jewellery"},
]

def test_generate_curated_outfits_male_all_types():
    for c_item in CLOTHING_TYPES:
        c_type = c_item["id"] if isinstance(c_item, dict) else c_item
        outfits = generate_curated_outfits(
            gender="male",
            clothing_type=c_type,
            weather="summer",
            palette=MOCK_PALETTE,
            undertone="Warm",
        )
        assert len(outfits) in [3, 4]
        for outfit in outfits:
            assert "look_id" in outfit
            assert "title" in outfit
            assert "svg" in outfit
            assert outfit["svg"].startswith("<svg")
            assert "pieces" in outfit
            pieces = outfit["pieces"]
            assert "upper" in pieces
            assert "bottom" in pieces
            assert "shoes" in pieces
            assert "jewellery" in pieces

            # Male jewellery checks
            jewel = pieces["jewellery"]
            assert "rings" in jewel
            assert "earrings" in jewel
            assert "watch" in jewel

def test_generate_curated_outfits_female_all_types():
    for c_item in CLOTHING_TYPES:
        c_type = c_item["id"] if isinstance(c_item, dict) else c_item
        outfits = generate_curated_outfits(
            gender="female",
            clothing_type=c_type,
            weather="winter",
            palette=MOCK_PALETTE,
            undertone="Cool",
        )
        assert len(outfits) in [3, 4]
        for outfit in outfits:
            assert "svg" in outfit
            assert outfit["svg"].startswith("<svg")
            pieces = outfit["pieces"]
            assert "upper" in pieces
            assert "bottom" in pieces
            assert "shoes" in pieces
            assert "jewellery" in pieces

            # Female jewellery & beauty checks
            jewel = pieces["jewellery"]
            assert "necklace" in jewel
            assert "earrings" in jewel
            assert "lipstick_tint" in jewel
            assert "finish" in jewel["lipstick_tint"]

def test_generate_curated_outfits_all_weathers():
    for w_item in WEATHER_TYPES:
        weather = w_item["id"] if isinstance(w_item, dict) else w_item
        outfits = generate_curated_outfits(
            gender="female",
            clothing_type="formal",
            weather=weather,
            palette=MOCK_PALETTE,
            undertone="Neutral",
        )
        assert len(outfits) >= 3

def test_api_wardrobe_filters(client):
    response = client.get("/api/wardrobe-filters")
    assert response.status_code == 200
    data = response.json()
    assert "clothing_types" in data
    assert "weather_types" in data
    assert any(item["id"] == "casual" for item in data["clothing_types"])
    assert any(item["id"] == "summer" for item in data["weather_types"])

def test_api_generate_outfits(client):
    payload = {
        "gender": "male",
        "clothing_type": "streetwear",
        "weather": "monsoon",
        "palette": MOCK_PALETTE,
        "undertone": "Warm",
    }
    response = client.post("/api/generate-outfits", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["outfits"]) in [3, 4]
    first_look = data["outfits"][0]
    assert first_look["pieces"]["jewellery"]["rings"] is not None
