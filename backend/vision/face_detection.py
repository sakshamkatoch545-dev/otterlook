"""
Face Detection and Facial Landmark Localization Module.
Powered by a 4-engine cascade: MediaPipe (most robust for selfies), 
YOLOv8-Face (deep SOTA), OpenCV YuNet (neural), and Haar Cascade (fallback).
Ensures that if no face is detected, no output or false positives are generated.
"""

import os
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple


def _preprocess_for_detection(image_bgr: np.ndarray) -> np.ndarray:
    """
    Apply CLAHE contrast enhancement to improve face detection on
    dim, overexposed, or low-contrast images. Returns a processed BGR copy.
    """
    try:
        lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_eq = clahe.apply(l)
        lab_eq = cv2.merge([l_eq, a, b])
        return cv2.cvtColor(lab_eq, cv2.COLOR_LAB2BGR)
    except Exception:
        return image_bgr


class FaceDetector:
    def __init__(self):
        self.yolo_detector = None
        self.yunet_detector = None
        self.mediapipe_detector = None
        self.facemark = None
        self.haar_cascade = None
        self._init_detectors()

    def _init_detectors(self):
        models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
        os.makedirs(models_dir, exist_ok=True)

        # 1. MediaPipe Tasks Face Detection (mediapipe >= 0.10 / 1.x API)
        try:
            from mediapipe.tasks.python import BaseOptions
            from mediapipe.tasks.python.vision import FaceDetector as MpFaceDetector, FaceDetectorOptions
            import urllib.request

            mp_model_path = os.path.join(models_dir, "blaze_face_short_range.tflite")
            if not os.path.exists(mp_model_path):
                url = (
                    "https://storage.googleapis.com/mediapipe-models/"
                    "face_detector/blaze_face_short_range/float16/1/"
                    "blaze_face_short_range.tflite"
                )
                try:
                    urllib.request.urlretrieve(url, mp_model_path)
                except Exception:
                    mp_model_path = None

            if mp_model_path and os.path.exists(mp_model_path):
                mp_opts = FaceDetectorOptions(
                    base_options=BaseOptions(model_asset_path=mp_model_path),
                    min_detection_confidence=0.30,
                )
                self.mediapipe_detector = MpFaceDetector.create_from_options(mp_opts)
            else:
                self.mediapipe_detector = None
        except Exception:
            self.mediapipe_detector = None

        # 2. YOLOv8-Face (Deep neural SOTA face detector)
        yolo_path = os.path.join(models_dir, "yolov8n-face.pt")
        if os.path.exists(yolo_path):
            try:
                from ultralytics import YOLO
                self.yolo_detector = YOLO(yolo_path)
            except Exception:
                self.yolo_detector = None

        # 3. OpenCV YuNet Neural Engine (secondary)
        yunet_path = os.path.join(models_dir, "face_detection_yunet_2023mar.onnx")
        if not os.path.exists(yunet_path):
            try:
                import urllib.request
                url = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
                urllib.request.urlretrieve(url, yunet_path)
            except Exception:
                pass

        if os.path.exists(yunet_path) and hasattr(cv2, "FaceDetectorYN"):
            try:
                self.yunet_detector = cv2.FaceDetectorYN.create(
                    model=yunet_path,
                    config="",
                    input_size=(320, 320),
                    score_threshold=0.30,   # Lowered from 0.50 for better recall
                    nms_threshold=0.3,
                    top_k=5000
                )
            except Exception:
                self.yunet_detector = None

        # 4. FacemarkLBF 68-Point Landmark Model
        lbf_path = os.path.join(models_dir, "lbfmodel.yaml")
        if os.path.exists(lbf_path) and hasattr(cv2, "face") and hasattr(cv2.face, "createFacemarkLBF"):
            try:
                self.facemark = cv2.face.createFacemarkLBF()
                self.facemark.loadModel(lbf_path)
            except Exception:
                self.facemark = None

        # 5. Fallback Haar Cascade
        cascade_path = os.path.join(models_dir, "haarcascade_frontalface_default.xml")
        if not os.path.exists(cascade_path) and hasattr(cv2, "data") and hasattr(cv2.data, "haarcascades"):
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        if os.path.exists(cascade_path):
            try:
                self.haar_cascade = cv2.CascadeClassifier(cascade_path)
            except Exception:
                self.haar_cascade = None

    def _extract_landmarks_lbf(self, image_bgr: np.ndarray, bbox: List[int]) -> Optional[List[Tuple[int, int, float]]]:
        """Extracts 68 facial landmarks using FacemarkLBF if available."""
        if self.facemark is None:
            return None
        try:
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            face_rect = np.array([[bbox[0], bbox[1], bbox[2], bbox[3]]], dtype=np.int32)
            ok, lms = self.facemark.fit(gray, face_rect)
            if ok and len(lms) > 0 and len(lms[0]) == 68:
                pts = lms[0].reshape(68, 2)
                return [(int(p[0]), int(p[1]), 0.0) for p in pts]
        except Exception:
            pass
        return None

    def _pick_best_face_bbox(self, candidates: List[Dict], img_w: int, img_h: int) -> Optional[Dict]:
        """Score candidates by: largest area × confidence × centrality, return best."""
        if not candidates:
            return None
        center_x, center_y = img_w / 2.0, img_h / 2.0
        best, best_score = None, -1.0
        for c in candidates:
            x, y, w, h = c["x"], c["y"], c["w"], c["h"]
            area = max(1, w * h)
            conf = c.get("conf", 0.75)
            cx, cy = x + w / 2.0, y + h / 2.0
            dist = (((cx - center_x) / img_w) ** 2 + ((cy - center_y) / img_h) ** 2) ** 0.5
            centrality = max(0.4, 1.0 - dist)
            score = (area ** 0.75) * conf * centrality
            if score > best_score:
                best_score = score
                best = c
        return best

    def _make_result(self, bbox, landmarks, regions, conf, detector_type, img_w, img_h):
        return {
            "success": True,
            "face_count": 1,
            "message": f"Face localized via {detector_type}.",
            "detector_type": detector_type,
            "confidence": conf,
            "landmarks": landmarks,
            "bounding_box": bbox,
            "regions": regions,
        }

    def detect_faces(self, image_bgr: np.ndarray) -> Dict[str, Any]:
        """
        Detects faces using a 4-engine cascade (MediaPipe → YOLO → YuNet → Haar).
        Each engine is tried on both the raw image and a CLAHE-enhanced version.
        Returns the single best face candidate, or success=False if none found.
        """
        if image_bgr is None or image_bgr.size == 0:
            return {
                "success": False, "face_count": 0,
                "message": "Empty or invalid image.",
                "landmarks": None, "bounding_box": None, "regions": {}
            }

        img_h, img_w = image_bgr.shape[:2]
        # Prepare CLAHE-enhanced version for difficult images
        enhanced = _preprocess_for_detection(image_bgr)
        images_to_try = [image_bgr, enhanced]

        # ── Engine 1: MediaPipe ──────────────────────────────────────────────
        if self.mediapipe_detector is not None:
            try:
                import mediapipe as mp
                for img_candidate in images_to_try:
                    img_rgb = cv2.cvtColor(img_candidate, cv2.COLOR_BGR2RGB)
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
                    mp_result = self.mediapipe_detector.detect(mp_image)
                    if mp_result.detections:
                        candidates = []
                        for det in mp_result.detections:
                            bb = det.bounding_box
                            x = max(0, bb.origin_x)
                            y = max(0, bb.origin_y)
                            w = max(10, min(bb.width, img_w - x))
                            h = max(10, min(bb.height, img_h - y))
                            conf = det.categories[0].score if det.categories else 0.6
                            candidates.append({"x": x, "y": y, "w": w, "h": h, "conf": float(conf)})
                        best = self._pick_best_face_bbox(candidates, img_w, img_h)
                        if best:
                            bbox = [best["x"], best["y"], best["w"], best["h"]]
                            landmarks = self._extract_landmarks_lbf(image_bgr, bbox)
                            regions = (self._get_regions_from_68_landmarks(landmarks, bbox, img_w, img_h)
                                       if landmarks else self._get_regions_from_bbox(bbox, img_w, img_h))
                            return self._make_result(bbox, landmarks, regions, best["conf"], "mediapipe", img_w, img_h)
            except Exception:
                pass

        # ── Engine 2: YOLO (multi-scale) ────────────────────────────────────
        if self.yolo_detector is not None:
            try:
                # Try multiple confidence thresholds and both raw + enhanced
                conf_thresholds = [0.35, 0.22, 0.12]
                scales = [1.0]
                # Also try rescaled versions if image is very large or very small
                shorter_side = min(img_w, img_h)
                if shorter_side > 800:
                    scales.append(640 / shorter_side)
                if shorter_side < 300:
                    scales.append(480 / shorter_side)

                for img_candidate in images_to_try:
                    for scale in scales:
                        if abs(scale - 1.0) > 0.05:
                            new_w = int(img_w * scale)
                            new_h = int(img_h * scale)
                            proc = cv2.resize(img_candidate, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
                        else:
                            proc = img_candidate
                            new_w, new_h = img_w, img_h

                        for conf_thresh in conf_thresholds:
                            results = self.yolo_detector(proc, conf=conf_thresh, verbose=False)
                            boxes = results[0].boxes if len(results) > 0 else None
                            if boxes is not None and len(boxes) > 0:
                                candidates = []
                                for b in boxes:
                                    x1, y1, x2, y2 = map(int, b.xyxy[0].tolist())
                                    # Rescale back to original image coords
                                    x1 = int(x1 / scale); y1 = int(y1 / scale)
                                    x2 = int(x2 / scale); y2 = int(y2 / scale)
                                    bw = max(10, min(x2 - x1, img_w - max(0, x1)))
                                    bh = max(10, min(y2 - y1, img_h - max(0, y1)))
                                    conf = float(b.conf[0]) if hasattr(b, 'conf') and len(b.conf) > 0 else 0.75
                                    candidates.append({"x": max(0, x1), "y": max(0, y1), "w": bw, "h": bh, "conf": conf})
                                best = self._pick_best_face_bbox(candidates, img_w, img_h)
                                if best:
                                    bbox = [best["x"], best["y"], best["w"], best["h"]]
                                    landmarks = self._extract_landmarks_lbf(image_bgr, bbox)
                                    regions = (self._get_regions_from_68_landmarks(landmarks, bbox, img_w, img_h)
                                               if landmarks else self._get_regions_from_bbox(bbox, img_w, img_h))
                                    return self._make_result(bbox, landmarks, regions, best["conf"], "yolo_face", img_w, img_h)
            except Exception:
                pass

        # ── Engine 3: OpenCV YuNet ───────────────────────────────────────────
        if self.yunet_detector is not None:
            try:
                for img_candidate in images_to_try:
                    self.yunet_detector.setInputSize((img_candidate.shape[1], img_candidate.shape[0]))
                    _, faces = self.yunet_detector.detect(img_candidate)
                    if faces is not None and len(faces) > 0:
                        valid_faces = [f for f in faces if f[-1] >= 0.18]
                        if valid_faces:
                            candidates = []
                            for f in valid_faces:
                                fx, fy, fw, fh = f[:4]
                                candidates.append({
                                    "x": max(0, int(fx)), "y": max(0, int(fy)),
                                    "w": max(10, min(int(fw), img_w - max(0, int(fx)))),
                                    "h": max(10, min(int(fh), img_h - max(0, int(fy)))),
                                    "conf": float(f[-1])
                                })
                            best = self._pick_best_face_bbox(candidates, img_w, img_h)
                            if best:
                                bbox = [best["x"], best["y"], best["w"], best["h"]]
                                landmarks = self._extract_landmarks_lbf(image_bgr, bbox)
                                regions = (self._get_regions_from_68_landmarks(landmarks, bbox, img_w, img_h)
                                           if landmarks else self._get_regions_from_bbox(bbox, img_w, img_h))
                                return self._make_result(bbox, landmarks, regions, best["conf"], "opencv_yunet", img_w, img_h)
            except Exception:
                pass

        # ── Engine 4: Haar Cascade (fallback) ───────────────────────────────
        if self.haar_cascade is not None and not self.haar_cascade.empty():
            try:
                for img_candidate in images_to_try:
                    gray = cv2.cvtColor(img_candidate, cv2.COLOR_BGR2GRAY)
                    for (sf, mn) in [(1.06, 3), (1.08, 4), (1.10, 3)]:
                        faces = self.haar_cascade.detectMultiScale(
                            gray, scaleFactor=sf, minNeighbors=mn, minSize=(28, 28)
                        )
                        if len(faces) >= 1:
                            candidates = [{"x": int(fx), "y": int(fy), "w": int(fw), "h": int(fh), "conf": 0.55}
                                          for fx, fy, fw, fh in faces]
                            best = self._pick_best_face_bbox(candidates, img_w, img_h)
                            if best:
                                bbox = [best["x"], best["y"], best["w"], best["h"]]
                                landmarks = self._extract_landmarks_lbf(image_bgr, bbox)
                                regions = (self._get_regions_from_68_landmarks(landmarks, bbox, img_w, img_h)
                                           if landmarks else self._get_regions_from_bbox(bbox, img_w, img_h))
                                return self._make_result(bbox, landmarks, regions, 0.55, "haar_cascade", img_w, img_h)
            except Exception:
                pass

        # STRICT: No face found across all 4 engines
        return {
            "success": False, "face_count": 0,
            "message": "No face detected. Please position your face clearly in the frame with good lighting.",
            "landmarks": None, "bounding_box": None, "regions": {}
        }

    def _get_regions_from_68_landmarks(
        self, landmarks: List[Tuple[int, int, float]], bbox: List[int], img_w: int, img_h: int
    ) -> Dict[str, Dict[str, int]]:
        pts = np.array([[p[0], p[1]] for p in landmarks], dtype=np.float32)
        bx, by, bw, bh = bbox

        eyebrow_pts = pts[17:27]
        brow_top_y = np.min(eyebrow_pts[:, 1])
        brow_center_x = np.mean(eyebrow_pts[:, 0])

        left_eye_center = np.mean(pts[36:42], axis=0)
        right_eye_center = np.mean(pts[42:48], axis=0)
        eye_dist = np.hypot(right_eye_center[0] - left_eye_center[0], right_eye_center[1] - left_eye_center[1])

        nose_tip = pts[30]
        nose_w = abs(pts[35, 0] - pts[31, 0])
        mouth_center = np.mean(pts[48:68], axis=0)
        mouth_w = abs(pts[54, 0] - pts[48, 0])
        chin_pt = pts[8]

        target_forehead_y = brow_top_y - max(15.0, eye_dist * 0.38)
        forehead_y = max(8, int(target_forehead_y))
        forehead_w = int(max(24, eye_dist * 0.75))
        forehead_h = int(max(18, min(abs(brow_top_y - forehead_y), bh * 0.20)))
        forehead_x = int(max(4, min(brow_center_x - forehead_w / 2, img_w - forehead_w - 4)))

        chk_l_x = int(pts[31, 0] - eye_dist * 0.55)
        chk_l_y = int((left_eye_center[1] + mouth_center[1]) / 2.0)
        chk_w = int(max(20, eye_dist * 0.40))
        chk_h = int(max(20, eye_dist * 0.36))

        chk_r_x = int(pts[35, 0] + eye_dist * 0.15)
        chk_r_y = int((right_eye_center[1] + mouth_center[1]) / 2.0)

        chin_y = int((pts[57, 1] + chin_pt[1]) / 2.0)
        chin_w = int(max(24, mouth_w * 0.85))
        chin_h = int(max(18, (chin_pt[1] - pts[57, 1]) * 0.90))

        def clamp_box(cx, cy, cw, ch):
            cw = max(14, min(cw, img_w - 6))
            ch = max(14, min(ch, img_h - 6))
            cx = max(3, min(cx, img_w - cw - 3))
            cy = max(3, min(cy, img_h - ch - 3))
            return {"x": int(cx), "y": int(cy), "w": int(cw), "h": int(ch)}

        return {
            "face": clamp_box(bx, by, bw, bh),
            "forehead": clamp_box(forehead_x, forehead_y, forehead_w, forehead_h),
            "left_cheek": clamp_box(chk_l_x, chk_l_y - chk_h // 2, chk_w, chk_h),
            "right_cheek": clamp_box(chk_r_x, chk_r_y - chk_h // 2, chk_w, chk_h),
            "nose": clamp_box(int(nose_tip[0] - nose_w * 0.5), int(nose_tip[1] - eye_dist * 0.25), int(nose_w), int(eye_dist * 0.35)),
            "mouth": clamp_box(int(mouth_center[0] - mouth_w * 0.5), int(mouth_center[1] - 12), int(mouth_w), 24),
            "chin": clamp_box(int(chin_pt[0] - chin_w * 0.5), chin_y - chin_h // 2, chin_w, chin_h)
        }

    def _get_regions_from_bbox(self, bbox: List[int], img_w: int, img_h: int) -> Dict[str, Dict[str, int]]:
        x, y, w, h = bbox
        return {
            "face": {
                "x": max(0, min(x, img_w - 12)),
                "y": max(0, min(y, img_h - 12)),
                "w": max(12, min(w, img_w - x)),
                "h": max(12, min(h, img_h - y))
            },
            "forehead": {
                "x": max(0, min(int(x + w * 0.24), img_w - 12)),
                "y": max(0, min(int(y + h * 0.08), img_h - 12)),
                "w": max(12, int(w * 0.52)),
                "h": max(12, int(h * 0.16))
            },
            "left_cheek": {
                "x": max(0, min(int(x + w * 0.10), img_w - 12)),
                "y": max(0, min(int(y + h * 0.44), img_h - 12)),
                "w": max(12, int(w * 0.28)),
                "h": max(12, int(h * 0.22))
            },
            "right_cheek": {
                "x": max(0, min(int(x + w * 0.62), img_w - 12)),
                "y": max(0, min(int(y + h * 0.44), img_h - 12)),
                "w": max(12, int(w * 0.28)),
                "h": max(12, int(h * 0.22))
            },
            "chin": {
                "x": max(0, min(int(x + w * 0.32), img_w - 12)),
                "y": max(0, min(int(y + h * 0.76), img_h - 12)),
                "w": max(12, int(w * 0.36)),
                "h": max(12, int(h * 0.16))
            },
            "nose": {
                "x": max(0, min(int(x + w * 0.40), img_w - 12)),
                "y": max(0, min(int(y + h * 0.46), img_h - 12)),
                "w": max(12, int(w * 0.20)),
                "h": max(12, int(h * 0.18))
            },
            "mouth": {
                "x": max(0, min(int(x + w * 0.32), img_w - 12)),
                "y": max(0, min(int(y + h * 0.66), img_h - 12)),
                "w": max(12, int(w * 0.36)),
                "h": max(12, int(h * 0.14))
            }
        }
