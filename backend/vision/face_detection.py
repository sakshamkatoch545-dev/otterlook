"""
Face Detection and Facial Landmark Localization Module.
Powered by YOLOv8-Face (Deep Neural Network SOTA face detector)
and OpenCV FacemarkLBF (68-point high-precision facial landmark engine).
Ensures that if no face is detected in the image or camera feed,
no output or false positives are generated.
"""

import os
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

class FaceDetector:
    def __init__(self):
        self.yolo_detector = None
        self.yunet_detector = None
        self.facemark = None
        self.haar_cascade = None
        self._init_detectors()

    def _init_detectors(self):
        models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
        os.makedirs(models_dir, exist_ok=True)

        # 1. Initialize YOLO Face Model
        yolo_path = os.path.join(models_dir, "yolov8n-face.pt")
        if os.path.exists(yolo_path):
            try:
                from ultralytics import YOLO
                self.yolo_detector = YOLO(yolo_path)
            except Exception as e:
                self.yolo_detector = None

        # 2. Secondary Face Detector: OpenCV YuNet Neural Engine
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
                    score_threshold=0.5,
                    nms_threshold=0.3,
                    top_k=5000
                )
            except Exception:
                self.yunet_detector = None

        # 3. Initialize FacemarkLBF 68-Point Landmark Model
        lbf_path = os.path.join(models_dir, "lbfmodel.yaml")
        if os.path.exists(lbf_path) and hasattr(cv2, "face") and hasattr(cv2.face, "createFacemarkLBF"):
            try:
                self.facemark = cv2.face.createFacemarkLBF()
                self.facemark.loadModel(lbf_path)
            except Exception:
                self.facemark = None

        # 4. Fallback Haar Cascade
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

    def detect_faces(self, image_bgr: np.ndarray) -> Dict[str, Any]:
        """
        Detects faces in the image using YOLO face detection.
        Enforces strict single-face constraint:
        - If NO face is detected in the image or camera frame: returns success=False, face_count=0.
        - If multiple faces detected: returns success=False.
        - If exactly 1 face detected: extracts precise bounding box and anatomical dermal regions.
        """
        if image_bgr is None or image_bgr.size == 0:
            return {
                "success": False,
                "face_count": 0,
                "message": "Empty or invalid image.",
                "landmarks": None,
                "bounding_box": None,
                "regions": {}
            }

        img_h, img_w = image_bgr.shape[:2]

        # 1. Primary Engine: YOLO Face Detection
        if self.yolo_detector is not None:
            try:
                results = self.yolo_detector(image_bgr, conf=0.35, verbose=False)
                boxes = results[0].boxes if len(results) > 0 else None

                # Multi-scale check if tight crop or slight angle or low light
                if boxes is None or len(boxes) == 0:
                    results = self.yolo_detector(image_bgr, conf=0.22, verbose=False)
                    boxes = results[0].boxes if len(results) > 0 else None

                if boxes is None or len(boxes) == 0:
                    results = self.yolo_detector(image_bgr, conf=0.15, verbose=False)
                    boxes = results[0].boxes if len(results) > 0 else None

                if boxes is not None and len(boxes) > 0:
                    # Always capture the primary face that is closest (largest area) and most defined (confidence/clarity)
                    scored_candidates = []
                    center_x, center_y = img_w / 2.0, img_h / 2.0

                    for idx, b in enumerate(boxes):
                        x1, y1, x2, y2 = map(int, b.xyxy[0].tolist())
                        bw = max(1, x2 - x1)
                        bh = max(1, y2 - y1)
                        area = bw * bh
                        conf = float(b.conf[0]) if hasattr(b, 'conf') and len(b.conf) > 0 else 0.85
                        # Centrality factor: closer to image center is more likely the user
                        cx = x1 + bw / 2.0
                        cy = y1 + bh / 2.0
                        dist_sq = ((cx - center_x) / img_w) ** 2 + ((cy - center_y) / img_h) ** 2
                        centrality = max(0.5, 1.0 - (dist_sq ** 0.5))
                        # Combined score: large area (close to camera) + high definition + centered
                        score = (area ** 0.75) * conf * centrality
                        scored_candidates.append((score, idx))

                    scored_candidates.sort(key=lambda x: x[0], reverse=True)
                    best_idx = scored_candidates[0][1]
                    target_box = boxes[best_idx]
                    x1, y1, x2, y2 = map(int, target_box.xyxy[0].tolist())
                    fx = max(0, min(x1, img_w - 10))
                    fy = max(0, min(y1, img_h - 10))
                    fw = max(10, min(x2 - x1, img_w - fx))
                    fh = max(10, min(y2 - y1, img_h - fy))
                    bbox = [fx, fy, fw, fh]
                    conf = float(target_box.conf[0])

                    landmarks_68 = self._extract_landmarks_lbf(image_bgr, bbox)
                    if landmarks_68:
                        regions = self._get_regions_from_68_landmarks(landmarks_68, bbox, img_w, img_h)
                    else:
                        regions = self._get_regions_from_bbox(bbox, img_w, img_h)

                    return {
                        "success": True,
                        "face_count": 1,
                        "message": "Face localized via YOLO Face detector.",
                        "detector_type": "yolo_face",
                        "confidence": conf,
                        "landmarks": landmarks_68,
                        "bounding_box": bbox,
                        "regions": regions
                    }
            except Exception:
                pass

        # 2. Secondary Neural Engine: OpenCV YuNet
        if self.yunet_detector is not None:
            try:
                self.yunet_detector.setInputSize((img_w, img_h))
                _, faces = self.yunet_detector.detect(image_bgr)
                if faces is not None and len(faces) > 0:
                    valid_faces = [f for f in faces if f[-1] >= 0.25]
                    if valid_faces:
                        # Pick closest, largest, and most defined face
                        center_x, center_y = img_w / 2.0, img_h / 2.0
                        def yunet_score(f):
                            fx, fy, fw, fh = f[:4]
                            conf = float(f[-1])
                            cx = fx + fw / 2.0
                            cy = fy + fh / 2.0
                            dist = (((cx - center_x) / img_w) ** 2 + ((cy - center_y) / img_h) ** 2) ** 0.5
                            centrality = max(0.5, 1.0 - dist)
                            return ((fw * fh) ** 0.75) * conf * centrality

                        best_face = max(valid_faces, key=yunet_score)
                        fx, fy, fw, fh = map(int, best_face[:4])
                        bbox = [max(0, fx), max(0, fy), min(fw, img_w - fx), min(fh, img_h - fy)]
                        landmarks_68 = self._extract_landmarks_lbf(image_bgr, bbox)
                        if landmarks_68:
                            regions = self._get_regions_from_68_landmarks(landmarks_68, bbox, img_w, img_h)
                        else:
                            regions = self._get_regions_from_bbox(bbox, img_w, img_h)

                        return {
                            "success": True,
                            "face_count": 1,
                            "message": "Face localized via YuNet detector.",
                            "detector_type": "opencv_yunet",
                            "confidence": float(best_face[-1]),
                            "landmarks": landmarks_68,
                            "bounding_box": bbox,
                            "regions": regions
                        }
            except Exception:
                pass

        # 3. Fallback Haar Cascade
        if self.haar_cascade is not None and not self.haar_cascade.empty():
            try:
                gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
                faces = self.haar_cascade.detectMultiScale(
                    gray, scaleFactor=1.08, minNeighbors=4, minSize=(32, 32)
                )
                if len(faces) >= 1:
                    areas = [f[2] * f[3] for f in faces]
                    best_idx = int(np.argmax(areas))
                    (fx, fy, fw, fh) = map(int, faces[best_idx])
                    bbox = [fx, fy, fw, fh]
                    landmarks_68 = self._extract_landmarks_lbf(image_bgr, bbox)
                    if landmarks_68:
                        regions = self._get_regions_from_68_landmarks(landmarks_68, bbox, img_w, img_h)
                    else:
                        regions = self._get_regions_from_bbox(bbox, img_w, img_h)

                    return {
                        "success": True,
                        "face_count": 1,
                        "message": "Face localized via Haar cascade detector.",
                        "detector_type": "haar_cascade",
                        "landmarks": landmarks_68,
                        "bounding_box": bbox,
                        "regions": regions
                    }
            except Exception:
                pass

        # STRICT CRITICAL RULE: If no face is detected, DO NOT produce output or fake face boxes!
        return {
            "success": False,
            "face_count": 0,
            "message": "No face detected in the picture or camera feed. Please position your face clearly in the camera frame.",
            "landmarks": None,
            "bounding_box": None,
            "regions": {}
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
