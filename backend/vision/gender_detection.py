"""
Facial Gender Detection Module.
Uses OpenCV DNN with gender_googlenet.onnx (Levi & Hassner / ONNX Model Zoo)
for fast, serverless-compatible male/female classification when "All Styles"
auto-detection is selected.
"""

import logging
import os
import urllib.request
from typing import Any, Dict, List, Optional

import cv2
import numpy as np

logger = logging.getLogger("otterlook.gender")

_GENDER_MODEL_URL = (
    "https://huggingface.co/onnxmodelzoo/gender_googlenet/resolve/main/gender_googlenet.onnx"
)
_GENDER_LABELS = ("male", "female")


class GenderDetector:
    """Lightweight OpenCV DNN gender classifier for cropped face regions."""

    def __init__(self) -> None:
        self.net = None
        self._load_attempted = False

    def _ensure_model(self) -> None:
        if self.net is not None or self._load_attempted:
            return
        self._load_attempted = True

        models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
        local_path = os.path.join(models_dir, "gender_googlenet.onnx")
        tmp_path = os.path.join("/tmp", "gender_googlenet.onnx")

        model_path: Optional[str] = None
        if os.path.exists(local_path):
            model_path = local_path
        elif os.path.exists(tmp_path):
            model_path = tmp_path
        else:
            target = local_path if os.access(models_dir, os.W_OK) else tmp_path
            try:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                urllib.request.urlretrieve(_GENDER_MODEL_URL, target)
                if os.path.exists(target):
                    model_path = target
            except Exception as exc:
                logger.warning("Could not download gender_googlenet.onnx: %s", exc)

        if model_path:
            try:
                self.net = cv2.dnn.readNetFromONNX(model_path)
            except Exception as exc:
                logger.warning("Failed to load gender_googlenet.onnx: %s", exc)
                self.net = None

    @staticmethod
    def _crop_face_with_padding(
        image_bgr: np.ndarray,
        bbox: Optional[List[int]],
        pad_ratio: float = 0.28,
    ) -> np.ndarray:
        h_img, w_img = image_bgr.shape[:2]
        if not bbox or len(bbox) < 4:
            return image_bgr

        x, y, w, h = [int(v) for v in bbox[:4]]
        if w <= 0 or h <= 0:
            return image_bgr

        pad_x = int(w * pad_ratio)
        pad_y = int(h * pad_ratio)
        x1 = max(0, x - pad_x)
        y1 = max(0, y - pad_y)
        x2 = min(w_img, x + w + pad_x)
        y2 = min(h_img, y + h + pad_y)
        crop = image_bgr[y1:y2, x1:x2]
        return crop if crop.size > 0 else image_bgr

    def detect_gender(
        self,
        image_bgr: np.ndarray,
        bbox: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """Classify face as 'male' or 'female' with confidence metadata."""
        self._ensure_model()

        if self.net is None or image_bgr is None or image_bgr.size == 0:
            return {
                "gender": "female",
                "label": "Women's Style",
                "confidence": 0.5,
                "confidence_percentage": 50.0,
                "auto_detected": False,
            }

        try:
            face_crop = self._crop_face_with_padding(image_bgr, bbox)
            blob = cv2.dnn.blobFromImage(
                face_crop,
                scalefactor=1.0,
                size=(224, 224),
                mean=(104.0, 117.0, 123.0),
                swapRB=False,
                crop=False,
            )
            self.net.setInput(blob)
            preds = self.net.forward().flatten()

            if preds.size >= 2:
                # Ensure valid probabilities even if logits are returned
                if np.any(preds < 0) or not np.isclose(np.sum(preds[:2]), 1.0, atol=0.05):
                    exp_p = np.exp(preds[:2] - np.max(preds[:2]))
                    probs = exp_p / np.sum(exp_p)
                else:
                    probs = preds[:2]

                idx = int(np.argmax(probs))
                detected = _GENDER_LABELS[idx]
                conf = float(probs[idx])
                return {
                    "gender": detected,
                    "label": "Women's Style" if detected == "female" else "Men's Style",
                    "confidence": round(conf, 4),
                    "confidence_percentage": round(conf * 100.0, 1),
                    "auto_detected": True,
                }
        except Exception as exc:
            logger.warning("Gender detection inference failed: %s", exc)

        return {
            "gender": "female",
            "label": "Women's Style",
            "confidence": 0.5,
            "confidence_percentage": 50.0,
            "auto_detected": False,
        }
