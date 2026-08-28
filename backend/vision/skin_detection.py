"""
Multi-Region Skin Extraction and Pixel Filtering Module.
Extracts skin patches from anatomical facial regions (forehead, left cheek,
right cheek, chin/jaw), filters non-skin artifacts, and removes statistical outliers.
"""

import cv2
import numpy as np
from typing import Dict, Any, List, Tuple

class SkinExtractor:
    def __init__(self):
        pass

    def extract_skin_pixels(self, image_bgr: np.ndarray, regions: Dict[str, Dict[str, int]]) -> Dict[str, Any]:
        """
        Samples and filters skin pixels across multiple facial regions.
        
        Returns:
            Dict containing:
                - pixels_bgr: np.ndarray of shape (N, 3) representing clean sampled skin pixels
                - region_samples: dict with per-region metrics, pixel count, and representative hex color
                - total_pixels: int
        """
        if image_bgr is None or not regions:
            return {
                "pixels_bgr": np.empty((0, 3), dtype=np.uint8),
                "region_samples": {},
                "total_pixels": 0
            }

        img_h, img_w = image_bgr.shape[:2]
        all_clean_pixels = []
        region_details = {}

        for reg_name, box in regions.items():
            x, y, w, h = box["x"], box["y"], box["w"], box["h"]
            
            # Boundary checks
            x1 = max(0, min(x, img_w - 1))
            y1 = max(0, min(y, img_h - 1))
            x2 = max(x1 + 1, min(x + w, img_w))
            y2 = max(y1 + 1, min(y + h, img_h))

            patch_bgr = image_bgr[y1:y2, x1:x2]
            if patch_bgr.size == 0:
                continue

            # Convert patch to HSV and YCrCb for skin segmentation
            patch_hsv = cv2.cvtColor(patch_bgr, cv2.COLOR_BGR2HSV)
            patch_ycrcb = cv2.cvtColor(patch_bgr, cv2.COLOR_BGR2YCrCb)

            # 1. YCrCb Skin Rule: Cr in [130, 175], Cb in [75, 130]
            cr = patch_ycrcb[:, :, 1]
            cb = patch_ycrcb[:, :, 2]
            ycrcb_mask = (cr >= 128) & (cr <= 178) & (cb >= 75) & (cb <= 135)

            # 2. HSV Skin Rule: Hue in [0, 45], Saturation in [20, 210], Value in [35, 250]
            hue = patch_hsv[:, :, 0]
            sat = patch_hsv[:, :, 1]
            val = patch_hsv[:, :, 2]
            hsv_mask = (hue <= 40) & (sat >= 18) & (sat <= 220) & (val >= 30) & (val <= 248)

            combined_mask = ycrcb_mask & hsv_mask

            # Candidate pixels
            candidate_pixels = patch_bgr[combined_mask]

            # If skin mask is too restrictive (e.g. unique lighting), fallback to center 60% of ROI
            if len(candidate_pixels) < 25:
                ch_h, ch_w = patch_bgr.shape[:2]
                center_crop = patch_bgr[int(ch_h*0.2):int(ch_h*0.8), int(ch_w*0.2):int(ch_w*0.8)]
                candidate_pixels = center_crop.reshape(-1, 3)

            if len(candidate_pixels) == 0:
                continue

            # 3. Statistical Outlier Removal using IQR on Luminance & Channels
            clean_patch_pixels = self._remove_outliers(candidate_pixels)
            
            if len(clean_patch_pixels) > 0:
                all_clean_pixels.append(clean_patch_pixels)
                mean_bgr = np.mean(clean_patch_pixels, axis=0)
                mean_rgb = [int(mean_bgr[2]), int(mean_bgr[1]), int(mean_bgr[0])]
                hex_code = f"#{mean_rgb[0]:02X}{mean_rgb[1]:02X}{mean_rgb[2]:02X}"
                
                region_details[reg_name] = {
                    "box": {"x": x1, "y": y1, "w": x2 - x1, "h": y2 - y1},
                    "pixel_count": len(clean_patch_pixels),
                    "mean_rgb": mean_rgb,
                    "hex": hex_code
                }

        if all_clean_pixels:
            combined_pixels = np.vstack(all_clean_pixels)
        else:
            combined_pixels = np.empty((0, 3), dtype=np.uint8)

        return {
            "pixels_bgr": combined_pixels,
            "region_samples": region_details,
            "total_pixels": len(combined_pixels)
        }

    def _remove_outliers(self, pixels_bgr: np.ndarray) -> np.ndarray:
        """
        Removes specular reflections, heavy shadows, and stray hair pixels
        using IQR (Interquartile Range) filtering across RGB channels.
        """
        if len(pixels_bgr) < 8:
            return pixels_bgr

        # Luminance proxy
        lum = 0.299 * pixels_bgr[:, 2] + 0.587 * pixels_bgr[:, 1] + 0.114 * pixels_bgr[:, 0]
        
        q25 = np.percentile(lum, 20)
        q75 = np.percentile(lum, 80)
        iqr = q75 - q25
        lower_bound = max(15.0, q25 - 1.2 * iqr)
        upper_bound = min(245.0, q75 + 1.2 * iqr)

        valid_mask = (lum >= lower_bound) & (lum <= upper_bound)
        filtered = pixels_bgr[valid_mask]

        return filtered if len(filtered) > 5 else pixels_bgr
