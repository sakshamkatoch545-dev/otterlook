"""
Unit tests for face detection, skin extraction, and colour feature extraction.
"""

import os
import sys
import cv2
import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from vision.face_detection import FaceDetector
from vision.skin_detection import SkinExtractor
from vision.colour_extraction import ColourFeatureExtractor
from generate_test_images import create_synthetic_portrait

@pytest.fixture
def face_detector():
    return FaceDetector()

@pytest.fixture
def skin_extractor():
    return SkinExtractor()

@pytest.fixture
def feature_extractor():
    return ColourFeatureExtractor()

def test_face_detection_on_portrait(face_detector):
    portrait = create_synthetic_portrait("Warm")
    result = face_detector.detect_faces(portrait)
    assert result["success"] is True
    assert result["face_count"] == 1
    assert "forehead" in result["regions"]
    assert "left_cheek" in result["regions"]
    assert "right_cheek" in result["regions"]
    assert "chin" in result["regions"]

def test_skin_extraction_on_regions(face_detector, skin_extractor):
    portrait = create_synthetic_portrait("Warm")
    face_res = face_detector.detect_faces(portrait)
    skin_res = skin_extractor.extract_skin_pixels(portrait, face_res["regions"])
    
    assert skin_res["total_pixels"] > 50
    assert len(skin_res["pixels_bgr"]) > 50
    assert "left_cheek" in skin_res["region_samples"]

def test_colour_feature_extraction(feature_extractor):
    # Mock skin pixels (BGR format: e.g. Warm peach)
    pixels = np.array([
        [140, 180, 230],
        [145, 185, 235],
        [142, 182, 232]
    ], dtype=np.uint8)
    
    features = feature_extractor.extract_features(pixels)
    ml_feats = features["ml_features"]
    
    assert "mean_r" in ml_feats
    assert "mean_lab_b" in ml_feats
    assert "mean_h" in ml_feats
    assert "ita" in ml_feats
    assert ml_feats["mean_r"] > 200
    assert "representative_hex" in features["display_metrics"]
