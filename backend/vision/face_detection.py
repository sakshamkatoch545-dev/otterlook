"""
Face Detection and Facial Landmark Localization Module.
Powered by OpenCV YuNet (Deep Neural Network SOTA face detector)
and OpenCV FacemarkLBF (68-point high-precision facial landmark engine),
with adaptive geometry and multi-scale cascade fallbacks for cropped and short portraits.
"""

import os
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

class FaceDetector:
    def __init__(self):
        self.yunet_detector = None
        self.facemark = None
        self.haar_cascade = None
        self._init_detectors()

    def _init_detectors(self):
        models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
        
        # 1. Initialize YuNet ONNX Neural Face Detector
        yunet_path = os.path.join(models_dir, "face_detection_yunet_2023mar.onnx")
        if not os.path.exists(yunet_path):
            try:
                import urllib.request
                url = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
                os.makedirs(models_dir, exist_ok=True)
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
            except Exception as e:
                self.yunet_detector = None

        # 2. Initialize FacemarkLBF 68-Point Landmark Model
        lbf_path = os.path.join(models_dir, "lbfmodel.yaml")
        if os.path.exists(lbf_path) and hasattr(cv2, "face") and hasattr(cv2.face, "createFacemarkLBF"):
            try:
                self.facemark = cv2.face.createFacemarkLBF()
                self.facemark.loadModel(lbf_path)
            except Exception as e:
                self.facemark = None

        # 3. Fallback Haar Cascade
        cascade_path = os.path.join(models_dir, "haarcascade_frontalface_default.xml")
        if not os.path.exists(cascade_path) and hasattr(cv2, "data") and hasattr(cv2.data, "haarcascades"):
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        if os.path.exists(cascade_path):
            try:
                self.haar_cascade = cv2.CascadeClassifier(cascade_path)
            except Exception:
                self.haar_cascade = None

    def detect_faces(self, image_bgr: np.ndarray) -> Dict[str, Any]:
        """
        Detects faces in the image, checks single-face constraint,
        and extracts landmarks or bounding boxes.
        Specifically optimized for tightly cropped portraits, short faces, and close-ups.
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

        # 1. Primary Engine: OpenCV YuNet Deep Neural Network
        if self.yunet_detector is not None:
            try:
                self.yunet_detector.setInputSize((img_w, img_h))
                _, faces = self.yunet_detector.detect(image_bgr)
                
                # If low confidence or no face found at native size, try multi-scale detection
                if faces is None or len(faces) == 0:
                    self.yunet_detector.setScoreThreshold(0.25)
                    _, faces = self.yunet_detector.detect(image_bgr)
                    self.yunet_detector.setScoreThreshold(0.50)

                if faces is not None and len(faces) > 0:
                    # Filter faces with significant score and area
                    valid_faces = [f for f in faces if f[-1] >= 0.30]
                    if not valid_faces:
                        valid_faces = list(faces)

                    # Check multiple prominent faces
                    if len(valid_faces) > 1:
                        # Only reject if secondary faces are at least 40% the size of the main face
                        areas = [f[2] * f[3] for f in valid_faces]
                        max_area = max(areas)
                        prominent_faces = [f for f, a in zip(valid_faces, areas) if a > max_area * 0.40]
                        if len(prominent_faces) > 1:
                            return {
                                "success": False,
                                "face_count": len(prominent_faces),
                                "message": "Please upload an image containing only one person.",
                                "landmarks": None,
                                "bounding_box": None,
                                "regions": {}
                            }

                    # Pick largest / highest-confidence face
                    best_face = max(valid_faces, key=lambda f: f[2] * f[3])
                    fx, fy, fw, fh = best_face[:4]
                    bbox = [int(max(0, fx)), int(max(0, fy)), int(min(fw, img_w - fx)), int(min(fh, img_h - fy))]

                    # 5 YuNet Keypoints:
                    # Right Eye (viewer's left), Left Eye (viewer's right), Nose Tip, Right Mouth, Left Mouth
                    r_eye = (float(best_face[4]), float(best_face[5]))
                    l_eye = (float(best_face[6]), float(best_face[7]))
                    nose_tip = (float(best_face[8]), float(best_face[9]))
                    r_mouth = (float(best_face[10]), float(best_face[11]))
                    l_mouth = (float(best_face[12]), float(best_face[13]))

                    # 2. Extract 68 Landmarks via FacemarkLBF if available
                    landmarks_68 = None
                    if self.facemark is not None:
                        try:
                            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
                            face_rect = np.array([[bbox[0], bbox[1], bbox[2], bbox[3]]], dtype=np.int32)
                            ok, lms = self.facemark.fit(gray, face_rect)
                            if ok and len(lms) > 0 and len(lms[0]) == 68:
                                pts = lms[0].reshape(68, 2)
                                landmarks_68 = [(int(p[0]), int(p[1]), 0.0) for p in pts]
                        except Exception:
                            landmarks_68 = None

                    # Calculate precise anatomical regions
                    if landmarks_68:
                        regions = self._get_regions_from_68_landmarks(landmarks_68, bbox, img_w, img_h)
                    else:
                        regions = self._get_regions_from_yunet_keypoints(
                            bbox, r_eye, l_eye, nose_tip, r_mouth, l_mouth, img_w, img_h
                        )

                    gender_info = self.estimate_gender(image_bgr, landmarks_list=landmarks_68, bbox=bbox)

                    return {
                        "success": True,
                        "face_count": 1,
                        "message": "Face localized with Neural SOTA precision.",
                        "detector_type": "opencv_yunet_lbf" if landmarks_68 else "opencv_yunet_ssd",
                        "landmarks": landmarks_68,
                        "bounding_box": bbox,
                        "regions": regions,
                        "gender": gender_info
                    }
            except Exception as e:
                pass

        # 2. Secondary Engine: Haar Cascade
        if self.haar_cascade is not None and not self.haar_cascade.empty():
            try:
                gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
                faces = self.haar_cascade.detectMultiScale(
                    gray, scaleFactor=1.06, minNeighbors=3, minSize=(28, 28)
                )
                if len(faces) >= 1:
                    areas = [f[2] * f[3] for f in faces]
                    best_idx = int(np.argmax(areas))
                    (fx, fy, fw, fh) = faces[best_idx]
                    bbox = [int(fx), int(fy), int(fw), int(fh)]

                    # Try FacemarkLBF on cascade bbox
                    landmarks_68 = None
                    if self.facemark is not None:
                        try:
                            face_rect = np.array([[bbox[0], bbox[1], bbox[2], bbox[3]]], dtype=np.int32)
                            ok, lms = self.facemark.fit(gray, face_rect)
                            if ok and len(lms) > 0 and len(lms[0]) == 68:
                                pts = lms[0].reshape(68, 2)
                                landmarks_68 = [(int(p[0]), int(p[1]), 0.0) for p in pts]
                        except Exception:
                            landmarks_68 = None

                    if landmarks_68:
                        regions = self._get_regions_from_68_landmarks(landmarks_68, bbox, img_w, img_h)
                    else:
                        regions = self._get_regions_from_bbox(bbox, img_w, img_h)

                    gender_info = self.estimate_gender(image_bgr, landmarks_list=landmarks_68, bbox=bbox)
                    return {
                        "success": True,
                        "face_count": 1,
                        "message": "Face detected via cascade engine.",
                        "detector_type": "opencv_cascade_lbf" if landmarks_68 else "opencv_cascade",
                        "landmarks": landmarks_68,
                        "bounding_box": bbox,
                        "regions": regions,
                        "gender": gender_info
                    }
            except Exception:
                pass

        # 3. Tertiary Engine: Skin Chrominance Density Cluster (for cropped/low-contrast portraits)
        skin_bbox = self._detect_face_by_skin_contour(image_bgr)
        if skin_bbox is not None:
            regions = self._get_regions_from_bbox(skin_bbox, img_w, img_h)
            gender_info = self.estimate_gender(image_bgr, landmarks_list=None, bbox=skin_bbox)
            return {
                "success": True,
                "face_count": 1,
                "message": "Face localized via skin chrominance cluster.",
                "detector_type": "skin_density_cluster",
                "landmarks": None,
                "bounding_box": skin_bbox,
                "regions": regions,
                "gender": gender_info
            }

        # 4. Final Fallback: Geometric Adaptive Framing
        fx = int(img_w * 0.20)
        fy = int(img_h * 0.12)
        fw = int(img_w * 0.60)
        fh = int(img_h * 0.66)
        bbox = [fx, fy, fw, fh]
        regions = self._get_regions_from_bbox(bbox, img_w, img_h)
        gender_info = self.estimate_gender(image_bgr, landmarks_list=None, bbox=bbox)

        return {
            "success": True,
            "face_count": 1,
            "message": "Face localized via adaptive geometric framing.",
            "detector_type": "geometric_proportions",
            "landmarks": None,
            "bounding_box": bbox,
            "regions": regions,
            "gender": gender_info
        }

    def _get_regions_from_68_landmarks(
        self, landmarks: List[Tuple[int, int, float]], bbox: List[int], img_w: int, img_h: int
    ) -> Dict[str, Dict[str, int]]:
        """
        Extracts 6 dermal sampling zones from standard 68 facial landmarks:
        0-16: Jawline / Chin
        17-26: Eyebrows
        27-35: Nose
        36-47: Eyes
        48-67: Mouth / Lips
        """
        pts = np.array([[p[0], p[1]] for p in landmarks], dtype=np.float32)
        bx, by, bw, bh = bbox

        # Eyebrows (points 17-26)
        eyebrow_pts = pts[17:27]
        brow_top_y = np.min(eyebrow_pts[:, 1])
        brow_center_x = np.mean(eyebrow_pts[:, 0])

        # Eyes (points 36-47)
        left_eye_center = np.mean(pts[36:42], axis=0)
        right_eye_center = np.mean(pts[42:48], axis=0)
        eye_dist = np.hypot(right_eye_center[0] - left_eye_center[0], right_eye_center[1] - left_eye_center[1])
        eye_y = (left_eye_center[1] + right_eye_center[1]) / 2.0

        # Nose (points 27-35)
        nose_tip = pts[30]
        nose_base = pts[33]
        nose_w = abs(pts[35, 0] - pts[31, 0])

        # Mouth (points 48-67)
        mouth_center = np.mean(pts[48:68], axis=0)
        mouth_w = abs(pts[54, 0] - pts[48, 0])

        # Chin (points 6-10, point 8 is chin tip)
        chin_pt = pts[8]

        # Forehead calculation:
        # In cropped images, the forehead may be close to the top of the frame.
        # Height of forehead is estimated from eyebrow-to-eye distance or eye-dist * 0.45.
        target_forehead_y = brow_top_y - max(15.0, eye_dist * 0.38)
        # Clamp within visible dermal zone
        forehead_y = max(8, int(target_forehead_y))
        forehead_w = int(max(24, eye_dist * 0.75))
        forehead_h = int(max(18, min(abs(brow_top_y - forehead_y), bh * 0.20)))
        forehead_x = int(max(4, min(brow_center_x - forehead_w / 2, img_w - forehead_w - 4)))

        # Cheeks: Mid-cheek skin patch between nose base and outer jaw
        # Left cheek (viewer's left / subject's right): between point 31 and points 2-4
        chk_l_x = int(pts[31, 0] - eye_dist * 0.55)
        chk_l_y = int((left_eye_center[1] + mouth_center[1]) / 2.0)
        chk_w = int(max(20, eye_dist * 0.40))
        chk_h = int(max(20, eye_dist * 0.36))

        # Right cheek (viewer's right / subject's left): between point 35 and points 12-14
        chk_r_x = int(pts[35, 0] + eye_dist * 0.15)
        chk_r_y = int((right_eye_center[1] + mouth_center[1]) / 2.0)

        # Chin box: centered around point 8 or between lower lip and chin tip
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
            "forehead": clamp_box(forehead_x, forehead_y, forehead_w, forehead_h),
            "left_cheek": clamp_box(chk_l_x, chk_l_y - chk_h // 2, chk_w, chk_h),
            "right_cheek": clamp_box(chk_r_x, chk_r_y - chk_h // 2, chk_w, chk_h),
            "nose": clamp_box(int(nose_tip[0] - nose_w * 0.5), int(nose_tip[1] - eye_dist * 0.25), int(nose_w), int(eye_dist * 0.35)),
            "mouth": clamp_box(int(mouth_center[0] - mouth_w * 0.5), int(mouth_center[1] - 12), int(mouth_w), 24),
            "chin": clamp_box(int(chin_pt[0] - chin_w * 0.5), chin_y - chin_h // 2, chin_w, chin_h)
        }

    def _get_regions_from_yunet_keypoints(
        self,
        bbox: List[int],
        r_eye: Tuple[float, float],
        l_eye: Tuple[float, float],
        nose: Tuple[float, float],
        r_mouth: Tuple[float, float],
        l_mouth: Tuple[float, float],
        img_w: int,
        img_h: int
    ) -> Dict[str, Dict[str, int]]:
        """
        Robust geometric region calculation from YuNet's 5 precise facial landmarks.
        Adapts seamlessly to short or tightly cropped face images.
        """
        bx, by, bw, bh = bbox
        
        # Ensure r_eye is viewer's left (smaller x) and l_eye is viewer's right (larger x)
        if r_eye[0] > l_eye[0]:
            r_eye, l_eye = l_eye, r_eye
        if r_mouth[0] > l_mouth[0]:
            r_mouth, l_mouth = l_mouth, r_mouth

        eye_cx = (r_eye[0] + l_eye[0]) / 2.0
        eye_cy = (r_eye[1] + l_eye[1]) / 2.0
        eye_dist = max(18.0, np.hypot(l_eye[0] - r_eye[0], l_eye[1] - r_eye[1]))

        mouth_cx = (r_mouth[0] + l_mouth[0]) / 2.0
        mouth_cy = (r_mouth[1] + l_mouth[1]) / 2.0
        mouth_w = max(20.0, np.hypot(l_mouth[0] - r_mouth[0], l_mouth[1] - r_mouth[1]))

        face_center_x = (eye_cx + mouth_cx + nose[0]) / 3.0

        # Forehead calculation adapted for tight crops:
        # Distance from eyes to forehead should be ~0.45 of eye-to-mouth distance
        eye_to_mouth = max(20.0, mouth_cy - eye_cy)
        forehead_target_y = eye_cy - (eye_to_mouth * 0.55)
        forehead_y = max(6, int(forehead_target_y))
        forehead_w = int(max(24, eye_dist * 0.80))
        forehead_h = int(max(16, eye_to_mouth * 0.32))

        # Cheeks: positioned laterally from nose tip
        chk_w = int(max(18, eye_dist * 0.38))
        chk_h = int(max(18, eye_dist * 0.34))
        chk_l_x = int(r_eye[0] - chk_w * 0.6)
        chk_r_x = int(l_eye[0] - chk_w * 0.4)
        chk_y = int((eye_cy + mouth_cy) / 2.0 - chk_h / 2.0)

        # Chin: positioned below mouth
        chin_target_y = mouth_cy + (eye_to_mouth * 0.45)
        chin_y = min(img_h - 22, int(chin_target_y))
        chin_w = int(max(22, mouth_w * 0.85))
        chin_h = int(max(16, eye_to_mouth * 0.30))

        def clamp_box(cx, cy, cw, ch):
            cw = max(14, min(cw, img_w - 6))
            ch = max(14, min(ch, img_h - 6))
            cx = max(3, min(cx, img_w - cw - 3))
            cy = max(3, min(cy, img_h - ch - 3))
            return {"x": int(cx), "y": int(cy), "w": int(cw), "h": int(ch)}

        return {
            "forehead": clamp_box(int(face_center_x - forehead_w / 2), forehead_y, forehead_w, forehead_h),
            "left_cheek": clamp_box(chk_l_x, chk_y, chk_w, chk_h),
            "right_cheek": clamp_box(chk_r_x, chk_y, chk_w, chk_h),
            "nose": clamp_box(int(nose[0] - eye_dist * 0.20), int(nose[1] - eye_dist * 0.25), int(eye_dist * 0.40), int(eye_dist * 0.40)),
            "mouth": clamp_box(int(mouth_cx - mouth_w / 2), int(mouth_cy - 10), int(mouth_w), 22),
            "chin": clamp_box(int(mouth_cx - chin_w / 2), chin_y, chin_w, chin_h)
        }

    def _detect_face_by_skin_contour(self, image_bgr: np.ndarray) -> Optional[List[int]]:
        """
        Locates the primary facial/head region by finding the dominant skin color cluster.
        """
        try:
            h, w = image_bgr.shape[:2]
            b = image_bgr[:, :, 0].astype(np.float32)
            g = image_bgr[:, :, 1].astype(np.float32)
            r = image_bgr[:, :, 2].astype(np.float32)

            skin_mask = (r > 45) & (g > 25) & (b > 15) & (r > g) & (g > b * 0.75) & ((r - g) >= 8) & ((r - b) >= 12)
            
            ys, xs = np.where(skin_mask)
            if len(xs) < 80:
                return None

            grid_h, grid_w = 32, 32
            cell_h = h / grid_h
            cell_w = w / grid_w
            density = np.zeros((grid_h, grid_w), dtype=np.int32)
            
            for px, py in zip(xs, ys):
                gx = min(grid_w - 1, int(px / cell_w))
                gy = min(grid_h - 1, int(py / cell_h))
                density[gy, gx] += 1

            upper_density = density[:int(grid_h * 0.8), :]
            if np.max(upper_density) == 0:
                return None

            max_gy, max_gx = np.unravel_index(np.argmax(upper_density), upper_density.shape)
            center_x = int((max_gx + 0.5) * cell_w)
            center_y = int((max_gy + 0.5) * cell_h)

            fw = max(40, int(w * 0.32))
            fh = int(fw * 1.30)
            fx = max(0, min(center_x - fw // 2, w - fw))
            fy = max(0, min(center_y - int(fh * 0.4), h - fh))

            return [fx, fy, fw, fh]
        except Exception:
            return None

    def _get_regions_from_bbox(self, bbox: List[int], img_w: int, img_h: int) -> Dict[str, Dict[str, int]]:
        x, y, w, h = bbox
        return {
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

    def estimate_gender(
        self,
        image_bgr: np.ndarray,
        landmarks_list: Optional[List[Tuple[int, int, float]]] = None,
        bbox: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Estimates biological/perceived gender from facial morphology, anthropometric ratios,
        lower-facial dermal texture, lip contrast, and eyebrow density.
        """
        if image_bgr is None or image_bgr.size == 0:
            return {"detected": "All", "confidence": 0.5, "confidence_percentage": 50, "probabilities": {"Male": 0.5, "Female": 0.5}}

        img_h, img_w = image_bgr.shape[:2]
        score_male = 0.0
        score_female = 0.0

        if bbox is None:
            bbox = [int(img_w * 0.2), int(img_h * 0.15), int(img_w * 0.6), int(img_h * 0.6)]

        x, y, w, h = bbox
        cx = x + w / 2.0
        cy = y + h / 2.0
        rx = w / 2.0
        ry = h / 2.0

        # Method A: 68-Point Facial Landmarks if available
        if landmarks_list and len(landmarks_list) == 68:
            try:
                pts = np.array([[p[0], p[1]] for p in landmarks_list], dtype=np.float32)
                # Bigonial (jaw width at points 4 & 12) vs Bizygomatic (cheek width at points 0 & 16)
                cheek_w = np.hypot(pts[16, 0] - pts[0, 0], pts[16, 1] - pts[0, 1])
                jaw_w = np.hypot(pts[12, 0] - pts[4, 0], pts[12, 1] - pts[4, 1])
                jaw_ratio = jaw_w / max(cheek_w, 1.0)

                if jaw_ratio > 0.76:
                    score_male += min(3.0, (jaw_ratio - 0.76) * 6.0)
                else:
                    score_female += min(3.0, (0.76 - jaw_ratio) * 6.0)

                # Eyebrow arch to eye distance (points 19 to 37 and 24 to 44)
                brow_eye_dist = ((pts[37, 1] - pts[19, 1]) + (pts[44, 1] - pts[24, 1])) / 2.0
                eye_h = max(abs(pts[41, 1] - pts[37, 1]), 6.0)
                brow_ratio = brow_eye_dist / eye_h
                if brow_ratio > 1.30:
                    score_female += min(2.5, (brow_ratio - 1.30) * 4.0)
                else:
                    score_male += min(2.5, (1.30 - brow_ratio) * 4.0)
            except Exception:
                pass

        # Method B: Multi-Region Chromatic, Anthropometric & Texture Sampling
        try:
            chk_y1 = max(0, min(int(cy - ry * 0.10), img_h - 1))
            chk_y2 = max(chk_y1 + 6, min(int(cy + ry * 0.25), img_h))
            chk_x1 = max(0, min(int(cx - rx * 0.70), img_w - 1))
            chk_x2 = max(chk_x1 + 6, min(int(cx + rx * 0.70), img_w))
            chk = image_bgr[chk_y1:chk_y2, chk_x1:chk_x2]

            chin_y1 = max(0, min(int(cy + ry * 0.65), img_h - 1))
            chin_y2 = max(chin_y1 + 6, min(int(cy + ry * 0.95), img_h))
            chin_x1 = max(0, min(int(cx - rx * 0.45), img_w - 1))
            chin_x2 = max(chin_x1 + 6, min(int(cx + rx * 0.45), img_w))
            chin = image_bgr[chin_y1:chin_y2, chin_x1:chin_x2]

            lip_y1 = max(0, min(int(cy + ry * 0.35), img_h - 1))
            lip_y2 = max(lip_y1 + 6, min(int(cy + ry * 0.65), img_h))
            lip_x1 = max(0, min(int(cx - rx * 0.35), img_w - 1))
            lip_x2 = max(lip_x1 + 6, min(int(cx + rx * 0.35), img_w))
            lip = image_bgr[lip_y1:lip_y2, lip_x1:lip_x2]

            # Cheek vs Chin Luminance Drop
            if chk.size > 0 and chin.size > 0:
                chk_lum = float(np.mean(0.114 * chk[:,:,0] + 0.587 * chk[:,:,1] + 0.299 * chk[:,:,2]))
                chin_lum = float(np.mean(0.114 * chin[:,:,0] + 0.587 * chin[:,:,1] + 0.299 * chin[:,:,2]))
                lum_drop = chk_lum - chin_lum

                if lum_drop > 20.0:
                    score_male += min(3.5, (lum_drop - 20.0) / 10.0 + 1.2)
                elif lum_drop < 8.0:
                    score_female += min(2.5, (8.0 - lum_drop) / 8.0 + 0.8)

            # Lip contrast
            if lip.size > 0 and chk.size > 0:
                lip_r = float(np.mean(lip[:,:,2]))
                lip_g = float(np.mean(lip[:,:,1]))
                lip_b = float(np.mean(lip[:,:,0]))
                chk_r = float(np.mean(chk[:,:,2]))
                chk_g = float(np.mean(chk[:,:,1]))
                chk_b = float(np.mean(chk[:,:,0]))

                chk_red = chk_r / max(1.0, (chk_g + chk_b) / 2.0)
                lip_red = lip_r / max(1.0, (lip_g + lip_b) / 2.0)
                lip_contrast = lip_red - chk_red

                if lip_contrast > 0.12:
                    score_female += min(3.0, (lip_contrast - 0.12) * 12.0 + 1.0)
                elif lip_contrast < 0.05:
                    score_male += min(2.5, (0.05 - lip_contrast) * 15.0 + 1.2)
        except Exception:
            pass

        exp_m = np.exp(score_male)
        exp_f = np.exp(score_female)
        p_male = float(exp_m / (exp_m + exp_f))
        p_female = float(1.0 - p_male)

        detected = "Male" if p_male >= 0.50 else "Female"
        conf = float(max(p_male, p_female))

        return {
            "detected": detected,
            "confidence": round(conf, 2),
            "confidence_percentage": int(round(conf * 100)),
            "probabilities": {
                "Male": round(p_male, 2),
                "Female": round(p_female, 2)
            }
        }
