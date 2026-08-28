"""
Image Quality Assessment Module.
Analyzes resolution, blur, contrast, and exposure (under/over-exposure)
before proceeding with facial detection and color extraction.
"""

import cv2
import numpy as np
from typing import Dict, Any, Tuple

def analyze_image_quality(image_bgr: np.ndarray) -> Dict[str, Any]:
    """
    Evaluates image quality metrics:
    1. Resolution: Width, Height, Aspect Ratio
    2. Blur: Laplacian operator variance
    3. Brightness: Mean gray intensity & over/under-exposure clipping
    4. Contrast: Standard deviation of pixel intensities
    
    Returns:
        Dict containing quality score (0-100), validity flag, status, and diagnostic messages.
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
    
    # 2. Blur Check using Laplacian Variance
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    
    # 3. Brightness & Exposure Check
    mean_brightness = float(np.mean(gray))
    
    # Check percentage of severely underexposed (< 15) and overexposed (> 245) pixels
    under_exposed_ratio = float(np.sum(gray < 15) / gray.size)
    over_exposed_ratio = float(np.sum(gray > 245) / gray.size)
    
    # 4. Contrast Check
    contrast_std = float(np.std(gray))
    
    # Compute sub-scores (0 to 100)
    # Blur score
    blur_score = min(100.0, (laplacian_var / 120.0) * 100.0)
    
    # Brightness score (ideal around 90-170)
    if 90 <= mean_brightness <= 170:
        bright_score = 100.0
    elif 60 <= mean_brightness < 90 or 170 < mean_brightness <= 200:
        bright_score = 75.0
    elif 40 <= mean_brightness < 60 or 200 < mean_brightness <= 225:
        bright_score = 45.0
    else:
        bright_score = 20.0
        
    # Contrast score (ideal std > 35)
    contrast_score = min(100.0, (contrast_std / 45.0) * 100.0)
    
    # Exposure penalty
    exposure_penalty = (under_exposed_ratio * 120.0) + (over_exposed_ratio * 120.0)
    
    overall_score = max(0, int(round((0.35 * blur_score + 0.35 * bright_score + 0.30 * contrast_score) - exposure_penalty)))
    overall_score = min(100, overall_score)
    
    issues = []
    if not is_res_ok:
        issues.append(f"Image resolution ({w}x{h}) is too low (minimum {min_dimension}x{min_dimension} required).")
    if laplacian_var < 35.0:
        issues.append("Image appears significantly blurry or out of focus.")
    if mean_brightness < 45.0 or under_exposed_ratio > 0.30:
        issues.append("Image is too dark or poorly lit.")
    if mean_brightness > 220.0 or over_exposed_ratio > 0.30:
        issues.append("Image is overexposed with harsh glare or blowout.")
    if contrast_std < 18.0:
        issues.append("Image lacks sufficient contrast.")
        
    if overall_score >= 70 and not issues:
        status = "Good"
        message = "Image quality is optimal for accurate color and undertone analysis."
        is_valid = True
    elif overall_score >= 45 and is_res_ok:
        status = "Acceptable"
        message = "Image quality is acceptable, though optimal natural lighting is recommended."
        is_valid = True
    else:
        status = "Poor"
        msg_details = " ".join(issues) if issues else "Lighting or focus is insufficient."
        message = f"Image quality is too low for reliable colour analysis: {msg_details} Please upload a clearer, well-lit front-facing portrait."
        is_valid = False
        
    return {
        "is_valid": is_valid,
        "score": overall_score,
        "status": status,
        "message": message,
        "metrics": {
            "resolution": f"{w}x{h}",
            "width": w,
            "height": h,
            "blur_variance": round(laplacian_var, 2),
            "mean_brightness": round(mean_brightness, 2),
            "contrast_std": round(contrast_std, 2),
            "underexposed_ratio": round(under_exposed_ratio, 4),
            "overexposed_ratio": round(over_exposed_ratio, 4)
        }
    }
