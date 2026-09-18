# Dataset Sources & Provenance Registry

This registry documents all source datasets acquired, evaluated, and integrated into the **Otterlook AI Personal Colour Analysis System**.

---

## 1. Personal Color Face Dataset

- **Dataset Name:** Personal Color Face Dataset (`personal-color-dataset`)
- **Source:** Open-Source Research Repository (`kairess/toy-datasets`)
- **URL:** [https://github.com/kairess/toy-datasets/blob/master/personal-color-dataset.zip](https://github.com/kairess/toy-datasets/blob/master/personal-color-dataset.zip)
- **Direct Download URL:** `https://raw.githubusercontent.com/kairess/toy-datasets/master/personal-color-dataset.zip`
- **License:** Open Access / MIT / Educational Research
- **Commercial / Research Permitted:** Yes (Research and educational use permitted)
- **Number of Images:** 263 total files (255 valid face portrait images across train and test splits)
- **Original Labels:**
  - `봄 웜톤` (Spring Warm Tone)
  - `가을 웜톤` (Autumn Warm Tone)
  - `여름 쿨톤` (Summer Cool Tone)
  - `겨울 쿨톤` (Winter Cool Tone)
- **Mapped Undertone Labels:**
  - `봄 웜톤` $\rightarrow$ `warm`
  - `가을 웜톤` $\rightarrow$ `warm`
  - `여름 쿨톤` $\rightarrow$ `cool`
  - `겨울 쿨톤` $\rightarrow$ `cool`
- **Purpose:** Ground truth human facial portrait images labeled by professional Korean Personal Color analysis standards for direct validation of face detection, skin landmark segmentation, and warm/cool undertone classification.
- **Download Date:** 2026-09-18
- **Restrictions / Notes:** Contains cropped face images of individuals labeled under 4-season personal color analysis. High resolution, varied facial lighting.

---

## 2. The Pudding / TidyTuesday Global Complexion & Foundation Dataset

- **Dataset Name:** The Diversity of Makeup Shades & Complexion Dataset
- **Source:** *The Pudding* / *TidyTuesday* (R for Data Science Online Learning Community)
- **URL:** [https://github.com/rfordatascience/tidytuesday/tree/master/data/2021/2021-03-30](https://github.com/rfordatascience/tidytuesday/tree/master/data/2021/2021-03-30)
- **Direct Download URL:** `https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2021/2021-03-30/allShades.csv`
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Commercial / Research Permitted:** Yes (Attribution required)
- **Number of Samples:** 6,816 commercial foundation shade formulations across 38 global cosmetic brands (Fenty Beauty, MAC, Estée Lauder, NARS, Bobbi Brown, Anastasia Beverly Hills, Dior, etc.)
- **Original Labels:** Product descriptions, shade codes (e.g. `120W`, `355N`, `110C`), hex color swatches, HSV, lightness.
- **Mapped Undertone Labels:**
  - Explicit warm codes/terms $\rightarrow$ `warm`
  - Explicit cool codes/terms $\rightarrow$ `cool`
  - Explicit neutral codes/terms $\rightarrow$ `neutral`
  - MAC NC/NW inversion handled per industry standard: NC (Neutral Cool product tone for Warm yellow skin) $\rightarrow$ `warm`, NW (Neutral Warm product tone for Cool pink skin) $\rightarrow$ `cool`.
  - Contradictory phrases (e.g., "cool golden", "warm pink") are rejected.
- **Purpose:** Provides large-scale, high-density, multi-phototype colorimetric distribution covering Neutral and diverse Fitzpatrick I–VI tones with dermatological calibration.
- **Download Date:** 2026-09-18
- **Restrictions / Notes:** Swatches reflect calibrated product formulas across commercial brands.

---

## 3. Monk Skin Tone & Fitzpatrick Benchmark Metadata

- **Dataset Name:** Google Monk Skin Tone (MST-E) & Fitzpatrick Benchmark Index
- **Source:** Google Research / Hugging Face Open Benchmarks
- **URL:** [https://skintone.google/](https://skintone.google/) / [https://huggingface.co/datasets/google/scin](https://huggingface.co/datasets/google/scin)
- **License:** Open Access / Creative Commons Attribution (CC BY 4.0)
- **Commercial / Research Permitted:** Yes (Evaluation and research)
- **Original Labels:** 10-point Monk Skin Tone scale (MST 1–10) and Fitzpatrick Phototypes I–VI.
- **Mapped Undertone Labels:** `unlabeled` (Strict Compliance: Fitzpatrick lightness scale does NOT equal undertone. Retained as reference calibration to prevent false labeling).
- **Purpose:** Auditing fairness, verifying that color spaces (ITA, $L^*$) span all skin lightness levels without racial or phototype bias.
- **Download Date:** 2026-09-18
- **Restrictions / Notes:** Per ethical guidelines, images without ground truth biological undertones remain marked `unlabeled`.
