"""
AuraColor AI - Streamlit Community Cloud Application
AI-Powered Personal Colour Analysis & Machine Learning Undertone Classification System
"""

import os
import sys
import cv2
import numpy as np
from PIL import Image
import streamlit as st

# Ensure backend directory is in sys.path
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

# Page Config
st.set_page_config(
    page_title="AuraColor AI | Personal Colour Analysis",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Luxury CSS Styling
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap');
  
  html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
  }
  
  .main-header {
    text-align: center;
    padding: 1.5rem 0 1rem;
  }
  
  .brand-badge {
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    background: rgba(212, 175, 55, 0.15);
    color: #D4AF37;
    border: 1px solid rgba(212, 175, 55, 0.35);
    margin-bottom: 0.5rem;
  }
  
  .main-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: clamp(2rem, 5vw, 3rem);
    font-weight: 700;
    margin-bottom: 0.5rem;
  }
  
  .undertone-pill {
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
    border: 1px solid rgba(249, 115, 22, 0.4);
  }
  
  .pill-Cool {
    color: #38BDF8;
    background: rgba(56, 189, 248, 0.15);
    border: 1px solid rgba(56, 189, 248, 0.4);
  }
  
  .pill-Neutral {
    color: #2DD4BF;
    background: rgba(45, 212, 191, 0.15);
    border: 1px solid rgba(45, 212, 191, 0.4);
  }
  
  .swatch-box {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(22, 30, 46, 0.7);
    margin-bottom: 0.75rem;
  }
  
  .swatch-color {
    height: 70px;
    width: 100%;
  }
  
  .swatch-label {
    padding: 0.5rem 0.6rem;
    font-size: 0.8rem;
    font-weight: 600;
  }
  
  .metric-badge {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 0.5rem 0.8rem;
    border-radius: 8px;
    margin-bottom: 0.4rem;
  }
</style>
""", unsafe_allow_html=True)

# Cache ML singletons for performance
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
<div class="main-header">
  <div class="brand-badge">Computer Vision & Colorimetry AI</div>
  <h1 class="main-title">AURACOLOR AI</h1>
  <p style="color: #94A3B8; max-width: 650px; margin: 0 auto;">
    Discover your signature personal colour harmony using anatomical face landmarking, CIELAB colorimetry, and Machine Learning classification.
  </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.shields.io/badge/AuraColor-AI%20Colorimetry-gold?style=for-the-badge", use_container_width=True)
    st.markdown("### 📸 Choose Input Mode")
    input_mode = st.radio(
        "Source",
        ["Take Live Selfie", "Upload Portrait", "Verified Presets"],
        label_visibility="collapsed"
    )
    
    selected_image = None
    
    if input_mode == "Take Live Selfie":
        camera_photo = st.camera_input("Take front-facing selfie")
        if camera_photo is not None:
            selected_image = Image.open(camera_photo)
            
    elif input_mode == "Upload Portrait":
        uploaded_file = st.file_uploader("Upload Image (JPG, PNG)", type=["jpg", "jpeg", "png", "webp"])
        if uploaded_file is not None:
            selected_image = Image.open(uploaded_file)
            
    elif input_mode == "Verified Presets":
        preset_choice = st.selectbox("Select Preset", ["Warm Undertone Preset", "Cool Undertone Preset", "Neutral Undertone Preset"])
        preset_map = {
            "Warm Undertone Preset": os.path.join(root_dir, "frontend", "assets", "samples", "sample_warm.jpg"),
            "Cool Undertone Preset": os.path.join(root_dir, "frontend", "assets", "samples", "sample_cool.jpg"),
            "Neutral Undertone Preset": os.path.join(root_dir, "frontend", "assets", "samples", "sample_neutral.jpg")
        }
        sample_path = preset_map[preset_choice]
        if os.path.exists(sample_path):
            selected_image = Image.open(sample_path)
            st.image(selected_image, caption=preset_choice, use_container_width=True)

    st.markdown("---")
    with st.expander("📚 ML Architecture & Viva Defense"):
        st.markdown("""
        **Pipeline Summary:**
        1. **Quality Check:** Laplacian variance (blur) & brightness histogram.
        2. **Landmarking:** MediaPipe 468-point 3D mesh for forehead, cheeks & chin regions.
        3. **Color Features:** CIELAB $b^*$ (yellow-blue), $a^*$ (erythema), ITA° typology angle.
        4. **Model:** Random Forest Classifier trained on colorimetric feature spaces.
        """)

# Main Execution Flow
if selected_image is None:
    st.info("👆 Please upload a front-facing portrait or take a selfie from the sidebar to begin analysis.")
else:
    # Convert PIL to BGR OpenCV
    image_np = np.array(selected_image.convert("RGB"))
    image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

    with st.spinner("Executing Computer Vision & ML Pipeline..."):
        # Step 1: Quality Check
        quality = analyze_image_quality(image_bgr)
        
        # Step 2: Face & ROI Detection
        face_result = pipeline["face_detector"].detect_faces(image_bgr)
        
        if not face_result["success"]:
            st.error(f"❌ Face Detection Error: {face_result['message']}")
        else:
            # Step 3: Skin Extraction
            skin_result = pipeline["skin_extractor"].extract_skin_pixels(image_bgr, face_result["regions"])
            
            if skin_result["total_pixels"] < 30:
                st.error("❌ Insufficient skin pixels detected. Please ensure front lighting and face visibility.")
            else:
                # Step 4: Color Feature Extraction
                color_features = pipeline["feature_extractor"].extract_features(skin_result["pixels_bgr"])
                metrics = color_features["display_metrics"]
                
                # Step 5: ML Prediction
                ml_pred = pipeline["undertone_predictor"].predict(color_features["ml_features"])
                undertone = ml_pred["label"]
                conf_pct = ml_pred["confidence_percentage"]
                
                # Step 6: Palette & Recommendation Synthesis
                recs = pipeline["palette_generator"].generate_recommendations(
                    undertone=undertone,
                    skin_metrics=metrics
                )

                # Draw Annotated Visualizer
                annotated_img = image_np.copy()
                region_colors_rgb = {
                    "forehead": (226, 114, 91),
                    "left_cheek": (56, 189, 248),
                    "right_cheek": (56, 189, 248),
                    "chin": (45, 212, 191)
                }
                for reg_name, box in face_result["regions"].items():
                    color = region_colors_rgb.get(reg_name, (212, 175, 55))
                    cv2.rectangle(annotated_img, (box["x"], box["y"]), (box["x"] + box["w"], box["y"] + box["h"]), color, 3)
                    cv2.putText(annotated_img, reg_name.replace("_", " ").upper(), (box["x"], max(20, box["y"] - 6)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

                st.success(f"Analysis Complete! Quality Score: {quality['score']}/100 ({quality['status']})")

                # Results Showcase Grid
                col1, col2 = st.columns([1, 1])

                with col1:
                    st.markdown("### 🏆 Skin Undertone Verdict")
                    st.markdown(f'<div class="undertone-pill pill-{undertone}">{undertone.upper()} UNDERTONE</div>', unsafe_allow_html=True)
                    st.progress(conf_pct / 100.0)
                    st.caption(f"Model Confidence: **{conf_pct}%** (Random Forest Classifier)")
                    st.write(ml_pred["explanation"])
                    
                    st.markdown("##### Key Predictive Factors:")
                    for factor in ml_pred["key_factors"]:
                        st.markdown(f"- {factor}")

                with col2:
                    st.markdown("### 🔬 Facial Region Colorimetry")
                    sub_col_a, sub_col_b = st.columns([1, 1])
                    with sub_col_a:
                        st.image(annotated_img, caption="MediaPipe Anatomical Sampling", use_container_width=True)
                    with sub_col_b:
                        st.markdown(f"""
                        <div class="metric-badge"><b>Representative HEX:</b> <code>{metrics['representative_hex']}</code></div>
                        <div class="metric-badge"><b>Phototype:</b> {metrics['phototype_estimate']}</div>
                        <div class="metric-badge"><b>CIELAB L* (Lightness):</b> {metrics['cielab']['L']}</div>
                        <div class="metric-badge"><b>CIELAB a* (Red-Green):</b> {metrics['cielab']['a']}</div>
                        <div class="metric-badge"><b>CIELAB b* (Yellow-Blue):</b> {metrics['cielab']['b']}</div>
                        <div class="metric-badge"><b>ITA° Typology Angle:</b> {metrics['ita_angle']}°</div>
                        """, unsafe_allow_html=True)

                st.markdown("---")

                # Core Curated Palette
                st.markdown(f"### 🎨 Signature Harmony — *{recs['seasonal_harmony']['season_name']}*")
                st.write(recs["stylist_summary"])

                palette_cols = st.columns(len(recs["palette"]))
                for i, color in enumerate(recs["palette"]):
                    with palette_cols[i]:
                        st.markdown(f"""
                        <div class="swatch-box">
                          <div class="swatch-color" style="background-color: {color['hex']};"></div>
                          <div class="swatch-label">
                            <div>{color['name']}</div>
                            <code style="font-size:0.75rem;">{color['hex']}</code>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("---")

                # Category Tabs
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "👔 Wardrobe & Clothing",
                    "💄 Makeup & Foundation",
                    "💍 Jewelry & Metals",
                    "⚪ Neutral Basics",
                    "⚠️ Colors to Avoid"
                ])

                def render_category_cols(items):
                    if not items:
                        st.write("No items found.")
                        return
                    cols = st.columns(min(4, len(items)))
                    for idx, item in enumerate(items):
                        with cols[idx % len(cols)]:
                            st.markdown(f"""
                            <div class="swatch-box">
                              <div class="swatch-color" style="background-color: {item['hex']};"></div>
                              <div class="swatch-label">
                                <b>{item['name']}</b><br>
                                <code>{item['hex']}</code><br>
                                <span style="font-size:0.75rem; color:#94A3B8;">{item.get('description', item.get('sub_category', ''))}</span>
                              </div>
                            </div>
                            """, unsafe_allow_html=True)

                with tab1:
                    render_category_cols(recs["recommendations"]["clothing"])

                with tab2:
                    st.info(f"💡 **Foundation Guidance:** {recs['foundation_advice']}")
                    render_category_cols(recs["recommendations"]["makeup"])

                with tab3:
                    render_category_cols(recs["recommendations"]["accessories"])

                with tab4:
                    render_category_cols(recs["recommendations"]["neutrals"])

                with tab5:
                    if recs["less_recommended"]:
                        for avoid_item in recs["less_recommended"]:
                            st.error(f"❌ **{avoid_item['name']} ({avoid_item['hex']})**: {avoid_item['reason']}")
                    else:
                        st.write("No specific avoid guidelines.")
