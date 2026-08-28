"""
Feature Engineering & Transformation Pipeline for Skin Undertone Analysis.
Author: AI Personal Colour Analysis System
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any

# Primary feature columns expected by the ML model in deterministic order
FEATURE_COLUMNS: List[str] = [
    "mean_r",
    "mean_g",
    "mean_b",
    "median_r",
    "median_g",
    "median_b",
    "std_r",
    "std_g",
    "std_b",
    "mean_h",
    "mean_s",
    "mean_v",
    "mean_l",
    "mean_a",
    "mean_lab_b",
    "std_l",
    "std_a",
    "std_lab_b",
    "ita",
    "b_to_a_ratio",
    "rg_ratio",
    "rb_ratio"
]

def calculate_derived_features(features: Dict[str, float]) -> Dict[str, float]:
    """
    Computes mathematical & colorimetric ratios from raw channel statistics.
    """
    feat = dict(features)
    
    mean_l = feat.get("mean_l", 60.0)
    mean_a = feat.get("mean_a", 15.0)
    mean_lab_b = feat.get("mean_lab_b", 15.0)
    
    mean_r = feat.get("mean_r", 150.0)
    mean_g = feat.get("mean_g", 120.0)
    mean_b = feat.get("mean_b", 100.0)
    
    # Individual Typology Angle (ITA) = arctan((L* - 50) / b*) * 180 / pi
    safe_b = max(mean_lab_b, 0.1)
    if "ita" not in feat:
        feat["ita"] = float(np.arctan((mean_l - 50.0) / safe_b) * 180.0 / np.pi)
        
    if "b_to_a_ratio" not in feat:
        feat["b_to_a_ratio"] = float(mean_lab_b / max(mean_a, 0.1))
        
    if "rg_ratio" not in feat:
        feat["rg_ratio"] = float(mean_r / max(mean_g, 1.0))
        
    if "rb_ratio" not in feat:
        feat["rb_ratio"] = float(mean_r / max(mean_b, 1.0))
        
    return feat

def extract_feature_vector(features: Dict[str, float]) -> np.ndarray:
    """
    Converts a feature dictionary to a 1D numpy array aligned with FEATURE_COLUMNS.
    """
    enriched = calculate_derived_features(features)
    vector = [enriched.get(col, 0.0) for col in FEATURE_COLUMNS]
    return np.array(vector, dtype=np.float32)
