"""
Facial Biometric Feature Extractor for Otterlook AI.
Computes a robust 128-dimensional normalized biometric face embedding
combining geometric landmark ratios, normalized spatial facial gradients,
and dermal colorimetric signatures.
"""

import math
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
import cv2

EMBEDDING_DIM = 128


def extract_face_embedding(
    image_bgr: np.ndarray,
    bbox: List[int],
    landmarks: Optional[List[Tuple[int, int, float]]] = None,
    skin_result: Optional[Dict[str, Any]] = None
) -> np.ndarray:
    """
    Extracts a scale-invariant, lighting-tolerant 128-dimensional facial biometric
    embedding vector from the given face crop and landmark data.
    
    Returns:
        np.ndarray of shape (128,) with dtype np.float32 and L2 unit norm.
    """
    if image_bgr is None or image_bgr.size == 0 or not bbox or len(bbox) < 4:
        # Fallback to zero embedding
        v = np.zeros(EMBEDDING_DIM, dtype=np.float32)
        v[0] = 1.0
        return v

    img_h, img_w = image_bgr.shape[:2]
    x, y, w, h = bbox
    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(img_w, x + w)
    y2 = min(img_h, y + h)

    if (x2 - x1) < 10 or (y2 - y1) < 10:
        v = np.zeros(EMBEDDING_DIM, dtype=np.float32)
        v[0] = 1.0
        return v

    face_crop = image_bgr[y1:y2, x1:x2]

    # ---------------------------------------------------------
    # Part 1: Geometric Landmark Ratios (48 dimensions)
    # ---------------------------------------------------------
    geom_features = np.zeros(48, dtype=np.float32)

    if landmarks and len(landmarks) >= 5:
        lms_arr = np.array([[p[0], p[1]] for p in landmarks], dtype=np.float32)
        
        # Center coordinates relative to bbox center
        cx, cy = x + w / 2.0, y + h / 2.0
        norm_lms = (lms_arr - [cx, cy]) / [max(1.0, float(w)), max(1.0, float(h))]

        if len(landmarks) == 68:
            # Full 68-point Facemark landmarks
            # Eyes: Left eye (36-41), Right eye (42-47)
            left_eye_center = np.mean(norm_lms[36:42], axis=0)
            right_eye_center = np.mean(norm_lms[42:48], axis=0)
            nose_tip = norm_lms[30]
            mouth_center = np.mean(norm_lms[48:68], axis=0)
            chin = norm_lms[8]

            iod = max(0.01, float(np.linalg.norm(right_eye_center - left_eye_center)))
            
            # Key geometric proportions
            geom_features[0] = iod
            geom_features[1] = float(np.linalg.norm(nose_tip - (left_eye_center + right_eye_center) / 2.0)) / iod
            geom_features[2] = float(np.linalg.norm(mouth_center - nose_tip)) / iod
            geom_features[3] = float(np.linalg.norm(chin - mouth_center)) / iod
            geom_features[4] = float(np.linalg.norm(norm_lms[54] - norm_lms[48])) / iod  # Mouth width
            geom_features[5] = float(h) / max(1.0, float(w))  # Aspect ratio

            # Eye aspect ratios
            left_ear = (np.linalg.norm(norm_lms[37] - norm_lms[41]) + np.linalg.norm(norm_lms[38] - norm_lms[40])) / (2.0 * max(0.01, np.linalg.norm(norm_lms[36] - norm_lms[39])))
            right_ear = (np.linalg.norm(norm_lms[43] - norm_lms[47]) + np.linalg.norm(norm_lms[44] - norm_lms[46])) / (2.0 * max(0.01, np.linalg.norm(norm_lms[42] - norm_lms[45])))
            geom_features[6] = float(left_ear)
            geom_features[7] = float(right_ear)

            # Sample 20 representative landmarks (normalized relative to inter-ocular distance)
            sample_idx = [0, 4, 8, 12, 16, 19, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 62, 66]
            for i, idx in enumerate(sample_idx):
                geom_features[8 + i * 2] = norm_lms[idx, 0] / iod
                geom_features[8 + i * 2 + 1] = norm_lms[idx, 1] / iod
        else:
            # 5 or 6 point landmarks (MediaPipe/YuNet)
            le = norm_lms[0]
            re = norm_lms[1]
            nose = norm_lms[2]
            mouth_r = norm_lms[3]
            mouth_l = norm_lms[4]

            iod = max(0.01, float(np.linalg.norm(re - le)))
            geom_features[0] = iod
            geom_features[1] = float(np.linalg.norm(nose - (le + re) / 2.0)) / iod
            geom_features[2] = float(np.linalg.norm((mouth_r + mouth_l) / 2.0 - nose)) / iod
            geom_features[3] = float(np.linalg.norm(mouth_r - mouth_l)) / iod
            geom_features[4] = float(h) / max(1.0, float(w))

            for i in range(min(5, len(norm_lms))):
                geom_features[5 + i * 2] = norm_lms[i, 0] / iod
                geom_features[5 + i * 2 + 1] = norm_lms[i, 1] / iod
    else:
        # Fallback geometry from zero-centered spatial projection profiles
        geom_features[0] = (float(h) / max(1.0, float(w))) - 1.25  # Zero-centered around standard face aspect 1.25
        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
        resized_gray = cv2.resize(gray, (32, 32)).astype(np.float32)
        mean_g = float(np.mean(resized_gray))
        std_g = max(1.0, float(np.std(resized_gray)))
        proj_x = (np.mean(resized_gray, axis=0) - mean_g) / std_g
        proj_y = (np.mean(resized_gray, axis=1) - mean_g) / std_g
        geom_features[1:17] = proj_x[:16]
        geom_features[17:33] = proj_y[:16]

    # ---------------------------------------------------------
    # Part 2: Spatial Facial Gradient Representation (64 dimensions)
    # ---------------------------------------------------------
    gray_face = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
    aligned_face = cv2.resize(gray_face, (64, 64))
    
    # CLAHE for lighting normalization
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
    norm_face = clahe.apply(aligned_face).astype(np.float32)
    face_mean = float(np.mean(norm_face))
    face_std = max(1.0, float(np.std(norm_face)))

    # Gradients (zero-centered)
    sobel_x = cv2.Sobel(norm_face, cv2.CV_32F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(norm_face, cv2.CV_32F, 0, 1, ksize=3)

    # 4x4 spatial grid (16 blocks, 4 features per block = 64 dimensions)
    spatial_features = np.zeros(64, dtype=np.float32)
    step = 16
    for row in range(4):
        for col in range(4):
            idx = (row * 4 + col) * 4
            block_img = norm_face[row*step:(row+1)*step, col*step:(col+1)*step]
            block_sx = sobel_x[row*step:(row+1)*step, col*step:(col+1)*step]
            block_sy = sobel_y[row*step:(row+1)*step, col*step:(col+1)*step]
            
            # Zero-centered spatial block contrast & signed gradient flow
            spatial_features[idx] = (float(np.mean(block_img)) - face_mean) / face_std
            spatial_features[idx + 1] = float(np.std(block_img)) / face_std
            spatial_features[idx + 2] = float(np.mean(block_sx)) / 100.0
            spatial_features[idx + 3] = float(np.mean(block_sy)) / 100.0

    # ---------------------------------------------------------
    # Part 3: Dermal Colorimetric Signature (16 dimensions)
    # ---------------------------------------------------------
    dermal_features = np.zeros(16, dtype=np.float32)

    # Extract color metrics in zero-centered space
    lab_face = cv2.cvtColor(face_crop, cv2.COLOR_BGR2LAB).astype(np.float32)
    hsv_face = cv2.cvtColor(face_crop, cv2.COLOR_BGR2HSV).astype(np.float32)

    mean_lab = np.mean(lab_face, axis=(0, 1))
    std_lab = np.std(lab_face, axis=(0, 1))
    mean_hsv = np.mean(hsv_face, axis=(0, 1))

    # Zero-centered CIELAB (L* centered at 128, a* and b* centered at neutral 128)
    dermal_features[0] = (float(mean_lab[0]) - 128.0) / 128.0
    dermal_features[1] = (float(mean_lab[1]) - 128.0) / 64.0
    dermal_features[2] = (float(mean_lab[2]) - 128.0) / 64.0
    dermal_features[3] = float(std_lab[0]) / 64.0
    dermal_features[4] = float(std_lab[1]) / 32.0
    dermal_features[5] = float(std_lab[2]) / 32.0

    # Zero-centered HSV (hue centered at 90°, saturation & value centered at 128)
    dermal_features[6] = (float(mean_hsv[0]) - 90.0) / 90.0
    dermal_features[7] = (float(mean_hsv[1]) - 128.0) / 128.0
    dermal_features[8] = (float(mean_hsv[2]) - 128.0) / 128.0

    # Regional skin contrast if available
    if skin_result and "region_samples" in skin_result:
        regions = skin_result["region_samples"]
        cheeks = regions.get("cheeks", {}).get("mean_rgb", [180, 140, 120])
        forehead = regions.get("forehead", {}).get("mean_rgb", [180, 140, 120])
        jawline = regions.get("jawline", {}).get("mean_rgb", [170, 130, 110])

        dermal_features[9] = float(cheeks[0] - forehead[0]) / 50.0
        dermal_features[10] = float(cheeks[1] - forehead[1]) / 50.0
        dermal_features[11] = float(cheeks[2] - forehead[2]) / 50.0
        dermal_features[12] = float(cheeks[0] - jawline[0]) / 50.0
        dermal_features[13] = float(cheeks[1] - jawline[1]) / 50.0
        dermal_features[14] = float(cheeks[2] - jawline[2]) / 50.0
        
        ita = skin_result.get("ita_angle", 20.0)
        dermal_features[15] = float(ita) / 50.0
    else:
        dermal_features[9:16] = 0.0

    # ---------------------------------------------------------
    # Concatenate & L2 Normalize to 128 Dimensions
    # ---------------------------------------------------------
    raw_vector = np.concatenate([geom_features, spatial_features, dermal_features])
    norm = np.linalg.norm(raw_vector)
    if norm > 1e-6:
        embedding = (raw_vector / norm).astype(np.float32)
    else:
        embedding = np.zeros(EMBEDDING_DIM, dtype=np.float32)
        embedding[0] = 1.0

    return embedding


def compute_face_similarity(embedding_a: np.ndarray, embedding_b: np.ndarray) -> float:
    """
    Computes cosine similarity between two face biometric embeddings.
    Returns float in range [-1.0, 1.0] (typically 0.0 to 1.0 for faces).
    """
    if embedding_a is None or embedding_b is None:
        return 0.0
    a = embedding_a.flatten().astype(np.float32)
    b = embedding_b.flatten().astype(np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a < 1e-6 or norm_b < 1e-6:
        return 0.0
    dot = np.dot(a, b) / (norm_a * norm_b)
    return float(np.clip(dot, -1.0, 1.0))
