"""
Image Quality Assessment Module.
Analyzes resolution, blur, contrast, and exposure (under/over-exposure)
before proceeding with facial detection and color extraction.
Includes pure NumPy fallbacks for cross-platform zero-dependency operation.
"""

import numpy as np
from typing import Dict, Any, Tuple

try:
    import cv2
except Exception:
    cv2 = None

def analyze_image_quality(image_bgr: np.ndarray) -> Dict[str, Any]:
    """
    Evaluates image quality metrics:
    1. Resolution: Width, Height, Aspect Ratio
    2. Blur: Laplacian operator variance
    3. Brightness: Mean gray intensity & over/under-exposure clipping
    4. Contrast: Standard deviation of pixel intensities
    """
    if image_bgr is None or image_bgr.size == 0:
        return {
            "is_valid": False,
            "score": 0,
            "status": "Invalid",
            "message": "The uploaded file could not be decoded as a valid image.",
            "metrics": {}
        }

    h, w = image_bgr.shape[:2]
    
    # 1. Resolution Check
    min_dimension = 160
    is_res_ok = (h >= min_dimension and w >= min_dimension)
    
    # Grayscale conversion
    if cv2 is not None:
        try:
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        except Exception:
            gray = (0.114 * image_bgr[:, :, 0] + 0.587 * image_bgr[:, :, 1] + 0.299 * image_bgr[:, :, 2]).astype(np.float64)
            lap = gray[:-2, 1:-1] + gray[2:, 1:-1] + gray[1:-1, :-2] + gray[1:-1, 2:] - 4 * gray[1:-1, 1:-1]
            laplacian_var = float(np.var(lap))
    else:
        gray = (0.114 * image_bgr[:, :, 0] + 0.587 * image_bgr[:, :, 1] + 0.299 * image_bgr[:, :, 2]).astype(np.float64)
        lap = gray[:-2, 1:-1] + gray[2:, 1:-1] + gray[1:-1, :-2] + gray[1:-1, 2:] - 4 * gray[1:-1, 1:-1]
        laplacian_var = float(np.var(lap))
    
    # 3. Brightness & Exposure Check
    mean_brightness = float(np.mean(gray))
    under_exposed_ratio = float(np.sum(gray < 15) / gray.size)
    over_exposed_ratio = float(np.sum(gray > 245) / gray.size)
    
    # 4. Contrast Check
    contrast_std = float(np.std(gray))
    
    # Compute sub-scores (0 to 100)
    blur_score = min(100.0, (laplacian_var / 120.0) * 100.0)
    
    if 90 <= mean_brightness <= 170:
        bright_score = 100.0
    elif 60 <= mean_brightness < 90 or 170 < mean_brightness <= 200:
        bright_score = 75.0
    elif 40 <= mean_brightness < 60 or 200 < mean_brightness <= 225:
        bright_score = 45.0
    else:
        bright_score = 20.0
        
    contrast_score = min(100.0, (contrast_std / 45.0) * 100.0)
    exposure_penalty = (under_exposed_ratio * 120.0) + (over_exposed_ratio * 120.0)
    
    overall_score = max(0, int(round((0.35 * blur_score + 0.35 * bright_score + 0.30 * contrast_score) - exposure_penalty)))
    overall_score = min(100, overall_score)
    
    issues = []
    if not is_res_ok:
        issues.append(f"Image resolution ({w}x{h}) is too low (minimum {min_dimension}x{min_dimension} required).")
    if laplacian_var < 20.0:
        issues.append("Image appears blurry or out of focus.")
    if mean_brightness < 40.0 or under_exposed_ratio > 0.35:
        issues.append("Image is too dark or poorly lit.")
    if mean_brightness > 225.0 or over_exposed_ratio > 0.35:
        issues.append("Image is overexposed with harsh glare.")
    if contrast_std < 15.0:
        issues.append("Image lacks sufficient contrast.")
        
    if overall_score >= 65 and not issues:
        status = "Good"
        message = "Image quality is optimal for accurate color and undertone analysis."
        is_valid = True
    elif overall_score >= 40 and is_res_ok:
        status = "Acceptable"
        message = "Image quality is acceptable, though optimal natural lighting is recommended."
        is_valid = True
    else:
        status = "Poor"
        msg_details = " ".join(issues) if issues else "Lighting or focus is insufficient."
        message = f"Image quality note: {msg_details}"
        is_valid = False
        
    return {
        "is_valid": is_valid,
        "score": overall_score,
        "status": status,
        "message": message,
        "metrics": {
            "resolution": {"width": w, "height": h},
            "blur_metric": round(laplacian_var, 2),
            "brightness_mean": round(mean_brightness, 2),
            "contrast_std": round(contrast_std, 2),
            "underexposed_pct": round(under_exposed_ratio * 100.0, 1),
            "overexposed_pct": round(over_exposed_ratio * 100.0, 1)
        }
    }
