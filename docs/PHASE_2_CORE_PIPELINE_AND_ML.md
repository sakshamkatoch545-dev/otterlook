# Phase 2: Core Module Development, Vision Pipeline & Machine Learning
### Timeline: Weeks 5 to 8 | Otterlook AI

---

## 1. Automated Image Quality Gate
Located in [`backend/utils/image_quality.py`](file:///c:/MY%20PROJECTS/otterlook/backend/utils/image_quality.py).

Before submitting an image to the vision and ML pipeline, the system verifies:
1. **Resolution:** Minimum dimensions $200\times200\text{px}$.
2. **Blur Detection:** Laplacian operator variance $\text{Var}(\nabla^2 I) \ge 50$.
3. **Brightness Check:** Mean pixel intensity $40 \le \mu_I \le 220$ to prevent severe underexposure or white clipping.
4. **Contrast Range:** Standard deviation $\sigma_I \ge 25$ to reject washed out or flat images.

---

## 2. Computer Vision & Anatomical Skin Segmentation
Located in [`backend/vision/face_detection.py`](file:///c:/MY%20PROJECTS/otterlook/backend/vision/face_detection.py) and [`backend/vision/colour_extraction.py`](file:///c:/MY%20PROJECTS/otterlook/backend/vision/colour_extraction.py).

### 2.1 MediaPipe Face Mesh & Anatomical ROIs
The system uses Google MediaPipe FaceMesh (468 3D landmarks) with fallback to OpenCV Haar Cascades. Four anatomically defined regions are extracted:
- **Forehead ROI:** Region above glabella and eyebrows, centered horizontally.
- **Left Cheek ROI:** Sub-orbital zygomatic patch avoiding alar base of nose and nasolabial folds.
- **Right Cheek ROI:** Sub-orbital zygomatic patch avoiding alar base of nose and nasolabial folds.
- **Jaw/Chin ROI:** Sub-labial mentalis region above lower mandible line.

### 2.2 Pixel Outlier Rejection (IQR Filter)
For each ROI, pixels are converted to CIELAB. The Interquartile Range (IQR) rule filters out anomalous pixels:
$$\text{Clean Pixels} = \{ p \in \text{ROI} \mid Q_1(b^*) - 1.5\cdot\text{IQR} \le p_{b^*} \le Q_3(b^*) + 1.5\cdot\text{IQR} \}$$
This removes facial hair, stray shadows, specular highlights, and freckles.

---

## 3. Feature Engineering Pipeline (18 Dimensions)
Located in [`training/feature_engineering.py`](file:///c:/MY%20PROJECTS/otterlook/training/feature_engineering.py).

| # | Feature Name | Space | Description |
|---|---|---|---|
| 1–3 | `mean_r`, `mean_g`, `mean_b` | sRGB | Mean channel values |
| 4–6 | `median_r`, `median_g`, `median_b` | sRGB | Median channel values |
| 7–9 | `std_r`, `std_g`, `std_b` | sRGB | Standard deviation of color distribution |
| 10–12 | `mean_h`, `mean_s`, `mean_v` | HSV | Hue, Saturation, Value moments |
| 13–15 | `mean_lab_l`, `mean_lab_a`, `mean_lab_b` | CIELAB | Luminance ($L^*$), Erythema ($a^*$), Yellow/Blue ($b^*$) |
| 16 | `ita` | ITA° | Individual Typology Angle |
| 17 | `b_to_a_ratio` | Ratio | $b^*/a^*$ (chromatic undertone balance) |
| 18 | `rg_ratio`, `rb_ratio` | Ratio | Red-to-Green and Red-to-Blue ratios |

---

## 4. Machine Learning Model Architecture & Performance
Located in [`training/train_undertone.py`](file:///c:/MY%20PROJECTS/otterlook/training/train_undertone.py) and [`models/evaluation_report.json`](file:///c:/MY%20PROJECTS/otterlook/models/evaluation_report.json).

### 4.1 Training Details
- **Algorithm:** `RandomForestClassifier` ensemble (150 estimators, max depth 12).
- **Validation:** 5-Fold Stratified Cross-Validation.
- **Dataset Size:** 1,350 balanced dermatological and synthetic face colorimetric records across Fitzpatrick I–VI.
- **Persistence:** Serialized via `joblib` to [`models/undertone_model.pkl`](file:///c:/MY%20PROJECTS/otterlook/models/undertone_model.pkl).

### 4.2 Evaluation Metrics
- **Overall Accuracy:** **98.22%**

```
              precision    recall  f1-score   support

        Cool       0.99      0.98      0.98       450
     Neutral       0.96      0.98      0.97       450
        Warm       0.99      0.99      0.99       450

    accuracy                           0.98      1350
   macro avg       0.98      0.98      0.98      1350
weighted avg       0.98      0.98      0.98      1350
```

### 4.3 Confusion Matrix
$$\begin{pmatrix} 439 & 11 & 0 \\ 3 & 443 & 4 \\ 0 & 6 & 444 \end{pmatrix}$$

### 4.4 Top Feature Importances
1. **`mean_h` (HSV Hue):** 23.01%
2. **`b_to_a_ratio` ($b^*/a^*$):** 20.42%
3. **`mean_lab_b` (CIELAB $b^*$):** 20.18%
4. **`rg_ratio`:** 5.74%
5. **`mean_a` (CIELAB $a^*$):** 4.54%
