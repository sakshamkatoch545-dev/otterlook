"""
Color Feature Extraction Module.
Transforms filtered multi-region skin pixels into sRGB, HSV, and CIELAB color spaces.
Computes comprehensive statistical moments, colorimetric ratios, and ITA° phototype index.
"""

import cv2
import numpy as np
from typing import Dict, Any

class ColourFeatureExtractor:
    def __init__(self):
        pass

    def extract_features(self, pixels_bgr: np.ndarray) -> Dict[str, Any]:
        """
        Calculates colorimetric metrics from an array of skin pixels (shape: [N, 3] in BGR).
        
        Returns:
            Dict of statistical features formatted for ML inference and frontend display.
        """
        if pixels_bgr is None or len(pixels_bgr) == 0:
            raise ValueError("No valid skin pixels available for color feature extraction.")

        # Ensure correct shape for OpenCV cvtColor (1, N, 3)
        pixels_bgr_2d = pixels_bgr.reshape(1, -1, 3).astype(np.uint8)

        # Convert to RGB, HSV, and LAB
        pixels_rgb_2d = cv2.cvtColor(pixels_bgr_2d, cv2.COLOR_BGR2RGB)
        pixels_hsv_2d = cv2.cvtColor(pixels_bgr_2d, cv2.COLOR_BGR2HSV)
        pixels_lab_2d = cv2.cvtColor(pixels_bgr_2d, cv2.COLOR_BGR2LAB)

        rgb = pixels_rgb_2d[0].astype(np.float64)
        hsv = pixels_hsv_2d[0].astype(np.float64)
        lab = pixels_lab_2d[0].astype(np.float64)

        # Standard OpenCV LAB scaling: L in [0, 255] (scaled from 0-100), a in [0, 255] (offset by 128), b in [0, 255] (offset by 128)
        # Convert OpenCV LAB to standard CIELAB units:
        # L* = L_cv * 100.0 / 255.0
        # a* = a_cv - 128.0
        # b* = b_cv - 128.0
        lab_l = lab[:, 0] * (100.0 / 255.0)
        lab_a = lab[:, 1] - 128.0
        lab_b = lab[:, 2] - 128.0

        # --- 1. RGB Statistics ---
        mean_r, mean_g, mean_b = np.mean(rgb[:, 0]), np.mean(rgb[:, 1]), np.mean(rgb[:, 2])
        median_r, median_g, median_b = np.median(rgb[:, 0]), np.median(rgb[:, 1]), np.median(rgb[:, 2])
        std_r, std_g, std_b = np.std(rgb[:, 0]), np.std(rgb[:, 1]), np.std(rgb[:, 2])
        var_r, var_g, var_b = np.var(rgb[:, 0]), np.var(rgb[:, 1]), np.var(rgb[:, 2])

        # --- 2. HSV Statistics ---
        mean_h, mean_s, mean_v = np.mean(hsv[:, 0]), np.mean(hsv[:, 1]), np.mean(hsv[:, 2])
        median_h, median_s, median_v = np.median(hsv[:, 0]), np.median(hsv[:, 1]), np.median(hsv[:, 2])
        std_h, std_s, std_v = np.std(hsv[:, 0]), np.std(hsv[:, 1]), np.std(hsv[:, 2])

        # --- 3. CIELAB Statistics ---
        mean_l, mean_a, mean_lab_b = np.mean(lab_l), np.mean(lab_a), np.mean(lab_b)
        median_l, median_a, median_lab_b = np.median(lab_l), np.median(lab_a), np.median(lab_b)
        std_l, std_a, std_lab_b = np.std(lab_l), np.std(lab_a), np.std(lab_b)

        # --- 4. Color Science Derived Ratios ---
        # Individual Typology Angle (ITA°) = arctan((L* - 50) / b*) * 180 / pi
        safe_b = max(mean_lab_b, 0.1)
        ita = float(np.arctan((mean_l - 50.0) / safe_b) * 180.0 / np.pi)

        b_to_a_ratio = float(mean_lab_b / max(mean_a, 0.1))
        rg_ratio = float(mean_r / max(mean_g, 1.0))
        rb_ratio = float(mean_r / max(mean_b, 1.0))

        # Representative skin color hex
        rep_r = int(np.clip(mean_r, 0, 255))
        rep_g = int(np.clip(mean_g, 0, 255))
        rep_b = int(np.clip(mean_b, 0, 255))
        representative_hex = f"#{rep_r:02X}{rep_g:02X}{rep_b:02X}"

        # Phototype category based on ITA & L*
        if ita > 55:
            phototype_desc = "Very Light / Fair (Fitzpatrick I)"
        elif ita > 41:
            phototype_desc = "Light (Fitzpatrick II)"
        elif ita > 28:
            phototype_desc = "Intermediate / Medium (Fitzpatrick III)"
        elif ita > 10:
            phototype_desc = "Tan / Olive (Fitzpatrick IV)"
        elif ita > -30:
            phototype_desc = "Brown / Deep (Fitzpatrick V)"
        else:
            phototype_desc = "Dark / Rich (Fitzpatrick VI)"

        return {
            # Features dictionary for ML model
            "ml_features": {
                "mean_r": float(round(mean_r, 3)),
                "mean_g": float(round(mean_g, 3)),
                "mean_b": float(round(mean_b, 3)),
                "median_r": float(round(median_r, 3)),
                "median_g": float(round(median_g, 3)),
                "median_b": float(round(median_b, 3)),
                "std_r": float(round(std_r, 3)),
                "std_g": float(round(std_g, 3)),
                "std_b": float(round(std_b, 3)),
                "mean_h": float(round(mean_h, 3)),
                "mean_s": float(round(mean_s, 3)),
                "mean_v": float(round(mean_v, 3)),
                "mean_l": float(round(mean_l, 3)),
                "mean_a": float(round(mean_a, 3)),
                "mean_lab_b": float(round(mean_lab_b, 3)),
                "std_l": float(round(std_l, 3)),
                "std_a": float(round(std_a, 3)),
                "std_lab_b": float(round(std_lab_b, 3)),
                "ita": float(round(ita, 3)),
                "b_to_a_ratio": float(round(b_to_a_ratio, 4)),
                "rg_ratio": float(round(rg_ratio, 4)),
                "rb_ratio": float(round(rb_ratio, 4))
            },
            # Display metrics for UI
            "display_metrics": {
                "representative_hex": representative_hex,
                "representative_rgb": [rep_r, rep_g, rep_b],
                "cielab": {
                    "L": round(mean_l, 1),
                    "a": round(mean_a, 1),
                    "b": round(mean_lab_b, 1),
                    "std_L": round(std_l, 2),
                    "std_a": round(std_a, 2),
                    "std_b": round(std_lab_b, 2)
                },
                "hsv": {
                    "H_deg": round(mean_h * 2.0, 1), # convert 0-180 to 0-360 degrees
                    "S_pct": round((mean_s / 255.0) * 100.0, 1),
                    "V_pct": round((mean_v / 255.0) * 100.0, 1)
                },
                "rgb": {
                    "R": round(mean_r, 1),
                    "G": round(mean_g, 1),
                    "B": round(mean_b, 1),
                    "variance": [round(var_r, 1), round(var_g, 1), round(var_b, 1)]
                },
                "ita_angle": round(ita, 1),
                "phototype_estimate": phototype_desc,
                "yellow_red_balance": round(b_to_a_ratio, 2)
            }
        }
