"""
Unit tests for image quality assessment module.
"""

import cv2
import numpy as np
import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.utils.image_quality import analyze_image_quality

def test_valid_sharp_image():
    # Create a sharp, well-lit test image
    img = np.random.randint(80, 200, (400, 400, 3), dtype=np.uint8)
    cv2.circle(img, (200, 200), 100, (220, 180, 140), -1)
    result = analyze_image_quality(img)
    assert result["is_valid"] is True
    assert result["score"] >= 45
    assert result["status"] in ["Good", "Acceptable"]

def test_too_small_resolution():
    small_img = np.full((100, 100, 3), 128, dtype=np.uint8)
    result = analyze_image_quality(small_img)
    assert result["is_valid"] is False
    assert "resolution" in result["message"].lower()

def test_extreme_darkness():
    dark_img = np.full((300, 300, 3), 8, dtype=np.uint8)
    result = analyze_image_quality(dark_img)
    assert result["is_valid"] is False
    assert result["status"] == "Poor"

def test_extreme_brightness():
    bright_img = np.full((300, 300, 3), 252, dtype=np.uint8)
    result = analyze_image_quality(bright_img)
    assert result["is_valid"] is False
    assert result["status"] == "Poor"


def test_face_scoped_quality_ignores_dark_background():
    """Verify bbox scoping evaluates lighting on the face region rather than a dark background."""
    img = np.full((400, 400, 3), 5, dtype=np.uint8)  # pitch-black background
    # Well-lit textured face patch in center [120, 120, 160, 160]
    face_patch = np.random.randint(95, 195, (160, 160, 3), dtype=np.uint8)
    img[120:280, 120:280] = face_patch

    full_res = analyze_image_quality(img)
    scoped_res = analyze_image_quality(img, bbox=[120, 120, 160, 160])

    assert full_res["is_valid"] is False
    assert scoped_res["is_valid"] is True
    assert scoped_res["status"] in ["Good", "Acceptable"]
