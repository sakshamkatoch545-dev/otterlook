# AI-Based Personal Colour Analysis and Personalized Colour Palette Recommendation System

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg?style=flat&logo=scikit-learn)](https://scikit-learn.org)
[![OpenCV](https://img.shields.io/badge/Vision-OpenCV-5C3EE8.svg?style=flat&logo=opencv)](https://opencv.org)
[![MediaPipe](https://img.shields.io/badge/Vision-MediaPipe-007FFF.svg?style=flat&logo=google)](https://developers.google.com/mediapipe)
[![Tests](https://img.shields.io/badge/Tests-13%20Passed-brightgreen.svg)](pytest)

---

## 1. Project Title & Overview
**AI-Based Personal Colour Analysis and Personalized Colour Palette Recommendation System** (Otterlook AI) is a major engineering project that bridges computer vision, dermatological colorimetry, and genuine machine learning to detect facial features, isolate anatomical skin regions, extract multi-space colorimetric feature moments, classify the user's skin undertone (**Warm**, **Cool**, or **Neutral**), and generate tailored styling palettes for clothing, makeup, and accessories.

---

## 2. Problem Statement
In personal styling and cosmetic matching, choosing harmonious clothing and makeup colors depends heavily on identifying a person's biological skin **undertone** (the subtle warm, cool, or neutral hue beneath the surface skin pigmentation). Traditional in-person color draping is expensive, subjective, and prone to lighting biases. Existing automated apps frequently rely on naive hard-coded RGB thresholds, which fail across diverse skin phototypes (Fitzpatrick I–VI) and varying camera sensors.

---

## 3. Objectives
1. Automatically detect a single front-facing human face and identify facial landmarks.
2. Segment 4 distinct anatomical skin patches (Forehead, Left Cheek, Right Cheek, Jaw/Chin) while eliminating non-skin elements (eyes, eyebrows, lips, hair, shadows, specular glare).
3. Compute statistical colorimetric feature moments across **sRGB**, **HSV**, and **CIELAB ($L^*a^*b^*$)** spaces, including the **Individual Typology Angle ($\text{ITA}^\circ$)**.
4. Predict undertones using a trained **Machine Learning pipeline** (Random Forest / SVM / Logistic Regression) with real confidence probabilities.
5. Generate categorized, personalized styling recommendations (Wardrobe, Cosmetics, Jewelry & Metals, Neutrals, Colors to Avoid, and Seasonal Harmony).
6. Provide a modern, intuitive, privacy-first web interface with live visual feedback.

---

## 4. Key Features
- **Strict Quality Control:** Pre-analysis checks for resolution, blur (Laplacian variance), brightness clipping, and contrast.
- **Anatomical Multi-Region Extraction:** Prevents single-pixel bias by sampling hundreds of clean skin pixels from anatomical ROIs.
- **Dermatological Color Science:** Leverages the CIELAB $b^*$ (yellow-blue) and $a^*$ (erythema/pink) axes alongside $\text{ITA}^\circ$.
- **Genuine ML Inference:** Serialized `RandomForestClassifier` ensemble saved as `models/undertone_model.pkl` with cross-validation.
- **Visual Landmark Overlay:** Interactive HTML5 Canvas displaying localized skin patches directly on the uploaded portrait.
- **Categorized Recommendations:**
  - 👔 **Clothing:** Core signature colors and casual/formal palettes.
  - 💄 **Makeup:** Foundation undertone advice, lipsticks, blush, and eyeshadow tones.
  - 💍 **Accessories:** Metal compatibility (18k Gold vs. Sterling Silver vs. Rose Gold) & gemstones.
  - ⚪ **Neutral Basics:** Tailored wardrobe anchors.
  - ⚠️ **Colors to Avoid:** Specific clashing hues with stylist explanations.
  - 🌿 **Seasonal Harmony:** 4-Season subtype (Spring, Summer, Autumn, Winter).
- **Privacy & In-Memory Processing:** Images are decoded and analyzed in RAM without persistent server-side storage.

---

## 5. System Architecture & Flow

```
                      [ User Uploads Facial Portrait ]
                                     ↓
                      [ Image Quality Assessment ]
                (Resolution, Blur Variance, Exposure)
                                     ↓
                     [ Face & Landmark Localization ]
                   (MediaPipe FaceMesh / OpenCV Cascade)
                                     ↓
                    [ Multi-Region Skin Extraction ]
                (Forehead, Cheeks, Jaw/Chin + Outlier IQR)
                                     ↓
                    [ Statistical Feature Extraction ]
            (sRGB Moments, HSV Hue/Sat, CIELAB L*a*b*, ITA°)
                                     ↓
                   [ Machine Learning Classification ]
                    (Random Forest Pipeline Inference)
                                     ↓
                    [ Predicted Undertone & Probabilities ]
                          (Warm / Cool / Neutral)
                                     ↓
                  [ Personalized Recommendation Engine ]
          (Curated Palette, Clothing, Makeup, Accessories, Avoid)
                                     ↓
                  [ Interactive Luxury Web UI Dashboard ]
```

---

## 6. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Programming Language** | Python 3.10+ / 3.14 | Core backend and ML pipeline |
| **Backend API** | FastAPI + Uvicorn | High-performance asynchronous REST API |
| **Computer Vision** | OpenCV + MediaPipe | Face detection, landmark mesh, skin segmentation |
| **Machine Learning** | Scikit-Learn, NumPy, Pandas | ML classification, preprocessing, evaluation |
| **Model Serialization** | Joblib | Model persistence (`undertone_model.pkl`) |
| **Frontend** | HTML5, Vanilla CSS3, JavaScript | Modern luxury dark/light UI with Canvas rendering |
| **Testing** | Pytest, TestClient | Automated test suite covering vision, ML, and API |

---

## 7. Computer Vision & Colorimetry Pipeline

### 7.1 Face Detection & Anatomical Regions
The system uses MediaPipe FaceMesh (468 landmarks) with an adaptive OpenCV Haar Cascade and skin-contour fallback. Four regions are extracted:
- **Forehead ROI:** Above eyebrow midpoint, avoiding hairline.
- **Left Cheek ROI:** Sub-orbital zone away from nose and mouth.
- **Right Cheek ROI:** Sub-orbital zone away from nose and mouth.
- **Jaw/Chin ROI:** Sub-labial mentalis region above the lower mandible.

### 7.2 Outlier & Glare Filtering
Skin candidate pixels are filtered using:
1. **YCrCb Mask:** $Cr \in [128, 178], Cb \in [75, 135]$
2. **HSV Mask:** $H \in [0, 40], S \in [18, 220], V \in [30, 248]$
3. **Statistical IQR Filtering:** Drops top 20% and bottom 20% luminance tails to eliminate specular highlights, flash glare, or stray hair.

### 7.3 Mathematical & Colorimetric Descriptors
- **CIELAB Color Space:**
  - $L^*$: Lightness (0–100)
  - $a^*$: Red-Green chromatic balance (positive = rosy/pink)
  - $b^*$: Yellow-Blue chromatic balance (positive = golden/amber)
- **Individual Typology Angle ($\text{ITA}^\circ$):**
  $$\text{ITA}^\circ = \arctan\left(\frac{L^* - 50}{b^*}\right) \times \frac{180}{\pi}$$
- **Yellow-to-Red Balance Ratio:** $\frac{b^*}{a^*}$

---

## 8. Machine Learning Methodology

### 8.1 Model Comparison & Selection
We evaluated three supervised classification algorithms across 5-fold stratified cross-validation on colorimetric feature spaces:

| Model | CV Accuracy | CV Macro F1 | Test Accuracy | Test Macro F1 |
|---|---|---|---|---|
| **Logistic Regression** | 87.22% (±2.95%) | 0.8727 | 90.00% | 0.9005 |
| **SVM (Linear Kernel)** | 87.50% (±2.65%) | 0.8754 | 90.00% | 0.9004 |
| **SVM (RBF Kernel)** | 85.56% (±2.96%) | 0.8562 | 90.00% | 0.9007 |
| **Random Forest Classifier** | **86.39% (±2.99%)** | **0.8640** | **90.74%** | **0.9075** |

**Selected Model:** `RandomForestClassifier` (150 trees, max depth 10, balanced splits) was chosen for its non-linear decision boundaries and probabilistic calibration.

### 8.2 Top Feature Importances
1. `mean_h` (HSV Hue Angle): 23.0%
2. `b_to_a_ratio` (CIELAB Yellow/Red Ratio): 20.4%
3. `mean_lab_b` (CIELAB Yellow chroma $b^*$): 20.2%
4. `rg_ratio` (Red-to-Green channel balance): 5.7%
5. `mean_a` (CIELAB Pink/Red chroma $a^*$): 4.5%

---

## 9. Dataset Format

The dataset is stored in `data/training.csv` with the following schema:
- `image_id`: Unique identifier
- `phototype`: Fitzpatrick skin category (Fair, Medium, Tan, Deep)
- `mean_r, mean_g, mean_b`: Channel averages in sRGB
- `median_r, median_g, median_b`: Median channel intensities
- `std_r, std_g, std_b`: Channel standard deviations
- `mean_h, mean_s, mean_v`: HSV statistics
- `mean_l, mean_a, mean_lab_b`: CIELAB color moments
- `ita`: Individual Typology Angle
- `b_to_a_ratio`: CIELAB yellow-to-erythema chromatic ratio
- `rg_ratio, rb_ratio`: Inter-channel RGB proportions
- `undertone`: Target class (`Warm`, `Cool`, `Neutral`)

---

## 10. API Documentation

### 1. `GET /api/health`
Checks backend service and model readiness.
```json
{
  "status": "healthy",
  "service": "AI Personal Colour Analysis System",
  "version": "1.0.0",
  "model_loaded": true,
  "model_name": "Random Forest Classifier",
  "classes": ["Cool", "Neutral", "Warm"]
}
```

### 2. `POST /api/analyze`
Receives multipart portrait file (`file: UploadFile`) and returns full analysis.
```json
{
  "success": true,
  "quality": { "score": 88, "status": "Good" },
  "face": { "face_count": 1, "regions": { ... } },
  "skin_analysis": {
    "total_sampled_pixels": 450,
    "metrics": {
      "representative_hex": "#E5B895",
      "cielab": { "L": 65.2, "a": 14.2, "b": 19.8 },
      "ita_angle": 37.5
    }
  },
  "undertone": {
    "label": "Warm",
    "confidence": 0.89,
    "confidence_percentage": 89.0,
    "probabilities": { "Warm": 0.89, "Neutral": 0.08, "Cool": 0.03 }
  },
  "palette": [
    { "name": "Terracotta", "hex": "#E2725B", "rgb": [226, 114, 91] },
    { "name": "Olive Green", "hex": "#708238", "rgb": [112, 130, 56] }
  ],
  "recommendations": { "clothing": [], "makeup": [], "accessories": [], "neutrals": [] },
  "less_recommended": []
}
```

---

## 11. Installation & Running Locally

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14

### Step 1: Clone or Navigate to Directory
```bash
cd "c:/MY PROJECTS/otterlook"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run Model Training & Evaluation (Optional - Pre-trained model included)
```bash
python data/generate_dataset.py
python training/train_undertone.py
python training/evaluate_model.py
```

### Step 4: Run Automated Tests
```bash
python -m pytest tests/ -v
```

### Step 5: Start the Web Application
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser and visit: **`http://127.0.0.1:8000`**

---

## 12. Project Structure

```
otterlook/
│
├── backend/
│   ├── main.py                        # FastAPI application & endpoints
│   ├── vision/
│   │   ├── face_detection.py          # MediaPipe & OpenCV landmark detector
│   │   ├── skin_detection.py          # Multi-region ROI & outlier filtering
│   │   └── colour_extraction.py       # sRGB, HSV, CIELAB & ITA extraction
│   ├── ml/
│   │   ├── predictor.py               # ML inference & confidence calculator
│   │   └── preprocessing.py           # Feature matrix formatting
│   ├── recommendations/
│   │   ├── palette_generator.py       # Recommendation synthesis engine
│   │   └── colour_database.json       # 80+ curated colors with metadata
│   └── utils/
│       └── image_quality.py           # Resolution, blur, and exposure checker
│
├── frontend/
│   ├── index.html                     # Responsive UI layout
│   ├── style.css                      # Modern luxury dark/light theme CSS
│   ├── script.js                      # Canvas rendering & API client
│   └── assets/
│       └── samples/                   # Preset benchmark test portraits
│
├── training/
│   ├── feature_engineering.py         # Feature columns and derived metrics
│   ├── train_undertone.py             # Model training (RF, SVM, LogReg)
│   └── evaluate_model.py              # Confusion matrix & metrics report
│
├── data/
│   ├── generate_dataset.py            # Dermatological colorimetry synthesizer
│   └── training.csv                   # Formatted ML training dataset
│
├── models/
│   ├── undertone_model.pkl            # Trained Random Forest artifact
│   ├── model_comparison.json          # CV & test benchmark results
│   └── evaluation_report.json         # Evaluation metrics & importances
│
├── tests/
│   ├── test_vision.py                 # Face & skin extraction tests
│   ├── test_image_quality.py          # Blur & exposure validation tests
│   ├── test_ml.py                     # Predictor and probability tests
│   ├── test_recommendations.py        # Palette generation tests
│   ├── test_api.py                    # FastAPI endpoint integration tests
│   └── generate_test_images.py        # Synthetic test portrait generator
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 13. Limitations & Future Scope

### Limitations
- **Severe Color Casts:** Very intense artificial blue or neon lighting in low-end webcams can shift the apparent skin color.
- **Heavy Makeup:** Full-coverage opaque foundation may reflect the applied makeup rather than the biological undertone.

### Future Scope
- **Automatic White-Balance Correction:** Incorporating Gray World / Color Constancy algorithms to neutralize ambient color temperature before sampling.
- **Real-Time Video Stream:** Enabling WebRTC live camera analysis with frame averaging.
- **Virtual Color Draping:** AR clothing and fabric overlay directly on the user's live avatar.

---

## 14. Viva & Oral Defense Q&A Guide

**Q1: Why is CIELAB better than RGB for skin undertone analysis?**  
*A: RGB mixes lightness and chrominance across all three channels ($R, G, B$). CIELAB separates lightness ($L^*$) from chromaticity ($a^*$: green-red and $b^*$: blue-yellow). Skin undertone is primarily governed by the yellow-blue $b^*$ balance and erythema $a^*$, making CIELAB invariant to pure intensity changes.*

**Q2: Why sample 4 regions instead of the entire face?**  
*A: The full face contains non-skin elements (hair, eyes, lips, nostrils, teeth, cast shadows from the nose/brow). By targeting the forehead, cheeks, and chin, and filtering via IQR, we ensure only clean, unadulterated dermis pixels are measured.*

**Q3: How does the system compute confidence without fake numbers?**  
*A: The confidence score is extracted directly from the Random Forest model's `predict_proba()` method, representing the fraction of decision trees voting for the winning class.*

---
*Developed for Academic Major Project Submission.*
