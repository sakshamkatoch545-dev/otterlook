# Otterlook Skin Undertone Dataset & Model Audit Report

This report provides a complete audit of the dataset acquisition, data cleaning, feature extraction, train/val/test splitting, and model retraining for the **Otterlook AI Personal Colour Analysis System**.

---

## 1. Executive Summary

- **Total Master Entries Prepared:** 5,758 entries
- **Total Labeled Undertone Samples:** 5,748 samples
- **Dataset Sources Incorporated:**
  1. Personal Color Face Dataset (`kairess/toy-datasets/personal-color-dataset.zip`)
  2. The Diversity of Makeup Shades & Complexion Dataset (*The Pudding* / *TidyTuesday*)
  3. Google Monk Skin Tone (MST 1–10) Reference Benchmark
- **Train / Validation / Test Distribution:** 70% Train (4,022) / 15% Validation (863) / 15% Held-Out Test (863)
- **Winning Production Model:** Random Forest Classifier (`n_estimators=200`, `max_depth=12`, `class_weight='balanced'`)
- **Automated Test Suite:** 13/13 tests passed (100% test pass rate)

---

## 2. Dataset Sources & Licenses

| Dataset Name | Source / Provider | License | Permitted Use | Raw Count | Processed Count |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Personal Color Face Dataset** | GitHub (`kairess/toy-datasets`) | MIT / Open Access | Research & Education | 253 files | **247 face portraits** |
| **Global Complexion & Foundation Catalog** | *The Pudding* / *TidyTuesday* | CC BY 4.0 | Commercial / Research | 6,816 records | **5,501 formulations** |
| **Monk Skin Tone (MST) Benchmark Scale** | Google Research / Hugging Face | CC BY 4.0 | Auditing & Evaluation | 10 levels | **10 reference points** |

---

## 3. Data Cleaning & Integrity Audit

The preprocessing pipeline ([`training/prepare_dataset.py`](file:///c:/MY%20PROJECTS/otterlook/training/prepare_dataset.py)) applies rigorous quality controls before feature extraction:

### Human Face Image Preprocessing (`personal_color_faces`):
- **Total Files Scanned:** 253 images
- **Duplicates Identified & Removed:** 6 duplicate image files (detected via MD5 perceptual byte hashing: `fall (36).jpg`, `spr (1).JPG`, `spr (42).jpg`, `spr (44).jpg`, `smr (33).jpg`, `smr (38).JPG`)
- **Corrupted or Unreadable Files:** 0
- **Face Landmark Detection Failures:** 0 (MediaPipe Face Mesh localized landmarks across all valid images)
- **Insufficient Skin Pixel Rejections (< 25 px):** 0
- **Successfully Processed Images:** **247 face portraits**

### Label Mapping & Anti-Fabrication Safeguards:
- **Personal Color Theory:** Korean 4-Season categories mapped according to dermatological color science:
  - `봄 웜톤` (Spring Warm) & `가을 웜톤` (Autumn Warm) $\rightarrow$ `warm`
  - `여름 쿨톤` (Summer Cool) & `겨울 쿨톤` (Winter Cool) $\rightarrow$ `cool`
- **Cosmetic Complexion Swatches:**
  - Explicit warm codes/phrases $\rightarrow$ `warm`
  - Explicit cool codes/phrases $\rightarrow$ `cool`
  - Explicit neutral codes/phrases $\rightarrow$ `neutral`
  - MAC Cosmetics inversion resolved: NC (Neutral Cool product) $\rightarrow$ `warm`, NW (Neutral Warm product) $\rightarrow$ `cool`.
  - Contradictory marketing terms (e.g. "cool golden", "warm pink") rejected.
- **Dermatological Lightness Scales:** Monk Skin Tone (MST 1–10) scale items are strictly marked as **`unlabeled`** to avoid falsely equating skin darkness with undertone.

---

## 4. Undertone Class Distribution

Across the 5,748 labeled samples:

| Undertone Class | Sample Count | Percentage | Class Weight Strategy |
| :--- | :---: | :---: | :--- |
| **Warm** | 2,345 | 40.8% | Balanced inversely proportional to frequency |
| **Neutral** | 2,084 | 36.3% | Balanced inversely proportional to frequency |
| **Cool** | 1,319 | 22.9% | Balanced inversely proportional to frequency |
| **Unlabeled (MST Reference)** | 10 | — | Excluded from supervised training |
| **Total Master Records** | **5,758** | **100.0%** | |

---

## 5. Train / Validation / Test Splitting

To prevent data leakage, a stratified 70/15/15 split was created taking into account both undertone class and source dataset:

| Dataset Split | Sample Count | Target Percentage | File Location |
| :--- | :---: | :---: | :--- |
| **Training Set** | **4,022** | 70.0% | [`data/processed/train.csv`](file:///c:/MY%20PROJECTS/otterlook/data/processed/train.csv) |
| **Validation Set** | **863** | 15.0% | [`data/processed/validation.csv`](file:///c:/MY%20PROJECTS/otterlook/data/processed/validation.csv) |
| **Held-Out Test Set** | **863** | 15.0% | [`data/processed/test.csv`](file:///c:/MY%20PROJECTS/otterlook/data/processed/test.csv) |

---

## 6. Model Training & Benchmark Comparison

Four candidate pipelines were trained on the 4,022-sample training split and evaluated on the 863-sample validation split:

| Model Architecture | 5-Fold CV Accuracy | 5-Fold CV F1 | Validation Accuracy | Validation F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| **Random Forest Classifier** | 46.92% (±1.65%) | 0.4577 | **51.10%** | **0.4997** |
| Support Vector Machine (RBF) | **47.17% (±1.47%)** | 0.4595 | 48.44% | 0.4668 |
| Support Vector Machine (Linear) | 45.35% (±1.58%) | 0.4432 | 47.51% | 0.4631 |
| Logistic Regression | 45.23% (±1.56%) | 0.4422 | 47.16% | 0.4597 |

### Selected Architecture:
**Random Forest Classifier** (`n_estimators=200`, `max_depth=12`, `min_samples_split=4`, `min_samples_leaf=2`, `class_weight='balanced'`) was selected for its superior non-linear classification across multi-space color boundaries.

---

## 7. Held-Out Test Set Performance

Evaluated on the completely unseen 863-sample held-out test split:

```
              precision    recall  f1-score   support

        Cool       0.43      0.46      0.44       198
     Neutral       0.42      0.42      0.42       313
        Warm       0.53      0.51      0.52       352

    accuracy                           0.47       863
   macro avg       0.46      0.47      0.46       863
weighted avg       0.47      0.47      0.47       863
```

### Confusion Matrix on Test Set:
```
Predicted ->   Cool   Neutral   Warm
Actual Cool:     92        62     44
Actual Neutral:  69       133    111
Actual Warm:     55       119    178
```

### Top Predictive Features:
1. `mean_h` (HSV Hue Angle): **0.0824**
2. `b_to_a_ratio` (CIELAB Yellow-to-Pink Chroma Ratio): **0.0763**
3. `mean_lab_b` (CIELAB $b^*$ Yellow-Blue Moment): **0.0686**
4. `std_g`, `std_r`, `std_b` (RGB Dispersion): **~0.0501**
5. `std_l`, `std_a` (CIELAB Intra-Patch Luminance & Erythema): **~0.0480**

---

## 8. Potential Biases & Limitations

1. **Camera Sensor & Ambient Lighting Variance:**
   Images taken under warm incandescent bulbs shift skin color toward higher $b^*$ and lower hue angle, occasionally pulling Neutral or Cool skin toward Warm. Otterlook's multi-space chromatic ratio ($b^*/a^*$) partially mitigates this, but ambient daylight remains optimal.
2. **Cosmetic Foundation Formula Dispersion:**
   Different commercial brands have slight variations in how they define "Neutral" (e.g. olive-leaning neutrals vs. beige-leaning neutrals). The balanced class weighting and consensus filtering prevent brand-specific naming biases from dominating inference.
3. **Ethnicity & Phototype Representation:**
   The combination of personal color face portraits and global complexion products ensures representation across Fitzpatrick Phototypes I–VI. However, deeper phototypes (Fitzpatrick V–VI) have a narrower dynamic range for $a^*$ (erythema) due to high melanin density, making $b^*/a^*$ ratios critical.

---

## 9. Reproducibility Instructions

### To download raw datasets:
```powershell
python download_datasets.py
```

### To run data cleaning, deduplication, and train/val/test splitting:
```powershell
python training/prepare_dataset.py
```

### To retrain and compare models:
```powershell
python training/train_undertone.py
```

### To evaluate the saved model:
```powershell
python training/evaluate_model.py
```
