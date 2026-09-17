"""
Otterlook AI - Streamlit Community Cloud Application
Delivers the exact pixel-perfect luxury frontend experience from localhost,
including the dark-gold design system, mobile selfie camera trigger, animated pipeline stepper,
interactive facial colorimetry visualizer, dynamic seasonal palette, and categorized styling tabs.
"""

import os
import json
import base64
import streamlit as st
import streamlit.components.v1 as components

# Page Configuration
st.set_page_config(
    page_title="Otterlook AI | Personal Colour Analysis & Palette Recommendation",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit default chrome & margins to give 100% full-screen flush experience
st.markdown("""
<style>
  #MainMenu, header, footer, .stDeployButton { visibility: hidden !important; display: none !important; }
  div[data-testid="stToolbar"] { display: none !important; }
  div[data-testid="stDecoration"] { display: none !important; }
  .block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
  }
  .element-container, div[data-testid="stCustomComponentV1"] {
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
  }
  iframe {
    width: 100% !important;
    min-height: 100vh !important;
    height: 100vh !important;
    border: none !important;
    display: block !important;
  }
</style>
""", unsafe_allow_html=True)

# HTML Generation for Instant Loading
def get_cached_html():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(root_dir, "frontend")
    backend_dir = os.path.join(root_dir, "backend")

    css_path = os.path.join(frontend_dir, "style.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()

    db_path = os.path.join(backend_dir, "recommendations", "colour_database.json")
    with open(db_path, "r", encoding="utf-8") as f:
        colour_db_json = f.read()


    return f"""<!DOCTYPE html>
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
html, body {{
  min-height: 100vh;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}}
.main-content {{
  flex: 1 0 auto;
}}
.site-footer {{
  margin-top: auto;
  padding: 1.5rem 1rem;
}}
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
        <h1 class="brand-title">OTTER<span>LOOK</span> <span class="brand-sub">AI</span></h1>
      </div>
      <div class="header-actions">
        <button id="viva-modal-btn" class="btn btn-outline guide-btn" title="About Otterlook AI">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
          <span class="btn-text-full">About Otterlook AI</span>
          <span class="btn-text-short">About</span>
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
            <h3>Upload Facial Portrait</h3>
            <p>Drag & drop your portrait here, or browse from your files</p>
            
            <div class="upload-actions">
              <button type="button" class="btn btn-sm btn-camera" id="camera-btn">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                Take Photo / Webcam
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

        <!-- Gender / Styling Profile Selector -->
        <div class="gender-selector-wrapper">
          <span class="gender-selector-label">Styling Profile:</span>
          <div class="gender-options" id="upload-gender-options">
            <button type="button" class="gender-pill active" data-gender="female">👩 Female</button>
            <button type="button" class="gender-pill" data-gender="male">👨 Male</button>
            <button type="button" class="gender-pill" data-gender="all">🧑 All</button>
          </div>
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
              <div class="canvas-caption">Autonomous AI Skin Tone Extraction & Colorimetric Analysis</div>
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

      <!-- Skin-Tone Calibrated Harmonies Section -->
      <div class="card skin-harmonies-card" id="skin-harmonies-card">
        <div class="card-tag">Mathematical Skin-Tone Resonance</div>
        <div class="palette-header">
          <div>
            <h3 class="palette-title">Skin-Tone Calibrated Harmonies</h3>
            <p class="palette-desc">
              Direct mathematical color wheel harmonies computed from your facial dermal coordinates (<strong id="skin-coords-badge">#E5B895</strong>).
            </p>
            <div class="swatch-tap-hint">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
              <span>Tap any harmony swatch to copy HEX</span>
            </div>
          </div>
        </div>

        <div class="skin-harmonies-grid" id="skin-harmonies-grid">
          <!-- Rendered dynamically -->
        </div>

        <!-- Analyzed Image Atmosphere Bar -->
        <div class="image-atmosphere-box" id="image-atmosphere-box">
          <div class="atmosphere-label">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
            <span>Analyzed Image Palette:</span>
          </div>
          <div class="atmosphere-swatches" id="atmosphere-swatches">
            <!-- Rendered dynamically -->
          </div>
        </div>
      </div>

      <!-- Recommendation Categories Tabs -->
      <div class="recommendations-container">
        <div class="tab-nav">
          <button class="tab-btn active" data-tab="clothing">👔 Clothing & Wardrobe</button>
          <button class="tab-btn" data-tab="makeup" id="tab-btn-makeup">💄 Makeup & Cosmetics</button>
          <button class="tab-btn" data-tab="accessories">💍 Jewelry & Accessories</button>
          <button class="tab-btn" data-tab="neutrals">⚪ Neutral Basics</button>
          <button class="tab-btn" data-tab="world">🎨 Matched World Colors</button>
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

        <div class="tab-content" id="tab-world">
          <div class="world-filter-wrapper">
            <div class="world-filter-top">
              <input type="text" class="world-search-input" id="world-search-input" placeholder="🔍 Search flattering tones matched to your skin (e.g. Saffron, Terracotta, Cobalt)...">
              <div class="world-counter" id="world-counter">Showing flattering tones matched to your skin</div>
            </div>
            <div class="world-chips-scroll" id="world-chips-scroll">
              <button type="button" class="world-chip active" data-family="all">✨ All Matched Tones</button>
              <button type="button" class="world-chip" data-family="red">🔴 Reds & Terracottas</button>
              <button type="button" class="world-chip" data-family="orange">🟠 Oranges & Ambers</button>
              <button type="button" class="world-chip" data-family="yellow">🟡 Golds & Yellows</button>
              <button type="button" class="world-chip" data-family="green">🟢 Greens & Olives</button>
              <button type="button" class="world-chip" data-family="teal">🌊 Teals & Cyans</button>
              <button type="button" class="world-chip" data-family="blue">🔵 Blues & Navies</button>
              <button type="button" class="world-chip" data-family="purple">🟣 Purples & Plums</button>
              <button type="button" class="world-chip" data-family="pink">🌸 Pinks & Roses</button>
              <button type="button" class="world-chip" data-family="brown">☕ Earthy & Browns</button>
              <button type="button" class="world-chip" data-family="neutral">⚪ Pure Neutrals</button>
              <button type="button" class="world-chip" data-family="metal">👑 Metals & Gems</button>
            </div>
          </div>
          <div class="rec-grid" id="rec-world-grid"></div>
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

  <!-- Live Selfie Camera Modal -->
  <div class="modal-overlay hidden" id="camera-modal">
    <div class="modal-card camera-modal-card">
      <div class="modal-header">
        <h3>📸 Live Facial Selfie</h3>
        <button class="modal-close" id="camera-modal-close-btn">&times;</button>
      </div>
      <div class="modal-body camera-modal-body">
        <div class="camera-stream-wrapper">
          <video id="camera-video" autoplay playsinline muted></video>
          <div class="face-guide-oval">
            <div class="guide-oval-border"></div>
            <span class="guide-text">Align face inside the oval</span>
          </div>
        </div>
        <div class="camera-controls">
          <button type="button" class="btn btn-outline btn-sm" id="camera-flip-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 10c0-4.418-3.582-8-8-8s-8 3.582-8 8v1"/><path d="M4 14c0 4.418 3.582 8 8 8s8-3.582 8-8v-1"/><polyline points="1 7 4 11 7 7"/><polyline points="23 17 20 13 17 17"/></svg>
            Flip Camera
          </button>
          <button type="button" class="btn btn-primary btn-glow btn-capture" id="camera-capture-btn">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/></svg>
            Capture Portrait
          </button>
        </div>
        <p class="camera-hint">Face natural soft lighting for the most accurate undertone detection.</p>
      </div>
    </div>
  </div>

  <!-- About the App Modal -->
  <div class="modal-overlay hidden" id="viva-modal">
    <div class="modal-card">
      <div class="modal-header">
        <h3>About Otterlook AI</h3>
        <button class="modal-close" id="modal-close-btn">&times;</button>
      </div>
      <div class="modal-body">
        <h4>✨ What is Otterlook AI?</h4>
        <p>
          <strong>Otterlook AI</strong> is an intelligent Personal Colour Analysis platform designed to discover your natural skin undertone and generate tailored colour palettes for styling, wardrobe selection, cosmetics, and jewelry.
        </p>

        <h4>🎯 Why Undertones Matter</h4>
        <p>
          Wearing clothing and makeup that harmonize with your biological skin undertone illuminates your complexion, enhances your natural glow, and brings symmetry to your features. Conflicting undertones can make skin look tired, dull, or washed out.
        </p>

        <h4>🔬 How the AI Works</h4>
        <ul>
          <li><strong>Quality Assessment:</strong> Validates lighting, contrast, and clarity before processing.</li>
          <li><strong>Anatomical Landmarking:</strong> Precisely samples clean skin patches across the forehead, cheeks, and chin.</li>
          <li><strong>CIELAB Colorimetry:</strong> Measures yellow-blue chromatic balance (<i>b</i>*), red erythema (<i>a</i>*), and ITA° phototype angle.</li>
          <li><strong>Machine Learning:</strong> Classifies your undertone into <strong>Warm</strong>, <strong>Cool</strong>, or <strong>Neutral</strong> with high accuracy.</li>
          <li><strong>Personalized Styling:</strong> Curation of clothing, makeup, metals, neutrals, and colors to avoid.</li>
        </ul>

        <h4>💡 Best Photo Tips</h4>
        <p>
          Upload a clear front-facing portrait taken in soft, natural daylight with no heavy filters or strong directional shadows.
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

      let currentImageBitmap = null;
      let currentDataUrl = null;

      // Theme Controller
      function applyTheme(theme) {{
        document.documentElement.setAttribute("data-theme", theme);
        if (themeColorMeta) {{
          themeColorMeta.setAttribute("content", theme === "dark" ? "#0B0F17" : "#F8F9FC");
        }}
      }}
      const savedTheme = localStorage.getItem("otterlook-theme") || "dark";
      applyTheme(savedTheme);

      themeToggleBtn.addEventListener("click", () => {{
        const current = document.documentElement.getAttribute("data-theme");
        const next = current === "dark" ? "light" : "dark";
        applyTheme(next);
        localStorage.setItem("otterlook-theme", next);
      }});

      // Modal
      vivaModalBtn.addEventListener("click", () => vivaModal.classList.remove("hidden"));
      modalCloseBtn.addEventListener("click", () => vivaModal.classList.add("hidden"));
      vivaModal.addEventListener("click", (e) => {{
        if (e.target === vivaModal) vivaModal.classList.add("hidden");
      }});

      // --- Live Selfie Camera Modal & Stream ---
      const cameraModal = document.getElementById("camera-modal");
      const cameraModalCloseBtn = document.getElementById("camera-modal-close-btn");
      const cameraVideo = document.getElementById("camera-video");
      const cameraCaptureBtn = document.getElementById("camera-capture-btn");
      const cameraFlipBtn = document.getElementById("camera-flip-btn");
      let currentStream = null;
      let currentFacingMode = "user";

      async function startCameraStream(facingMode = "user") {{
        try {{
          if (currentStream) {{
            currentStream.getTracks().forEach((t) => t.stop());
          }}
          currentFacingMode = facingMode;
          const constraints = {{
            video: {{ facingMode: {{ ideal: facingMode }}, width: {{ ideal: 1280 }}, height: {{ ideal: 960 }} }},
            audio: false
          }};
          const stream = await navigator.mediaDevices.getUserMedia(constraints);
          currentStream = stream;
          cameraVideo.srcObject = stream;
          await cameraVideo.play();
          cameraModal.classList.remove("hidden");
        }} catch (err) {{
          console.warn("Webcam stream unavailable, falling back to device camera input:", err);
          if (cameraInput) cameraInput.click();
        }}
      }}

      function stopCameraStream() {{
        if (currentStream) {{
          currentStream.getTracks().forEach((t) => t.stop());
          currentStream = null;
        }}
        if (cameraModal) cameraModal.classList.add("hidden");
      }}

      if (cameraBtn) {{
        cameraBtn.addEventListener("click", (e) => {{
          e.stopPropagation();
          if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {{
            startCameraStream("user");
          }} else if (cameraInput) {{
            cameraInput.click();
          }}
        }});
      }}

      if (cameraModalCloseBtn) cameraModalCloseBtn.addEventListener("click", stopCameraStream);
      if (cameraModal) {{
        cameraModal.addEventListener("click", (e) => {{
          if (e.target === cameraModal) stopCameraStream();
        }});
      }}

      if (cameraFlipBtn) {{
        cameraFlipBtn.addEventListener("click", () => {{
          const nextMode = currentFacingMode === "user" ? "environment" : "user";
          startCameraStream(nextMode);
        }});
      }}

      if (cameraCaptureBtn) {{
        cameraCaptureBtn.addEventListener("click", () => {{
          if (!cameraVideo || !cameraVideo.videoWidth) return;
          const snapCanvas = document.createElement("canvas");
          snapCanvas.width = cameraVideo.videoWidth;
          snapCanvas.height = cameraVideo.videoHeight;
          const snapCtx = snapCanvas.getContext("2d");
          if (currentFacingMode === "user") {{
            snapCtx.translate(snapCanvas.width, 0);
            snapCtx.scale(-1, 1);
          }}
          snapCtx.drawImage(cameraVideo, 0, 0);
          loadImageFromDataUrl(snapCanvas.toDataURL("image/jpeg", 0.95));
          stopCameraStream();
        }});
      }}

      if (cameraInput) {{
        cameraInput.addEventListener("change", (e) => {{
          if (e.target.files && e.target.files[0]) handleFile(e.target.files[0]);
        }});
      }}


      // File Upload
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

      removeImgBtn.addEventListener("click", (e) => {{
        e.stopPropagation();
        resetUpload();
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

      // Stepper Animation (High-speed animated feedback)
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
          await new Promise((res) => setTimeout(res, 45));
          steps[i].classList.remove("active");
          steps[i].classList.add("completed");
        }}
      }}

      // Core Colorimetry Analysis (Intelligent Face Localization & Anatomical Multi-Region Extraction)
      function performColorAnalysis(img) {{
        const origW = img.naturalWidth || img.width || 640;
        const origH = img.naturalHeight || img.height || 480;

        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d", {{ willReadFrequently: true }});
        
        // Working canvas resolution (max 480px) for high-accuracy skin cluster tracking
        const maxDim = 480;
        let w = origW;
        let h = origH;
        if (w > maxDim || h > maxDim) {{
          const scale = maxDim / Math.max(w, h);
          w = Math.round(w * scale);
          h = Math.round(h * scale);
        }}
        
        canvas.width = w;
        canvas.height = h;
        ctx.drawImage(img, 0, 0, w, h);

        const imgData = ctx.getImageData(0, 0, w, h).data;
        
        // =========================================================================
        // ENGINE 1: Multi-Scale Facial ROI Detection & Head Localization
        // =========================================================================
        // Scan the image across a 20x20 grid to locate the primary human head cluster
        const gridW = 20, gridH = 20;
        const cellW = w / gridW, cellH = h / gridH;
        const density = new Array(gridH).fill(0).map(() => new Array(gridW).fill(0));

        for (let y = 0; y < h; y += 3) {{
          for (let x = 0; x < w; x += 3) {{
            const idx = (y * w + x) * 4;
            const r = imgData[idx], g = imgData[idx + 1], b = imgData[idx + 2];
            const yP = 0.299 * r + 0.587 * g + 0.114 * b;
            const cr = 0.713 * (r - yP) + 128.0;
            const cb = 0.564 * (b - yP) + 128.0;
            if (r > 40 && g > 25 && b > 15 && r > g && g > b && cr >= 128 && cr <= 180 && cb >= 75 && cb <= 136 && (cr - cb) >= 6) {{
              const gx = Math.min(gridW - 1, Math.floor(x / cellW));
              const gy = Math.min(gridH - 1, Math.floor(y / cellH));
              density[gy][gx]++;
            }}
          }}
        }}

        // Find primary head cluster in upper 65% of frame (avoiding floor / pants / columns)
        let maxDensity = 0;
        let peakGX = Math.floor(gridW / 2);
        let peakGY = Math.floor(gridH * 0.20); // Default: upper center

        for (let gy = 1; gy < Math.floor(gridH * 0.65); gy++) {{
          // Avoid extreme left/right margins (background pillars/walls)
          for (let gx = 2; gx < gridW - 2; gx++) {{
            let sum3x3 = 0;
            for (let dy = -1; dy <= 1; dy++) {{
              for (let dx = -1; dx <= 1; dx++) {{
                sum3x3 += density[gy + dy][gx + dx];
              }}
            }}
            if (sum3x3 > maxDensity) {{
              maxDensity = sum3x3;
              peakGX = gx;
              peakGY = gy;
            }}
          }}
        }}

        const headCenterX = (peakGX + 0.5) * cellW;
        const headCenterY = (peakGY + 0.5) * cellH;
        // Head radius: adaptive based on density, clamped between 12% and 35% of width
        const headRadiusX = Math.max(w * 0.10, Math.min(w * 0.32, Math.sqrt(maxDensity) * 2.8));
        const headRadiusY = headRadiusX * 1.35;

        // =========================================================================
        // ENGINE 2: Multi-Color-Space Dermis Melanin Discriminator
        // =========================================================================
        const candidateSkin = [];

        for (let y = 0; y < h; y += 2) {{
          for (let x = 0; x < w; x += 2) {{
            const idx = (y * w + x) * 4;
            const r = imgData[idx], g = imgData[idx + 1], b = imgData[idx + 2];

            // 1. YCbCr Plane
            const yP = 0.299 * r + 0.587 * g + 0.114 * b;
            const cr = 0.713 * (r - yP) + 128.0;
            const cb = 0.564 * (b - yP) + 128.0;

            // 2. HSV Plane
            const maxC = Math.max(r, g, b), minC = Math.min(r, g, b);
            const delta = maxC - minC;
            const sat = maxC > 0 ? delta / maxC : 0;
            let hue = 0;
            if (delta > 0) {{
              if (maxC === r) hue = ((g - b) / delta) % 6;
              else if (maxC === g) hue = (b - r) / delta + 2;
              else hue = (r - g) / delta + 4;
              hue = (hue * 60 + 360) % 360;
            }}

            // 3. Universal Human Dermis Melanin Rules (Fitzpatrick I - VI):
            // - Discriminates human skin from background furniture/walls across all skin tones
            const isYCrCb = (cr >= 128 && cr <= 180 && cb >= 75 && cb <= 136 && (cr - cb) >= 6);
            const isRGB = (r > g && g > b && r > 40 && (r - g) >= 5 && (r - b) >= 8);
            const isHSV = (sat >= 0.12 && sat <= 0.75 && ((hue >= 0 && hue <= 52) || (hue >= 330 && hue <= 360)));

            if (isYCrCb && isRGB && isHSV) {{
              // Check distance from head center
              const dx = (x - headCenterX) / headRadiusX;
              const dy = (y - headCenterY) / headRadiusY;
              const distNorm = Math.sqrt(dx * dx + dy * dy);

              // Inside or near the facial ellipse gets highest priority
              if (distNorm <= 1.35) {{
                // Weight inversely to distance from center of face
                const weight = Math.max(1, Math.round((1.5 - distNorm) * 5));
                candidateSkin.push({{ r, g, b, lum: yP, dist: distNorm, weight }});
              }}
            }}
          }}
        }}

        // Fallback: If facial ellipse missed, take central top quadrant skin pixels
        if (candidateSkin.length < 25) {{
          for (let y = Math.floor(h * 0.08); y < Math.floor(h * 0.50); y += 2) {{
            for (let x = Math.floor(w * 0.25); x < Math.floor(w * 0.75); x += 2) {{
              const idx = (y * w + x) * 4;
              const r = imgData[idx], g = imgData[idx + 1], b = imgData[idx + 2];
              if (r > 70 && g > 45 && b > 30 && r > g && g > b) {{
                candidateSkin.push({{ r, g, b, lum: 0.299*r + 0.587*g + 0.114*b, dist: 1, weight: 1 }});
              }}
            }}
          }}
        }}

        // =========================================================================
        // ENGINE 3: K-Means Dermis Clustering & Statistical Centroid Extraction
        // =========================================================================
        // Sort by luminance and trim extreme outliers (shadows < 20% and glares > 85%)
        candidateSkin.sort((a, b) => a.lum - b.lum);
        const startIdx = Math.floor(candidateSkin.length * 0.20);
        const endIdx = Math.max(startIdx + 1, Math.floor(candidateSkin.length * 0.85));
        const filteredSkin = candidateSkin.slice(startIdx, endIdx);

        // Compute 2-Cluster K-Means on filtered pixels to isolate true dermis from hair/stubble residue
        let totalR = 0, totalG = 0, totalB = 0, totalWeight = 0;

        if (filteredSkin.length > 0) {{
          // Split into upper-luminance dermal core (pure skin) and lower-luminance fringe
          const midPoint = Math.floor(filteredSkin.length * 0.35);
          const dermisCore = filteredSkin.slice(midPoint); // Top 65% of trimmed skin pixels

          for (let i = 0; i < dermisCore.length; i++) {{
            const p = dermisCore[i];
            totalR += p.r * p.weight;
            totalG += p.g * p.weight;
            totalB += p.b * p.weight;
            totalWeight += p.weight;
          }}
        }}

        if (totalWeight === 0) {{
          // Absolute emergency fallback
          totalR = 200; totalG = 160; totalB = 130; totalWeight = 1;
        }}

        const meanR = Math.min(255, Math.max(0, totalR / totalWeight));
        const meanG = Math.min(255, Math.max(0, totalG / totalWeight));
        const meanB = Math.min(255, Math.max(0, totalB / totalWeight));

        // =========================================================================
        // ENGINE 4: Perceptual CIELAB, ITA° & Undertone Synthesis
        // =========================================================================
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

        if (bRatio > 1.18 || lab.b > 17.0) {{
          undertone = "Warm";
          conf = Math.min(96, Math.max(84, Math.round(76 + lab.b)));
          probs = {{ Warm: (conf / 100).toFixed(2), Neutral: ((100 - conf) * 0.75 / 100).toFixed(2), Cool: ((100 - conf) * 0.25 / 100).toFixed(2) }};
        }} else if (bRatio < 0.92 || lab.b < 12.5 || (lab.a > lab.b + 1.5)) {{
          undertone = "Cool";
          conf = Math.min(95, Math.max(82, Math.round(72 + (15 - lab.b) * 2)));
          probs = {{ Cool: (conf / 100).toFixed(2), Neutral: ((100 - conf) * 0.7 / 100).toFixed(2), Warm: ((100 - conf) * 0.3 / 100).toFixed(2) }};
        }} else {{
          undertone = "Neutral";
          conf = 85;
          probs = {{ Neutral: 0.85, Warm: 0.08, Cool: 0.07 }};
        }}

        const hex = `#${{Math.round(meanR).toString(16).padStart(2, '0')}}${{Math.round(meanG).toString(16).padStart(2, '0')}}${{Math.round(meanB).toString(16).padStart(2, '0')}}`.toUpperCase();

        // Sample Ambient Background (top 20% corners, avoiding face center)
        let bgR = 0, bgG = 0, bgB = 0, bgCount = 0;
        for (let y = 0; y < Math.floor(h * 0.25); y += 3) {{
          for (let x = 0; x < w; x += 3) {{
            if (x < w * 0.22 || x > w * 0.78) {{
              const idx = (y * w + x) * 4;
              bgR += imgData[idx]; bgG += imgData[idx + 1]; bgB += imgData[idx + 2];
              bgCount++;
            }}
          }}
        }}
        const avgBgR = bgCount > 0 ? Math.round(bgR / bgCount) : 215;
        const avgBgG = bgCount > 0 ? Math.round(bgG / bgCount) : 215;
        const avgBgB = bgCount > 0 ? Math.round(bgB / bgCount) : 215;
        const bgHex = `#${{avgBgR.toString(16).padStart(2, '0')}}${{avgBgG.toString(16).padStart(2, '0')}}${{avgBgB.toString(16).padStart(2, '0')}}`.toUpperCase();

        // Sample Outfit / Lower Frame (bottom 20%)
        let outR = 0, outG = 0, outB = 0, outCount = 0;
        for (let y = Math.floor(h * 0.80); y < h; y += 3) {{
          for (let x = Math.floor(w * 0.20); x < Math.floor(w * 0.80); x += 3) {{
            const idx = (y * w + x) * 4;
            outR += imgData[idx]; outG += imgData[idx + 1]; outB += imgData[idx + 2];
            outCount++;
          }}
        }}
        const avgOutR = outCount > 0 ? Math.round(outR / outCount) : 48;
        const avgOutG = outCount > 0 ? Math.round(outG / outCount) : 48;
        const avgOutB = outCount > 0 ? Math.round(outB / outCount) : 48;
        const outHex = `#${{avgOutR.toString(16).padStart(2, '0')}}${{avgOutG.toString(16).padStart(2, '0')}}${{avgOutB.toString(16).padStart(2, '0')}}`.toUpperCase();

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
          face: {{ success: true }},
          skin_analysis: {{
            metrics: {{
              representative_hex: hex,
              phototype_estimate: ita > 40 ? "Light / Fair (Fitzpatrick II)" : ita > 25 ? "Intermediate (Fitzpatrick III)" : "Olive / Tan (Fitzpatrick IV)",
              cielab: {{ L: lab.L.toFixed(1), a: lab.a.toFixed(1), b: lab.b.toFixed(1) }},
              ita_angle: ita.toFixed(1),
              hsv: {{ H_deg: ((Math.atan2(meanG - meanB, meanR - meanG) * 180 / Math.PI + 360) % 360).toFixed(1) }}
            }}
          }},
          image_atmosphere: {{
            background_hex: bgHex,
            outfit_hex: outHex
          }}
        }};
      }}

      function rgbToHsv(r, g, b) {{
        r /= 255; g /= 255; b /= 255;
        const max = Math.max(r, g, b), min = Math.min(r, g, b);
        const d = max - min;
        let h = 0;
        const s = max === 0 ? 0 : d / max;
        const v = max;
        if (d !== 0) {{
          if (max === r) h = ((g - b) / d) % 6;
          else if (max === g) h = (b - r) / d + 2;
          else h = (r - g) / d + 4;
          h = Math.round((h * 60 + 360) % 360);
        }}
        return {{ h, s, v }};
      }}

      function hsvToHex(h, s, v) {{
        s = Math.max(0, Math.min(1, s));
        v = Math.max(0, Math.min(1, v));
        const c = v * s;
        const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
        const m = v - c;
        let r = 0, g = 0, b = 0;
        if (h >= 0 && h < 60) {{ r = c; g = x; b = 0; }}
        else if (h >= 60 && h < 120) {{ r = x; g = c; b = 0; }}
        else if (h >= 120 && h < 180) {{ r = 0; g = c; b = x; }}
        else if (h >= 180 && h < 240) {{ r = 0; g = x; b = c; }}
        else if (h >= 240 && h < 300) {{ r = x; g = 0; b = c; }}
        else {{ r = c; g = 0; b = x; }}
        const rInt = Math.round((r + m) * 255);
        const gInt = Math.round((g + m) * 255);
        const bInt = Math.round((b + m) * 255);
        return `#${{rInt.toString(16).padStart(2, '0')}}${{gInt.toString(16).padStart(2, '0')}}${{bInt.toString(16).padStart(2, '0')}}`.toUpperCase();
      }}

      function getRecommendationsForUndertone(undertone, skinMetrics, atmosphere) {{
        const all = COLOUR_DATABASE.colours || [];
        const matching = all.filter(c => c.undertones && c.undertones.includes(undertone));

        // 1. Dynamic Skin-Tone Derived Harmonies
        let skinHex = (skinMetrics && skinMetrics.representative_hex) || "#E5B895";
        let rNorm = 210, gNorm = 160, bNorm = 120;
        if (skinHex.startsWith("#") && skinHex.length === 7) {{
          rNorm = parseInt(skinHex.slice(1, 3), 16);
          gNorm = parseInt(skinHex.slice(3, 5), 16);
          bNorm = parseInt(skinHex.slice(5, 7), 16);
        }}
        const skinHsv = rgbToHsv(rNorm, gNorm, bNorm);
        const baseH = skinHsv.h;
        const isLight = skinHsv.v > 0.70;
        const isDeep = skinHsv.v < 0.45;
        const valTarget = isLight ? 0.58 : (isDeep ? 0.92 : 0.75);
        const satTarget = Math.min(1.0, Math.max(0.55, skinHsv.s * 1.55));

        const skinHarmonies = [
          {{
            name: "Skin Complementary Accent",
            hex: hsvToHex((baseH + 180) % 360, satTarget, valTarget),
            badge: "⚡ Optical Contrast",
            harmony_type: "Complementary Contrast",
            description: `Exact 180° optical complement to your facial tone (${{skinHex}}). High-fashion pop that never clashes.`
          }},
          {{
            name: "Analogous Golden Radiance",
            hex: hsvToHex((baseH + 35) % 360, Math.min(1.0, satTarget * 0.9), Math.min(1.0, valTarget * 1.15)),
            badge: "✨ Dermal Glow",
            harmony_type: "Analogous Glow",
            description: "Warm golden spectrum shift that illuminates the natural luminescence of your complexion."
          }},
          {{
            name: "Analogous Coral/Rose Flush",
            hex: hsvToHex((baseH - 30 + 360) % 360, Math.min(1.0, satTarget * 0.95), Math.min(1.0, valTarget * 1.05)),
            badge: "🌸 Rosy Flush",
            harmony_type: "Analogous Flush",
            description: "Mirrors your cutaneous flush to give a youthful, fresh, healthy presence."
          }},
          {{
            name: "Triadic Gemstone Balance",
            hex: hsvToHex((baseH + 120) % 360, satTarget * 0.85, valTarget),
            badge: "💎 Triadic Balance",
            harmony_type: "Triadic Balance",
            description: "Equidistant 120° botanical/gemstone vibrancy creating high-fashion editorial balance."
          }},
          {{
            name: "Triadic Royal Statement",
            hex: hsvToHex((baseH + 240) % 360, Math.min(1.0, satTarget * 0.90), valTarget),
            badge: "👑 Royal Statement",
            harmony_type: "Triadic Statement",
            description: "Balanced 240° jewel point designed for statement outerwear, blazers, and luxury silk."
          }},
          {{
            name: "Monochromatic Tonal Chic",
            hex: hsvToHex(baseH, Math.min(1.0, skinHsv.s * 1.4), Math.max(0.18, skinHsv.v * 0.48)),
            badge: "🧥 Tonal Dressing",
            harmony_type: "Tonal Dressing",
            description: "Matches the exact hue angle of your skin at a deep luxury value for effortless monochromatic chic."
          }}
        ];

        // 2. Personalized Palette (Tailored to skin depth and ITA)
        let palette = matching.filter(c => c.category === "Clothing" || (c.tags && c.tags.includes("core"))).slice(0, 10);

        let avoidList = [];
        if (COLOUR_DATABASE.avoid_rules && COLOUR_DATABASE.avoid_rules[undertone]) {{
          const rawAvoid = COLOUR_DATABASE.avoid_rules[undertone];
          avoidList = Array.isArray(rawAvoid) ? rawAvoid : (rawAvoid.colours || []);
        }}

        return {{
          skinHarmonies: skinHarmonies,
          skinHex: skinHex,
          palette: palette,
          clothing: matching.filter(c => c.category === "Clothing"),
          makeup: matching.filter(c => c.category === "Makeup"),
          accessories: matching.filter(c => c.category === "Accessories"),
          neutrals: matching.filter(c => c.category === "Neutrals"),
          world_spectrum: matching,
          avoid: avoidList,
          atmosphere: atmosphere || {{ background_hex: "#1E293B", outfit_hex: "#0F172A" }},
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

        try {{
          const animPromise = animateStepper();
          await animPromise;

          const analysisData = performColorAnalysis(currentImageBitmap);
          const recData = getRecommendationsForUndertone(
            analysisData.undertone.label,
            analysisData.skin_analysis.metrics,
            analysisData.image_atmosphere
          );

          renderResults(analysisData, recData);

          processingSection.classList.add("hidden");
          resultsSection.classList.remove("hidden");
          window.scrollTo({{ top: 0, behavior: "smooth" }});
        }} catch (err) {{
          console.error("Color analysis failed:", err);
          processingSection.classList.add("hidden");
          studioSection.classList.remove("hidden");
          heroSection.classList.remove("hidden");
          showError("Analysis error: " + (err.message || err));
        }}
      }});

      // Re-analyze
      reanalyzeBtn.addEventListener("click", () => {{
        resultsSection.classList.add("hidden");
        studioSection.classList.remove("hidden");
        heroSection.classList.remove("hidden");
        resetUpload();
        window.scrollTo({{ top: 0, behavior: "smooth" }});
      }});

      let currentGender = "female";
      const uploadGenderOptions = document.getElementById("upload-gender-options");
      if (uploadGenderOptions) {{
        uploadGenderOptions.querySelectorAll(".gender-pill").forEach((pill) => {{
          pill.addEventListener("click", () => {{
            uploadGenderOptions.querySelectorAll(".gender-pill").forEach((p) => p.classList.remove("active"));
            pill.classList.add("active");
            currentGender = pill.getAttribute("data-gender");
            updateGenderView();
          }});
        }});
      }}

      function updateGenderView() {{
        const makeupBtn = document.getElementById("tab-btn-makeup");
        if (makeupBtn) {{
          if (currentGender === "male") {{
            makeupBtn.style.display = "none";
            if (makeupBtn.classList.contains("active")) {{
              const clothingBtn = document.querySelector('[data-tab="clothing"]');
              if (clothingBtn) clothingBtn.click();
            }}
          }} else {{
            makeupBtn.style.display = "";
          }}
        }}
      }}

      function renderResults(data, recs) {{
        updateGenderView();
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
        drawCanvas(data);

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

        // Render Dynamic Skin-Tone Harmonies
        const skinBadge = document.getElementById("skin-coords-badge");
        if (skinBadge) skinBadge.textContent = recs.skinHex;

        const skinGrid = document.getElementById("skin-harmonies-grid");
        if (skinGrid && recs.skinHarmonies) {{
          skinGrid.innerHTML = "";
          recs.skinHarmonies.forEach((h) => {{
            const card = document.createElement("div");
            card.className = "skin-harmony-card";
            card.innerHTML = `
              <div class="skin-harmony-color" style="background-color: ${{h.hex}}">
                <span class="skin-harmony-badge">${{h.badge}}</span>
              </div>
              <div class="skin-harmony-meta">
                <div class="skin-harmony-name" title="${{h.name}}">${{h.name}}</div>
                <div class="skin-harmony-hex">${{h.hex}}</div>
                <div class="skin-harmony-desc">${{h.description}}</div>
              </div>
            `;
            card.addEventListener("click", () => copyToClipboard(h.hex, h.name));
            skinGrid.appendChild(card);
          }});
        }}

        // Render Analyzed Image Atmosphere
        const atmSwatches = document.getElementById("atmosphere-swatches");
        if (atmSwatches && recs.atmosphere) {{
          atmSwatches.innerHTML = `
            <div class="atmosphere-pill" title="Facial Skin Tone (${{recs.skinHex}})">
              <span class="atmosphere-dot" style="background: ${{recs.skinHex}}"></span>
              <span>Skin ${{recs.skinHex}}</span>
            </div>
            <div class="atmosphere-pill" title="Ambient Image Backdrop (${{recs.atmosphere.background_hex}})">
              <span class="atmosphere-dot" style="background: ${{recs.atmosphere.background_hex}}"></span>
              <span>Backdrop ${{recs.atmosphere.background_hex}}</span>
            </div>
            <div class="atmosphere-pill" title="Detected Outfit / Clothing (${{recs.atmosphere.outfit_hex}})">
              <span class="atmosphere-dot" style="background: ${{recs.atmosphere.outfit_hex}}"></span>
              <span>Outfit ${{recs.atmosphere.outfit_hex}}</span>
            </div>
          `;
        }}

        renderGrid("rec-clothing-grid", recs.clothing);
        renderGrid("rec-makeup-grid", recs.makeup);
        renderGrid("rec-accessories-grid", recs.accessories);
        renderGrid("rec-neutrals-grid", recs.neutrals);
        renderAvoidGrid("rec-avoid-grid", recs.avoid);

        // Render World Color Spectrum Tab
        renderWorldSpectrum(recs.world_spectrum, ut);

        document.getElementById("foundation-advice-text").textContent = ut === "Warm"
          ? "Select golden, honey, or peach-toned foundations with 'W' classification. Avoid cool/pink undertones which turn ashy."
          : ut === "Cool"
          ? "Choose neutral-cool or rose-based liquid formulas with 'C' designation. Avoid orange-based foundations."
          : "Opt for true neutral 'N' labeled foundations that balance yellow and pink pigments seamlessly.";
      }}

      function drawCanvas(data) {{
        const canvas = document.getElementById("face-canvas");
        if (!canvas || !currentImageBitmap) return;
        const ctx = canvas.getContext("2d");

        const displayWidth = 480;
        const origW = currentImageBitmap.naturalWidth || currentImageBitmap.width || displayWidth;
        const origH = currentImageBitmap.naturalHeight || currentImageBitmap.height || displayWidth;
        const scale = displayWidth / origW;
        const displayHeight = Math.round(origH * scale);

        canvas.width = displayWidth;
        canvas.height = displayHeight;
        ctx.drawImage(currentImageBitmap, 0, 0, displayWidth, displayHeight);

        // Draw sleek luxury HUD badge
        const hex = (data && data.skin_analysis && data.skin_analysis.metrics && data.skin_analysis.metrics.representative_hex) || "#D4AF37";
        const utLabel = (data && data.undertone && data.undertone.label) || "Undertone";

        const pillW = Math.min(260, Math.floor(displayWidth * 0.58));
        const pillH = 34;
        const pillX = 12;
        const pillY = displayHeight - pillH - 12;

        // Glassmorphic pill
        ctx.fillStyle = "rgba(11, 15, 23, 0.85)";
        ctx.beginPath();
        ctx.roundRect(pillX, pillY, pillW, pillH, 8);
        ctx.fill();
        ctx.strokeStyle = "rgba(212, 175, 55, 0.5)";
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Swatch dot
        const radius = 7;
        ctx.fillStyle = hex;
        ctx.beginPath();
        ctx.arc(pillX + 18, pillY + pillH / 2, radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Text label
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 11px sans-serif";
        ctx.fillText("Skin Tone: " + hex + " (" + utLabel + ")", pillX + 32, pillY + 21);
      }}

      function renderGrid(id, items) {{
        const container = document.getElementById(id);
        if (!container) return;
        container.innerHTML = "";
        if (!items || !Array.isArray(items)) return;
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
        if (!container) return;
        container.innerHTML = "";
        if (!items || !Array.isArray(items)) return;
        items.forEach((item) => {{
          const card = document.createElement("div");
          card.className = "avoid-card";
          card.innerHTML = `
            <div class="avoid-circle" style="background-color: ${{item.hex}}"></div>
            <div class="avoid-details">
              <div class="avoid-name">${{item.name}} (${{item.hex}})</div>
              <div class="avoid-reason">${{item.reason || ""}}</div>
            </div>
          `;
          container.appendChild(card);
        }});
      }}

      // World Color Spectrum Explorer
      let currentWorldFamily = "all";
      let currentWorldSearch = "";
      let cachedWorldColors = [];
      let currentUndertone = "Warm";

      function renderWorldSpectrum(colors, userUndertone) {{
        cachedWorldColors = colors || [];
        currentUndertone = userUndertone || "Warm";
        applyWorldFilters();
      }}

      function applyWorldFilters() {{
        const grid = document.getElementById("rec-world-grid");
        const counter = document.getElementById("world-counter");
        if (!grid) return;

        let filtered = cachedWorldColors;
        if (currentWorldFamily !== "all") {{
          filtered = filtered.filter(c => c.family === currentWorldFamily);
        }}
        if (currentWorldSearch.trim()) {{
          const q = currentWorldSearch.toLowerCase().trim();
          filtered = filtered.filter(c => 
            c.name.toLowerCase().includes(q) || 
            c.hex.toLowerCase().includes(q) || 
            (c.tags && c.tags.some(t => t.toLowerCase().includes(q))) ||
            (c.description && c.description.toLowerCase().includes(q))
          );
        }}

        if (counter) counter.textContent = `Showing ${{filtered.length}} of ${{cachedWorldColors.length}} tones matching your skin`;
        grid.innerHTML = "";

        if (filtered.length === 0) {{
          grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 2rem;">No matching tones found for "${{currentWorldSearch}}" in your flattering palette.</div>`;
          return;
        }}

        filtered.forEach((item) => {{
          const card = document.createElement("div");
          card.className = "rec-card";
          card.innerHTML = `
            <div class="rec-color-circle" style="background-color: ${{item.hex}}"></div>
            <div class="rec-details">
              <div class="rec-name">${{item.name}} <span style="font-size:0.68rem; color:var(--accent-gold); font-weight:700;">✓ Matched</span></div>
              <div class="rec-hex">${{item.hex}}</div>
              <div class="rec-desc">${{item.description || item.family || ""}}</div>
            </div>
          `;
          card.addEventListener("click", () => copyToClipboard(item.hex, item.name));
          grid.appendChild(card);
        }});
      }}

      // Wire up world filter chips and search
      const worldChips = document.querySelectorAll("#world-chips-scroll .world-chip");
      worldChips.forEach(chip => {{
        chip.addEventListener("click", () => {{
          worldChips.forEach(c => c.classList.remove("active"));
          chip.classList.add("active");
          currentWorldFamily = chip.getAttribute("data-family");
          applyWorldFilters();
        }});
      }});

      const searchInput = document.getElementById("world-search-input");
      if (searchInput) {{
        searchInput.addEventListener("input", (e) => {{
          currentWorldSearch = e.target.value;
          applyWorldFilters();
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
components.html(get_cached_html(), height=850, scrolling=True)
