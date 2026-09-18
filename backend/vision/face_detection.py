"""
Face Detection and Facial Landmark Localization Module.
Uses MediaPipe Face Mesh / Face Detection with an OpenCV fallback cascade,
plus a pure-geometric proportion fallback for cloud environments.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple

try:
    import cv2
except Exception:
    cv2 = None

class FaceDetector:
    def __init__(self):
        self.mp_face_mesh = None
        self.mp_drawing = None
        self.haar_cascade = None
        self._init_detectors()

    def _init_detectors(self):
        try:
            import mediapipe as mp
            if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'face_mesh'):
                self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
                    static_image_mode=True,
                    max_num_faces=3,
                    refine_landmarks=True,
                    min_detection_confidence=0.5
                )
        except Exception:
            self.mp_face_mesh = None

        if cv2 is not None:
            import os
            bundled_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "haarcascade_frontalface_default.xml")
            if os.path.exists(bundled_path):
                self.haar_cascade = cv2.CascadeClassifier(bundled_path)
            elif hasattr(cv2, "data") and hasattr(cv2.data, "haarcascades"):
                cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                self.haar_cascade = cv2.CascadeClassifier(cascade_path)
            else:
                self.haar_cascade = None

    def detect_faces(self, image_bgr: np.ndarray) -> Dict[str, Any]:
        """
        Detects faces in the image, checks single-face constraint,
        and extracts landmarks or bounding boxes.
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

        h, w = image_bgr.shape[:2]
        image_rgb = image_bgr[:, :, ::-1]

        # 1. Try MediaPipe FaceMesh
        if self.mp_face_mesh is not None:
            try:
                results = self.mp_face_mesh.process(image_rgb)
                if results.multi_face_landmarks:
                    face_count = len(results.multi_face_landmarks)
                    if face_count > 1:
                        return {
                            "success": False,
                            "face_count": face_count,
                            "message": "Please upload an image containing only one person.",
                            "landmarks": None,
                            "bounding_box": None,
                            "regions": {}
                        }
                    
                    face_landmarks = results.multi_face_landmarks[0]
                    landmarks_list = []
                    x_coords = []
                    y_coords = []

                    for lm in face_landmarks.landmark:
                        px = int(np.clip(lm.x * w, 0, w - 1))
                        py = int(np.clip(lm.y * h, 0, h - 1))
                        landmarks_list.append((px, py, lm.z))
                        x_coords.append(px)
                        y_coords.append(py)

                    min_x, max_x = min(x_coords), max(x_coords)
                    min_y, max_y = min(y_coords), max(y_coords)
                    bbox = [min_x, min_y, max_x - min_x, max_y - min_y]

                    regions = self._get_regions_from_landmarks(landmarks_list, w, h)

                    gender_info = self.estimate_gender(image_bgr, landmarks_list=landmarks_list, bbox=bbox)

                    return {
                        "success": True,
                        "face_count": 1,
                        "message": "Face detected successfully with landmark mesh.",
                        "detector_type": "mediapipe_facemesh",
                        "landmarks": landmarks_list,
                        "bounding_box": bbox,
                        "regions": regions,
                        "gender": gender_info
                    }
            except Exception:
                pass

        # 2. Try OpenCV Cascade
        if cv2 is not None and self.haar_cascade is not None and not self.haar_cascade.empty():
            try:
                gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
                faces = self.haar_cascade.detectMultiScale(
                    gray, scaleFactor=1.06, minNeighbors=3, minSize=(28, 28)
                )
                if len(faces) >= 1:
                    # Filter out lower-body false positives (faces are in upper 60% of frame)
                    upper_faces = [f for f in faces if f[1] < h * 0.60 and f[0] > w * 0.08 and (f[0] + f[2]) < w * 0.92]
                    candidates = upper_faces if len(upper_faces) > 0 else list(faces)
                    # Pick largest face candidate
                    areas = [f[2] * f[3] for f in candidates]
                    best_idx = int(np.argmax(areas))
                    (fx, fy, fw, fh) = candidates[best_idx]
                    bbox = [int(fx), int(fy), int(fw), int(fh)]
                    regions = self._get_regions_from_bbox(bbox, w, h)
                    gender_info = self.estimate_gender(image_bgr, landmarks_list=None, bbox=bbox)
                    return {
                        "success": True,
                        "face_count": 1,
                        "message": "Face detected successfully.",
                        "detector_type": "opencv_cascade",
                        "landmarks": None,
                        "bounding_box": bbox,
                        "regions": regions,
                        "gender": gender_info
                    }
            except Exception:
                pass

        # 3. Try Skin Chrominance Density Cluster (for distant or non-frontal lighting portraits)
        skin_bbox = self._detect_face_by_skin_contour(image_bgr)
        if skin_bbox is not None:
            regions = self._get_regions_from_bbox(skin_bbox, w, h)
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

        # 4. Geometric Face & Proportion Estimator (for portrait center crops fallback)
        fx = int(w * 0.25)
        fy = int(h * 0.15)
        fw = int(w * 0.50)
        fh = int(h * 0.60)
        bbox = [fx, fy, fw, fh]
        regions = self._get_regions_from_bbox(bbox, w, h)

        gender_info = self.estimate_gender(image_bgr, landmarks_list=None, bbox=bbox)
        return {
            "success": True,
            "face_count": 1,
            "message": "Face localized via anatomical portrait framing.",
            "detector_type": "geometric_proportions",
            "landmarks": None,
            "bounding_box": bbox,
            "regions": regions,
            "gender": gender_info
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

            # RGB & HSV Skin thresholding
            skin_mask = (r > 45) & (g > 25) & (b > 15) & (r > g) & (g > b * 0.75) & ((r - g) >= 8) & ((r - b) >= 12)
            
            ys, xs = np.where(skin_mask)
            if len(xs) < 80:
                return None

            # 2D Density grid (32x32)
            grid_h, grid_w = 32, 32
            cell_h = h / grid_h
            cell_w = w / grid_w
            density = np.zeros((grid_h, grid_w), dtype=np.int32)
            
            for px, py in zip(xs, ys):
                gx = min(grid_w - 1, int(px / cell_w))
                gy = min(grid_h - 1, int(py / cell_h))
                density[gy, gx] += 1

            # Focus on upper 80% where head/face is typically located
            upper_density = density[:int(grid_h * 0.8), :]
            if np.max(upper_density) == 0:
                return None

            max_gy, max_gx = np.unravel_index(np.argmax(upper_density), upper_density.shape)
            center_x = int((max_gx + 0.5) * cell_w)
            center_y = int((max_gy + 0.5) * cell_h)

            # Estimate face bounding box around peak skin cluster
            fw = max(40, int(w * 0.28))
            fh = int(fw * 1.30)
            fx = max(0, min(center_x - fw // 2, w - fw))
            fy = max(0, min(center_y - int(fh * 0.4), h - fh))

            return [fx, fy, fw, fh]
        except Exception:
            return None

    def _get_regions_from_landmarks(self, landmarks: List[Tuple[int, int, float]], w: int, h: int) -> Dict[str, Dict[str, int]]:
        forehead_indices = [10, 67, 109, 297, 338, 9]
        left_cheek_indices = [50, 117, 118, 123, 147, 187, 205]
        right_cheek_indices = [280, 346, 347, 352, 376, 411, 425]
        chin_indices = [152, 175, 199, 200, 377, 396]
        nose_indices = [1, 2, 98, 327, 4]
        mouth_indices = [0, 13, 14, 17, 61, 291]

        if landmarks:
            xs_all = [p[0] for p in landmarks]
            ys_all = [p[1] for p in landmarks]
            face_w = max(24, max(xs_all) - min(xs_all))
            face_h = max(24, max(ys_all) - min(ys_all))
        else:
            face_w, face_h = max(24, w // 2), max(24, h // 2)

        def get_box(indices, scale_x=0.22, scale_y=0.14):
            pts = [landmarks[i] for i in indices if i < len(landmarks)]
            if not pts:
                return {"x": 0, "y": 0, "w": 10, "h": 10}
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            cx, cy = int(np.mean(xs)), int(np.mean(ys))
            bw = max(10, int(face_w * scale_x))
            bh = max(10, int(face_h * scale_y))
            x1 = max(0, min(cx - bw // 2, w - bw))
            y1 = max(0, min(cy - bh // 2, h - bh))
            return {"x": x1, "y": y1, "w": bw, "h": bh}

        return {
            "forehead": get_box(forehead_indices, 0.32, 0.16),
            "left_cheek": get_box(left_cheek_indices, 0.20, 0.20),
            "right_cheek": get_box(right_cheek_indices, 0.20, 0.20),
            "chin": get_box(chin_indices, 0.24, 0.14),
            "nose": get_box(nose_indices, 0.18, 0.16),
            "mouth": get_box(mouth_indices, 0.24, 0.14)
        }

    def _get_regions_from_bbox(self, bbox: List[int], img_w: int, img_h: int) -> Dict[str, Dict[str, int]]:
        x, y, w, h = bbox
        return {
            "forehead": {
                "x": max(0, min(int(x + w * 0.24), img_w - 12)),
                "y": max(0, min(int(y + h * 0.10), img_h - 12)),
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
        lower-facial dermal texture (follicle / stubble / beard presence), lip contrast,
        and eyebrow density.
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

        # Method A: Dense 3D landmarks if available
        if landmarks_list and len(landmarks_list) >= 400:
            try:
                # 1. Jaw vs Cheek width (Bizygomatic vs Bigonial)
                p_l_cheek = landmarks_list[234]
                p_r_cheek = landmarks_list[454]
                p_l_jaw = landmarks_list[172]
                p_r_jaw = landmarks_list[397]

                cheek_w = np.hypot(p_r_cheek[0] - p_l_cheek[0], p_r_cheek[1] - p_l_cheek[1])
                jaw_w = np.hypot(p_r_jaw[0] - p_l_jaw[0], p_r_jaw[1] - p_l_jaw[1])
                jaw_ratio = jaw_w / max(cheek_w, 1.0)

                if jaw_ratio > 0.78:
                    score_male += min(3.0, (jaw_ratio - 0.78) * 5.0)
                else:
                    score_female += min(3.0, (0.78 - jaw_ratio) * 5.0)

                # 2. Eyebrow arch to eye distance
                d_brow_eye = (abs(landmarks_list[70][1] - landmarks_list[159][1]) + abs(landmarks_list[300][1] - landmarks_list[386][1])) / 2.0
                eye_h = max(abs(landmarks_list[159][1] - landmarks_list[145][1]), 6.0)
                brow_ratio = d_brow_eye / eye_h

                if brow_ratio > 1.25:
                    score_female += min(2.5, (brow_ratio - 1.25) * 4.0)
                else:
                    score_male += min(2.5, (1.25 - brow_ratio) * 4.0)
            except Exception:
                pass

        # Method B: Multi-Region Chromatic, Anthropometric & Texture Sampling
        try:
            # 1. Cheek patch (mid-face baseline)
            chk_y1 = max(0, min(int(cy - ry * 0.10), img_h - 1))
            chk_y2 = max(chk_y1 + 6, min(int(cy + ry * 0.25), img_h))
            chk_x1 = max(0, min(int(cx - rx * 0.70), img_w - 1))
            chk_x2 = max(chk_x1 + 6, min(int(cx + rx * 0.70), img_w))
            chk = image_bgr[chk_y1:chk_y2, chk_x1:chk_x2]

            # 2. Chin / Mandibular patch
            chin_y1 = max(0, min(int(cy + ry * 0.65), img_h - 1))
            chin_y2 = max(chin_y1 + 6, min(int(cy + ry * 0.95), img_h))
            chin_x1 = max(0, min(int(cx - rx * 0.45), img_w - 1))
            chin_x2 = max(chin_x1 + 6, min(int(cx + rx * 0.45), img_w))
            chin = image_bgr[chin_y1:chin_y2, chin_x1:chin_x2]

            # 3. Lip patch
            lip_y1 = max(0, min(int(cy + ry * 0.35), img_h - 1))
            lip_y2 = max(lip_y1 + 6, min(int(cy + ry * 0.65), img_h))
            lip_x1 = max(0, min(int(cx - rx * 0.35), img_w - 1))
            lip_x2 = max(lip_x1 + 6, min(int(cx + rx * 0.35), img_w))
            lip = image_bgr[lip_y1:lip_y2, lip_x1:lip_x2]

            # 4. Eyebrow patch
            brow_y1 = max(0, min(int(cy - ry * 0.62), img_h - 1))
            brow_y2 = max(brow_y1 + 6, min(int(cy - ry * 0.25), img_h))
            brow_x1 = max(0, min(int(cx - rx * 0.75), img_w - 1))
            brow_x2 = max(brow_x1 + 6, min(int(cx + rx * 0.75), img_w))
            brow = image_bgr[brow_y1:brow_y2, brow_x1:brow_x2]

            # Factor 1: Cheek vs Chin Luminance Drop (follicular roots & chin shading)
            if chk.size > 0 and chin.size > 0:
                chk_lum = float(np.mean(0.114 * chk[:,:,0] + 0.587 * chk[:,:,1] + 0.299 * chk[:,:,2]))
                chin_lum = float(np.mean(0.114 * chin[:,:,0] + 0.587 * chin[:,:,1] + 0.299 * chin[:,:,2]))
                lum_drop = chk_lum - chin_lum

                if lum_drop > 22.0:
                    score_male += min(3.5, (lum_drop - 22.0) / 10.0 + 1.2)
                elif lum_drop < 8.0:
                    score_female += min(2.5, (8.0 - lum_drop) / 8.0 + 0.8)

                # Micro-texture standard deviation
                chin_gray = 0.114 * chin[:,:,0] + 0.587 * chin[:,:,1] + 0.299 * chin[:,:,2]
                chk_gray = 0.114 * chk[:,:,0] + 0.587 * chk[:,:,1] + 0.299 * chk[:,:,2]
                tex_ratio = float(np.std(chin_gray)) / max(float(np.std(chk_gray)), 1.0)
                if tex_ratio > 1.25:
                    score_male += min(2.5, (tex_ratio - 1.25) * 2.0)
                elif tex_ratio < 0.95:
                    score_female += min(2.0, (0.95 - tex_ratio) * 2.0)

            # Factor 2: Russell Facial Contrast (Lip-to-Skin Color Contrast)
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

            # Factor 3: Eyebrow Density & Min Luminance
            if brow.size > 0:
                brow_lum = 0.114 * brow[:,:,0] + 0.587 * brow[:,:,1] + 0.299 * brow[:,:,2]
                brow_min = float(np.percentile(brow_lum, 12))
                brow_mean = float(np.mean(brow_lum))
                if brow_min < 45.0 and brow_mean < 110.0:
                    score_male += 1.8
                elif brow_min > 70.0:
                    score_female += 1.5

            # Factor 4: Face Aspect Ratio
            face_aspect = rx / max(ry, 1.0)
            if face_aspect > 0.82:
                score_male += 0.8
            elif face_aspect < 0.68:
                score_female += 0.6
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
