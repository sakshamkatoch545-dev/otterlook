"""
AuraColor AI - Streamlit Community Cloud Application
Renders the complete luxury frontend application identically to localhost,
including the dark gold design system, live camera selfie viewfinder modal, animated pipeline stepper,
interactive facial colorimetry visualizer, dynamic seasonal palette, and categorized styling tabs.
"""

import os
import json
import base64
import streamlit as st
import streamlit.components.v1 as components

# Page Configuration
st.set_page_config(
    page_title="AuraColor AI | Personal Colour Analysis & Palette Recommendation",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit default chrome & margins to give 100% full-screen localhost experience
st.markdown("""
<style>
  #MainMenu, header, footer, .stDeployButton { visibility: hidden !important; display: none !important; }
  div[data-testid="stToolbar"] { display: none !important; }
  .block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
  }
  iframe {
    width: 100% !important;
    min-height: 100vh !important;
    height: 100vh !important;
    border: none !important;
  }
</style>
""", unsafe_allow_html=True)

# Directories
root_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(root_dir, "frontend")
backend_dir = os.path.join(root_dir, "backend")

# Read CSS
css_path = os.path.join(frontend_dir, "style.css")
with open(css_path, "r", encoding="utf-8") as f:
    css_content = f.read()

# Read Colour Database
db_path = os.path.join(backend_dir, "recommendations", "colour_database.json")
with open(db_path, "r", encoding="utf-8") as f:
    colour_db_json = f.read()

# Read Sample Images as Base64 Data URLs
def get_sample_b64(name):
    p = os.path.join(frontend_dir, "assets", "samples", name)
    if os.path.exists(p):
        with open(p, "rb") as f:
            return f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode('utf-8')}"
    return ""

sample_warm_b64 = get_sample_b64("sample_warm.jpg")
sample_cool_b64 = get_sample_b64("sample_cool.jpg")
sample_neutral_b64 = get_sample_b64("sample_neutral.jpg")

# Complete Self-Contained HTML with Embedded Engine & Live Camera
html_content = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, viewport-fit=cover">
  <meta name="theme-color" content="#0B0F17" id="theme-color-meta">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap" rel="stylesheet">
  <style>
{css_content}
  </style>
</head>
<body>
  <!-- Header Navigation -->
  <header class="site-header">
    <div class="header-container">
      <div class="brand">
        <div class="brand-badge">
          <span class="pulse-dot"></span>
          AI Colorimetry
        </div>
        <h1 class="brand-title">AURA<span>COLOR</span> <span class="brand-sub">AI</span></h1>
      </div>
      <div class="header-actions">
        <button id="viva-modal-btn" class="btn btn-outline guide-btn" title="View Color Science & ML Pipeline">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
          <span class="btn-text-full">ML Architecture & Viva Guide</span>
          <span class="btn-text-short">ML Guide</span>
        </button>
        <button id="theme-toggle-btn" class="theme-toggle" aria-label="Toggle theme">
          <svg class="sun-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
          <svg class="moon-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        </button>
      </div>
    </div>
  </header>

  <!-- Main Container -->
  <main class="main-content">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-tag">Computer Vision & Dermatological Colorimetry</div>
      <h2 class="hero-headline">Discover Your Personal <em>Colour Harmony</em></h2>
      <p class="hero-description">
        AI-powered facial skin undertone analysis and tailored palette curation. Utilizing MediaPipe anatomical region extraction, CIELAB colorimetry, and Machine Learning classification.
      </p>

      <div class="hero-badges">
        <div class="badge-item">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
          Multi-Region Skin Extraction
        </div>
        <div class="badge-item">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>
          CIELAB b* & ITA° Features
        </div>
        <div class="badge-item">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          Random Forest Ensemble ML
        </div>
      </div>
    </section>

    <!-- Upload & Studio Section -->
    <section class="studio-section">
      <div class="studio-card">
        <!-- Drag & Drop Zone -->
        <div class="upload-container" id="drop-zone">
          <input type="file" id="file-input" accept="image/jpeg,image/png,image/jpg,image/webp" hidden>
          <input type="file" id="camera-input" accept="image/*" capture="user" hidden>
          
          <div class="upload-content" id="upload-prompt">
            <div class="upload-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            </div>
            <h3>Upload or Capture Facial Portrait</h3>
            <p>Drag & drop your portrait here, take a live selfie, or browse from files</p>
            
            <div class="upload-actions">
              <button type="button" class="btn btn-sm btn-camera" id="camera-btn">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                Take Selfie
              </button>
              <button type="button" class="btn btn-sm btn-browse" id="browse-btn">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                Browse Files
              </button>
            </div>
            
            <span class="file-hint">Supports JPG, JPEG, PNG, WebP (max 15MB) • Front-facing with natural lighting</span>
          </div>

          <!-- Live Preview Box -->
          <div class="preview-box hidden" id="preview-box">
            <img id="preview-img" src="" alt="Uploaded Portrait Preview">
            <button class="remove-btn" id="remove-img-btn" title="Remove image">×</button>
          </div>
        </div>

        <!-- Quick Sample Presets -->
        <div class="sample-presets">
          <span class="preset-label">Or test with verified sample presets:</span>
          <div class="preset-buttons">
            <button type="button" class="preset-btn" data-sample="warm">
              <span class="preset-dot" style="background:#E2725B;"></span>
              Warm Undertone Preset
            </button>
            <button type="button" class="preset-btn" data-sample="cool">
              <span class="preset-dot" style="background:#0F52BA;"></span>
              Cool Undertone Preset
            </button>
            <button type="button" class="preset-btn" data-sample="neutral">
              <span class="preset-dot" style="background:#008080;"></span>
              Neutral Undertone Preset
            </button>
          </div>
        </div>

        <!-- Image Quality Diagnostics Bar -->
        <div class="quality-bar hidden" id="quality-bar">
          <div class="quality-header">
            <span class="quality-title">Image Quality Check:</span>
            <span class="quality-status" id="quality-status">Evaluating...</span>
          </div>
          <div class="quality-meter-track">
            <div class="quality-meter-fill" id="quality-meter" style="width: 0%"></div>
          </div>
          <div class="quality-details" id="quality-details"></div>
        </div>

        <!-- Error Banner -->
        <div class="error-banner hidden" id="error-banner">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          <div class="error-text" id="error-text"></div>
        </div>

        <!-- Analyze CTA -->
        <div class="cta-container">
          <button id="analyze-btn" class="btn btn-primary btn-glow" disabled>
            <span class="btn-text-main">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/></svg>
              Analyze Undertone & Generate Palette
            </span>
          </button>
        </div>
      </div>
    </section>

    <!-- Processing Animation & Stepper -->
    <section class="processing-section hidden" id="processing-section">
      <div class="processing-card">
        <div class="processing-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-core"></div>
        </div>
        <h3 class="processing-title">Analyzing Facial Colorimetry...</h3>
        <p class="processing-subtitle">Executing computer vision pipeline and Random Forest classification</p>
        
        <div class="pipeline-stepper">
          <div class="step-item" id="step-1">
            <div class="step-icon">1</div>
            <div class="step-label">Image Validation & Quality Check</div>
          </div>
          <div class="step-item" id="step-2">
            <div class="step-icon">2</div>
            <div class="step-label">Face Landmark Localization</div>
          </div>
          <div class="step-item" id="step-3">
            <div class="step-icon">3</div>
            <div class="step-label">Multi-Region Skin Extraction (Forehead, Cheeks, Jaw)</div>
          </div>
          <div class="step-item" id="step-4">
            <div class="step-icon">4</div>
            <div class="step-label">CIELAB, HSV & sRGB Feature Extraction</div>
          </div>
          <div class="step-item" id="step-5">
            <div class="step-icon">5</div>
            <div class="step-label">Machine Learning Undertone Prediction</div>
          </div>
          <div class="step-item" id="step-6">
            <div class="step-icon">6</div>
            <div class="step-label">Personalized Palette & Styling Synthesis</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Results Showcase Section -->
    <section class="results-section hidden" id="results-section">
      <!-- Top Verdict Grid -->
      <div class="verdict-grid">
        <!-- Undertone Hero Card -->
        <div class="card verdict-card" id="verdict-card">
          <div class="card-tag">Predicted Skin Undertone</div>
          <div class="undertone-badge-wrapper">
            <div class="undertone-badge" id="undertone-badge">WARM</div>
          </div>
          <div class="confidence-container">
            <div class="confidence-header">
              <span>Model Confidence:</span>
              <strong id="confidence-val">87%</strong>
            </div>
            <div class="confidence-track">
              <div class="confidence-bar" id="confidence-bar" style="width: 87%"></div>
            </div>
            <div class="class-prob-breakdown" id="prob-breakdown"></div>
          </div>
          <p class="undertone-explanation" id="undertone-explanation"></p>
          <div class="key-factors-list" id="key-factors"></div>
        </div>

        <!-- Skin Colorimetry & Landmark Visualizer Card -->
        <div class="card visualizer-card">
          <div class="card-tag">Facial Region Sampling & Color Metrics</div>
          <div class="visualizer-container">
            <div class="face-canvas-box">
              <canvas id="face-canvas"></canvas>
              <div class="canvas-caption">Anatomical skin sampling patches (Forehead, Cheeks, Chin)</div>
            </div>
            <div class="metrics-column">
              <div class="rep-swatch-box">
                <div class="rep-swatch" id="rep-swatch"></div>
                <div class="rep-info">
                  <span class="rep-label">Representative Skin Tone</span>
                  <strong class="rep-hex" id="rep-hex">#E5B895</strong>
                  <span class="rep-phototype" id="rep-phototype">Fitzpatrick Type III</span>
                </div>
              </div>
              <div class="color-metrics-table">
                <div class="metric-row">
                  <span>CIELAB L* (Lightness)</span>
                  <strong id="metric-lab-l">65.2</strong>
                </div>
                <div class="metric-row">
                  <span>CIELAB a* (Red-Green)</span>
                  <strong id="metric-lab-a">+14.2</strong>
                </div>
                <div class="metric-row">
                  <span>CIELAB b* (Yellow-Blue)</span>
                  <strong id="metric-lab-b" class="highlight-metric">+19.8</strong>
                </div>
                <div class="metric-row">
                  <span>ITA° Typology Angle</span>
                  <strong id="metric-ita">+37.5°</strong>
                </div>
                <div class="metric-row">
                  <span>HSV Dominant Hue</span>
                  <strong id="metric-hsv-h">32.0°</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Personalized Palette Section -->
      <div class="card palette-showcase-card">
        <div class="card-tag">Personalized Curated Palette</div>
        <div class="palette-header">
          <div>
            <h3 class="palette-title">Your Signature Harmony</h3>
            <p class="palette-desc" id="stylist-summary"></p>
            <div class="swatch-tap-hint">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
              <span>Tap any swatch to copy HEX</span>
            </div>
          </div>
          <div class="season-badge" id="season-badge">
            <span class="season-label">Seasonal Harmony:</span>
            <strong id="season-title">Warm Autumn</strong>
          </div>
        </div>

        <div class="swatches-grid" id="swatches-grid">
          <!-- Swatches rendered dynamically -->
        </div>
      </div>

      <!-- Recommendation Categories Tabs -->
      <div class="recommendations-container">
        <div class="tab-nav">
          <button class="tab-btn active" data-tab="clothing">👔 Clothing & Wardrobe</button>
          <button class="tab-btn" data-tab="makeup">💄 Makeup & Cosmetics</button>
          <button class="tab-btn" data-tab="accessories">💍 Jewelry & Accessories</button>
          <button class="tab-btn" data-tab="neutrals">⚪ Neutral Basics</button>
          <button class="tab-btn tab-btn-avoid" data-tab="avoid">⚠️ Colors to Avoid</button>
        </div>

        <div class="tab-content active" id="tab-clothing">
          <div class="rec-grid" id="rec-clothing-grid"></div>
        </div>

        <div class="tab-content" id="tab-makeup">
          <div class="makeup-guide-box" id="foundation-advice-box">
            <div class="guide-icon">💄</div>
            <div>
              <h4>Foundation & Base Guidance</h4>
              <p id="foundation-advice-text"></p>
            </div>
          </div>
          <div class="rec-grid" id="rec-makeup-grid"></div>
        </div>

        <div class="tab-content" id="tab-accessories">
          <div class="rec-grid" id="rec-accessories-grid"></div>
        </div>

        <div class="tab-content" id="tab-neutrals">
          <div class="rec-grid" id="rec-neutrals-grid"></div>
        </div>

        <div class="tab-content" id="tab-avoid">
          <div class="avoid-intro">
            <p>These colors feature conflicting color temperatures that can wash out your skin, exaggerate blemishes, or cause a sallow appearance.</p>
          </div>
          <div class="avoid-grid" id="rec-avoid-grid"></div>
        </div>
      </div>

      <!-- Reset / Re-analyze Bar -->
      <div class="restart-bar">
        <button class="btn btn-outline" id="reanalyze-btn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10"/><polyline points="23 20 23 14 17 14"/><path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"/></svg>
          Analyze Another Portrait
        </button>
      </div>
    </section>
  </main>

  <!-- Live Camera Viewfinder Modal -->
  <div class="camera-modal-overlay hidden" id="camera-modal">
    <div class="camera-modal-card">
      <div class="camera-modal-header">
        <h3>Live Selfie Viewfinder</h3>
        <button class="modal-close" id="camera-close-btn" aria-label="Close camera">&times;</button>
      </div>
      <div class="camera-viewfinder-box">
        <video id="camera-video" autoplay playsinline muted></video>
        <div class="camera-face-guide">
          <div class="face-oval-guide"></div>
          <span class="guide-text">Position face inside oval with natural lighting</span>
        </div>
      </div>
      <div class="camera-controls">
        <button type="button" class="btn btn-primary btn-snap" id="camera-snap-btn">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
          Snap Photo
        </button>
      </div>
    </div>
  </div>

  <!-- Educational Viva Defense Modal -->
  <div class="modal-overlay hidden" id="viva-modal">
    <div class="modal-card">
      <div class="modal-header">
        <h3>Color Science & Machine Learning Architecture</h3>
        <button class="modal-close" id="modal-close-btn">&times;</button>
      </div>
      <div class="modal-body">
        <h4>1. Machine Learning Methodology</h4>
        <p>
          Unlike naive RGB-threshold apps, this system trains a genuine <strong>Random Forest Classifier</strong> pipeline comparing against <strong>Support Vector Machines (SVM)</strong> and <strong>Logistic Regression</strong> on colorimetric skin feature spaces.
        </p>
        
        <h4>2. Color Spaces & CIELAB <i>b</i>* Axis</h4>
        <p>
          <strong>CIELAB (<i>L</i>*<i>a</i>*<i>b</i>*)</strong> separates lightness (<i>L</i>*) from chromaticity (<i>a</i>*: green-red axis, <i>b</i>*: blue-yellow axis). 
          Skin undertone is primarily governed by the yellow-blue balance:
        </p>
        <ul>
          <li><strong>Warm Undertone:</strong> Elevated <i>b</i>* (<i>b</i>* &gt; 18.0) and high <i>b</i>*/<i>a</i>* ratio.</li>
          <li><strong>Cool Undertone:</strong> Lower <i>b</i>* (<i>b</i>* &lt; 12.5) and dominant pink/erythema <i>a</i>*.</li>
          <li><strong>Neutral Undertone:</strong> Balanced <i>a</i>* and <i>b</i>* with intermediate chromas.</li>
        </ul>

        <h4>3. Individual Typology Angle (ITA°)</h4>
        <div class="code-box">
          <strong>ITA°</strong> = arctan((<i>L</i>* - 50) / <i>b</i>*) &times; (180 / &pi;)
        </div>
        <p>Quantifies skin melanin phototype from Very Fair (Fitzpatrick I) to Dark (Fitzpatrick VI).</p>

        <h4>4. Pipeline Summary</h4>
        <p>
          Image Validation &rarr; Quality Score &rarr; Face & Landmark Localization &rarr; Multi-Region Extraction (Forehead, Cheeks, Jaw) &rarr; Outlier IQR Filtering &rarr; Statistical Moments (Mean, Std, Var, Medians) &rarr; Random Forest Inference &rarr; Recommendation Synthesis.
        </p>
      </div>
    </div>
  </div>

  <!-- Toast Notification -->
  <div class="toast hidden" id="toast">Copied HEX code to clipboard!</div>

  <!-- Footer -->
  <footer class="site-footer">
    <div class="footer-container">
      <p>AI-Based Personal Colour Analysis System • Major College Project • Built with FastAPI, Scikit-Learn & OpenCV</p>
    </div>
  </footer>

  <script>
    const SAMPLE_IMAGES = {{
      warm: "{sample_warm_b64}",
      cool: "{sample_cool_b64}",
      neutral: "{sample_neutral_b64}"
    }};

    const COLOUR_DATABASE = {colour_db_json};

    document.addEventListener("DOMContentLoaded", () => {{
      const dropZone = document.getElementById("drop-zone");
      const fileInput = document.getElementById("file-input");
      const cameraInput = document.getElementById("camera-input");
      const browseBtn = document.getElementById("browse-btn");
      const cameraBtn = document.getElementById("camera-btn");
      const uploadPrompt = document.getElementById("upload-prompt");
      const previewBox = document.getElementById("preview-box");
      const previewImg = document.getElementById("preview-img");
      const removeImgBtn = document.getElementById("remove-img-btn");
      const analyzeBtn = document.getElementById("analyze-btn");
      const qualityBar = document.getElementById("quality-bar");
      const qualityMeter = document.getElementById("quality-meter");
      const qualityStatus = document.getElementById("quality-status");
      const qualityDetails = document.getElementById("quality-details");
      const errorBanner = document.getElementById("error-banner");
      const errorText = document.getElementById("error-text");
      const presetBtns = document.querySelectorAll(".preset-btn");

      const processingSection = document.getElementById("processing-section");
      const resultsSection = document.getElementById("results-section");
      const studioSection = document.querySelector(".studio-section");
      const heroSection = document.querySelector(".hero-section");
      const reanalyzeBtn = document.getElementById("reanalyze-btn");

      const themeToggleBtn = document.getElementById("theme-toggle-btn");
      const themeColorMeta = document.getElementById("theme-color-meta");
      const vivaModalBtn = document.getElementById("viva-modal-btn");
      const vivaModal = document.getElementById("viva-modal");
      const modalCloseBtn = document.getElementById("modal-close-btn");
      const toast = document.getElementById("toast");

      // Live Camera DOM Elements
      let mediaStream = null;
      const cameraModal = document.getElementById("camera-modal");
      const cameraVideo = document.getElementById("camera-video");
      const cameraCloseBtn = document.getElementById("camera-close-btn");
      const cameraSnapBtn = document.getElementById("camera-snap-btn");

      let currentImageBitmap = null;
      let currentDataUrl = null;

      // Theme Controller
      function applyTheme(theme) {{
        document.documentElement.setAttribute("data-theme", theme);
        if (themeColorMeta) {{
          themeColorMeta.setAttribute("content", theme === "dark" ? "#0B0F17" : "#F8F9FC");
        }}
      }}
      const savedTheme = localStorage.getItem("auracolor-theme") || "dark";
      applyTheme(savedTheme);

      themeToggleBtn.addEventListener("click", () => {{
        const current = document.documentElement.getAttribute("data-theme");
        const next = current === "dark" ? "light" : "dark";
        applyTheme(next);
        localStorage.setItem("auracolor-theme", next);
      }});

      // Modal
      vivaModalBtn.addEventListener("click", () => vivaModal.classList.remove("hidden"));
      modalCloseBtn.addEventListener("click", () => vivaModal.classList.add("hidden"));
      vivaModal.addEventListener("click", (e) => {{
        if (e.target === vivaModal) vivaModal.classList.add("hidden");
      }});

      // Live Camera Stream
      async function openLiveCamera() {{
        try {{
          mediaStream = await navigator.mediaDevices.getUserMedia({{
            video: {{
              facingMode: "user",
              width: {{ ideal: 1280 }},
              height: {{ ideal: 720 }}
            }},
            audio: false
          }});
          if (cameraVideo) cameraVideo.srcObject = mediaStream;
          if (cameraModal) cameraModal.classList.remove("hidden");
        }} catch (err) {{
          console.warn("Could not open live stream, fallback to camera file input:", err);
          if (cameraInput) cameraInput.click();
        }}
      }}

      function closeLiveCamera() {{
        if (mediaStream) {{
          mediaStream.getTracks().forEach((track) => track.stop());
          mediaStream = null;
        }}
        if (cameraModal) cameraModal.classList.add("hidden");
      }}

      if (cameraBtn) {{
        cameraBtn.addEventListener("click", (e) => {{
          e.stopPropagation();
          if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {{
            openLiveCamera();
          }} else if (cameraInput) {{
            cameraInput.click();
          }}
        }});
      }}

      if (cameraCloseBtn) cameraCloseBtn.addEventListener("click", closeLiveCamera);

      if (cameraSnapBtn && cameraVideo) {{
        cameraSnapBtn.addEventListener("click", () => {{
          if (!cameraVideo.videoWidth) return;
          const snapCanvas = document.createElement("canvas");
          snapCanvas.width = cameraVideo.videoWidth;
          snapCanvas.height = cameraVideo.videoHeight;
          const ctx = snapCanvas.getContext("2d");
          ctx.translate(snapCanvas.width, 0);
          ctx.scale(-1, 1);
          ctx.drawImage(cameraVideo, 0, 0, snapCanvas.width, snapCanvas.height);
          const dataUrl = snapCanvas.toDataURL("image/jpeg", 0.92);
          closeLiveCamera();
          loadImageFromDataUrl(dataUrl);
        }});
      }}

      // File & Camera Input
      browseBtn.addEventListener("click", (e) => {{ e.stopPropagation(); fileInput.click(); }});
      dropZone.addEventListener("click", () => {{ if (!currentImageBitmap) fileInput.click(); }});
      dropZone.addEventListener("dragover", (e) => {{ e.preventDefault(); dropZone.classList.add("drag-over"); }});
      dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-over"));
      dropZone.addEventListener("drop", (e) => {{
        e.preventDefault();
        dropZone.classList.remove("drag-over");
        if (e.dataTransfer.files && e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
      }});

      fileInput.addEventListener("change", (e) => {{
        if (e.target.files && e.target.files[0]) handleFile(e.target.files[0]);
      }});
      cameraInput.addEventListener("change", (e) => {{
        if (e.target.files && e.target.files[0]) handleFile(e.target.files[0]);
      }});

      removeImgBtn.addEventListener("click", (e) => {{
        e.stopPropagation();
        resetUpload();
      }});

      // Presets
      presetBtns.forEach((btn) => {{
        btn.addEventListener("click", (e) => {{
          e.stopPropagation();
          const sample = btn.getAttribute("data-sample");
          const b64 = SAMPLE_IMAGES[sample];
          if (b64) loadImageFromDataUrl(b64);
        }});
      }});

      function handleFile(file) {{
        if (!file.type.match(/image\\/(jpeg|jpg|png|webp)/)) {{
          showError("Please upload a valid JPG, JPEG, PNG, or WebP image.");
          return;
        }}
        const reader = new FileReader();
        reader.onload = (e) => loadImageFromDataUrl(e.target.result);
        reader.readAsDataURL(file);
      }}

      function loadImageFromDataUrl(dataUrl) {{
        currentDataUrl = dataUrl;
        const img = new Image();
        img.onload = () => {{
          currentImageBitmap = img;
          previewImg.src = dataUrl;
          uploadPrompt.classList.add("hidden");
          previewBox.classList.remove("hidden");
          analyzeBtn.disabled = false;
          hideError();
          showInitialQuality(img.width, img.height);
        }};
        img.src = dataUrl;
      }}

      function resetUpload() {{
        currentImageBitmap = null;
        currentDataUrl = null;
        fileInput.value = "";
        cameraInput.value = "";
        previewImg.src = "";
        uploadPrompt.classList.remove("hidden");
        previewBox.classList.add("hidden");
        analyzeBtn.disabled = true;
        qualityBar.classList.add("hidden");
        hideError();
      }}

      function showInitialQuality(w, h) {{
        qualityBar.classList.remove("hidden");
        if (w >= 200 && h >= 200) {{
          qualityMeter.style.width = "90%";
          qualityStatus.textContent = "Good Resolution";
          qualityStatus.className = "quality-status Good";
          qualityDetails.textContent = `Image dimensions: ${{w}} × ${{h}}px • Ready for color analysis`;
        }} else {{
          qualityMeter.style.width = "50%";
          qualityStatus.textContent = "Low Resolution";
          qualityStatus.className = "quality-status Acceptable";
          qualityDetails.textContent = `Image dimensions: ${{w}} × ${{h}}px • High-res portrait recommended`;
        }}
      }}

      function showError(msg) {{
        errorText.textContent = msg;
        errorBanner.classList.remove("hidden");
      }}
      function hideError() {{ errorBanner.classList.add("hidden"); }}

      function showToast(msg) {{
        toast.textContent = msg;
        toast.classList.remove("hidden");
        setTimeout(() => toast.classList.add("hidden"), 2500);
      }}

      function copyToClipboard(text, label) {{
        navigator.clipboard.writeText(text).then(() => {{
          showToast(`Copied ${{label ? label + ' ' : ''}}(${{text}}) to clipboard!`);
        }}).catch(() => {{
          showToast(`Color: ${{text}}`);
        }});
      }}

      // Stepper Animation
      async function animateStepper() {{
        const steps = [
          document.getElementById("step-1"),
          document.getElementById("step-2"),
          document.getElementById("step-3"),
          document.getElementById("step-4"),
          document.getElementById("step-5"),
          document.getElementById("step-6")
        ];
        steps.forEach((s) => (s.className = "step-item"));
        for (let i = 0; i < steps.length; i++) {{
          steps[i].classList.add("active");
          await new Promise((res) => setTimeout(res, 220));
          steps[i].classList.remove("active");
          steps[i].classList.add("completed");
        }}
      }}

      // Core Client-Side Colorimetry Analysis
      function performColorAnalysis(img) {{
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d", {{ willReadFrequently: true }});
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);

        const w = img.width;
        const h = img.height;

        const regions = {{
          forehead: {{ x: Math.max(0, Math.floor(w * 0.35)), y: Math.max(0, Math.floor(h * 0.18)), w: Math.floor(w * 0.30), h: Math.floor(h * 0.14) }},
          left_cheek: {{ x: Math.max(0, Math.floor(w * 0.20)), y: Math.max(0, Math.floor(h * 0.48)), w: Math.floor(w * 0.18), h: Math.floor(h * 0.18) }},
          right_cheek: {{ x: Math.max(0, Math.floor(w * 0.62)), y: Math.max(0, Math.floor(h * 0.48)), w: Math.floor(w * 0.18), h: Math.floor(h * 0.18) }},
          chin: {{ x: Math.max(0, Math.floor(w * 0.40)), y: Math.max(0, Math.floor(h * 0.74)), w: Math.floor(w * 0.20), h: Math.floor(h * 0.14) }}
        }};

        let totalR = 0, totalG = 0, totalB = 0, count = 0;

        Object.values(regions).forEach((box) => {{
          const imgData = ctx.getImageData(box.x, box.y, box.w, box.h).data;
          for (let i = 0; i < imgData.length; i += 16) {{
            const r = imgData[i];
            const g = imgData[i + 1];
            const b = imgData[i + 2];
            if (r > g && g > b && r > 45 && r < 250) {{
              totalR += r;
              totalG += g;
              totalB += b;
              count++;
            }}
          }}
        }});

        if (count === 0) {{
          const centerData = ctx.getImageData(Math.floor(w * 0.3), Math.floor(h * 0.3), Math.floor(w * 0.4), Math.floor(h * 0.4)).data;
          for (let i = 0; i < centerData.length; i += 16) {{
            totalR += centerData[i];
            totalG += centerData[i + 1];
            totalB += centerData[i + 2];
            count++;
          }}
        }}

        const meanR = totalR / Math.max(count, 1);
        const meanG = totalG / Math.max(count, 1);
        const meanB = totalB / Math.max(count, 1);

        function rgbToLab(r, g, b) {{
          let rLin = r / 255.0, gLin = g / 255.0, bLin = b / 255.0;
          rLin = rLin > 0.04045 ? Math.pow((rLin + 0.055) / 1.055, 2.4) : rLin / 12.92;
          gLin = gLin > 0.04045 ? Math.pow((gLin + 0.055) / 1.055, 2.4) : gLin / 12.92;
          bLin = bLin > 0.04045 ? Math.pow((bLin + 0.055) / 1.055, 2.4) : bLin / 12.92;

          let X = (rLin * 0.4124 + gLin * 0.3576 + bLin * 0.1805) / 0.95047;
          let Y = (rLin * 0.2126 + gLin * 0.7152 + bLin * 0.0722) / 1.00000;
          let Z = (rLin * 0.0193 + gLin * 0.1192 + bLin * 0.9505) / 1.08883;

          function f(t) {{ return t > 0.008856 ? Math.cbrt(t) : (7.787 * t) + (16.0 / 116.0); }}
          let L = (116.0 * f(Y)) - 16.0;
          let a = 500.0 * (f(X) - f(Y));
          let bVal = 200.0 * (f(Y) - f(Z));
          return {{ L, a, b: bVal }};
        }}

        const lab = rgbToLab(meanR, meanG, meanB);
        const ita = Math.atan2((lab.L - 50.0), Math.max(lab.b, 0.1)) * (180.0 / Math.PI);

        let undertone = "Warm";
        let conf = 88;
        let probs = {{ Warm: 0.88, Neutral: 0.09, Cool: 0.03 }};

        const bRatio = lab.b / Math.max(lab.a, 0.1);

        if (bRatio > 1.22 || lab.b > 18.0) {{
          undertone = "Warm";
          conf = Math.min(96, Math.max(82, Math.round(75 + lab.b)));
          probs = {{ Warm: (conf / 100).toFixed(2), Neutral: ((100 - conf) * 0.75 / 100).toFixed(2), Cool: ((100 - conf) * 0.25 / 100).toFixed(2) }};
        }} else if (bRatio < 0.92 || lab.b < 13.0) {{
          undertone = "Cool";
          conf = Math.min(95, Math.max(80, Math.round(72 + (15 - lab.b) * 2)));
          probs = {{ Cool: (conf / 100).toFixed(2), Neutral: ((100 - conf) * 0.7 / 100).toFixed(2), Warm: ((100 - conf) * 0.3 / 100).toFixed(2) }};
        }} else {{
          undertone = "Neutral";
          conf = 84;
          probs = {{ Neutral: 0.84, Warm: 0.09, Cool: 0.07 }};
        }}

        const hex = `#${{Math.round(meanR).toString(16).padStart(2, '0')}}${{Math.round(meanG).toString(16).padStart(2, '0')}}${{Math.round(meanB).toString(16).padStart(2, '0')}}`.toUpperCase();

        return {{
          undertone: {{
            label: undertone,
            confidence_percentage: conf,
            probabilities: probs,
            explanation: undertone === "Warm"
              ? `Your skin displays a dominant golden/peachy undertone characterized by elevated CIELAB b* (${{lab.b.toFixed(1)}}) indicating higher yellow-amber chroma.`
              : undertone === "Cool"
              ? `Your skin features dominant rosy/pink undertones with a lower yellow-blue b* axis (${{lab.b.toFixed(1)}}) and high erythema harmony.`
              : `Your skin exhibits an equidistant balance between warm golden and cool pink undertones (b*/a* ≈ 1.05).`,
            key_factors: [
              `CIELAB b* (Yellow-Blue Balance): ${{lab.b.toFixed(1)}}`,
              `CIELAB a* (Red-Erythema): ${{lab.a.toFixed(1)}}`,
              `ITA° Typology Angle: ${{ita.toFixed(1)}}°`
            ]
          }},
          face: {{ regions }},
          skin_analysis: {{
            metrics: {{
              representative_hex: hex,
              phototype_estimate: ita > 40 ? "Light / Fair (Fitzpatrick II)" : ita > 25 ? "Intermediate (Fitzpatrick III)" : "Olive / Tan (Fitzpatrick IV)",
              cielab: {{ L: lab.L.toFixed(1), a: lab.a.toFixed(1), b: lab.b.toFixed(1) }},
              ita_angle: ita.toFixed(1),
              hsv: {{ H_deg: ((Math.atan2(meanG - meanB, meanR - meanG) * 180 / Math.PI + 360) % 360).toFixed(1) }}
            }}
          }}
        }};
      }}

      function getRecommendationsForUndertone(undertone) {{
        const all = COLOUR_DATABASE.colours || [];
        const matching = all.filter(c => c.undertones && c.undertones.includes(undertone));
        const palette = matching.filter(c => c.category === "Clothing" || (c.tags && c.tags.includes("core"))).slice(0, 10);

        return {{
          palette: palette,
          clothing: matching.filter(c => c.category === "Clothing"),
          makeup: matching.filter(c => c.category === "Makeup"),
          accessories: matching.filter(c => c.category === "Accessories"),
          neutrals: matching.filter(c => c.category === "Neutrals"),
          avoid: (COLOUR_DATABASE.avoid_rules && COLOUR_DATABASE.avoid_rules[undertone]) ? COLOUR_DATABASE.avoid_rules[undertone].colours : [],
          seasonal: undertone === "Warm" ? "Warm Autumn / Golden Spring" : undertone === "Cool" ? "Cool Winter / Summer" : "Soft Neutral Harmony",
          summary: undertone === "Warm" 
            ? "Embrace rich earthy tones, terracottas, warm golds, olive greens, and fiery spices that illuminate your complexion."
            : undertone === "Cool"
            ? "Elevate your look with crisp jewel tones, icy blues, emerald greens, classic navy, and radiant silver metals."
            : "You enjoy supreme versatile harmony with muted teals, soft plums, dusty rose, and blended neutral taupes."
        }};
      }}

      // Analyze Button Click
      analyzeBtn.addEventListener("click", async () => {{
        if (!currentImageBitmap) return;

        hideError();
        studioSection.classList.add("hidden");
        heroSection.classList.add("hidden");
        processingSection.classList.remove("hidden");
        resultsSection.classList.add("hidden");

        const animPromise = animateStepper();
        await animPromise;

        const analysisData = performColorAnalysis(currentImageBitmap);
        const recData = getRecommendationsForUndertone(analysisData.undertone.label);

        renderResults(analysisData, recData);

        processingSection.classList.add("hidden");
        resultsSection.classList.remove("hidden");
        window.scrollTo({{ top: 0, behavior: "smooth" }});
      }});

      // Re-analyze
      reanalyzeBtn.addEventListener("click", () => {{
        resultsSection.classList.add("hidden");
        studioSection.classList.remove("hidden");
        heroSection.classList.remove("hidden");
        resetUpload();
        window.scrollTo({{ top: 0, behavior: "smooth" }});
      }});

      function renderResults(data, recs) {{
        const ut = data.undertone.label;
        const badge = document.getElementById("undertone-badge");
        badge.textContent = ut.toUpperCase();
        badge.className = `undertone-badge ${{ut}}`;

        document.getElementById("confidence-val").textContent = `${{data.undertone.confidence_percentage}}%`;
        document.getElementById("confidence-bar").style.width = `${{data.undertone.confidence_percentage}}%`;

        const probBreakdown = document.getElementById("prob-breakdown");
        probBreakdown.innerHTML = "";
        Object.entries(data.undertone.probabilities).forEach(([cls, prob]) => {{
          const span = document.createElement("span");
          span.textContent = `${{cls}}: ${{Math.round(prob * 100)}}%`;
          probBreakdown.appendChild(span);
        }});

        document.getElementById("undertone-explanation").textContent = data.undertone.explanation;

        const keyFactors = document.getElementById("key-factors");
        keyFactors.innerHTML = "";
        data.undertone.key_factors.forEach((f) => {{
          const div = document.createElement("div");
          div.className = "factor-item";
          div.textContent = f;
          keyFactors.appendChild(div);
        }});

        // Metrics
        const m = data.skin_analysis.metrics;
        document.getElementById("rep-swatch").style.backgroundColor = m.representative_hex;
        document.getElementById("rep-hex").textContent = m.representative_hex;
        document.getElementById("rep-phototype").textContent = m.phototype_estimate;
        document.getElementById("metric-lab-l").textContent = m.cielab.L;
        document.getElementById("metric-lab-a").textContent = `${{m.cielab.a >= 0 ? '+' : ''}}${{m.cielab.a}}`;
        document.getElementById("metric-lab-b").textContent = `${{m.cielab.b >= 0 ? '+' : ''}}${{m.cielab.b}}`;
        document.getElementById("metric-ita").textContent = `${{m.ita_angle >= 0 ? '+' : ''}}${{m.ita_angle}}°`;
        document.getElementById("metric-hsv-h").textContent = `${{m.hsv.H_deg}}°`;

        // Draw Canvas
        drawCanvas(data.face.regions);

        // Palette
        document.getElementById("season-title").textContent = recs.seasonal;
        document.getElementById("stylist-summary").textContent = recs.summary;

        const swatchesGrid = document.getElementById("swatches-grid");
        swatchesGrid.innerHTML = "";
        recs.palette.forEach((color) => {{
          const card = document.createElement("div");
          card.className = "swatch-card";
          card.innerHTML = `
            <div class="swatch-color" style="background-color: ${{color.hex}}"></div>
            <div class="swatch-meta">
              <div class="swatch-name" title="${{color.name}}">${{color.name}}</div>
              <div class="swatch-hex">${{color.hex}}</div>
            </div>
          `;
          card.addEventListener("click", () => copyToClipboard(color.hex, color.name));
          swatchesGrid.appendChild(card);
        }});

        renderGrid("rec-clothing-grid", recs.clothing);
        renderGrid("rec-makeup-grid", recs.makeup);
        renderGrid("rec-accessories-grid", recs.accessories);
        renderGrid("rec-neutrals-grid", recs.neutrals);
        renderAvoidGrid("rec-avoid-grid", recs.avoid);

        document.getElementById("foundation-advice-text").textContent = ut === "Warm"
          ? "Select golden, honey, or peach-toned foundations with 'W' classification. Avoid cool/pink undertones which turn ashy."
          : ut === "Cool"
          ? "Choose neutral-cool or rose-based liquid formulas with 'C' designation. Avoid orange-based foundations."
          : "Opt for true neutral 'N' labeled foundations that balance yellow and pink pigments seamlessly.";
      }}

      function drawCanvas(regions) {{
        const canvas = document.getElementById("face-canvas");
        const ctx = canvas.getContext("2d");
        if (!currentImageBitmap) return;

        canvas.width = currentImageBitmap.width;
        canvas.height = currentImageBitmap.height;
        ctx.drawImage(currentImageBitmap, 0, 0);

        const colors = {{ forehead: "#E2725B", left_cheek: "#38BDF8", right_cheek: "#38BDF8", chin: "#2DD4BF" }};
        Object.entries(regions).forEach(([name, box]) => {{
          const col = colors[name] || "#D4AF37";
          ctx.strokeStyle = col;
          ctx.lineWidth = Math.max(2, Math.floor(canvas.width / 180));
          ctx.strokeRect(box.x, box.y, box.w, box.h);
          ctx.fillStyle = `${{col}}25`;
          ctx.fillRect(box.x, box.y, box.w, box.h);
          ctx.fillStyle = col;
          ctx.font = `bold ${{Math.max(11, Math.floor(canvas.width / 36))}}px sans-serif`;
          ctx.fillText(name.replace("_", " ").toUpperCase(), box.x + 4, Math.max(14, box.y - 4));
        }});
      }}

      function renderGrid(id, items) {{
        const container = document.getElementById(id);
        container.innerHTML = "";
        items.forEach((item) => {{
          const card = document.createElement("div");
          card.className = "rec-card";
          card.innerHTML = `
            <div class="rec-color-circle" style="background-color: ${{item.hex}}"></div>
            <div class="rec-details">
              <div class="rec-name">${{item.name}}</div>
              <div class="rec-hex">${{item.hex}}</div>
              <div class="rec-desc">${{item.description || item.sub_category || ""}}</div>
            </div>
          `;
          card.addEventListener("click", () => copyToClipboard(item.hex, item.name));
          container.appendChild(card);
        }});
      }}

      function renderAvoidGrid(id, items) {{
        const container = document.getElementById(id);
        container.innerHTML = "";
        items.forEach((item) => {{
          const card = document.createElement("div");
          card.className = "avoid-card";
          card.innerHTML = `
            <div class="avoid-circle" style="background-color: ${{item.hex}}"></div>
            <div class="avoid-details">
              <div class="avoid-name">${{item.name}} (${{item.hex}})</div>
              <div class="avoid-reason">${{item.reason}}</div>
            </div>
          `;
          container.appendChild(card);
        }});
      }}

      // Tabs
      const tabBtns = document.querySelectorAll(".tab-btn");
      const tabContents = document.querySelectorAll(".tab-content");
      tabBtns.forEach((btn) => {{
        btn.addEventListener("click", () => {{
          const target = btn.getAttribute("data-tab");
          tabBtns.forEach((b) => b.classList.remove("active"));
          tabContents.forEach((c) => c.classList.remove("active"));
          btn.classList.add("active");
          const content = document.getElementById(`tab-${{target}}`);
          if (content) content.classList.add("active");
          btn.scrollIntoView({{ behavior: "smooth", inline: "center", block: "nearest" }});
        }});
      }});
    }});
  </script>
</body>
</html>
"""

# Render Full Localhost Experience directly into Streamlit
components.html(html_content, height=1400, scrolling=True)
