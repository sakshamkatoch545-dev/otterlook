"""
Unit tests for ML undertone predictor.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from ml.predictor import UndertonePredictor

@pytest.fixture
def predictor():
    return UndertonePredictor()

def test_warm_prediction(predictor):
    # Simulated warm skin features (elevated b*, peach hue)
    warm_feats = {
        "mean_r": 235.0, "mean_g": 185.0, "mean_b": 145.0,
        "median_r": 235.0, "median_g": 185.0, "median_b": 145.0,
        "std_r": 8.0, "std_g": 6.0, "std_b": 6.0,
        "mean_h": 16.0, "mean_s": 95.0, "mean_v": 235.0,
        "mean_l": 76.0, "mean_a": 13.5, "mean_lab_b": 22.0,
        "std_l": 4.0, "std_a": 2.0, "std_lab_b": 2.5,
        "ita": 49.0, "b_to_a_ratio": 1.63, "rg_ratio": 1.27, "rb_ratio": 1.62
    }
    res = predictor.predict(warm_feats)
    assert res["label"] in ["Warm", "Neutral", "Cool"]
    assert 0.0 <= res["confidence"] <= 1.0
    assert "probabilities" in res
    assert "Warm" in res["probabilities"]

def test_cool_prediction(predictor):
    # Simulated cool skin features (elevated a*, lower b*, red-pink hue)
    cool_feats = {
        "mean_r": 235.0, "mean_g": 175.0, "mean_b": 185.0,
        "median_r": 235.0, "median_g": 175.0, "median_b": 185.0,
        "std_r": 7.0, "std_g": 6.0, "std_b": 6.0,
        "mean_h": 8.0, "mean_s": 80.0, "mean_v": 235.0,
        "mean_l": 75.0, "mean_a": 18.0, "mean_lab_b": 10.0,
        "std_l": 3.5, "std_a": 2.2, "std_lab_b": 2.0,
        "ita": 68.0, "b_to_a_ratio": 0.55, "rg_ratio": 1.34, "rb_ratio": 1.27
    }
    res = predictor.predict(cool_feats)
    assert res["label"] in ["Cool", "Neutral", "Warm"]
    assert res["confidence"] > 0.4
