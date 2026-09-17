# Phase 3: Frontend Development, API Integration & Testing
### Timeline: Weeks 9 to 12 | Otterlook AI

---

## 1. Backend REST API Architecture
Built with **FastAPI** in [`backend/main.py`](file:///c:/MY%20PROJECTS/otterlook/backend/main.py).

### Endpoints:
- `GET /`: Serves the Single Page Application frontend.
- `GET /api/health`: Health status and model readiness.
- `POST /api/analyze`: Multipart form upload accepting portrait image. Performs quality check, vision feature extraction, ML inference, and palette generation.
- `GET /api/recommendations/{undertone}`: Retrieves full styling palette for a specific undertone.

---

## 2. Recommendation Engine & Color Science
Located in [`backend/recommendations/palette_generator.py`](file:///c:/MY%20PROJECTS/otterlook/backend/recommendations/palette_generator.py) and [`backend/recommendations/colour_database.json`](file:///c:/MY%20PROJECTS/otterlook/backend/recommendations/colour_database.json).

### Categorized Recommendations:
1. **Signature Wardrobe Colors:** 6 high-contrast flattering colors with HEX codes and styling names.
2. **Cosmetics & Makeup:**
   - *Foundation:* Undertone classification & match guidance.
   - *Lipstick:* Berry/rose/coral/nude shades tailored to undertone.
   - *Blush:* Peach, terracotta, soft pink, plum.
   - *Eyeshadow:* Warm bronze, cool taupe, champagne, olive.
3. **Jewelry & Metals:**
   - *Warm:* Yellow Gold (18k), Rose Gold, Amber, Citrine, Warm Pearls.
   - *Cool:* Sterling Silver, White Gold, Platinum, Sapphire, Emerald, Cool White Pearls.
   - *Neutral:* Two-tone metals, Rose Gold, Platinum, Mixed Pearls.
4. **Wardrobe Neutrals:** Cream/Camel vs. Crisp White/Charcoal vs. Soft Greige/Navy.
5. **Colors to Avoid:** Specific clashing shades (e.g., Cool Pastels for Deep Warm, Mustard Yellow for Cool Winter) with stylist rationale.
6. **Seasonal Sub-Type:** 4-Season matching (Spring, Summer, Autumn, Winter).

---

## 3. Interactive Web Frontend
Built with HTML5, Vanilla CSS3, and JavaScript:
- [`frontend/index.html`](file:///c:/MY%20PROJECTS/otterlook/frontend/index.html)
- [`frontend/style.css`](file:///c:/MY%20PROJECTS/otterlook/frontend/style.css)
- [`frontend/script.js`](file:///c:/MY%20PROJECTS/otterlook/frontend/script.js)

### Key Frontend Features:
- **Interactive Landmark Canvas:** Visualizes the detected face bounding box and the 4 anatomical skin ROIs directly on the user's uploaded portrait.
- **Copy-to-Clipboard Hex Badges:** One-click copy for designers and shoppers.
- **Confidence Gauge & Probability Bars:** Real-time visual display of classification probabilities for Warm, Cool, and Neutral.
- **Mobile Responsive & Dark Mode:** Fluid CSS grid and flexbox layout.

---

## 4. Automated Testing Suite & Bug Fixing
Executed via `pytest` under [`tests/`](file:///c:/MY%20PROJECTS/otterlook/tests/).

| Test Module | Coverage | Status |
|---|---|---|
| [`test_image_quality.py`](file:///c:/MY%20PROJECTS/otterlook/tests/test_image_quality.py) | Sharpness, blur rejection, brightness bounds, contrast clipping | **100% Passed** |
| [`test_vision.py`](file:///c:/MY%20PROJECTS/otterlook/tests/test_vision.py) | Face detection, ROI extraction, skin mask segmentation, fallback cascades | **100% Passed** |
| [`test_ml.py`](file:///c:/MY%20PROJECTS/otterlook/tests/test_ml.py) | Feature vector dimensions, model inference, probability distribution | **100% Passed** |
| [`test_api.py`](file:///c:/MY%20PROJECTS/otterlook/tests/test_api.py) | FastAPI endpoints, multipart upload, health check, schema validation | **100% Passed** |

**Summary:** 13/13 test cases passed.
