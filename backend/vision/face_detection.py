"""
Face Detection and Facial Landmark Localization Module.
Powered by a 4-engine cascade: MediaPipe (most robust for selfies), 
YOLOv8-Face (deep SOTA), OpenCV YuNet (neural), and Haar Cascade (fallback).
Ensures that if no face is detected, no output or false positives are generated.
"""

import os
import hashlib
from collections import OrderedDict
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

try:
    import mediapipe as _mp
except Exception:
    _mp = None


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
        self._detect_cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._cache_max_entries = 32
        self._init_detectors()

    def _init_detectors(self):
        models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
        try:
            os.makedirs(models_dir, exist_ok=True)
        except OSError:
            pass

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
                    min_detection_confidence=0.50,
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
                    score_threshold=0.26,
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

        # Pre-warm neural models to eliminate first-request cold-start latency
        self._warmup_models()

    def _warmup_models(self):
        """Pre-warms neural engines on startup to eliminate first-request cold start latency."""
        try:
            dummy = np.zeros((64, 64, 3), dtype=np.uint8)
            dummy[16:48, 16:48] = [180, 150, 130]
            # 1. MediaPipe warmup
            if self.mediapipe_detector is not None:
                try:
                    import mediapipe as mp
                    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=dummy)
                    self.mediapipe_detector.detect(mp_img)
                except Exception:
                    pass
            # 2. YOLO warmup (pre-allocates Torch graph)
            if self.yolo_detector is not None:
                try:
                    self.yolo_detector(dummy, imgsz=64, verbose=False)
                except Exception:
                    pass
            # 3. YuNet warmup
            if self.yunet_detector is not None:
                try:
                    self.yunet_detector.setInputSize((64, 64))
                    self.yunet_detector.detect(dummy)
                except Exception:
                    pass
        except Exception:
            pass

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

    def _validate_human_face(self, image_bgr: np.ndarray, bbox: List[int]) -> bool:
        """
        Validates that a candidate bounding box represents a genuine human face
        rather than a flat dark/bright surface, noise pattern, solid wall, or background object.
        Inclusive across Fitzpatrick I–VI and varied lighting.
        """
        if image_bgr is None or image_bgr.size == 0 or not bbox or len(bbox) < 4:
            return False

        x, y, w, h = bbox
        img_h, img_w = image_bgr.shape[:2]

        # Minimum face dimensions for biometric analysis (allow smaller faces in hi-res images)
        min_face = max(20, int(0.025 * min(img_w, img_h)))
        if w < min_face or h < min_face:
            return False

        # Human face aspect ratio (height / width) is typically between 0.55 and 2.10
        aspect = h / float(w)
        if aspect < 0.55 or aspect > 2.10:
            return False

        # Extract crop safely within bounds
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(img_w, x + w)
        y2 = min(img_h, y + h)
        if (x2 - x1) < 16 or (y2 - y1) < 16:
            return False

        crop = image_bgr[y1:y2, x1:x2]
        if crop.size == 0:
            return False

        # 1. Variance check: reject solid black, white, gray, or flat uniform patches
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        var = float(np.var(gray))
        if var < 10.0:  # flat surfaces, solid colors, black screen
            return False

        # 2. Chromaticity & facial texture check:
        # Detect human cutaneous melanin/hemoglobin spectrum across Fitzpatrick I to VI.
        # Widened YCrCb ranges to remain inclusive of deep and fair complexions.
        ycrcb = cv2.cvtColor(crop, cv2.COLOR_BGR2YCrCb)
        cr = ycrcb[:, :, 1].astype(np.float64)
        cb = ycrcb[:, :, 2].astype(np.float64)
        # Broad skin-tone band: covers light porcelain through deep melanin complexions
        skin_mask = (cr >= 110) & (cr <= 200) & (cb >= 60) & (cb <= 165) & (cr > cb)
        skin_ratio = float(np.mean(skin_mask))

        # Real faces have skin pigments or distinct facial feature edges (eyes/brows/mouth).
        # Accept if enough skin pixels OR enough texture variance (facial features).
        if skin_ratio < 0.010 and var < 30.0:
            return False

        return True

    def _rank_face_candidates(self, candidates: List[Dict], img_w: int, img_h: int, image_bgr: Optional[np.ndarray] = None) -> List[Dict]:
        """Validate and sort face candidates favoring closer, sharper, central foreground subjects."""
        if not candidates:
            return []

        if image_bgr is not None:
            valid_candidates = []
            for c in candidates:
                bb = [c["x"], c["y"], c["w"], c["h"]]
                if self._validate_human_face(image_bgr, bb):
                    valid_candidates.append(c)
            candidates = valid_candidates
            if not candidates:
                return []

        center_x, center_y = img_w / 2.0, img_h / 2.0
        scored = []
        for c in candidates:
            x, y, w, h = c["x"], c["y"], c["w"], c["h"]
            area = max(1, w * h)
            conf = c.get("conf", 0.75)
            cx, cy = x + w / 2.0, y + h / 2.0
            dist = (((cx - center_x) / img_w) ** 2 + ((cy - center_y) / img_h) ** 2) ** 0.5
            centrality = max(0.4, 1.0 - dist)

            # Measure local sharpness (Laplacian variance) when image_bgr is available
            sharpness_boost = 1.0
            if image_bgr is not None:
                try:
                    crop = image_bgr[max(0, y):min(img_h, y + h), max(0, x):min(img_w, x + w)]
                    if crop.size > 0:
                        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                        lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
                        sharpness_boost = min(1.5, max(0.6, 0.6 + (lap_var / 150.0) * 0.9))
                except Exception:
                    pass

            score = (area ** 1.15) * conf * centrality * sharpness_boost
            scored.append((score, c))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in scored]

    def _foreground_faces(self, ranked: List[Dict]) -> List[List[int]]:
        """Return only the single closest, clearest primary foreground face."""
        if not ranked:
            return []
        primary = ranked[0]
        return [[primary["x"], primary["y"], primary["w"], primary["h"]]]

    def _pick_best_face_bbox(self, candidates: List[Dict], img_w: int, img_h: int, image_bgr: Optional[np.ndarray] = None) -> Optional[Dict]:
        """Score candidates by: largest area × confidence × centrality, return best valid face."""
        ranked = self._rank_face_candidates(candidates, img_w, img_h, image_bgr)
        return ranked[0] if ranked else None

    def _make_result(self, bbox, landmarks, regions, conf, detector_type, img_w, img_h, all_faces: Optional[List[List[int]]] = None):
        faces_list = all_faces if all_faces else [bbox]
        return {
            "success": True,
            "face_count": len(faces_list),
            "message": f"Face localized via {detector_type}.",
            "detector_type": detector_type,
            "confidence": conf,
            "landmarks": landmarks,
            "bounding_box": bbox,
            "all_faces": faces_list,
            "regions": regions,
        }

    def _detect_on_frame(
        self,
        image_bgr: np.ndarray,
        allow_slow_fallbacks: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Runs the fast-first detection cascade (MediaPipe -> OpenCV YuNet -> YOLOv8 -> Haar)
        on a single frame and returns the best verified bounding box & confidence, or None.
        """
        img_h, img_w = image_bgr.shape[:2]
        enhanced = None

        # ── Engine 1: MediaPipe ──────────────────────────────────────────────
        if self.mediapipe_detector is not None and _mp is not None:
            try:
                img_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
                mp_image = _mp.Image(image_format=_mp.ImageFormat.SRGB, data=img_rgb)
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
                        if conf >= 0.50:
                            candidates.append({"x": x, "y": y, "w": w, "h": h, "conf": float(conf)})
                    ranked = self._rank_face_candidates(candidates, img_w, img_h, image_bgr)
                    if ranked:
                        best = ranked[0]
                        return {
                            "bounding_box": [best["x"], best["y"], best["w"], best["h"]],
                            "all_faces": self._foreground_faces(ranked),
                            "confidence": best["conf"],
                            "detector_type": "mediapipe",
                        }

                # Lazily try CLAHE on MediaPipe only if raw image produced no valid face
                if enhanced is None:
                    enhanced = _preprocess_for_detection(image_bgr)
                enh_rgb = cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB)
                enh_image = _mp.Image(image_format=_mp.ImageFormat.SRGB, data=enh_rgb)
                enh_result = self.mediapipe_detector.detect(enh_image)
                if enh_result.detections:
                    candidates = []
                    for det in enh_result.detections:
                        bb = det.bounding_box
                        x = max(0, bb.origin_x)
                        y = max(0, bb.origin_y)
                        w = max(10, min(bb.width, img_w - x))
                        h = max(10, min(bb.height, img_h - y))
                        conf = det.categories[0].score if det.categories else 0.6
                        if conf >= 0.50:
                            candidates.append({"x": x, "y": y, "w": w, "h": h, "conf": float(conf)})
                    ranked = self._rank_face_candidates(candidates, img_w, img_h, image_bgr)
                    if ranked:
                        best = ranked[0]
                        return {
                            "bounding_box": [best["x"], best["y"], best["w"], best["h"]],
                            "all_faces": self._foreground_faces(ranked),
                            "confidence": best["conf"],
                            "detector_type": "mediapipe",
                        }
            except Exception:
                pass

        # ── Engine 2: OpenCV YuNet (fast ONNX neural detector) ───────────────
        if self.yunet_detector is not None:
            try:
                for frame_to_try in (image_bgr, None):
                    if frame_to_try is None:
                        if enhanced is None:
                            enhanced = _preprocess_for_detection(image_bgr)
                        frame_to_try = enhanced
                    self.yunet_detector.setInputSize((img_w, img_h))
                    _, faces = self.yunet_detector.detect(frame_to_try)
                    if faces is not None and len(faces) > 0:
                        candidates = []
                        for f in faces:
                            if f[-1] < 0.26:
                                continue
                            fx, fy, fw, fh = f[:4]
                            bx = max(0, int(fx))
                            by = max(0, int(fy))
                            bw = max(10, min(int(fw), img_w - bx))
                            bh = max(10, min(int(fh), img_h - by))
                            candidates.append({"x": bx, "y": by, "w": bw, "h": bh, "conf": float(f[-1])})
                        ranked = self._rank_face_candidates(candidates, img_w, img_h, image_bgr)
                        if ranked:
                            best = ranked[0]
                            return {
                                "bounding_box": [best["x"], best["y"], best["w"], best["h"]],
                                "all_faces": self._foreground_faces(ranked),
                                "confidence": best["conf"],
                                "detector_type": "opencv_yunet",
                            }
            except Exception:
                pass

        if not allow_slow_fallbacks:
            return None

        # ── Engine 3: YOLOv8-Face (PyTorch fallback) ─────────────────────────
        if self.yolo_detector is not None:
            try:
                results = self.yolo_detector(image_bgr, conf=0.38, imgsz=640, verbose=False)
                boxes = results[0].boxes if len(results) > 0 else None
                if boxes is not None and len(boxes) > 0:
                    candidates = []
                    for b in boxes:
                        x1, y1, x2, y2 = map(int, b.xyxy[0].tolist())
                        bx, by = max(0, x1), max(0, y1)
                        bw = max(10, min(x2 - bx, img_w - bx))
                        bh = max(10, min(y2 - by, img_h - by))
                        conf = float(b.conf[0]) if hasattr(b, 'conf') and len(b.conf) > 0 else 0.75
                        if conf >= 0.38:
                            candidates.append({"x": bx, "y": by, "w": bw, "h": bh, "conf": conf})
                    ranked = self._rank_face_candidates(candidates, img_w, img_h, image_bgr)
                    if ranked:
                        best = ranked[0]
                        return {
                            "bounding_box": [best["x"], best["y"], best["w"], best["h"]],
                            "all_faces": self._foreground_faces(ranked),
                            "confidence": best["conf"],
                            "detector_type": "yolo_face",
                        }
            except Exception:
                pass

        # ── Engine 4: Haar Cascade (emergency fallback) ──
        if self.haar_cascade is not None and not self.haar_cascade.empty():
            try:
                gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
                faces = self.haar_cascade.detectMultiScale(
                    gray, scaleFactor=1.15, minNeighbors=8, minSize=(60, 60)
                )
                if len(faces) >= 1:
                    candidates = []
                    min_face_area = int(0.015 * img_w * img_h)
                    for fx, fy, fw, fh in faces:
                        bx = max(0, int(fx))
                        by = max(0, int(fy))
                        bw = max(10, min(int(fw), img_w - bx))
                        bh = max(10, min(int(fh), img_h - by))
                        if (bw * bh) >= min_face_area:
                            candidates.append({"x": bx, "y": by, "w": bw, "h": bh, "conf": 0.60})
                    best = self._pick_best_face_bbox(candidates, img_w, img_h, image_bgr)
                    if best:
                        return {
                            "bounding_box": [best["x"], best["y"], best["w"], best["h"]],
                            "confidence": 0.60,
                            "detector_type": "haar_cascade",
                        }
            except Exception:
                pass

        return None

    def _finalize_detection(
        self,
        image_bgr: np.ndarray,
        bbox: List[int],
        conf: float,
        detector_type: str,
        extract_landmarks: bool = True,
        all_faces: Optional[List[List[int]]] = None
    ) -> Dict[str, Any]:
        """Populates landmarks & regions (when requested) and formats the response."""
        img_h, img_w = image_bgr.shape[:2]
        if extract_landmarks:
            landmarks = self._extract_landmarks_lbf(image_bgr, bbox)
            regions = (
                self._get_regions_from_68_landmarks(landmarks, bbox, img_w, img_h)
                if landmarks else self._get_regions_from_bbox(bbox, img_w, img_h)
            )
        else:
            landmarks = None
            regions = {}
        return self._make_result(bbox, landmarks, regions, conf, detector_type, img_w, img_h, all_faces=all_faces)

    def detect_faces(
        self,
        image_bgr: np.ndarray,
        extract_landmarks: bool = True
    ) -> Dict[str, Any]:
        """
        Detects faces using a fast-first cascade (MediaPipe -> YuNet -> YOLOv8 -> Haar)
        on a <=640px detection proxy, with LRU caching for repeated /api/detect-face -> /api/analyze calls.
        """
        if image_bgr is None or image_bgr.size == 0:
            return {
                "success": False, "face_count": 0,
                "message": "Empty or invalid image.",
                "landmarks": None, "bounding_box": None, "regions": {}
            }

        img_h, img_w = image_bgr.shape[:2]
        if img_h < 30 or img_w < 30:
            return {
                "success": False, "face_count": 0,
                "message": "Image resolution is too small to detect a human face.",
                "landmarks": None, "bounding_box": None, "regions": {}
            }

        # Check LRU detection cache (speeds up /api/detect-face -> /api/analyze)
        img_hash = hashlib.sha256(image_bgr.tobytes()).hexdigest()
        cached = self._detect_cache.get(img_hash)
        if cached is not None:
            self._detect_cache.move_to_end(img_hash)
            if not cached.get("success"):
                return dict(cached)
            if not extract_landmarks or cached.get("regions"):
                return dict(cached)
            # Upgrade cached bbox-only result with landmarks/regions on original frame
            upgraded = self._finalize_detection(
                image_bgr,
                cached["bounding_box"],
                cached["confidence"],
                cached["detector_type"],
                extract_landmarks=True,
                all_faces=cached.get("all_faces"),
            )
            self._detect_cache[img_hash] = upgraded
            return dict(upgraded)

        # Build <=640px proxy for fast detection
        max_det_dim = 640
        max_side = max(img_w, img_h)
        if max_side > max_det_dim:
            proxy_scale = max_det_dim / float(max_side)
            pw = max(64, int(round(img_w * proxy_scale)))
            ph = max(64, int(round(img_h * proxy_scale)))
            det_frame = cv2.resize(image_bgr, (pw, ph), interpolation=cv2.INTER_AREA)
        else:
            pw, ph = img_w, img_h
            det_frame = image_bgr

        # 1. Primary pass on <=640px frame
        det = self._detect_on_frame(det_frame, allow_slow_fallbacks=True)

        # 2. Single fast zoomed retry on small/distant faces using neural engines only
        if det is None and max(pw, ph) >= 240:
            try:
                rw, rh = int(pw * 1.4), int(ph * 1.4)
                resized = cv2.resize(det_frame, (rw, rh), interpolation=cv2.INTER_LINEAR)
                retry_det = self._detect_on_frame(resized, allow_slow_fallbacks=False)
                if retry_det is not None:
                    sx = pw / float(rw)
                    sy = ph / float(rh)
                    rb = retry_det["bounding_box"]
                    retry_det["bounding_box"] = [
                        int(rb[0] * sx), int(rb[1] * sy),
                        int(rb[2] * sx), int(rb[3] * sy)
                    ]
                    det = retry_det
            except Exception:
                pass

        if det is not None:
            sx = img_w / float(pw)
            sy = img_h / float(ph)
            def _scale_box(b):
                return [
                    max(0, int(round(b[0] * sx))),
                    max(0, int(round(b[1] * sy))),
                    max(10, min(int(round(b[2] * sx)), img_w)),
                    max(10, min(int(round(b[3] * sy)), img_h)),
                ]
            bbox = _scale_box(det["bounding_box"])
            raw_faces = det.get("all_faces") or [det["bounding_box"]]
            scaled_faces = [_scale_box(fb) for fb in raw_faces]
            result = self._finalize_detection(
                image_bgr, bbox, det["confidence"], det["detector_type"],
                extract_landmarks=extract_landmarks, all_faces=scaled_faces
            )
        else:
            result = {
                "success": False, "face_count": 0,
                "message": "No human face detected. Please position your face clearly in the frame with good lighting.",
                "landmarks": None, "bounding_box": None, "regions": {}
            }

        self._detect_cache[img_hash] = result
        if len(self._detect_cache) > self._cache_max_entries:
            self._detect_cache.popitem(last=False)

        return dict(result)

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
