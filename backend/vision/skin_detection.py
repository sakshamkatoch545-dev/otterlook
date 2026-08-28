"""
Multi-Region Skin Extraction and Pixel Filtering Module.
Extracts skin patches from anatomical facial regions (forehead, left cheek,
right cheek, chin/jaw), filters non-skin artifacts, and removes statistical outliers.
Includes pure NumPy fallbacks for cross-platform zero-dependency operation.
"""

import numpy as np
from typing import Dict, Any, List, Tuple

try:
    import cv2
except Exception:
    cv2 = None

class SkinExtractor:
    def __init__(self):
        pass

    def extract_skin_pixels(self, image_bgr: np.ndarray, regions: Dict[str, Dict[str, int]]) -> Dict[str, Any]:
        """
        Samples and filters skin pixels across multiple facial regions.
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

            b = patch_bgr[:, :, 0].astype(np.float64)
            g = patch_bgr[:, :, 1].astype(np.float64)
            r = patch_bgr[:, :, 2].astype(np.float64)

            # YCrCb Skin Rule: Cr in [128, 178], Cb in [75, 135]
            y_plane = 0.299 * r + 0.587 * g + 0.114 * b
            cr_plane = (r - y_plane) * 0.713 + 128.0
            cb_plane = (b - y_plane) * 0.564 + 128.0
            ycrcb_mask = (cr_plane >= 125) & (cr_plane <= 180) & (cb_plane >= 70) & (cb_plane <= 140)

            # RGB Skin Rule: R > G > B and brightness check
            rgb_mask = (r > g) & (g > b) & (r > 40) & (r < 250)

            combined_mask = ycrcb_mask | rgb_mask

            candidate_pixels = patch_bgr[combined_mask]

            # If skin mask is too restrictive, fallback to center 60% of ROI
            if len(candidate_pixels) < 20:
                ch_h, ch_w = patch_bgr.shape[:2]
                center_crop = patch_bgr[int(ch_h * 0.2):int(ch_h * 0.8), int(ch_w * 0.2):int(ch_w * 0.8)]
                candidate_pixels = center_crop.reshape(-1, 3)

            if len(candidate_pixels) == 0:
                continue

            # Statistical Outlier Removal using IQR on Luminance & Channels
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
            "total_pixels": int(len(combined_pixels))
        }

    def _remove_outliers(self, pixels: np.ndarray) -> np.ndarray:
        """
        Removes noisy pixels (hair, glare, shadows) using Interquartile Range (IQR) on luminance.
        """
        if len(pixels) < 15:
            return pixels

        # Calculate luminance
        lum = 0.114 * pixels[:, 0] + 0.587 * pixels[:, 1] + 0.299 * pixels[:, 2]
        
        q25, q75 = np.percentile(lum, [25, 75])
        iqr = q75 - q25
        
        lower_bound = max(15.0, q25 - 1.5 * iqr)
        upper_bound = min(245.0, q75 + 1.5 * iqr)
        
        valid_mask = (lum >= lower_bound) & (lum <= upper_bound)
        filtered = pixels[valid_mask]
        
        return filtered if len(filtered) > 10 else pixels
