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

            # Multi-Space Human Skin Rule: YCbCr & RGB & Saturation
            y_plane = 0.299 * r + 0.587 * g + 0.114 * b
            cr_plane = (r - y_plane) * 0.713 + 128.0
            cb_plane = (b - y_plane) * 0.564 + 128.0
            ycrcb_mask = (cr_plane >= 130) & (cr_plane <= 178) & (cb_plane >= 75) & (cb_plane <= 135) & ((cr_plane - cb_plane) >= 8)

            rgb_mask = (r > g) & (g > b) & (r > 50) & (g > 30) & (b > 18) & ((r - g) >= 6) & ((r - b) >= 10)

            cmax = np.maximum(np.maximum(r, g), b)
            cmin = np.minimum(np.minimum(r, g), b)
            sat = np.where(cmax > 0, (cmax - cmin) / np.maximum(cmax, 1e-6), 0)
            sat_mask = (sat >= 0.14) & (sat <= 0.72)

            combined_mask = ycrcb_mask & rgb_mask & sat_mask

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

        if len(combined_pixels) < 30:
            auto_res = self.extract_skin_pixels_autonomous(image_bgr)
            if auto_res["total_pixels"] > len(combined_pixels):
                return auto_res

        return {
            "pixels_bgr": combined_pixels,
            "region_samples": region_details,
            "total_pixels": int(len(combined_pixels))
        }

    def extract_skin_pixels_autonomous(self, image_bgr: np.ndarray, bbox: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Autonomously extracts skin pixels across the full image / face region.
        """
        if image_bgr is None or image_bgr.size == 0:
            return {"pixels_bgr": np.empty((0, 3), dtype=np.uint8), "region_samples": {}, "total_pixels": 0}

        img_h, img_w = image_bgr.shape[:2]
        
        if bbox is not None and len(bbox) == 4:
            bx, by, bw, bh = bbox
            x1 = max(0, int(bx - bw * 0.1))
            y1 = max(0, int(by - bh * 0.1))
            x2 = min(img_w, int(bx + bw * 1.1))
            y2 = min(img_h, int(by + bh * 1.1))
            roi = image_bgr[y1:y2, x1:x2]
        else:
            roi = image_bgr

        b = roi[:, :, 0].astype(np.float64)
        g = roi[:, :, 1].astype(np.float64)
        r = roi[:, :, 2].astype(np.float64)

        # YCrCb Skin Rule with strict Wood/Background discrimination
        y_plane = 0.299 * r + 0.587 * g + 0.114 * b
        cr_plane = (r - y_plane) * 0.713 + 128.0
        cb_plane = (b - y_plane) * 0.564 + 128.0
        ycrcb_mask = (cr_plane >= 133) & (cr_plane <= 175) & (cb_plane >= 80) & (cb_plane <= 130) & ((cr_plane - cb_plane) >= 12)

        # RGB & Saturation Skin Rule
        rgb_mask = (r > g) & (g > b) & (r > 70) & (g > 45) & (b > 30) & ((r - g) >= 10) & ((r - b) >= 16)
        
        cmax = np.maximum(np.maximum(r, g), b)
        cmin = np.minimum(np.minimum(r, g), b)
        sat = np.where(cmax > 0, (cmax - cmin) / np.maximum(cmax, 1e-6), 0)
        sat_mask = (sat >= 0.16) & (sat <= 0.68)

        combined_mask = ycrcb_mask & rgb_mask & sat_mask

        candidate_pixels = roi[combined_mask]
        clean_pixels = self._remove_outliers(candidate_pixels)

        if len(clean_pixels) == 0:
            clean_pixels = np.empty((0, 3), dtype=np.uint8)

        mean_bgr = np.mean(clean_pixels, axis=0) if len(clean_pixels) > 0 else np.array([128, 128, 128])
        mean_rgb = [int(mean_bgr[2]), int(mean_bgr[1]), int(mean_bgr[0])]
        hex_code = f"#{mean_rgb[0]:02X}{mean_rgb[1]:02X}{mean_rgb[2]:02X}"

        return {
            "pixels_bgr": clean_pixels,
            "region_samples": {
                "autonomous_skin": {
                    "box": {"x": 0, "y": 0, "w": img_w, "h": img_h},
                    "pixel_count": len(clean_pixels),
                    "mean_rgb": mean_rgb,
                    "hex": hex_code
                }
            },
            "total_pixels": int(len(clean_pixels))
        }

    def _remove_outliers(self, pixels: np.ndarray) -> np.ndarray:
        """
        Removes noisy pixels (hair, glare, shadows) using luminance percentile filtering.
        """
        if len(pixels) < 15:
            return pixels

        # Calculate luminance (Y in sRGB)
        lum = 0.114 * pixels[:, 0].astype(np.float64) + 0.587 * pixels[:, 1].astype(np.float64) + 0.299 * pixels[:, 2].astype(np.float64)
        
        # Discard dark hair / deep cast shadows (lum < 55) and extreme glares (lum > 250)
        valid_lum_mask = (lum >= 55.0) & (lum <= 250.0)
        valid_pixels = pixels[valid_lum_mask]
        if len(valid_pixels) < 10:
            valid_pixels = pixels
        
        lum_valid = 0.114 * valid_pixels[:, 0].astype(np.float64) + 0.587 * valid_pixels[:, 1].astype(np.float64) + 0.299 * valid_pixels[:, 2].astype(np.float64)
        
        # Core Dermal Centroid: Keep 25th to 85th percentiles of valid luminance
        p25 = np.percentile(lum_valid, 25)
        p85 = np.percentile(lum_valid, 85)
        
        core_mask = (lum_valid >= p25) & (lum_valid <= p85)
        filtered = valid_pixels[core_mask]
        
        return filtered if len(filtered) > 10 else valid_pixels
