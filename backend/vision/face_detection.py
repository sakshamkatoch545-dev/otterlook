"""
Face Detection and Facial Landmark Localization Module.
Uses MediaPipe Face Mesh / Face Detection with an OpenCV fallback cascade.
Ensures single-person validation and extracts landmarks for skin region targeting.
"""

import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

class FaceDetector:
    def __init__(self):
        self.mp_face_mesh = None
        self.mp_drawing = None
        self.haar_cascade = None
        self._init_detectors()

    def _init_detectors(self):
        try:
            import mediapipe as mp
            # Try new or legacy mediapipe API
            if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'face_mesh'):
                self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
                    static_image_mode=True,
                    max_num_faces=3,
                    refine_landmarks=True,
                    min_detection_confidence=0.5
                )
            elif hasattr(mp, 'tasks'):
                # Newer task-based or fallback
                pass
        except Exception as e:
            print(f"[FaceDetector] MediaPipe FaceMesh init note: {e}")

        # Initialize OpenCV Haar Cascade as robust fallback / multi-face verifier
        try:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self.haar_cascade = cv2.CascadeClassifier(cascade_path)
        except Exception as e:
            print(f"[FaceDetector] Haar cascade load note: {e}")

    def detect_faces(self, image_bgr: np.ndarray) -> Dict[str, Any]:
        """
        Detects faces in the image, checks single-face constraint,
        and extracts landmarks or bounding boxes.
        
        Returns:
            Dict containing:
                - success: bool
                - face_count: int
                - message: str
                - landmarks: list of normalized (x, y, z) or pixel coordinates
                - bounding_box: [x, y, w, h] in pixels
                - regions: dictionary of anatomical ROI pixel boxes
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
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

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

                    # Extract anatomical skin regions from landmark indices
                    regions = self._get_regions_from_landmarks(landmarks_list, w, h)

                    return {
                        "success": True,
                        "face_count": 1,
                        "message": "Face detected successfully with landmark mesh.",
                        "detector_type": "mediapipe_facemesh",
                        "landmarks": landmarks_list,
                        "bounding_box": bbox,
                        "regions": regions
                    }
            except Exception as e:
                print(f"[FaceDetector] MediaPipe processing error: {e}. Falling back to OpenCV.")

        # 2. Fallback: OpenCV Cascade / Multi-scale detector
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        faces = []
        if self.haar_cascade is not None and not self.haar_cascade.empty():
            # Try standard scale
            faces = self.haar_cascade.detectMultiScale(
                gray, scaleFactor=1.05, minNeighbors=3, minSize=(int(w * 0.15), int(h * 0.15))
            )

        if len(faces) == 0:
            # 3. Geometric / Skin-contour fallback for stylized portraits or soft-lit faces
            ycrcb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2YCrCb)
            cr = ycrcb[:, :, 1]
            cb = ycrcb[:, :, 2]
            skin_mask = (cr >= 125) & (cr <= 180) & (cb >= 70) & (cb <= 140)
            skin_mask = (skin_mask.astype(np.uint8)) * 255
            
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
            skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
            skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)
            
            contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            valid_contours = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > (w * h * 0.08):  # at least 8% of image area
                    valid_contours.append(cnt)
                    
            if len(valid_contours) == 1:
                cnt = valid_contours[0]
                bx, by, bw, bh = cv2.boundingRect(cnt)
                # Check reasonable aspect ratio for a face
                aspect_ratio = bh / float(bw)
                if 0.7 <= aspect_ratio <= 2.2:
                    bbox = [int(bx), int(by), int(bw), int(bh)]
                    regions = self._get_regions_from_bbox(bbox, w, h)
                    return {
                        "success": True,
                        "face_count": 1,
                        "message": "Face localized successfully via skin contour analysis.",
                        "detector_type": "skin_contour_fallback",
                        "landmarks": None,
                        "bounding_box": bbox,
                        "regions": regions
                    }
            elif len(valid_contours) > 1:
                return {
                    "success": False,
                    "face_count": len(valid_contours),
                    "message": "Please upload an image containing only one person.",
                    "landmarks": None,
                    "bounding_box": None,
                    "regions": {}
                }

            return {
                "success": False,
                "face_count": 0,
                "message": "Unable to detect a face. Please upload a clear front-facing image.",
                "landmarks": None,
                "bounding_box": None,
                "regions": {}
            }
        elif len(faces) > 1:
            return {
                "success": False,
                "face_count": len(faces),
                "message": "Please upload an image containing only one person.",
                "landmarks": None,
                "bounding_box": None,
                "regions": {}
            }

        (fx, fy, fw, fh) = faces[0]
        bbox = [int(fx), int(fy), int(fw), int(fh)]
        regions = self._get_regions_from_bbox(bbox, w, h)

        return {
            "success": True,
            "face_count": 1,
            "message": "Face detected successfully.",
            "detector_type": "opencv_cascade",
            "landmarks": None,
            "bounding_box": bbox,
            "regions": regions
        }

    def _get_regions_from_landmarks(self, lms: List[Tuple[int, int, float]], img_w: int, img_h: int) -> Dict[str, Dict[str, int]]:
        """
        Uses MediaPipe landmark anchors to carve precise skin patches:
        - Forehead (lm 10, 9, 151)
        - Left cheek (lm 118, 50, 101)
        - Right cheek (lm 347, 280, 330)
        - Chin / Jaw (lm 152, 175)
        """
        def clamp_box(cx, cy, radius_x, radius_y):
            x1 = max(0, cx - radius_x)
            y1 = max(0, cy - radius_y)
            x2 = min(img_w, cx + radius_x)
            y2 = min(img_h, cy + radius_y)
            return {"x": int(x1), "y": int(y1), "w": int(x2 - x1), "h": int(y2 - y1)}

        # Approximate face scale
        face_w = abs(lms[454][0] - lms[234][0]) if len(lms) > 454 else 100
        rx = max(10, int(face_w * 0.08))
        ry = max(10, int(face_w * 0.08))

        # Forehead center around landmark 10 (top) and 9/151
        forehead_pt = lms[10] if len(lms) > 10 else (img_w//2, img_h//3, 0)
        # Shift slightly down from top hairline
        f_cy = forehead_pt[1] + int(ry * 0.8)
        forehead_box = clamp_box(forehead_pt[0], f_cy, int(rx * 1.5), ry)

        # Left Cheek (viewer's left / face's right or lm 118, 50)
        l_cheek_pt = lms[118] if len(lms) > 118 else lms[50]
        left_cheek_box = clamp_box(l_cheek_pt[0], l_cheek_pt[1], rx, ry)

        # Right Cheek (viewer's right / face's left or lm 347, 280)
        r_cheek_pt = lms[347] if len(lms) > 347 else lms[280]
        right_cheek_box = clamp_box(r_cheek_pt[0], r_cheek_pt[1], rx, ry)

        # Chin / Jaw around landmark 152 / 175
        chin_pt = lms[175] if len(lms) > 175 else lms[152]
        chin_box = clamp_box(chin_pt[0], chin_pt[1] - int(ry * 0.5), int(rx * 1.2), ry)

        return {
            "forehead": forehead_box,
            "left_cheek": left_cheek_box,
            "right_cheek": right_cheek_box,
            "chin": chin_box
        }

    def _get_regions_from_bbox(self, bbox: List[int], img_w: int, img_h: int) -> Dict[str, Dict[str, int]]:
        """
        Geometrically extracts anatomically sound skin regions from a face bounding box.
        """
        x, y, w, h = bbox
        
        # Forehead: top 12% to 28% of face height, middle 40% width
        f_x = int(x + w * 0.30)
        f_y = int(y + h * 0.12)
        f_w = int(w * 0.40)
        f_h = int(h * 0.16)

        # Left Cheek (viewer's left): 45% to 65% height, 15% to 35% width
        lc_x = int(x + w * 0.15)
        lc_y = int(y + h * 0.48)
        lc_w = int(w * 0.20)
        lc_h = int(h * 0.18)

        # Right Cheek (viewer's right): 45% to 65% height, 65% to 85% width
        rc_x = int(x + w * 0.65)
        rc_y = int(y + h * 0.48)
        rc_w = int(w * 0.20)
        rc_h = int(h * 0.18)

        # Chin: 80% to 92% height, 35% to 65% width
        ch_x = int(x + w * 0.35)
        ch_y = int(y + h * 0.80)
        ch_w = int(w * 0.30)
        ch_h = int(h * 0.12)

        return {
            "forehead": {"x": max(0, f_x), "y": max(0, f_y), "w": min(f_w, img_w - f_x), "h": min(f_h, img_h - f_y)},
            "left_cheek": {"x": max(0, lc_x), "y": max(0, lc_y), "w": min(lc_w, img_w - lc_x), "h": min(lc_h, img_h - lc_y)},
            "right_cheek": {"x": max(0, rc_x), "y": max(0, rc_y), "w": min(rc_w, img_w - rc_x), "h": min(rc_h, img_h - rc_y)},
            "chin": {"x": max(0, ch_x), "y": max(0, ch_y), "w": min(ch_w, img_w - ch_x), "h": min(ch_h, img_h - ch_y)}
        }
