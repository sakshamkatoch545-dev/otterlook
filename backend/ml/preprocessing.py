"""
Feature Preprocessing and Vectorization for ML Inference.
"""

import numpy as np
from typing import Dict, List, Any

# Primary feature columns in exact order
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

def prepare_feature_array(features_dict: Dict[str, float]) -> np.ndarray:
    """
    Transforms a features dictionary into a 2D float32 numpy array [1, num_features]
    ready for model inference.
    """
    vector = []
    for col in FEATURE_COLUMNS:
        val = features_dict.get(col, 0.0)
        vector.append(float(val))
        
    return np.array([vector], dtype=np.float32)
