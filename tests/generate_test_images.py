"""
Utility to generate synthetic facial portrait images for automated testing and UI demonstration.
"""

import os
import cv2
import numpy as np

def create_synthetic_portrait(undertone: str, width: int = 400, height: int = 500) -> np.ndarray:
    """
    Renders a realistic synthetic face with distinct skin tone, eyes, eyebrows, lips, and hair.
    """
    img = np.full((height, width, 3), (240, 240, 245), dtype=np.uint8)
    
    # Background subtle gradient
    for y in range(height):
        factor = y / height
        img[y, :] = (int(235 - 30 * factor), int(240 - 25 * factor), int(245 - 20 * factor))

    # Base skin tone in BGR
    if undertone == "Warm":
        # Golden peachy (higher R, moderate G, lower B)
        skin_bgr = (145, 185, 235)  # B=145, G=185, R=235
    elif undertone == "Cool":
        # Rosy pinkish (higher R, moderate G, higher B)
        skin_bgr = (185, 175, 235)  # B=185, G=175, R=235
    else: # Neutral
        # Balanced beige
        skin_bgr = (165, 180, 225)  # B=165, G=180, R=225

    center_x, center_y = width // 2, int(height * 0.48)
    face_rx, face_ry = int(width * 0.32), int(height * 0.38)

    # Face Oval
    cv2.ellipse(img, (center_x, center_y), (face_rx, face_ry), 0, 0, 360, skin_bgr, -1, cv2.LINE_AA)

    # Hair (dark brown / black)
    hair_color = (30, 25, 40)
    cv2.ellipse(img, (center_x, center_y - int(face_ry * 0.45)), (int(face_rx * 1.08), int(face_ry * 0.65)), 0, 180, 360, hair_color, -1, cv2.LINE_AA)

    # Left & Right Eyebrows
    brow_color = (40, 35, 45)
    cv2.line(img, (center_x - 70, center_y - 70), (center_x - 20, center_y - 75), brow_color, 4, cv2.LINE_AA)
    cv2.line(img, (center_x + 20, center_y - 75), (center_x + 70, center_y - 70), brow_color, 4, cv2.LINE_AA)

    # Left & Right Eyes (Sclera + Iris)
    eye_y = center_y - 45
    for ex in [center_x - 45, center_x + 45]:
        cv2.ellipse(img, (ex, eye_y), (18, 10), 0, 0, 360, (250, 250, 250), -1, cv2.LINE_AA)
        cv2.circle(img, (ex, eye_y), 7, (60, 40, 30), -1, cv2.LINE_AA) # iris
        cv2.circle(img, (ex, eye_y), 3, (15, 10, 10), -1, cv2.LINE_AA) # pupil

    # Nose line
    nose_color = (max(0, skin_bgr[0]-35), max(0, skin_bgr[1]-35), max(0, skin_bgr[2]-35))
    cv2.line(img, (center_x, center_y - 30), (center_x - 5, center_y + 15), nose_color, 2, cv2.LINE_AA)
    cv2.line(img, (center_x - 5, center_y + 15), (center_x + 5, center_y + 15), nose_color, 2, cv2.LINE_AA)

    # Lips
    lip_y = center_y + 60
    if undertone == "Warm":
        lip_color = (120, 130, 210) # warm peachy-coral
    elif undertone == "Cool":
        lip_color = (160, 110, 210) # cool berry-rose
    else:
        lip_color = (140, 120, 200) # neutral rose
    cv2.ellipse(img, (center_x, lip_y), (28, 10), 0, 0, 360, lip_color, -1, cv2.LINE_AA)

    return img

def generate_samples(target_dir: str):
    os.makedirs(target_dir, exist_ok=True)
    for tone in ["Warm", "Cool", "Neutral"]:
        img = create_synthetic_portrait(tone)
        filepath = os.path.join(target_dir, f"sample_{tone.lower()}.jpg")
        cv2.imwrite(filepath, img)
        print(f"Generated sample portrait: {filepath}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    samples_dir = os.path.join(base_dir, "frontend", "assets", "samples")
    generate_samples(samples_dir)
