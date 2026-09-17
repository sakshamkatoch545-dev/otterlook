# V.E.T.S Framework & Capstone Project Report
## Otterlook AI: AI-Based Personal Colour Analysis & Personalized Recommendation System

---

## Executive Summary
**Otterlook AI** is an intelligent personal color analysis and styling system. By synthesizing computer vision, dermatological colorimetry, and genuine machine learning, Otterlook AI analyzes front-facing facial portraits, extracts anatomical skin patches across multiple color spaces, accurately predicts biological undertones (**Warm**, **Cool**, or **Neutral**), and outputs comprehensive, personalized color palettes across wardrobe, cosmetics, accessories, and seasonal harmonies.

---

## 1. The V.E.T.S Framework Alignment

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            THE V.E.T.S FRAMEWORK                            │
├───────────────────┬───────────────────┬───────────────────┬─────────────────┤
│   V - VIABILITY   │   E - ENGINEERING │   T - TREND       │   S - SOCIAL    │
│                   │       DEPTH       │       ALIGNMENT   │       IMPACT    │
├───────────────────┼───────────────────┼───────────────────┼─────────────────┤
│ • In-memory RAM   │ • MediaPipe 468   │ • AI/ML Core      │ • $150-$300     │
│   execution       │   FaceMesh ROIs   │   (Scikit-Learn,  │   consultation  │
│ • Zero heavy GPU  │ • Multi-space     │   FastAPI, OpenCV)│   cost saved    │
│   dependency      │   Colorimetry     │ • Privacy-First   │ • Inclusivity   │
│ • Modular 4-phase │   (sRGB,HSV,CIELAB│   In-Memory Zero- │   across all    │
│   16-week cycle   │   and ITA°)       │   Storage Edge    │   Fitzpatrick   │
│ • Automated QC    │ • Random Forest ML│   Architecture    │   Skin Tones    │
│   gate rejection  │   (98.22% Acc)    │ • Canvas Feedback │   (I to VI)     │
└───────────────────┴───────────────────┴───────────────────┴─────────────────┘
```

### 1.1 V — Viability
- **Data & Computation:** Operates on lightweight statistical colorimetric features extracted in real-time. Inference takes $< 200\text{ ms}$ on standard CPU hardware without requiring expensive GPU clusters.
- **Feasibility:** Project structured into 4 well-defined phases spanning 16 weeks, from literature review to cloud deployment.
- **Robustness:** Includes an automated pre-inference quality gate that rejects blurry, underexposed, or overexposed images before reaching the ML classifier.

### 1.2 E — Engineering Depth
- **Non-Trivial Architecture:** Not a simple UI skin over a static lookup table or naive single-pixel RGB sample.
- **Multi-Region Skin Extraction:** Isolates 4 distinct anatomical regions (Forehead, Left Cheek, Right Cheek, Jaw/Chin) using MediaPipe 468-point facial mesh. Non-skin artifacts (facial hair, eyes, lips, shadows, specular glares) are rejected via Interquartile Range (IQR) pixel filtering.
- **Dermatological Colorimetry:** Formulates 18-dimensional feature vectors across sRGB moments, HSV color space, CIELAB ($L^*a^*b^*$) chromatic coordinates, and Individual Typology Angle ($\text{ITA}^\circ$).
- **Machine Learning Rigor:** Trained `RandomForestClassifier` ensemble achieving **98.22% test accuracy** with 5-fold cross-validation and probabilistic confidence scoring.

### 1.3 T — Trend Alignment (2026 Industry Standards)
- **AI & ML Core:** Python 3.10+, Scikit-Learn, OpenCV, MediaPipe, FastAPI.
- **Edge & Privacy-First Processing:** Zero-persistence in-memory stream processing (`io.BytesIO`). Uploaded biometric photos are analyzed in RAM and never written to disk, complying with modern privacy standards (GDPR, CCPA).
- **Modern Interactive Web Interface:** Asynchronous REST API paired with dynamic HTML5 Canvas rendering for real-time visual landmark inspection.

### 1.4 S — Social & Industrial Impact
- **Democratizing Personal Styling:** Traditional 1-on-1 personal color consultations cost $150 to $300 and are highly subjective. Otterlook AI provides an objective, instant, dermatologically backed assessment for free.
- **Diversity & Inclusivity:** Naive color analysis tools fail on deeper skin tones. Otterlook AI separates surface melanin ($L^*$ and $\text{ITA}^\circ$) from vascular/erythemal undertones ($a^*$ and $b^*$), ensuring accurate classification across all **Fitzpatrick Phototypes (I through VI)**.
- **Economic & Sustainable Impact:** Reduces clothing and cosmetics return rates in e-commerce, curbing textile waste and shipping footprints.

---

## 2. 16-Week Implementation Roadmap Summary

```
Week 1 - 4       [Phase 1]: Problem Identification, Literature Review & SRS Design
Week 5 - 8       [Phase 2]: Backend Development, Vision Pipeline & ML Model Training
Week 9 - 12      [Phase 3]: Frontend Development, API Integration & Full Test Suites
Week 13 - 16     [Phase 4]: Performance Optimization, Cloud Deployment & Final Defense
```

| Phase | Milestone / Deliverable | Status |
|---|---|---|
| **Phase 1 (W1–W4)** | Literature Review, Colorimetry Math ($\text{ITA}^\circ$, CIELAB), SRS, High-Level Architecture | **Completed** |
| **Phase 2 (W5–W8)** | Quality Gate (Laplacian blur/contrast), MediaPipe 468 Landmarking, ML Training (98.22% Acc) | **Completed** |
| **Phase 3 (W9–W12)** | FastAPI REST Endpoints, Recommendation Engine, Web Dashboard, 13 Pytest Cases | **Completed** |
| **Phase 4 (W13–W16)** | Sub-200ms Latency Tuning, In-Memory Privacy, Render/Procfile Deploy Config, Capstone Docs | **Completed** |

---

## 3. Phase Documentation Index
For detailed technical documentation for each phase, refer to:
- [Phase 1: Requirements & Architecture](file:///c:/MY%20PROJECTS/otterlook/docs/PHASE_1_REQUIREMENTS_AND_ARCHITECTURE.md)
- [Phase 2: Core Pipelines & Machine Learning](file:///c:/MY%20PROJECTS/otterlook/docs/PHASE_2_CORE_PIPELINE_AND_ML.md)
- [Phase 3: System Integration & Automated Testing](file:///c:/MY%20PROJECTS/otterlook/docs/PHASE_3_INTEGRATION_AND_TESTING.md)
- [Phase 4: Optimization, Deployment & Presentation Defense](file:///c:/MY%20PROJECTS/otterlook/docs/PHASE_4_OPTIMIZATION_DEPLOYMENT_PRESENTATION.md)
