"""
AuraColor AI - Streamlit Community Cloud Application
AI-Powered Personal Colour Analysis & Machine Learning Undertone Classification System
With Native Live Camera Viewfinder & Luxury Dark Gold Design System
"""

import os
import sys
import numpy as np
from PIL import Image, ImageDraw
import streamlit as st

# Setup system path
root_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(root_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from utils.image_quality import analyze_image_quality
from vision.face_detection import FaceDetector
from vision.skin_detection import SkinExtractor
from vision.colour_extraction import ColourFeatureExtractor
from ml.predictor import UndertonePredictor
from recommendations.palette_generator import PaletteGenerator

# Page Configuration
st.set_page_config(
    page_title="AuraColor AI | Personal Colour Analysis",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Luxury Dark-Gold CSS Design System
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap');
  
  :root {
    --bg-main: #0B0F17;
    --bg-surface: #121824;
    --bg-card: rgba(22, 30, 46, 0.85);
    --border-color: rgba(255, 255, 255, 0.08);
    --accent-gold: #D4AF37;
    --accent-gold-glow: rgba(212, 175, 55, 0.25);
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
  }
  
  html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
  }
  
  /* Header styling */
  .header-wrapper {
    text-align: center;
    padding: 1.5rem 0 1rem;
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 1.5rem;
  }
  
  .brand-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    padding: 0.3rem 0.85rem;
    border-radius: 9999px;
    background: rgba(212, 175, 55, 0.12);
    color: var(--accent-gold);
    border: 1px solid rgba(212, 175, 55, 0.35);
    margin-bottom: 0.75rem;
  }
  
  .pulse-dot {
    width: 6px;
    height: 6px;
    background: var(--accent-gold);
    border-radius: 50%;
    box-shadow: 0 0 8px var(--accent-gold);
  }
  
  .brand-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: clamp(2rem, 4.5vw, 3.2rem);
    font-weight: 700;
    letter-spacing: -0.02em;
    margin: 0;
  }
  
  .brand-title span {
    color: var(--accent-gold);
  }
  
  .hero-desc {
    color: var(--text-secondary);
    font-size: 0.95rem;
    max-width: 680px;
    margin: 0.5rem auto 0;
    line-height: 1.5;
  }
  
  /* Undertone Verdict Card */
  .verdict-hero-card {
    background: rgba(22, 30, 46, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  }
  
  .card-tag {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--accent-gold);
    margin-bottom: 0.75rem;
  }
  
  .undertone-pill-badge {
    display: inline-block;
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2.2rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    padding: 0.4rem 1.8rem;
    border-radius: 12px;
    margin: 0.5rem 0 1rem;
    text-align: center;
  }
  
  .pill-Warm {
    color: #F97316;
    background: rgba(249, 115, 22, 0.15);
    border: 1px solid rgba(249, 115, 22, 0.45);
    box-shadow: 0 0 24px rgba(249, 115, 22, 0.2);
  }
  
  .pill-Cool {
    color: #38BDF8;
    background: rgba(56, 189, 248, 0.15);
    border: 1px solid rgba(56, 189, 248, 0.45);
    box-shadow: 0 0 24px rgba(56, 189, 248, 0.2);
  }
  
  .pill-Neutral {
    color: #2DD4BF;
    background: rgba(45, 212, 191, 0.15);
    border: 1px solid rgba(45, 212, 191, 0.45);
    box-shadow: 0 0 24px rgba(45, 212, 191, 0.2);
  }
  
  /* Swatch Card */
  .swatch-card {
    background: rgba(22, 30, 46, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 0.85rem;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  
  .swatch-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
    border-color: rgba(212, 175, 55, 0.4);
  }
  
  .swatch-color {
    height: 75px;
    width: 100%;
  }
  
  .swatch-meta {
    padding: 0.6rem 0.75rem;
  }
  
  .swatch-name {
    font-size: 0.85rem;
    font-weight: 700;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .swatch-hex {
    font-size: 0.72rem;
    font-family: monospace;
    color: #94A3B8;
  }
  
  /* Metric Tile */
  .metric-tile {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 0.65rem 0.9rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
  }
  
  .metric-tile strong {
    color: var(--accent-gold);
    font-family: monospace;
    font-size: 0.95rem;
  }
  
  /* Guide Box */
  .guide-card {
    background: rgba(212, 175, 55, 0.06);
    border: 1px solid rgba(212, 175, 55, 0.25);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 1.25rem;
  }
</style>
""", unsafe_allow_html=True)

# Cache ML singletons
@st.cache_resource
def load_pipeline():
    return {
        "face_detector": FaceDetector(),
        "skin_extractor": SkinExtractor(),
        "feature_extractor": ColourFeatureExtractor(),
        "undertone_predictor": UndertonePredictor(),
        "palette_generator": PaletteGenerator()
    }

pipeline = load_pipeline()

# Header
st.markdown("""
<div class="header-wrapper">
  <div class="brand-badge">
    <span class="pulse-dot"></span>
    AI Dermatological Colorimetry
  </div>
  <h1 class="brand-title">AURA<span>COLOR</span> AI</h1>
  <p class="hero-desc">
    Personal Colour Analysis & Signature Palette Generator powered by MediaPipe Anatomical Landmarking, CIELAB Colorimetry, and Random Forest ML.
  </p>
</div>
""", unsafe_allow_html=True)

# Viva / ML Architecture Collapsible
with st.expander("📚 ML Architecture & Viva Defense Guide (Click to expand)"):
    st.markdown("""
    #### 1. Machine Learning Methodology
    Unlike basic RGB-heuristic apps, this system trains a genuine **Random Forest Classifier** pipeline evaluated against **Support Vector Machines (SVM)** and **Logistic Regression** across high-dimensional colorimetric feature spaces.
    
    #### 2. Color Spaces & CIELAB $b^*$ Axis
    **CIELAB ($L^*a^*b^*$)** decouples luminance ($L^*$) from chromatic axes ($a^*$: red-green, $b^*$: yellow-blue):
    - **Warm Undertone:** Elevated $b^*$ ($b^* > 18.0$) and high yellow-to-erythema ratio ($b^*/a^* > 1.2$).
    - **Cool Undertone:** Low $b^*$ ($b^* < 12.5$) and dominant pink/rosy tones.
    - **Neutral Undertone:** Equidistant balance between warm golden and cool pink axes ($b^*/a^* \\approx 1.05$).
    
    #### 3. Individual Typology Angle (ITA°)
    $$\\text{ITA}^\\circ = \\arctan\\left(\\frac{L^* - 50}{b^*}\\right) \\times \\frac{180}{\\pi}$$
    Quantifies skin melanin phototype from Very Fair (Fitzpatrick I) to Deep/Dark (Fitzpatrick VI).
    """)

# Input Mode Selector
st.markdown("### 📸 Choose Input Source")
input_tab1, input_tab2, input_tab3 = st.tabs([
    "📸 Live Camera Selfie",
    "📁 Upload Portrait File",
    "🎨 Verified Presets"
])

selected_image = None

with input_tab1:
    st.info("💡 Look straight into your front camera with balanced, natural daylight.")
    camera_photo = st.camera_input("Take Live Front-Facing Selfie", label_visibility="collapsed")
    if camera_photo is not None:
        selected_image = Image.open(camera_photo)

with input_tab2:
    uploaded_file = st.file_uploader(
        "Upload Image (JPG, JPEG, PNG, WebP)",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed"
    )
    if uploaded_file is not None:
        selected_image = Image.open(uploaded_file)

with input_tab3:
    preset_choice = st.radio(
        "Select Verified Sample",
        ["Warm Undertone Preset (Terracotta/Gold)", "Cool Undertone Preset (Rose/Jewel)", "Neutral Undertone Preset (Balanced Olive)"],
        horizontal=True
    )
    sample_map = {
        "Warm Undertone Preset (Terracotta/Gold)": os.path.join(root_dir, "frontend", "assets", "samples", "sample_warm.jpg"),
        "Cool Undertone Preset (Rose/Jewel)": os.path.join(root_dir, "frontend", "assets", "samples", "sample_cool.jpg"),
        "Neutral Undertone Preset (Balanced Olive)": os.path.join(root_dir, "frontend", "assets", "samples", "sample_neutral.jpg")
    }
    sample_path = sample_map[preset_choice]
    if os.path.exists(sample_path):
        selected_image = Image.open(sample_path)
        st.image(selected_image, width=280, caption=f"Selected: {preset_choice}")

st.markdown("---")

# Execution Flow
if selected_image is None:
    st.info("👆 Take a live selfie or upload an image above to run color analysis.")
else:
    # Prepare image arrays
    image_rgb_pil = selected_image.convert("RGB")
    image_rgb = np.array(image_rgb_pil)
    image_bgr = image_rgb[:, :, ::-1]

    with st.spinner("Analyzing Facial Colorimetry & Undertone..."):
        # Pipeline Steps
        quality = analyze_image_quality(image_bgr)
        face_result = pipeline["face_detector"].detect_faces(image_bgr)
        
        if not face_result["success"]:
            st.error(f"❌ Face Localization: {face_result['message']}")
        else:
            skin_result = pipeline["skin_extractor"].extract_skin_pixels(image_bgr, face_result["regions"])
            
            if skin_result["total_pixels"] < 20:
                st.error("❌ Insufficient facial skin pixels detected. Please ensure front lighting.")
            else:
                color_features = pipeline["feature_extractor"].extract_features(skin_result["pixels_bgr"])
                metrics = color_features["display_metrics"]
                ml_pred = pipeline["undertone_predictor"].predict(color_features["ml_features"])
                undertone = ml_pred["label"]
                conf_pct = ml_pred["confidence_percentage"]
                
                recs = pipeline["palette_generator"].generate_recommendations(
                    undertone=undertone,
                    skin_metrics=metrics
                )

                # Draw Annotated Visualizer with Pillow
                annotated_img = image_rgb_pil.copy()
                draw = ImageDraw.Draw(annotated_img)
                region_colors = {
                    "forehead": "#E2725B",
                    "left_cheek": "#38BDF8",
                    "right_cheek": "#38BDF8",
                    "chin": "#2DD4BF"
                }
                
                for reg_name, box in face_result["regions"].items():
                    color = region_colors.get(reg_name, "#D4AF37")
                    x0, y0 = box["x"], box["y"]
                    x1, y1 = x0 + box["w"], y0 + box["h"]
                    draw.rectangle([x0, y0, x1, y1], outline=color, width=4)

                # Quality Banner
                st.success(f"✓ Analysis Complete • Quality Score: {quality['score']}/100 ({quality['status']})")

                # Top Results Grid
                col1, col2 = st.columns([1.1, 0.9])

                with col1:
                    st.markdown("""
                    <div class="card-tag">Predicted Skin Undertone</div>
                    """, unsafe_allow_html=True)
                    st.markdown(f'<div class="undertone-pill-badge pill-{undertone}">{undertone.upper()} UNDERTONE</div>', unsafe_allow_html=True)
                    
                    st.progress(conf_pct / 100.0)
                    st.caption(f"Model Confidence: **{conf_pct}%** (Random Forest Classifier)")
                    
                    # Probability chips
                    probs = ml_pred.get("probabilities", {})
                    prob_text = " • ".join([f"**{k}**: {int(v*100)}%" for k, v in probs.items()])
                    st.markdown(f"<small style='color:#94A3B8;'>Probabilities: {prob_text}</small>", unsafe_allow_html=True)
                    
                    st.write(ml_pred["explanation"])
                    
                    st.markdown("##### Key Predictive Factors:")
                    for factor in ml_pred["key_factors"]:
                        st.markdown(f"- {factor}")

                with col2:
                    st.markdown('<div class="card-tag">Facial Region Sampling & Color Metrics</div>', unsafe_allow_html=True)
                    sub_col_a, sub_col_b = st.columns([1, 1])
                    
                    with sub_col_a:
                        st.image(annotated_img, caption="Anatomical Sampling Patches", use_container_width=True)
                    
                    with sub_col_b:
                        st.markdown(f"""
                        <div style="background:{metrics['representative_hex']}; height:48px; border-radius:8px; margin-bottom:8px; border:1px solid rgba(255,255,255,0.2);"></div>
                        <div class="metric-tile"><span>Rep. HEX:</span><strong>{metrics['representative_hex']}</strong></div>
                        <div class="metric-tile"><span>CIELAB L*:</span><strong>{metrics['cielab']['L']}</strong></div>
                        <div class="metric-tile"><span>CIELAB a*:</span><strong>+{metrics['cielab']['a']}</strong></div>
                        <div class="metric-tile"><span>CIELAB b*:</span><strong>+{metrics['cielab']['b']}</strong></div>
                        <div class="metric-tile"><span>ITA° Angle:</span><strong>{metrics['ita_angle']}°</strong></div>
                        <div class="metric-tile"><span>Phototype:</span><small style="color:#D4AF37;">{metrics['phototype_estimate'].split('(')[0]}</small></div>
                        """, unsafe_allow_html=True)

                st.markdown("---")

                # Signature Harmony Palette
                st.markdown(f"### 🎨 Signature Harmony — *{recs['seasonal_harmony']['season_name']}*")
                st.write(recs["stylist_summary"])

                palette_cols = st.columns(len(recs["palette"]))
                for i, color in enumerate(recs["palette"]):
                    with palette_cols[i]:
                        st.markdown(f"""
                        <div class="swatch-card">
                          <div class="swatch-color" style="background-color: {color['hex']};"></div>
                          <div class="swatch-meta">
                            <div class="swatch-name" title="{color['name']}">{color['name']}</div>
                            <div class="swatch-hex">{color['hex']}</div>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("---")

                # Category Tabs
                rec_tab1, rec_tab2, rec_tab3, rec_tab4, rec_tab5 = st.tabs([
                    "👔 Clothing & Wardrobe",
                    "💄 Makeup & Cosmetics",
                    "💍 Jewelry & Metals",
                    "⚪ Neutral Basics",
                    "⚠️ Colors to Avoid"
                ])

                def render_items(items):
                    if not items:
                        st.write("No items found.")
                        return
                    cols = st.columns(min(4, len(items)))
                    for idx, item in enumerate(items):
                        with cols[idx % len(cols)]:
                            st.markdown(f"""
                            <div class="swatch-card">
                              <div class="swatch-color" style="background-color: {item['hex']};"></div>
                              <div class="swatch-meta">
                                <div class="swatch-name">{item['name']}</div>
                                <div class="swatch-hex">{item['hex']}</div>
                                <div style="font-size:0.75rem; color:#94A3B8; margin-top:4px;">{item.get('description', item.get('sub_category', ''))}</div>
                              </div>
                            </div>
                            """, unsafe_allow_html=True)

                with rec_tab1:
                    render_items(recs["recommendations"]["clothing"])

                with rec_tab2:
                    st.markdown(f"""
                    <div class="guide-card">
                      <h4 style="color:#D4AF37; margin:0 0 6px;">💄 Foundation Guidance</h4>
                      <p style="margin:0; font-size:0.88rem; color:#E2E8F0;">{recs['foundation_advice']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    render_items(recs["recommendations"]["makeup"])

                with rec_tab3:
                    render_items(recs["recommendations"]["accessories"])

                with rec_tab4:
                    render_items(recs["recommendations"]["neutrals"])

                with rec_tab5:
                    st.warning("These colors feature contrasting temperatures that can clash with your undertone.")
                    if recs["less_recommended"]:
                        avoid_cols = st.columns(min(3, len(recs["less_recommended"])))
                        for idx, avoid_item in enumerate(recs["less_recommended"]):
                            with avoid_cols[idx % len(avoid_cols)]:
                                st.markdown(f"""
                                <div class="swatch-card" style="border-color: rgba(239, 68, 68, 0.4);">
                                  <div class="swatch-color" style="background-color: {avoid_item['hex']};"></div>
                                  <div class="swatch-meta">
                                    <div class="swatch-name" style="color:#F87171;">{avoid_item['name']}</div>
                                    <div class="swatch-hex">{avoid_item['hex']}</div>
                                    <div style="font-size:0.75rem; color:#94A3B8; margin-top:4px;">{avoid_item['reason']}</div>
                                  </div>
                                </div>
                                """, unsafe_allow_html=True)
