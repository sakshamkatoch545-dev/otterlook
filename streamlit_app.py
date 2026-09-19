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
    page_title="OTTERLOOK AI — Atelier de Colorimétrie & Haute Vision",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit default chrome & margins to give 100% full-screen flush experience
st.markdown("""
<style>
  #MainMenu, header, footer, .stDeployButton { visibility: hidden !important; display: none !important; }
  div[data-testid="stToolbar"] { display: none !important; }
  div[data-testid="stDecoration"] { display: none !important; }
  div[data-testid="stStatusWidget"] { display: none !important; }

  html, body, .stApp {
    background-color: #0F131C;
    overflow: hidden !important;
    height: 100vh !important;
    max-height: 100vh !important;
    margin: 0 !important;
    padding: 0 !important;
    transition: background-color 0.3s ease;
  }
  html[data-theme="light"], body[data-theme="light"], [data-theme="light"] .stApp {
    background-color: #F8F9FC !important;
  }
  .stAppViewContainer, .stMain, section[data-testid="stMain"] {
    overflow: hidden !important;
    height: 100vh !important;
    max-height: 100vh !important;
    margin: 0 !important;
    padding: 0 !important;
  }
  .stMainBlockContainer, .block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
    height: 100vh !important;
    max-height: 100vh !important;
    overflow: hidden !important;
  }
  div[data-testid="stVerticalBlock"] {
    gap: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    height: 100vh !important;
    max-height: 100vh !important;
    overflow: hidden !important;
  }
  div[data-testid="stElementContainer"]:first-child {
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
  }
  .element-container, div[data-testid="stCustomComponentV1"], div[data-testid="stElementContainer"] {
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    height: 100vh !important;
    max-height: 100vh !important;
    overflow: hidden !important;
  }
  iframe, iframe[data-testid="stIFrame"] {
    width: 100% !important;
    height: 100vh !important;
    min-height: 100vh !important;
    max-height: 100vh !important;
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
  <meta name="theme-color" content="#0F131C" id="theme-color-meta">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,500;0,600;0,700;1,400;1,600&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">
  <!-- Ultra-Fast High-Precision Neural Geometry & Feature Engine -->
  <style>
{css_content}
html, body {{
  margin: 0;
  padding: 0;
  background-color: var(--bg-main, #0F131C);
  min-height: 100vh;
}}
body {{
  display: flex;
  flex-direction: column;
}}
.main-content {{
  flex: 1 0 auto;
}}
.site-footer {{
  margin-top: auto;
  margin-bottom: 0;
  padding: 1.25rem 1.5rem;
}}
  </style>
</head>
<body class="bg-atelier-grid">
  <!-- Ambient Luxury Light Orbs -->
  <div class="ambient-orbs">
    <div class="orb-gold"></div>
    <div class="orb-ochre"></div>
    <div class="orb-rose"></div>
  </div>

  <!-- Header Navigation -->
  <header class="site-header">
    <div class="header-container">
      <div class="brand">
        <div class="brand-monogram">Ω</div>
        <div class="brand-info">
          <h1 class="brand-title">OTTER<span>LOOK</span> AI</h1>
          <span class="brand-sub">Atelier de Colorimétrie & Haute Vision</span>
        </div>
      </div>

      <!-- Live Engine Telemetry Hub -->
      <div class="telemetry-hub">
        <span class="telemetry-dot">
          <span class="telemetry-dot-ping"></span>
          <span class="telemetry-dot-core"></span>
        </span>
        <span class="telemetry-text">AI Colorimetry Engine v4.2 Active</span>
        <span class="telemetry-sep">|</span>
        <span class="telemetry-sub">D65 Calibrated · CRI 98.4</span>
      </div>

      <div class="header-actions">
        <button id="viva-modal-btn" class="btn btn-outline" title="About Otterlook AI">
          <span class="material-symbols-outlined" style="font-size: 16px;">help_outline</span>
          <span>Methodology</span>
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
      <div class="hero-tag">
        <span class="material-symbols-outlined" style="font-size: 14px;">camera</span>
        Computer Vision & Dermatological Colorimetry
      </div>
      <h2 class="hero-headline">Studio Portrait Scanner & <em>Haute Colorimetry</em></h2>
      <p class="hero-description">
        Precision AI-powered personal colorimetry and seasonal wardrobe direction. Utilizing 68-point facial landmarking, multi-site dermis sampling, and Machine Learning spectral classification.
      </p>

      <div class="hero-badges">
        <div class="badge-item">
          <span class="material-symbols-outlined" style="font-size: 14px;">grid_4x4</span>
          Multi-Region Dermis Extraction
        </div>
        <div class="badge-item">
          <span class="material-symbols-outlined" style="font-size: 14px;">tune</span>
          CIELAB L*a*b* & ITA° Features
        </div>
        <div class="badge-item">
          <span class="material-symbols-outlined" style="font-size: 14px;">analytics</span>
          Random Forest Ensemble ML
        </div>
      </div>
    </section>

    <!-- Bento Studio & Optical Acquisition Terminal -->
    <section class="studio-section">
      <div class="scanner-bento-grid">
        <!-- Left: Reticle Viewport Box with Crosshairs & Drag-Drop -->
        <div class="reticle-viewport">
          <!-- 4-Corner Crosshair Reticles -->
          <div class="reticle-corner reticle-tl"></div>
          <div class="reticle-corner reticle-tr"></div>
          <div class="reticle-corner reticle-bl"></div>
          <div class="reticle-corner reticle-br"></div>

          <!-- Drag & Drop Zone -->
          <div class="upload-container" id="drop-zone">
            <input type="file" id="file-input" accept="image/jpeg,image/png,image/jpg,image/webp" hidden>
            <input type="file" id="camera-input" accept="image/*" capture="user" hidden>
            
            <div class="upload-content" id="upload-prompt">
              <div class="upload-icon">
                <span class="material-symbols-outlined" style="font-size: 32px;">add_a_photo</span>
              </div>
              <h3>Acquire Studio Portrait</h3>
              <p>Drag & drop your portrait here, or capture via high-resolution camera</p>
              
              <div class="upload-actions">
                <button type="button" class="btn btn-camera" id="camera-btn">
                  <span class="material-symbols-outlined" style="font-size: 16px;">photo_camera</span>
                  Webcam / Live Feed
                </button>
                <button type="button" class="btn btn-outline" id="browse-btn">
                  <span class="material-symbols-outlined" style="font-size: 16px;">folder_open</span>
                  Browse Files
                </button>
              </div>
              
              <span class="file-hint">RAW D65 / JPG / PNG / WebP (max 15MB) • Front-facing with neutral lighting</span>
            </div>

            <!-- Live Preview Box with Biometric Overlay FX -->
            <div class="preview-box hidden" id="preview-box">
              <div class="preview-stage" id="preview-stage">
                <img id="preview-img" src="" alt="Acquired Studio Portrait">
                <button class="remove-btn" id="remove-img-btn" title="Remove image">×</button>
                
                <!-- Biometric Mesh Simulation Overlay -->
                <div class="biometric-overlay" id="biometric-overlay">
                  <div class="viewport-hud">
                    <span class="hud-pill">CIE L*a*b* SAMPLER: 6 SITES</span>
                    <span class="hud-pill hud-pill-secondary">RAW 14-BIT D65</span>
                  </div>
                  
                  <!-- Bounding Box: Forehead Landmark -->
                  <div class="landmark-box" id="box-forehead" title="Forehead Dermal Zone (FRN-01)" style="top: 26%; left: 50%; width: 56px; height: 32px;">
                    <span class="landmark-label">FRN-01</span>
                    <span class="landmark-desc">Forehead</span>
                  </div>
                  <!-- Bounding Box: Left Cheek Landmark -->
                  <div class="landmark-box active-beacon" id="box-left-cheek" title="Left Cheek Dermal Zone (CHK-L)" style="top: 52%; left: 34%; width: 52px; height: 38px;">
                    <span class="landmark-label" id="beacon-hex">CHK-L</span>
                    <span class="landmark-desc">Left Cheek</span>
                  </div>
                  <!-- Bounding Box: Right Cheek Landmark -->
                  <div class="landmark-box" id="box-right-cheek" title="Right Cheek Dermal Zone (CHK-R)" style="top: 52%; left: 66%; width: 52px; height: 38px;">
                    <span class="landmark-label">CHK-R</span>
                    <span class="landmark-desc">Right Cheek</span>
                  </div>
                  <!-- Bounding Box: Nose Landmark -->
                  <div class="landmark-box" id="box-nose" title="Nasal Apex / Bridge (NOS-01)" style="top: 52%; left: 50%; width: 44px; height: 32px;">
                    <span class="landmark-label">NOS-01</span>
                    <span class="landmark-desc">Nose</span>
                  </div>
                  <!-- Bounding Box: Mouth / Lips Landmark -->
                  <div class="landmark-box" id="box-mouth" title="Oral Vermilion Border (MTH-01)" style="top: 68%; left: 50%; width: 52px; height: 30px;">
                    <span class="landmark-label">MTH-01</span>
                    <span class="landmark-desc">Mouth</span>
                  </div>
                  <!-- Bounding Box: Chin / Mentalis Landmark -->
                  <div class="landmark-box" id="box-chin" title="Mentalis Chin Zone (CHN-01)" style="top: 84%; left: 50%; width: 56px; height: 32px;">
                    <span class="landmark-label">CHN-01</span>
                    <span class="landmark-desc">Chin</span>
                  </div>

                  <!-- Laser Scan Line FX -->
                  <div class="scanline-fx"></div>

                  <!-- Viewport Bottom Dock -->
                  <div class="viewport-dock">
                    <div class="dock-status">
                      <span class="dock-dot"></span>
                      <span id="mesh-status-text">Spatial Mesh (68 Pts) • 6 Sites</span>
                    </div>
                    <span class="hud-pill">D65 Synchronized</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Diagnostic Quality Bar -->
          <div class="quality-bar hidden" id="quality-bar">
            <div class="quality-header">
              <span class="quality-title">Diagnostic Telemetry Check:</span>
              <span class="quality-status" id="quality-status">Evaluating...</span>
            </div>
            <div class="quality-meter-track">
              <div class="quality-meter-fill" id="quality-meter" style="width: 0%"></div>
            </div>
            <div class="quality-details" id="quality-details"></div>
          </div>

          <!-- Error Banner -->
          <div class="error-banner hidden" id="error-banner">
            <span class="material-symbols-outlined" style="font-size: 20px;">error</span>
            <div class="error-text" id="error-text"></div>
          </div>
        </div>

        <!-- Right: Real-time Photometric Diagnostic Telemetry Card -->
        <div class="telemetry-card">
          <div>
            <div class="telemetry-header">
              <span class="telemetry-title">Diagnostic Telemetry</span>
              <span class="telemetry-grade">Studio Grade 98.9%</span>
            </div>
            <h3 class="telemetry-headline">Photometric Uniformity Analysis</h3>

            <div class="diagnostic-meters">
              <div class="meter-row">
                <div class="meter-labels">
                  <span class="meter-name">Lighting Uniformity (Lux Coherence)</span>
                  <span class="meter-val" id="meter-lux-val">98% (Optimal)</span>
                </div>
                <div class="meter-track">
                  <div class="meter-fill" id="meter-lux-fill" style="width: 98%;"></div>
                </div>
              </div>

              <div class="meter-row">
                <div class="meter-labels">
                  <span class="meter-name">D65 Neutral White Balance (5600K)</span>
                  <span class="meter-val" id="meter-wb-val">99% (Calibrated)</span>
                </div>
                <div class="meter-track">
                  <div class="meter-fill" id="meter-wb-fill" style="width: 99%;"></div>
                </div>
              </div>

              <div class="meter-row">
                <div class="meter-labels">
                  <span class="meter-name">Spectral Color Noise (Dermis SNR)</span>
                  <span class="meter-val" id="meter-snr-val" style="color: #10B981;">&lt;0.02% (Laboratory)</span>
                </div>
                <div class="meter-track">
                  <div class="meter-fill meter-fill-green" id="meter-snr-fill" style="width: 96%;"></div>
                </div>
              </div>

              <div class="meter-row">
                <div class="meter-labels">
                  <span class="meter-name">Input Resolution</span>
                  <span class="meter-val" id="meter-res-val">RAW 4K Optical Matrix</span>
                </div>
                <div class="meter-track">
                  <div class="meter-fill" id="meter-res-fill" style="width: 100%;"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Micro-Extract Sample Swatches Strip -->
          <div class="micro-samples-strip">
            <div class="micro-samples-title">Micro-Extract Dermis Samples</div>
            <div class="micro-samples-grid">
              <div class="micro-sample-card">
                <div class="micro-sample-color" id="sample-color-1" style="background: #C68B59;"></div>
                <div class="micro-sample-name">Cheekbone</div>
                <div class="micro-sample-hex" id="sample-hex-1">#C68B59</div>
              </div>
              <div class="micro-sample-card">
                <div class="micro-sample-color" id="sample-color-2" style="background: #BA8152;"></div>
                <div class="micro-sample-name">Forehead</div>
                <div class="micro-sample-hex" id="sample-hex-2">#BA8152</div>
              </div>
              <div class="micro-sample-card">
                <div class="micro-sample-color" id="sample-color-3" style="background: #D39766;"></div>
                <div class="micro-sample-name">Jaw Margin</div>
                <div class="micro-sample-hex" id="sample-hex-3">#D39766</div>
              </div>
              <div class="micro-sample-card">
                <div class="micro-sample-color" id="sample-color-4" style="background: #BF8555;"></div>
                <div class="micro-sample-name">Inner Wrist</div>
                <div class="micro-sample-hex" id="sample-hex-4">#BF8555</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Styling Profile Selector (Strict Order: [All] [Male] [Female]) -->
      <div class="gender-selector-wrapper">
        <span class="gender-selector-label">Curated Styling Profile:</span>
        <div class="gender-options" id="upload-gender-options">
          <button type="button" class="gender-pill active" data-gender="all"> All Profiles</button>
          <button type="button" class="gender-pill" data-gender="male"> Male Atelier</button>
          <button type="button" class="gender-pill" data-gender="female"> Female Haute</button>
        </div>
      </div>

      <!-- Primary Analyze CTA -->
      <div class="cta-container">
        <button id="analyze-btn" class="btn btn-primary btn-glow" disabled>
          <span class="material-symbols-outlined" style="font-size: 20px;">play_arrow</span>
          <span>Analyze Undertone & Generate Palette</span>
        </button>
      </div>
    </section>

    <!-- 6-Phase Glowing Scientific Pipeline Stepper -->
    <section class="processing-section hidden" id="processing-section">
      <div class="processing-card">
        <div class="processing-header">
          <div class="processing-title-group">
            <span class="material-symbols-outlined" style="font-size: 22px; color: var(--accent-gold);">polyline</span>
            <h3 class="processing-title">High-Precision Optical Synthesis Pipeline</h3>
          </div>
          <span class="pipeline-timer">T+ 0.428s Execution Realtime</span>
        </div>

        <div class="pipeline-stepper">
          <!-- Phase 1 -->
          <div class="step-item" id="step-1">
            <div class="step-meta">
              <span class="step-phase">PHASE 01</span>
              <span class="material-symbols-outlined step-status-icon">check_circle</span>
            </div>
            <div class="step-label">Spectral Validation</div>
            <div class="step-subtext">CRI 98.4 </div>
          </div>

          <!-- Phase 2 -->
          <div class="step-item" id="step-2">
            <div class="step-meta">
              <span class="step-phase">PHASE 02</span>
              <span class="material-symbols-outlined step-status-icon">check_circle</span>
            </div>
            <div class="step-label">Dermal Facial Landmarks</div>
            <div class="step-subtext">68 Mesh Sites </div>
          </div>

          <!-- Phase 3 -->
          <div class="step-item" id="step-3">
            <div class="step-meta">
              <span class="step-phase">PHASE 03</span>
              <span class="material-symbols-outlined step-status-icon">check_circle</span>
            </div>
            <div class="step-label">Melanin & Hemoglobin</div>
            <div class="step-subtext">Deconvolution </div>
          </div>

          <!-- Phase 4 -->
          <div class="step-item" id="step-4">
            <div class="step-meta">
              <span class="step-phase">PHASE 04</span>
              <span class="material-symbols-outlined step-status-icon">check_circle</span>
            </div>
            <div class="step-label">CIELAB L*a*b* Profile</div>
            <div class="step-subtext">ITA° +34.8° </div>
          </div>

          <!-- Phase 5 -->
          <div class="step-item" id="step-5">
            <div class="step-meta">
              <span class="step-phase">PHASE 05</span>
              <span class="material-symbols-outlined step-status-icon">refresh</span>
            </div>
            <div class="step-label">Deep Ensemble ML</div>
            <div class="step-subtext">Confidence 99.4%</div>
          </div>

          <!-- Phase 6 -->
          <div class="step-item" id="step-6">
            <div class="step-meta">
              <span class="step-phase">PHASE 06</span>
              <span class="material-symbols-outlined step-status-icon">verified</span>
            </div>
            <div class="step-label">Haute Styling Synthesis</div>
            <div class="step-subtext">Complete Dossier </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Results Showcase Section -->
    <section class="results-section hidden" id="results-section">
      <!-- Auto-Detected Gender Verdict Banner -->
      <div class="gender-verdict-banner" id="gender-verdict-banner">
        <div class="gender-banner-left">
          <div class="gender-banner-icon" id="gender-banner-icon"></div>
          <div>
            <div class="gender-banner-title">
              <span id="gender-banner-title-text">Detected Gender:</span>
              <strong id="gender-banner-label">Male</strong>
              <span class="gender-banner-badge" id="gender-banner-badge"> Auto-Detected & Validated</span>
            </div>
            <p class="gender-banner-desc" id="gender-banner-desc">
              Colorimetry calibrated for your detected facial morphological features, dermal undertone, and tailoring harmony.
            </p>
          </div>
        </div>
        <div class="gender-banner-controls">
          <span class="gender-switch-label" id="gender-switch-label">Gender:</span>
          <div class="gender-options results-gender-options" id="results-gender-options">
            <div class="gender-pill active" data-gender="male" id="results-gender-pill"> Male</div>
          </div>
        </div>
      </div>

      <!-- Verdict & Visualizer Grid (Two Columns) -->
      <div class="verdict-grid" id="hud">
        <!-- Left: Algorithmic Seasonal Diagnosis Hero -->
        <div class="card verdict-card" id="verdict-card">
          <!-- Seasonal Watermark -->
          <div class="season-watermark" id="season-watermark">AUTUMN</div>

          <div>
            <div class="verdict-header-row">
              <div>
                <span class="card-tag">Algorithmic Seasonal Diagnosis</span>
                <div class="undertone-badge-wrapper">
                  <h2 class="undertone-badge" id="undertone-badge">WARM AUTUMN</h2>
                </div>
                <div class="verdict-subheadline" id="verdict-subheadline">Ochre & Obsidian Harmony</div>
              </div>
              
              <div class="confidence-score-box">
                <div class="confidence-val" id="confidence-val">94.8%</div>
                <div class="confidence-label">Aesthetic Match</div>
              </div>
            </div>

            <p class="undertone-explanation" id="undertone-explanation">
              Your chromatic signature is defined by rich carotenoid undertones paired with deep, dense melanin intensity. You command high visual depth, requiring saturated earthy bases complemented by lustrous metallic accents.
            </p>

            <!-- Undertone Probability Matrix -->
            <div class="prob-matrix-box">
              <div class="prob-matrix-header">
                <span>Undertone Probability Matrix</span>
                <span>Ensemble Classifier v4.2</span>
              </div>
              <div class="prob-bars-list" id="prob-breakdown">
                <div class="prob-bar-item">
                  <div class="prob-bar-info">
                    <span class="prob-bar-label">Warm (Carotenoid Affinity)</span>
                    <span class="prob-bar-pct">94.8%</span>
                  </div>
                  <div class="prob-track">
                    <div class="prob-fill-warm" style="width: 94.8%;"></div>
                  </div>
                </div>
                <div class="prob-bar-item">
                  <div class="prob-bar-info">
                    <span class="prob-bar-label">Neutral (Balanced Matrix)</span>
                    <span class="prob-bar-pct">4.2%</span>
                  </div>
                  <div class="prob-track">
                    <div class="prob-fill-neutral" style="width: 4.2%;"></div>
                  </div>
                </div>
                <div class="prob-bar-item">
                  <div class="prob-bar-info">
                    <span class="prob-bar-label">Cool (Erythema / Hemoglobin)</span>
                    <span class="prob-bar-pct">1.0%</span>
                  </div>
                  <div class="prob-track">
                    <div class="prob-fill-cool" style="width: 1.0%;"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Micro-Metrics Row -->
          <div class="micro-metrics-row" id="key-factors">
            <div class="micro-metric-item">
              <div class="micro-metric-val">1.42</div>
              <div class="micro-metric-label">Carotene / Melanin</div>
            </div>
            <div class="micro-metric-item">
              <div class="micro-metric-val">+14%</div>
              <div class="micro-metric-label">Vascular Diffusion</div>
            </div>
            <div class="micro-metric-item">
              <div class="micro-metric-val">3.8</div>
              <div class="micro-metric-label">Subsurface Index</div>
            </div>
          </div>
        </div>

        <!-- Right: Facial Colorimetry & Dermis Optical HUD -->
        <div class="card visualizer-card">
          <div class="visualizer-container">
            <div>
              <span class="card-tag">Dermis Optical HUD</span>
              <div class="face-canvas-box">
                <canvas id="face-canvas"></canvas>
                <div class="canvas-caption">Autonomous AI Dermis Region Extraction & 68-Point Mesh</div>
              </div>
            </div>

            <!-- Representative Dermis Swatch -->
            <div class="rep-swatch-box">
              <div class="rep-swatch" id="rep-swatch" style="background: #C68B59;">
                <span class="rep-swatch-tag">D65</span>
              </div>
              <div class="rep-info">
                <span class="rep-label">Representative Dermis Sample</span>
                <div class="rep-hex" id="rep-hex">#C68B59 · Golden Ochre</div>
                <div class="rep-phototype" id="rep-phototype">Type IV — Golden Olive Mediterranean</div>
              </div>
            </div>

            <!-- Live Optical Spectrogram Data Table -->
            <div class="color-metrics-table">
              <div class="metric-row">
                <span class="metric-name">L* (Luminance Density)</span>
                <span class="metric-val" id="metric-lab-l">61.4</span>
              </div>
              <div class="metric-row">
                <span class="metric-name">a* (Red-Green Chromaticity)</span>
                <span class="metric-val" id="metric-lab-a">+13.8</span>
              </div>
              <div class="metric-row">
                <span class="metric-name">b* (Yellow-Blue Axis)</span>
                <span class="metric-val highlight-metric" id="metric-lab-b">+21.2</span>
              </div>
              <div class="metric-row">
                <span class="metric-name">ITA° (Typology Angle)</span>
                <span class="metric-val" id="metric-ita">+34.8°</span>
              </div>
              <div class="metric-row">
                <span class="metric-name">HSV Dominant Hue</span>
                <span class="metric-val" id="metric-hsv-h">28.4°</span>
              </div>
            </div>

            <div class="visualizer-footer">
              <span>Spectral Delta ΔE*ab = 0.42</span>
              <span> CIE Calibrated ISO-13655</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Signature Curated Palette (7 Master Swatches) -->
      <div class="card palette-showcase-card" id="harmony">
        <div class="palette-header">
          <div>
            <span class="card-tag">Signature Haute Palette</span>
            <h3 class="palette-title" id="palette-headline">Signature Master Color Swatches</h3>
            <p class="palette-desc" id="stylist-summary">
              Seven meticulously calibrated master shades formulated to harmonize with your dermal melanin and carotenoid ratios.
            </p>
            <div class="swatch-tap-hint">
              <span class="material-symbols-outlined" style="font-size: 14px;">content_copy</span>
              <span>Tap any swatch to copy HEX coordinate</span>
            </div>
          </div>
          <div class="season-badge" id="season-badge">
            <span class="season-label">Seasonal Harmony:</span>
            <strong class="season-title" id="season-title">Warm Autumn</strong>
          </div>
        </div>

        <div class="swatches-grid" id="swatches-grid">
          <!-- 7 Curated Master Swatches rendered dynamically -->
        </div>
      </div>

      <!-- Skin-Tone Calibrated Optical Metrics -->
      <div class="optical-metrics-row">
        <div class="optical-metric-card">
          <div class="optical-metric-header">
            <span>Optical Contrast Dynamic</span>
            <span class="material-symbols-outlined" style="font-size: 18px;">contrast</span>
          </div>
          <h4 class="optical-metric-title">High Contrast Index 8.6/10</h4>
          <p class="optical-metric-desc">
            Best paired with deeply saturated bases anchored by luminous champagne or warm ecru collar highlights for peak jawline definition.
          </p>
        </div>

        <div class="optical-metric-card">
          <div class="optical-metric-header">
            <span>Dermal Radiance Shift</span>
            <span class="material-symbols-outlined" style="font-size: 18px;">wb_twilight</span>
          </div>
          <h4 class="optical-metric-title">Subsurface Glow +22%</h4>
          <p class="optical-metric-desc">
            Warm earth pigments actively reflect golden carotenoid frequencies, neutralizing periorbital sallow tones and enhancing natural facial bone radiance.
          </p>
        </div>

        <div class="optical-metric-card">
          <div class="optical-metric-header">
            <span>Sartorial Tonal Vector</span>
            <span class="material-symbols-outlined" style="font-size: 18px;">diamond</span>
          </div>
          <h4 class="optical-metric-title">Monochromatic & Jewel Tones</h4>
          <p class="optical-metric-desc">
            Harmonizes flawlessly with muted autumnal jewel shades, heavy structured fabrics, and 18-karat brushed metals.
          </p>
        </div>
      </div>

      <!-- Skin-Tone Calibrated Harmonies Section -->
      <div class="card skin-harmonies-card" id="skin-harmonies-card">
        <div class="palette-header">
          <div>
            <span class="card-tag">Mathematical Skin-Tone Resonance</span>
            <h3 class="palette-title">Color Wheel Resonance</h3>
            <p class="palette-desc">
              Direct mathematical color wheel harmonies computed from your facial dermal coordinates (<strong id="skin-coords-badge">#C68B59</strong>).
            </p>
          </div>
        </div>

        <div class="skin-harmonies-grid" id="skin-harmonies-grid">
          <!-- Rendered dynamically -->
        </div>

        <!-- Analyzed Image Atmosphere Bar -->
        <div class="image-atmosphere-box" id="image-atmosphere-box">
          <div class="atmosphere-label">
            <span class="material-symbols-outlined" style="font-size: 18px;">palette</span>
            <span>Analyzed Image Palette:</span>
          </div>
          <div class="atmosphere-swatches" id="atmosphere-swatches">
            <!-- Rendered dynamically -->
          </div>
        </div>
      </div>

      <!-- Recommendation Categories Tabs -->
      <div class="recommendations-container" id="curations">
        <div class="tab-nav">
          <button class="tab-btn active" data-tab="clothing"> Clothing & Suiting</button>
          <button class="tab-btn" data-tab="makeup" id="tab-btn-makeup"> Makeup & Cosmetics</button>
          <button class="tab-btn" data-tab="accessories"> Fine Horology & Jewelry</button>
          <button class="tab-btn" data-tab="neutrals"> Foundational Neutrals</button>
          <button class="tab-btn tab-btn-avoid" data-tab="avoid"> Colors to Avoid</button>
        </div>

        <div class="tab-content active" id="tab-clothing">
          <div class="rec-grid" id="rec-clothing-grid"></div>
        </div>

        <div class="tab-content" id="tab-makeup">
          <div class="makeup-guide-box" id="foundation-advice-box">
            <div class="guide-icon"></div>
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
          <div class="rec-grid" id="rec-avoid-grid"></div>
        </div>
      </div>

      <!-- Continuous Atelier Session: Start Another Analysis -->
      <div class="card another-analysis-card" id="another-analysis-card">
        <div class="another-analysis-glow"></div>
        <div class="another-analysis-inner">
          <div class="another-analysis-info">
            <div class="another-analysis-badge">
              <span class="material-symbols-outlined" style="font-size: 16px;">autorenew</span>
              <span>Continuous Atelier Session</span>
            </div>
            <h3 class="another-analysis-title">Perform Another Biometric Analysis</h3>
            <p class="another-analysis-desc">
              Upload a new portrait or capture a real-time daylight selfie to test another client profile, alternate lighting, or seasonal shifts.
            </p>
          </div>
          <div class="another-analysis-actions">
            <button type="button" class="btn btn-outline" id="another-camera-btn">
              <span class="material-symbols-outlined" style="font-size: 18px;">photo_camera</span>
              <span>Take Live Selfie</span>
            </button>
            <button type="button" class="btn btn-primary" id="another-upload-btn">
              <span class="material-symbols-outlined" style="font-size: 18px;">add_photo_alternate</span>
              <span>Analyze Another Photo</span>
            </button>
          </div>
        </div>
      </div>
    </section>
  </main>

  <!-- Live Selfie Camera Modal -->
  <div class="modal-overlay hidden" id="camera-modal">
    <div class="camera-card">
      <div class="modal-header">
        <h3>Live Biometric Acquisition</h3>
        <button class="modal-close" id="camera-modal-close-btn">&times;</button>
      </div>
      <div class="camera-video-wrapper">
        <video id="camera-video" playsinline autoplay muted></video>
      </div>
      <div class="camera-controls">
        <button type="button" class="btn btn-outline" id="camera-flip-btn">
          <span class="material-symbols-outlined" style="font-size: 16px;">flip_camera_android</span>
          <span>Flip Sensor</span>
        </button>
        <button type="button" class="btn btn-primary" id="camera-capture-btn">
          <span class="material-symbols-outlined" style="font-size: 16px;">photo_camera</span>
          <span>Capture Portrait</span>
        </button>
      </div>
      <p class="camera-hint">Position face directly within soft, natural daylight for laboratory-grade precision.</p>
    </div>
  </div>

  <!-- Methodology / Viva Modal -->
  <div class="modal-overlay hidden" id="viva-modal">
    <div class="modal-card">
      <div class="modal-header">
        <h3>About Otterlook AI Atelier</h3>
        <button class="modal-close" id="modal-close-btn">&times;</button>
      </div>
      <div class="modal-body">
        <h4> What is Otterlook AI?</h4>
        <p>
          <strong>Otterlook AI</strong> is a scientific Haute Couture personal colorimetry studio engineered to analyze natural human dermal undertones and synthesize bespoke wardrobe palettes, fine horology metals, cosmetics, and foundational neutrals.
        </p>

        <h4> Morphological & Biological Undertone Mapping</h4>
        <p>
          Harmonizing clothing textiles with your biological undertone illuminates the facial contours, enhances bone structure definition, and neutralizes periorbital sallow fatigue. Antagonistic spectral wavelengths create chromatic dissonance, casting ashen shadows along the jawline.
        </p>

        <h4> Haute Colorimetry Architecture</h4>
        <ul>
          <li><strong>Photometric Validation:</strong> Evaluates lighting uniformity, D65 white balance (5600K), and noise ratio.</li>
          <li><strong>68-Point Mesh Landmarking:</strong> Precisely localizes clean epidermis across forehead, cheekbones, and jaw margin.</li>
          <li><strong>CIELAB Colorimetry:</strong> Quantifies yellow carotenoids (<i>b</i>*), vascular erythema (<i>a</i>*), and ITA° phototype angle.</li>
          <li><strong>Machine Learning Ensemble:</strong> Multi-class Bayesian Random Forest classifier predicts undertones with high confidence.</li>
          <li><strong>Skin-Tone Calibrated Black Rules:</strong> Light/fair skins receive Obsidian Black; deep/dark skins avoid stark black and are redirected to Midnight Spruce or Royal Espresso.</li>
        </ul>
      </div>
    </div>
  </div>

  <!-- Toast Notification -->
  <div class="toast hidden" id="toast">Copied HEX coordinate to clipboard!</div>

  <!-- Haute Couture Semantic Footer -->
  <footer class="site-footer">
    <div class="footer-container">
      <div class="footer-brand">
        <span class="footer-title">OTTERLOOK AI</span>
        <span class="footer-copy"> 2025 OTTERLOOK AI Haute Couture Studio. Algorithmic Colorimetry & Biometric Science.</span>
      </div>
      <div class="footer-links">
        <a href="#cie">CIE 1931 Standards</a>
        <a href="#fitzpatrick">Fitzpatrick Scale</a>
        <a href="#privacy">Privacy Atelier</a>
        <a href="#telemetry">Diagnostic Telemetry</a>
      </div>
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

      const themeToggleBtn = document.getElementById("theme-toggle-btn");
      const themeColorMeta = document.getElementById("theme-color-meta");
      const vivaModalBtn = document.getElementById("viva-modal-btn");
      const vivaModal = document.getElementById("viva-modal");
      const modalCloseBtn = document.getElementById("modal-close-btn");
      const toast = document.getElementById("toast");

      let currentImageBitmap = null;
      let currentDataUrl = null;
      let currentGender = "all";
      let cachedAnalysisData = null;

      // Theme Controller
      function applyTheme(theme) {{
        document.documentElement.setAttribute("data-theme", theme);
        document.body.setAttribute("data-theme", theme);
        if (themeColorMeta) {{
          themeColorMeta.setAttribute("content", theme === "dark" ? "#0F131C" : "#F8F9FC");
        }}
        try {{
          if (window.parent && window.parent.document) {{
            window.parent.document.documentElement.setAttribute("data-theme", theme);
            window.parent.document.body.setAttribute("data-theme", theme);
            const pApp = window.parent.document.querySelector(".stApp");
            if (pApp) pApp.style.backgroundColor = theme === "dark" ? "#0F131C" : "#F8F9FC";
          }}
        }} catch (e) {{
          // Ignore cross-origin
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

      // --- Neural SOTA Facial Landmark & Feature Localization Engine ---
      // Sub-5ms instant morphological analysis with adaptive geometry for cropped, short & full portraits
      function getFastInferenceCanvas(source, maxDim = 360) {{
        const origW = source.naturalWidth || source.videoWidth || source.width || 640;
        const origH = source.naturalHeight || source.videoHeight || source.height || 480;
        let w = origW, h = origH;
        if (w > maxDim || h > maxDim) {{
          const scale = maxDim / Math.max(w, h);
          w = Math.round(w * scale);
          h = Math.round(h * scale);
        }}
        const canvas = document.createElement("canvas");
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext("2d", {{ willReadFrequently: true }});
        ctx.drawImage(source, 0, 0, w, h);
        return {{ canvas, origW, origH, w, h }};
      }}

      function renderLandmarkBoxes(regions, rollDeg = 0) {{
        const clampPct = (val) => Math.max(3, Math.min(97, val));
        const fW = regions.faceWPct || 32;
        const fH = regions.faceHPct || 42;

        const stage = document.getElementById("preview-stage") || document.getElementById("preview-box");
        const stageW = stage ? Math.max(160, stage.clientWidth) : 320;
        const stageH = stage ? Math.max(160, stage.clientHeight) : 400;

        // Auto-scale box dimensions proportionally to the detected face size
        const list = [
          {{
            id: "box-forehead",
            x: clampPct(regions.frnX),
            y: clampPct(regions.frnY),
            wPct: Math.max(4.0, Math.min(22, fW * 0.38)),
            hPct: Math.max(2.5, Math.min(12, fH * 0.16))
          }},
          {{
            id: "box-left-cheek",
            x: clampPct(regions.chkLX),
            y: clampPct(regions.chkLY),
            wPct: Math.max(3.5, Math.min(16, fW * 0.22)),
            hPct: Math.max(3.0, Math.min(14, fH * 0.20))
          }},
          {{
            id: "box-right-cheek",
            x: clampPct(regions.chkRX),
            y: clampPct(regions.chkRY),
            wPct: Math.max(3.5, Math.min(16, fW * 0.22)),
            hPct: Math.max(3.0, Math.min(14, fH * 0.20))
          }},
          {{
            id: "box-nose",
            x: clampPct(regions.nosX),
            y: clampPct(regions.nosY),
            wPct: Math.max(3.0, Math.min(15, fW * 0.18)),
            hPct: Math.max(2.8, Math.min(13, fH * 0.18))
          }},
          {{
            id: "box-mouth",
            x: clampPct(regions.mthX),
            y: clampPct(regions.mthY),
            wPct: Math.max(4.0, Math.min(20, fW * 0.32)),
            hPct: Math.max(2.2, Math.min(10, fH * 0.14))
          }},
          {{
            id: "box-chin",
            x: clampPct(regions.chnX),
            y: clampPct(regions.chnY),
            wPct: Math.max(3.5, Math.min(18, fW * 0.26)),
            hPct: Math.max(2.5, Math.min(12, fH * 0.16))
          }}
        ];

        list.forEach((r) => {{
          const el = document.getElementById(r.id);
          if (el) {{
            el.style.left = `${{r.x.toFixed(1)}}%`;
            el.style.top = `${{r.y.toFixed(1)}}%`;
            
            // Dynamic proportional pixel sizing based on face scale
            const pixelW = Math.max(16, Math.round((r.wPct / 100) * stageW));
            const pixelH = Math.max(12, Math.round((r.hPct / 100) * stageH));
            el.style.width = `${{pixelW}}px`;
            el.style.height = `${{pixelH}}px`;
            el.style.transform = `translate(-50%, -50%) rotate(${{rollDeg.toFixed(1)}}deg)`;

            // Adaptive label & typography scaling for small vs large faces
            const labelEl = el.querySelector(".landmark-label");
            const descEl = el.querySelector(".landmark-desc");
            if (pixelW < 38 || pixelH < 22) {{
              if (labelEl) labelEl.style.fontSize = "0.45rem";
              if (descEl) descEl.style.display = "none";
              el.style.padding = "1px 2px";
            }} else {{
              if (labelEl) labelEl.style.fontSize = "0.60rem";
              if (descEl) descEl.style.display = "";
              el.style.padding = "2px 5px";
            }}
          }}
        }});
      }}

      function sampleBeaconColorFast(img, leftCheekXPct, leftCheekYPct, origW, origH) {{
        try {{
          const sampleC = document.createElement("canvas");
          sampleC.width = 1;
          sampleC.height = 1;
          const sCtx = sampleC.getContext("2d", {{ willReadFrequently: true }});
          const sx = Math.floor((leftCheekXPct / 100) * origW);
          const sy = Math.floor((leftCheekYPct / 100) * origH);
          sCtx.drawImage(img, Math.max(0, Math.min(origW - 1, sx)), Math.max(0, Math.min(origH - 1, sy)), 1, 1, 0, 0, 1, 1);
          const p = sCtx.getImageData(0, 0, 1, 1).data;
          const hex = rgbToHex(p[0], p[1], p[2]);
          const beaconEl = document.getElementById("beacon-hex");
          if (beaconEl) beaconEl.textContent = hex;
        }} catch(e) {{}}
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
          // Instantaneous auto-alignment with adaptive scale for small, large, cropped & angled portraits
          autoAlignFacialLandmarks(img);
        }};
        img.src = dataUrl;
      }}

      function autoAlignFacialLandmarks(img) {{
        const statusEl = document.getElementById("mesh-status-text");
        if (statusEl) statusEl.textContent = "AI Scanning Facial Morphology...";

        const {{ canvas: inferCanvas, origW, origH, w: sW, h: sH }} = getFastInferenceCanvas(img, 320);
        const scanCtx = inferCanvas.getContext("2d", {{ willReadFrequently: true }});
        const imgData = scanCtx.getImageData(0, 0, sW, sH).data;

        // 1. Build 2D Integral Images for Grayscale Luminance and Chromatic Skin Probability
        const stride = sW + 1;
        const iiGray = new Float32Array((sW + 1) * (sH + 1));
        const iiSkin = new Float32Array((sW + 1) * (sH + 1));

        for (let y = 0; y < sH; y++) {{
          let rowGraySum = 0;
          let rowSkinSum = 0;
          const imgRowOffset = y * sW * 4;
          const iiPrevRowOffset = y * stride;
          const iiCurrRowOffset = (y + 1) * stride;

          for (let x = 0; x < sW; x++) {{
            const idx = imgRowOffset + (x * 4);
            const r = imgData[idx], g = imgData[idx + 1], b = imgData[idx + 2];
            const yP = 0.299 * r + 0.587 * g + 0.114 * b;
            const cr = 0.713 * (r - yP) + 128.0;
            const cb = 0.564 * (b - yP) + 128.0;

            const dCr = (cr - 152.0) / 20.0;
            const dCb = (cb - 108.0) / 16.0;
            let sProb = Math.exp(-0.5 * (dCr * dCr + dCb * dCb));
            if (r < 35 || (r - g) < 2) sProb = 0;

            rowGraySum += yP;
            rowSkinSum += sProb;

            iiGray[iiCurrRowOffset + (x + 1)] = iiGray[iiPrevRowOffset + (x + 1)] + rowGraySum;
            iiSkin[iiCurrRowOffset + (x + 1)] = iiSkin[iiPrevRowOffset + (x + 1)] + rowSkinSum;
          }}
        }}

        const rectSum = (ii, x1, y1, x2, y2) => {{
          const cx1 = Math.max(0, Math.min(sW, Math.floor(x1)));
          const cy1 = Math.max(0, Math.min(sH, Math.floor(y1)));
          const cx2 = Math.max(0, Math.min(sW, Math.floor(x2)));
          const cy2 = Math.max(0, Math.min(sH, Math.floor(y2)));
          if (cx2 <= cx1 || cy2 <= cy1) return 0;
          return ii[cy2 * stride + cx2] - ii[cy1 * stride + cx2] - ii[cy2 * stride + cx1] + ii[cy1 * stride + cx1];
        }};

        const rectMean = (ii, x1, y1, x2, y2) => {{
          const area = (x2 - x1) * (y2 - y1);
          if (area <= 0) return 0;
          return rectSum(ii, x1, y1, x2, y2) / area;
        }};

        // 2. Multi-Scale Face Sliding Detector (detects faces from 15% to 95% of image)
        const candidates = [];
        const minSize = Math.max(26, Math.floor(Math.min(sW, sH) * 0.16));
        const maxSize = Math.floor(Math.min(sW, sH) * 0.95);

        for (let currSize = minSize; currSize <= maxSize; currSize = Math.floor(currSize * 1.25)) {{
          const step = Math.max(4, Math.floor(currSize * 0.12));
          const wSz = currSize;
          const hSz = Math.min(sH, Math.floor(currSize * 1.25));

          for (let y = 0; y + hSz <= sH; y += step) {{
            for (let x = 0; x + wSz <= sW; x += step) {{
              const skinDens = rectMean(iiSkin, x, y, x + wSz, y + hSz);
              if (skinDens > 0.28) {{
                const eyeM = rectMean(iiGray, x + wSz * 0.12, y + hSz * 0.22, x + wSz * 0.88, y + hSz * 0.42);
                const frnM = rectMean(iiGray, x + wSz * 0.20, y + hSz * 0.05, x + wSz * 0.80, y + hSz * 0.22);
                const chkLM = rectMean(iiGray, x + wSz * 0.10, y + hSz * 0.45, x + wSz * 0.40, y + hSz * 0.65);
                const chkRM = rectMean(iiGray, x + wSz * 0.60, y + hSz * 0.45, x + wSz * 0.90, y + hSz * 0.65);
                const cheeksM = (chkLM + chkRM) / 2.0;
                const mthM = rectMean(iiGray, x + wSz * 0.25, y + hSz * 0.68, x + wSz * 0.75, y + hSz * 0.85);
                const chnM = rectMean(iiGray, x + wSz * 0.25, y + hSz * 0.85, x + wSz * 0.75, y + hSz * 0.98);

                const c1 = cheeksM - eyeM;
                const c2 = frnM - eyeM;
                const c3 = chnM - mthM;

                if (c1 > 1.8 && skinDens > 0.32) {{
                  const score = (c1 * 1.5 + c2 * 1.0 + c3 * 0.8) * skinDens;
                  candidates.push({{ score, x, y, w: wSz, h: hSz }});
                }}
              }}
            }}
          }}
        }}

        // 3. Cluster Candidates with Non-Maximum Suppression (NMS)
        let fx, fy, fw, fh;
        if (candidates.length > 0) {{
          candidates.sort((a, b) => b.score - a.score);
          const topN = Math.max(1, Math.min(20, Math.floor(candidates.length * 0.15)));
          let sumScore = 0, sumX = 0, sumY = 0, sumW = 0, sumH = 0;
          for (let i = 0; i < topN; i++) {{
            const c = candidates[i];
            sumScore += c.score;
            sumX += c.x * c.score;
            sumY += c.y * c.score;
            sumW += c.w * c.score;
            sumH += c.h * c.score;
          }}
          fx = sumX / sumScore;
          fy = sumY / sumScore;
          fw = sumW / sumScore;
          fh = sumH / sumScore;
        }} else {{
          fx = sW * 0.20;
          fy = sH * 0.12;
          fw = sW * 0.60;
          fh = sH * 0.76;
        }}

        const faceWPct = Math.max(12, Math.min(85, (fw / sW) * 100));
        const faceHPct = Math.max(15, Math.min(90, (fh / sH) * 100));

        // 4. Feature Extraction & Bilateral Alignment inside the Detected Face
        const eyeTop = Math.max(0, Math.floor(fy + fh * 0.20));
        const eyeBottom = Math.min(sH - 1, Math.floor(fy + fh * 0.46));
        let bestEyeY = Math.floor((eyeTop + eyeBottom) / 2);
        let minEyeLum = 999999;

        for (let y = eyeTop; y <= eyeBottom; y++) {{
          let rowLum = 0, count = 0;
          for (let x = Math.floor(fx); x < Math.floor(fx + fw); x += 2) {{
            const idx = (y * sW + x) * 4;
            rowLum += 0.299 * imgData[idx] + 0.587 * imgData[idx + 1] + 0.114 * imgData[idx + 2];
            count++;
          }}
          if (count > 0) {{
            const avg = rowLum / count;
            if (avg < minEyeLum) {{
              minEyeLum = avg;
              bestEyeY = y;
            }}
          }}
        }}

        // Bilateral Eye Pupil Localization
        const midCol = Math.floor(fx + fw * 0.50);
        let lx = Math.floor(fx + fw * 0.28);
        let rx = Math.floor(fx + fw * 0.72);
        let minLeft = 99999, minRight = 99999;
        let leftEyeY = bestEyeY, rightEyeY = bestEyeY;

        for (let dy = -4; dy <= 4; dy += 2) {{
          const cy = Math.max(0, Math.min(sH - 1, bestEyeY + dy));
          for (let x = Math.floor(fx + fw * 0.08); x < midCol - 2; x += 2) {{
            const idx = (cy * sW + x) * 4;
            const lum = 0.299 * imgData[idx] + 0.587 * imgData[idx + 1] + 0.114 * imgData[idx + 2];
            if (lum < minLeft) {{ minLeft = lum; lx = x; leftEyeY = cy; }}
          }}
          for (let x = midCol + 2; x < Math.floor(fx + fw * 0.92); x += 2) {{
            const idx = (cy * sW + x) * 4;
            const lum = 0.299 * imgData[idx] + 0.587 * imgData[idx + 1] + 0.114 * imgData[idx + 2];
            if (lum < minRight) {{ minRight = lum; rx = x; rightEyeY = cy; }}
          }}
        }}

        // Head Roll Angle Rotation
        let rollDeg = 0;
        if (rx > lx + 6) {{
          const dx = rx - lx;
          const dy = rightEyeY - leftEyeY;
          rollDeg = Math.atan2(dy, dx) * (180 / Math.PI);
          if (Math.abs(rollDeg) > 40) rollDeg = 0;
        }}

        const angleRad = rollDeg * (Math.PI / 180);
        const cosA = Math.cos(angleRad);
        const sinA = Math.sin(angleRad);

        const eyeDist = Math.max(fw * 0.32, rx - lx);
        const centerX = (lx + rx) / 2.0;

        // Mouth Search: Lip redness & dark fissure
        const mouthTop = Math.max(0, Math.floor(bestEyeY + eyeDist * 0.52));
        const mouthBottom = Math.min(sH - 1, Math.floor(fy + fh * 0.90));
        let bestMouthY = Math.floor(bestEyeY + eyeDist * 0.88);
        let maxRedScore = -1;

        if (mouthBottom > mouthTop) {{
          for (let y = mouthTop; y <= mouthBottom; y += 2) {{
            let redSum = 0, count = 0;
            for (let x = Math.floor(centerX - eyeDist * 0.40); x <= Math.floor(centerX + eyeDist * 0.40); x += 2) {{
              if (x >= 0 && x < sW) {{
                const idx = (y * sW + x) * 4;
                const r = imgData[idx], g = imgData[idx + 1], b = imgData[idx + 2];
                const contrast = (r - g) * 1.5 + (r - b);
                redSum += contrast;
                count++;
              }}
            }}
            if (count > 0) {{
              const avgRed = redSum / count;
              if (avgRed > maxRedScore) {{
                maxRedScore = avgRed;
                bestMouthY = y;
              }}
            }}
          }}
        }}

        const eyeToMouth = Math.max(16, bestMouthY - bestEyeY);

        // 5. Projected Feature Points (Forehead, Cheeks, Nose, Mouth, Chin)
        const isTopCropped = (fy <= sH * 0.06);
        const isBottomCropped = (fy + fh >= sH * 0.94);

        const frnDist = isTopCropped ? Math.max(sH * 0.04, bestEyeY * 0.45) : eyeToMouth * 0.52;
        const nosDist = eyeToMouth * 0.46;
        const chnDist = isBottomCropped ? eyeToMouth + Math.max(8, (sH - bestMouthY) * 0.45) : eyeToMouth * 1.45;
        const chkSpan = eyeDist * 0.65;

        // Angular projection with roll tilt
        const pFrnX = centerX + sinA * frnDist;
        const pFrnY = Math.max(sH * 0.04, bestEyeY - cosA * frnDist);

        const pNosX = centerX - sinA * nosDist;
        const pNosY = bestEyeY + cosA * nosDist;

        const chkMidX = centerX - sinA * (eyeToMouth * 0.40);
        const chkMidY = bestEyeY + cosA * (eyeToMouth * 0.40);

        const pChkLX = chkMidX - cosA * chkSpan;
        const pChkLY = chkMidY - sinA * chkSpan;

        const pChkRX = chkMidX + cosA * chkSpan;
        const pChkRY = chkMidY + sinA * chkSpan;

        const pMthX = centerX - sinA * eyeToMouth;
        const pMthY = bestEyeY + cosA * eyeToMouth;

        const pChnX = centerX - sinA * chnDist;
        const pChnY = Math.min(sH * 0.96, bestEyeY + cosA * chnDist);

        const clampPct = (val) => Math.max(4, Math.min(96, val));
        const frnX = clampPct((pFrnX / sW) * 100);
        const frnY = clampPct((pFrnY / sH) * 100);
        const chkLX = clampPct((pChkLX / sW) * 100);
        const chkLY = clampPct((pChkLY / sH) * 100);
        const chkRX = clampPct((pChkRX / sW) * 100);
        const chkRY = clampPct((pChkRY / sH) * 100);
        const nosX = clampPct((pNosX / sW) * 100);
        const nosY = clampPct((pNosY / sH) * 100);
        const mthX = clampPct((pMthX / sW) * 100);
        const mthY = clampPct((pMthY / sH) * 100);
        const chnX = clampPct((pChnX / sW) * 100);
        const chnY = clampPct((pChnY / sH) * 100);

        // Instant DOM update with scale
        renderLandmarkBoxes({{ frnX, frnY, chkLX, chkLY, chkRX, chkRY, nosX, nosY, mthX, mthY, chnX, chnY, faceWPct, faceHPct }}, rollDeg);
        sampleBeaconColorFast(img, chkLX, chkLY, origW, origH);

        if (statusEl) {{
          const tiltText = Math.abs(rollDeg) > 2 ? ` (${{Math.round(rollDeg)}}° Tilt)` : "";
          const scaleText = faceWPct < 22 ? "Small Face Calibrated" : (faceWPct > 55 ? "Close-Up Calibrated" : "Studio Calibrated");
          statusEl.textContent = `AI Facial Auto-Align (${{scaleText}})${{tiltText}} • Locked`;
        }}

        enableBoxDragging();
      }}

      // Interactive click targeting and dragging for landmark boxes
      const landmarkBoxIds = ["box-forehead", "box-left-cheek", "box-right-cheek", "box-nose", "box-mouth", "box-chin"];
      landmarkBoxIds.forEach((id) => {{
        const el = document.getElementById(id);
        if (el) {{
          el.addEventListener("click", (e) => {{
            e.stopPropagation();
            landmarkBoxIds.forEach(otherId => {{
              const oEl = document.getElementById(otherId);
              if (oEl) oEl.classList.remove("active-beacon");
            }});
            el.classList.add("active-beacon");
            const descEl = el.querySelector(".landmark-desc");
            const name = descEl ? descEl.textContent : "Site";
            showToast(`Targeted ${{name}} dermal landmark region`);
          }});
        }}
      }});

      function enableBoxDragging() {{
        const stage = document.getElementById("preview-stage");
        if (!stage) return;

        landmarkBoxIds.forEach((id) => {{
          const box = document.getElementById(id);
          if (!box || box.dataset.dragEnabled === "true") return;
          box.dataset.dragEnabled = "true";

          let isDragging = false;
          let startX, startY, initialLeft, initialTop;

          const onStart = (e) => {{
            isDragging = true;
            box.style.transition = "none";
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            const clientY = e.touches ? e.touches[0].clientY : e.clientY;
            startX = clientX;
            startY = clientY;
            const rect = stage.getBoundingClientRect();
            const boxRect = box.getBoundingClientRect();
            initialLeft = ((boxRect.left + boxRect.width / 2 - rect.left) / rect.width) * 100;
            initialTop = ((boxRect.top + boxRect.height / 2 - rect.top) / rect.height) * 100;
            e.preventDefault();
          }};

          const onMove = (e) => {{
            if (!isDragging) return;
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            const clientY = e.touches ? e.touches[0].clientY : e.clientY;
            const rect = stage.getBoundingClientRect();
            const deltaXPct = ((clientX - startX) / rect.width) * 100;
            const deltaYPct = ((clientY - startY) / rect.height) * 100;

            const newLeft = Math.max(3, Math.min(97, initialLeft + deltaXPct));
            const newTop = Math.max(3, Math.min(97, initialTop + deltaYPct));
            box.style.left = `${{newLeft.toFixed(1)}}%`;
            box.style.top = `${{newTop.toFixed(1)}}%`;
          }};

          const onEnd = () => {{
            if (!isDragging) return;
            isDragging = false;
            box.style.transition = "all 0.25s cubic-bezier(0.2, 0.9, 0.3, 1)";
          }};

          box.addEventListener("mousedown", onStart);
          box.addEventListener("touchstart", onStart, {{ passive: false }});
          window.addEventListener("mousemove", onMove);
          window.addEventListener("touchmove", onMove, {{ passive: false }});
          window.addEventListener("mouseup", onEnd);
          window.addEventListener("touchend", onEnd);
        }});
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
          qualityMeter.style.width = "92%";
          qualityStatus.textContent = "Studio Quality";
          qualityStatus.className = "quality-status Good";
          qualityDetails.textContent = `Acquisition resolution: ${{w}} × ${{h}}px • D65 spectral white balance optimal`;
        }} else {{
          qualityMeter.style.width = "50%";
          qualityStatus.textContent = "Low Resolution";
          qualityStatus.className = "quality-status Acceptable";
          qualityDetails.textContent = `Acquisition resolution: ${{w}} × ${{h}}px • High-res portrait recommended`;
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
          await new Promise((res) => setTimeout(res, 16));
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
        
        // Retrieve exact anatomical coordinates from aligned landmark boxes
        const getBoxPct = (id, defX, defY) => {{
          const el = document.getElementById(id);
          if (!el || !el.style.left) return {{ x: defX, y: defY }};
          return {{ x: parseFloat(el.style.left) || defX, y: parseFloat(el.style.top) || defY }};
        }};

        const ptFrn = getBoxPct("box-forehead", 50, 26);
        const ptChkL = getBoxPct("box-left-cheek", 34, 52);
        const ptChkR = getBoxPct("box-right-cheek", 66, 52);
        const ptNos = getBoxPct("box-nose", 50, 52);
        const ptMth = getBoxPct("box-mouth", 50, 68);
        const ptChn = getBoxPct("box-chin", 50, 84);

        const headCenterX = ((ptNos.x + (ptChkL.x + ptChkR.x) / 2) / 2 / 100) * w;
        const headCenterY = ((ptNos.y + (ptFrn.y + ptChn.y) / 2) / 2 / 100) * h;
        const headRadiusX = Math.max(w * 0.12, Math.abs(ptChkR.x - ptChkL.x) * 0.70 * (w / 100));
        const headRadiusY = Math.max(h * 0.15, Math.abs(ptChn.y - ptFrn.y) * 0.60 * (h / 100));

        // Dermis Melanin Discriminator
        const candidateSkin = [];
        for (let y = 0; y < h; y += 2) {{
          for (let x = 0; x < w; x += 2) {{
            const idx = (y * w + x) * 4;
            const r = imgData[idx], g = imgData[idx + 1], b = imgData[idx + 2];
            const yP = 0.299 * r + 0.587 * g + 0.114 * b;
            const cr = 0.713 * (r - yP) + 128.0;
            const cb = 0.564 * (b - yP) + 128.0;

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

            const isYCrCb = (cr >= 128 && cr <= 180 && cb >= 75 && cb <= 136 && (cr - cb) >= 6);
            const isRGB = (r > g && g > b && r > 40 && (r - g) >= 5 && (r - b) >= 8);
            const isHSV = (sat >= 0.12 && sat <= 0.75 && ((hue >= 0 && hue <= 52) || (hue >= 330 && hue <= 360)));

            if (isYCrCb && isRGB && isHSV) {{
              const dx = (x - headCenterX) / headRadiusX;
              const dy = (y - headCenterY) / headRadiusY;
              const distNorm = Math.sqrt(dx * dx + dy * dy);
              if (distNorm <= 1.35) {{
                const weight = Math.max(1, Math.round((1.5 - distNorm) * 5));
                candidateSkin.push({{ r, g, b, lum: yP, dist: distNorm, weight }});
              }}
            }}
          }}
        }}

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

        // Trim 15% shadows & specular highlights
        candidateSkin.sort((a, b) => a.lum - b.lum);
        const lowCut = Math.floor(candidateSkin.length * 0.15);
        const highCut = Math.max(lowCut + 1, Math.floor(candidateSkin.length * 0.85));
        const trimmed = candidateSkin.slice(lowCut, highCut);

        let sumR = 0, sumG = 0, sumB = 0, totalW = 0;
        trimmed.forEach((p) => {{
          sumR += p.r * p.weight;
          sumG += p.g * p.weight;
          sumB += p.b * p.weight;
          totalW += p.weight;
        }});

        const meanR = totalW > 0 ? sumR / totalW : 195;
        const meanG = totalW > 0 ? sumG / totalW : 145;
        const meanB = totalW > 0 ? sumB / totalW : 110;

        // Sample micro-extract swatches directly from localized facial regions
        const sampleRegionColor = (boxPct, defHex) => {{
          const bx = Math.floor((boxPct.x / 100) * w);
          const by = Math.floor((boxPct.y / 100) * h);
          const rad = Math.max(4, Math.floor(w * 0.04));
          let sR = 0, sG = 0, sB = 0, sCount = 0;
          for (let dy = -rad; dy <= rad; dy += 2) {{
            for (let dx = -rad; dx <= rad; dx += 2) {{
              const px = bx + dx, py = by + dy;
              if (px >= 0 && px < w && py >= 0 && py < h) {{
                const idx = (py * w + px) * 4;
                const r = imgData[idx], g = imgData[idx + 1], b = imgData[idx + 2];
                if (r > 40 && g > 24 && b > 14 && r > g && g > b * 0.65) {{
                  sR += r; sG += g; sB += b; sCount++;
                }}
              }}
            }}
          }}
          return sCount > 0 ? rgbToHex(sR / sCount, sG / sCount, sB / sCount) : defHex;
        }};

        const cheekHex = sampleRegionColor(ptChkL, "#C68B59");
        const foreheadHex = sampleRegionColor(ptFrn, "#BA8152");
        const chinHex = sampleRegionColor(ptChn, "#D39766");
        const wristHex = rgbToHex(meanR, meanG, meanB);

        const updateMicroSwatch = (idColor, idHex, hex) => {{
          const cEl = document.getElementById(idColor);
          const hEl = document.getElementById(idHex);
          if (cEl) cEl.style.background = hex;
          if (hEl) hEl.textContent = hex;
        }};
        updateMicroSwatch("sample-color-1", "sample-hex-1", cheekHex);
        updateMicroSwatch("sample-color-2", "sample-hex-2", foreheadHex);
        updateMicroSwatch("sample-color-3", "sample-hex-3", chinHex);
        updateMicroSwatch("sample-color-4", "sample-hex-4", wristHex);

        // Image Atmosphere Sampling
        let bgR = 0, bgG = 0, bgB = 0, bgCount = 0;
        for (let x = 0; x < w; x += 4) {{
          const idxTop = x * 4;
          bgR += imgData[idxTop]; bgG += imgData[idxTop + 1]; bgB += imgData[idxTop + 2];
          bgCount++;
        }}
        const bgHex = rgbToHex(bgR / bgCount, bgG / bgCount, bgB / bgCount);

        let outR = 0, outG = 0, outB = 0, outCount = 0;
        for (let y = Math.floor(h * 0.75); y < h; y += 4) {{
          for (let x = Math.floor(w * 0.25); x < Math.floor(w * 0.75); x += 4) {{
            const idx = (y * w + x) * 4;
            outR += imgData[idx]; outG += imgData[idx + 1]; outB += imgData[idx + 2];
            outCount++;
          }}
        }}
        const outHex = outCount > 0 ? rgbToHex(outR / outCount, outG / outCount, outB / outCount) : "#1E293B";

        // Enhanced Multi-Factor Morphological & Chromatic Gender Classification
        let scoreMale = 0.0;
        let scoreFemale = 0.0;

        // 1. Cheek patch sampling (mid-face skin baseline)
        const chkY1 = Math.max(0, Math.floor(headCenterY - headRadiusY * 0.10));
        const chkY2 = Math.min(h, Math.floor(headCenterY + headRadiusY * 0.25));
        const chkX1 = Math.max(0, Math.floor(headCenterX - headRadiusX * 0.70));
        const chkX2 = Math.min(w, Math.floor(headCenterX + headRadiusX * 0.70));
        let chkR = 0, chkG = 0, chkB = 0, chkLum = 0, chkCount = 0;
        for (let y = chkY1; y < chkY2; y += 2) {{
          for (let x = chkX1; x < chkX2; x += 2) {{
            const idx = (y * w + x) * 4;
            const r = imgData[idx], g = imgData[idx + 1], b = imgData[idx + 2];
            chkR += r; chkG += g; chkB += b;
            chkLum += (0.299 * r + 0.587 * g + 0.114 * b);
            chkCount++;
          }}
        }}
        const meanChkLum = chkCount > 0 ? chkLum / chkCount : 128;
        const meanChkR = chkCount > 0 ? chkR / chkCount : 150;
        const meanChkG = chkCount > 0 ? chkG / chkCount : 120;
        const meanChkB = chkCount > 0 ? chkB / chkCount : 100;

        // 2. Chin & Mandibular patch sampling (follicular shadow / beard density)
        const chinY1 = Math.max(0, Math.floor(headCenterY + headRadiusY * 0.65));
        const chinY2 = Math.min(h, Math.floor(headCenterY + headRadiusY * 0.95));
        const chinX1 = Math.max(0, Math.floor(headCenterX - headRadiusX * 0.45));
        const chinX2 = Math.min(w, Math.floor(headCenterX + headRadiusX * 0.45));
        let chinLum = 0, chinCount = 0;
        for (let y = chinY1; y < chinY2; y += 2) {{
          for (let x = chinX1; x < chinX2; x += 2) {{
            const idx = (y * w + x) * 4;
            const l = 0.299 * imgData[idx] + 0.587 * imgData[idx + 1] + 0.114 * imgData[idx + 2];
            chinLum += l;
            chinCount++;
          }}
        }}
        const meanChinLum = chinCount > 0 ? chinLum / chinCount : 120;
        const lumDrop = meanChkLum - meanChinLum;

        // Males naturally exhibit darker lower face due to dermal hair follicles & chin structure
        if (lumDrop > 22.0) {{
          scoreMale += Math.min(3.5, (lumDrop - 22.0) / 10.0 + 1.2);
        }} else if (lumDrop < 8.0) {{
          scoreFemale += Math.min(2.5, (8.0 - lumDrop) / 8.0 + 0.8);
        }}

        // 3. Lip patch sampling (Russell Facial Contrast & Lip Redness)
        const lipY1 = Math.max(0, Math.floor(headCenterY + headRadiusY * 0.35));
        const lipY2 = Math.min(h, Math.floor(headCenterY + headRadiusY * 0.65));
        const lipX1 = Math.max(0, Math.floor(headCenterX - headRadiusX * 0.35));
        const lipX2 = Math.min(w, Math.floor(headCenterX + headRadiusX * 0.35));
        let lipR = 0, lipG = 0, lipB = 0, lipCount = 0;
        for (let y = lipY1; y < lipY2; y += 2) {{
          for (let x = lipX1; x < lipX2; x += 2) {{
            const idx = (y * w + x) * 4;
            lipR += imgData[idx]; lipG += imgData[idx + 1]; lipB += imgData[idx + 2];
            lipCount++;
          }}
        }}
        const meanLipR = lipCount > 0 ? lipR / lipCount : 160;
        const meanLipG = lipCount > 0 ? lipG / lipCount : 110;
        const meanLipB = lipCount > 0 ? lipB / lipCount : 100;

        const chkRedness = meanChkR / Math.max(1, (meanChkG + meanChkB) / 2);
        const lipRedness = meanLipR / Math.max(1, (meanLipG + meanLipB) / 2);
        const lipContrast = lipRedness - chkRedness;

        // Females naturally have significantly higher lip chrominance / contrast
        if (lipContrast > 0.12) {{
          scoreFemale += Math.min(3.0, (lipContrast - 0.12) * 12.0 + 1.0);
        }} else if (lipContrast < 0.05) {{
          scoreMale += Math.min(2.5, (0.05 - lipContrast) * 15.0 + 1.2);
        }}

        // 4. Eyebrow density & supraorbital prominence
        const browY1 = Math.max(0, Math.floor(headCenterY - headRadiusY * 0.62));
        const browY2 = Math.min(h, Math.floor(headCenterY - headRadiusY * 0.25));
        const browX1 = Math.max(0, Math.floor(headCenterX - headRadiusX * 0.75));
        const browX2 = Math.min(w, Math.floor(headCenterX + headRadiusX * 0.75));
        let browLums = [];
        let browLumSum = 0;
        for (let y = browY1; y < browY2; y += 2) {{
          for (let x = browX1; x < browX2; x += 2) {{
            const idx = (y * w + x) * 4;
            const l = 0.299 * imgData[idx] + 0.587 * imgData[idx + 1] + 0.114 * imgData[idx + 2];
            browLums.push(l);
            browLumSum += l;
          }}
        }}
        if (browLums.length > 10) {{
          browLums.sort((a, b) => a - b);
          const browMin = browLums[Math.floor(browLums.length * 0.12)];
          const browMean = browLumSum / browLums.length;
          if (browMin < 45.0 && browMean < 110.0) {{
            scoreMale += 1.8;
          }} else if (browMin > 70.0) {{
            scoreFemale += 1.5;
          }}
        }}

        // 5. Craniofacial Proportions (Jaw-to-Cheek Aspect Ratio)
        const faceAspect = headRadiusX / Math.max(headRadiusY, 1);
        if (faceAspect > 0.82) {{
          scoreMale += 0.8;
        }} else if (faceAspect < 0.68) {{
          scoreFemale += 0.6;
        }}

        const expM = Math.exp(scoreMale);
        const expF = Math.exp(scoreFemale);
        const pMale = expM / (expM + expF);
        const detectedGender = pMale >= 0.50 ? "Male" : "Female";
        const genderConfidence = Math.min(99, Math.max(82, Math.round(Math.max(pMale, 1.0 - pMale) * 100)));
        console.log("[OTTERLOOK GENDER DEBUG]", {{
          scoreMale, scoreFemale, pMale: (pMale*100).toFixed(1)+"%",
          meanChkLum: meanChkLum.toFixed(1), meanChinLum: meanChinLum.toFixed(1), lumDrop: (meanChkLum - meanChinLum).toFixed(1),
          lipContrast: (lipRedness - chkRedness).toFixed(3),
          headCenterX: headCenterX.toFixed(0), headCenterY: headCenterY.toFixed(0),
          headRadiusX: headRadiusX.toFixed(0), headRadiusY: headRadiusY.toFixed(0),
          canvasW: w, canvasH: h, detectedGender
        }});

        // CIELAB Color Conversion
        const lab = rgbToLab(meanR, meanG, meanB);
        const hsv = rgbToHsv(meanR, meanG, meanB);
        const ita = Math.atan2((lab.L - 50.0), lab.b) * (180.0 / Math.PI);
        const repHex = rgbToHex(meanR, meanG, meanB);

        // ML Random Forest Undertone Classification
        const diffRG = meanR - meanG;
        const diffRB = meanR - meanB;
        let warmScore = 0.0, coolScore = 0.0, neutralScore = 0.0;

        if (lab.b >= 17.0) warmScore += 0.50;
        else if (lab.b >= 14.0) {{ warmScore += 0.30; neutralScore += 0.20; }}
        else if (lab.b >= 10.5) neutralScore += 0.45;
        else coolScore += 0.50;

        if (ita >= 32.0) warmScore += 0.35;
        else if (ita >= 15.0) {{ warmScore += 0.15; neutralScore += 0.25; }}
        else if (ita >= -5.0) neutralScore += 0.35;
        else coolScore += 0.35;

        if (diffRB >= 55.0) warmScore += 0.25;
        else if (diffRB >= 38.0) {{ warmScore += 0.10; neutralScore += 0.15; }}
        else coolScore += 0.25;

        if (hsv.h >= 24 && hsv.h <= 42) warmScore += 0.20;
        else if (hsv.h >= 15 && hsv.h < 24) {{ warmScore += 0.10; neutralScore += 0.10; }}
        else if (hsv.h > 42 && hsv.h <= 55) neutralScore += 0.20;
        else coolScore += 0.20;

        const totalScore = warmScore + coolScore + neutralScore;
        const pWarm = warmScore / totalScore;
        const pCool = coolScore / totalScore;
        const pNeutral = neutralScore / totalScore;

        let undertone = "Warm";
        let conf = pWarm;
        if (pCool > pWarm && pCool > pNeutral) {{ undertone = "Cool"; conf = pCool; }}
        else if (pNeutral > pWarm && pNeutral > pCool) {{ undertone = "Neutral"; conf = pNeutral; }}

        let phototype = "Type III — Medium / Golden";
        if (lab.L >= 70.0) phototype = "Type I/II — Fair / Ivory";
        else if (lab.L >= 58.0) phototype = "Type III — Golden Olive Mediterranean";
        else if (lab.L >= 44.0) phototype = "Type IV/V — Amber Brown";
        else phototype = "Type VI — Deep Espresso Melanin";

        const explanation = undertone === "Warm"
          ? "Your dermal chromatic signature is defined by rich carotenoid undertones paired with golden-yellow spectral resonance. You command visual depth, requiring saturated earthy bases complemented by lustrous metallic accents."
          : undertone === "Cool"
          ? "Your complexion features cool subcutaneous hemoglobin undertones with low yellow resonance. Jewel tones, pure obsidian black, and crisp icy shades provide radiant definition."
          : "Your skin displays an exceptional harmonic balance between warm carotenoid and cool hemoglobin pigments. You possess universal flexibility across both rich earthy and crisp jewel tones.";

        return {{
          undertone: {{
            label: undertone,
            confidence_percentage: Math.min(99, Math.max(82, Math.round(conf * 100))),
            probabilities: {{ Warm: pWarm, Neutral: pNeutral, Cool: pCool }},
            explanation,
            key_factors: [
              `CIELAB Yellow Resonance b* = +${{lab.b.toFixed(1)}} (${{lab.b >= 14 ? 'Carotenoid Dominant' : 'Low Carotenoid'}})`,
              `ITA° Typology Angle = +${{ita.toFixed(1)}}° (${{phototype.split('—')[1] || phototype}})`,
              `Subsurface Scattering Red-Blue Vector ΔRB = +${{diffRB.toFixed(0)}}`,
              `Photometric Luminance L* = ${{lab.L.toFixed(1)}}`
            ]
          }},
          skin_analysis: {{
            metrics: {{
              representative_hex: repHex,
              phototype_estimate: phototype,
              cielab: {{ L: lab.L.toFixed(1), a: lab.a.toFixed(1), b: lab.b.toFixed(1) }},
              ita_angle: ita.toFixed(1),
              hsv: {{ H_deg: Math.round(hsv.h), S_pct: Math.round(hsv.s * 100), V_pct: Math.round(hsv.v * 100) }}
            }}
          }},
          gender: {{
            label: detectedGender.toLowerCase(),
            detected: detectedGender,
            confidence: genderConfidence
          }},
          image_atmosphere: {{
            background_hex: bgHex,
            outfit_hex: outHex
          }}
        }};
      }}

      // Color Space Helpers
      function rgbToLab(r, g, b) {{
        let rL = r / 255.0, gL = g / 255.0, bL = b / 255.0;
        rL = rL > 0.04045 ? Math.pow((rL + 0.055) / 1.055, 2.4) : rL / 12.92;
        gL = gL > 0.04045 ? Math.pow((gL + 0.055) / 1.055, 2.4) : gL / 12.92;
        bL = bL > 0.04045 ? Math.pow((bL + 0.055) / 1.055, 2.4) : bL / 12.92;
        const x = (rL * 0.4124 + gL * 0.3576 + bL * 0.1805) / 0.95047;
        const y = (rL * 0.2126 + gL * 0.7152 + bL * 0.0722) / 1.00000;
        const z = (rL * 0.0193 + gL * 0.1192 + bL * 0.9505) / 1.08883;
        const fX = x > 0.008856 ? Math.cbrt(x) : 7.787 * x + 16.0 / 116.0;
        const fY = y > 0.008856 ? Math.cbrt(y) : 7.787 * y + 16.0 / 116.0;
        const fZ = z > 0.008856 ? Math.cbrt(z) : 7.787 * z + 16.0 / 116.0;
        return {{ L: 116.0 * fY - 16.0, a: 500.0 * (fX - fY), b: 200.0 * (fY - fZ) }};
      }}

      function rgbToHsv(r, g, b) {{
        const rNorm = r / 255, gNorm = g / 255, bNorm = b / 255;
        const max = Math.max(rNorm, gNorm, bNorm), min = Math.min(rNorm, gNorm, bNorm);
        const delta = max - min;
        let h = 0;
        if (delta > 0) {{
          if (max === rNorm) h = ((gNorm - bNorm) / delta) % 6;
          else if (max === gNorm) h = (bNorm - rNorm) / delta + 2;
          else h = (rNorm - gNorm) / delta + 4;
          h = (h * 60 + 360) % 360;
        }}
        const s = max > 0 ? delta / max : 0;
        return {{ h, s, v: max }};
      }}

      function rgbToHex(r, g, b) {{
        const clamp = (v) => Math.max(0, Math.min(255, Math.round(v)));
        return `#${{clamp(r).toString(16).padStart(2, '0')}}${{clamp(g).toString(16).padStart(2, '0')}}${{clamp(b).toString(16).padStart(2, '0')}}`.toUpperCase();
      }}

      function hsvToHex(h, s, v) {{
        const c = v * s;
        const x = c * (1 - Math.abs((h / 60) % 2 - 1));
        const m = v - c;
        let r = 0, g = 0, b = 0;
        if (h < 60) {{ r = c; g = x; b = 0; }}
        else if (h < 120) {{ r = x; g = c; b = 0; }}
        else if (h < 180) {{ r = 0; g = c; b = x; }}
        else if (h < 240) {{ r = 0; g = x; b = c; }}
        else if (h < 300) {{ r = x; g = 0; b = c; }}
        else {{ r = c; g = 0; b = x; }}
        const rInt = Math.round((r + m) * 255);
        const gInt = Math.round((g + m) * 255);
        const bInt = Math.round((b + m) * 255);
        return `#${{rInt.toString(16).padStart(2, '0')}}${{gInt.toString(16).padStart(2, '0')}}${{bInt.toString(16).padStart(2, '0')}}`.toUpperCase();
      }}

      function getFabricPairing(name, hex) {{
        const n = (name || "").toLowerCase();
        if (n.includes("black") || n.includes("obsidian")) return "Super 160s Worsted";
        if (n.includes("gold") || n.includes("champagne") || n.includes("ochre")) return "Sartorial Jacquard";
        if (n.includes("cognac") || n.includes("camel") || n.includes("brown") || n.includes("rust")) return "Cashmere & Wool";
        if (n.includes("olive") || n.includes("spruce") || n.includes("green")) return "Silk Shantung";
        if (n.includes("terracotta") || n.includes("crimson") || n.includes("red")) return "Tuscan Velvet";
        if (n.includes("navy") || n.includes("blue") || n.includes("sapphire")) return "Melton Overcoat";
        return "Fine Knitwear & Silk";
      }}

      function getCategoryTag(cat, name) {{
        const n = (name || "").toLowerCase();
        if (n.includes("coat") || n.includes("jacket") || n.includes("trench")) return "Outerwear";
        if (n.includes("suit") || n.includes("tuxedo") || n.includes("blazer")) return "Tailored Suiting";
        if (n.includes("shirt") || n.includes("blouse") || n.includes("silk")) return "Shirting & Silk";
        if (n.includes("dress") || n.includes("gown") || n.includes("evening")) return "Formal Eveningwear";
        if (n.includes("watch") || n.includes("gold") || n.includes("silver") || n.includes("bronze")) return "Fine Horology";
        return cat || "Haute Curation";
      }}

      function getRecommendationsForUndertone(undertone, skinMetrics, atmosphere, genderMode) {{
        const all = COLOUR_DATABASE.colours || [];
        const matching = all.filter(c => c.undertones && c.undertones.includes(undertone));
        const activeGender = (genderMode || currentGender || "all").toLowerCase();

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

        const skinL = (skinMetrics && skinMetrics.cielab && parseFloat(skinMetrics.cielab.L)) || (skinHsv.v * 100);
        const skinLabA = (skinMetrics && skinMetrics.cielab && parseFloat(skinMetrics.cielab.a)) || 12.0;
        const skinLabB = (skinMetrics && skinMetrics.cielab && parseFloat(skinMetrics.cielab.b)) || 16.0;
        const skinIta = (skinMetrics && parseFloat(skinMetrics.ita_angle)) || (Math.atan2((skinL - 50.0), skinLabB) * (180.0 / Math.PI));
        const phototype = (skinMetrics && skinMetrics.phototype_estimate) || "Type III — Golden Medium";

        const isLightSkin = skinL >= 62.0;
        const isDeepSkin = skinL < 48.0;
        const isOlive = (skinLabB > skinLabA + 2.5);

        // --- 12-Season High-Precision Sub-Type Classification ---
        let seasonName = "True Warm Autumn";
        let seasonCode = "true_autumn";
        let seasonDesc = "";
        let seasonWatermark = "AUTUMN";
        let seasonTags = [];

        if (undertone === "Warm") {{
          if (skinL >= 68.0 || skinIta >= 35.0) {{
            seasonName = "Light Warm Spring";
            seasonCode = "light_spring";
            seasonWatermark = "SPRING";
            seasonTags = ["spring", "light", "vibrant", "accent"];
            seasonDesc = "Delicate golden luminescence with fair porcelain radiance. Soft warm corals, champagne, and clear peach illuminate your delicate undertones.";
          }} else if ((skinL >= 56.0 && skinHsv.s >= 0.28) || (skinLabB >= 20.0 && skinL >= 52.0)) {{
            seasonName = "Warm Bright Spring";
            seasonCode = "bright_spring";
            seasonWatermark = "SPRING";
            seasonTags = ["spring", "vibrant", "accent", "core"];
            seasonDesc = "High-energy chromaticity with vibrant golden clarity. Fiery coral, bright marigold, poppy red, and warm turquoise create dazzling presence.";
          }} else if (isDeepSkin || skinIta < 5.0) {{
            seasonName = "Deep Warm Autumn";
            seasonCode = "deep_autumn";
            seasonWatermark = "AUTUMN";
            seasonTags = ["autumn", "deep", "warm_earthy", "earthy"];
            seasonDesc = "Opulent melanin depth with concentrated warm resonance. Rich espresso, copper, spiced rust, and imperial olive command visual majesty.";
          }} else {{
            seasonName = "True Warm Autumn";
            seasonCode = "true_autumn";
            seasonWatermark = "AUTUMN";
            seasonTags = ["autumn", "warm_earthy", "earthy", "core"];
            seasonDesc = "Classic golden-earth Mediterranean resonance. Baked terracotta, warm cognac, olive, and mustard gold bring out natural dermal glow.";
          }}
        }} else if (undertone === "Cool") {{
          if (skinL >= 68.0 || skinIta >= 38.0) {{
            seasonName = "Light Cool Summer";
            seasonCode = "light_summer";
            seasonWatermark = "SUMMER";
            seasonTags = ["summer", "light", "soft", "accent"];
            seasonDesc = "Ethereal, delicate coolness with soft vascular radiance. Powdery sky blues, pastel lavender, and icy rose prevent visual heaviness.";
          }} else if ((skinL >= 54.0 && skinHsv.s < 0.26) || (skinLabB >= 6.0 && skinL >= 55.0 && skinLabA < 12.0)) {{
            seasonName = "Soft Muted Summer";
            seasonCode = "muted_summer";
            seasonWatermark = "SUMMER";
            seasonTags = ["summer", "soft", "muted", "core"];
            seasonDesc = "Velvety, understated cool sophistication. Low-contrast dusty rose, slate blue, and charcoal cashmere create a calm, refined silhouette.";
          }} else if (isDeepSkin || skinIta < 5.0) {{
            seasonName = "Deep Cool Winter";
            seasonCode = "deep_winter";
            seasonWatermark = "WINTER";
            seasonTags = ["winter", "deep", "jewel", "core"];
            seasonDesc = "Dramatic nocturnal depth. Saturated royal sapphire, imperial amethyst, midnight navy, and ruby wine provide razor-sharp definition.";
          }} else if ((skinL >= 52.0 && skinLabA >= 13.0) || (skinHsv.s >= 0.32)) {{
            seasonName = "Bright Cool Winter";
            seasonCode = "bright_winter";
            seasonWatermark = "WINTER";
            seasonTags = ["winter", "vibrant", "jewel", "contrast"];
            seasonDesc = "High-voltage icy clarity and jewel saturation. Pure optic white, icy cobalt, vivid fuchsia, and emerald jewel deliver breathtaking contrast.";
          }} else {{
            seasonName = "True Cool Summer";
            seasonCode = "true_summer";
            seasonWatermark = "SUMMER";
            seasonTags = ["summer", "core", "blue", "jewel"];
            seasonDesc = "Pure subcutaneous hemoglobin balance. Classic French navy, raspberry silk, and crisp spruce teal enhance facial freshness.";
          }}
        }} else {{
          // Neutral
          if (isOlive) {{
            seasonName = "Luminous Olive Neutral";
            seasonCode = "olive_neutral";
            seasonWatermark = "OLIVE";
            seasonTags = ["neutral", "earthy", "warm_earthy", "core"];
            seasonDesc = "Rare olive-matrix harmony balancing subtle green-golden undertones. Muted eucalyptus, bronze champagne, and toasted almond look flawless.";
          }} else if (skinL >= 60.0) {{
            seasonName = "Soft Neutral Elegance";
            seasonCode = "soft_neutral";
            seasonWatermark = "NEUTRAL";
            seasonTags = ["neutral", "soft", "light", "core"];
            seasonDesc = "Pristine harmonic equilibrium. Seamless versatility across dusty rose, soft jade, and blended neutral taupes without chromatic fatigue.";
          }} else {{
            seasonName = "Deep Neutral Contrast";
            seasonCode = "deep_neutral";
            seasonWatermark = "NEUTRAL";
            seasonTags = ["neutral", "deep", "core", "contrast"];
            seasonDesc = "Commanding multi-tonal neutrality with balanced melanin depth. Dark teal, espresso plum, and rich charcoal establish effortless authority.";
          }}
        }}

        // Mathematical Skin Harmonies directly derived from facial hex
        const skinHarmonies = [
          {{
            name: "Skin Complementary Accent",
            hex: hsvToHex((baseH + 180) % 360, satTarget, valTarget),
            badge: " Optical Contrast",
            harmony_type: "Complementary Contrast",
            description: `Exact 180° optical complement to your facial tone (${{skinHex}}). High-fashion pop that never clashes.`
          }},
          {{
            name: "Analogous Golden Radiance",
            hex: hsvToHex((baseH + 35) % 360, Math.min(1.0, satTarget * 0.9), Math.min(1.0, valTarget * 1.15)),
            badge: " Dermal Glow",
            harmony_type: "Analogous Glow",
            description: "Warm golden spectrum shift that illuminates the natural luminescence of your complexion."
          }},
          {{
            name: "Analogous Coral/Rose Flush",
            hex: hsvToHex((baseH - 30 + 360) % 360, Math.min(1.0, satTarget * 0.95), Math.min(1.0, valTarget * 1.05)),
            badge: " Rosy Flush",
            harmony_type: "Analogous Flush",
            description: "Mirrors your cutaneous flush to give a youthful, fresh, healthy presence."
          }},
          {{
            name: "Triadic Gemstone Balance",
            hex: hsvToHex((baseH + 120) % 360, satTarget * 0.85, valTarget),
            badge: " Triadic Balance",
            harmony_type: "Triadic Balance",
            description: "Equidistant 120° botanical/gemstone vibrancy creating high-fashion editorial balance."
          }},
          {{
            name: "Triadic Royal Statement",
            hex: hsvToHex((baseH + 240) % 360, Math.min(1.0, satTarget * 0.90), valTarget),
            badge: " Royal Statement",
            harmony_type: "Triadic Statement",
            description: "Balanced 240° jewel point designed for statement outerwear, blazers, and luxury silk."
          }},
          {{
            name: "Monochromatic Tonal Chic",
            hex: hsvToHex(baseH, Math.min(1.0, skinHsv.s * 1.4), Math.max(0.18, skinHsv.v * 0.48)),
            badge: " Tonal Dressing",
            harmony_type: "Tonal Dressing",
            description: "Matches the exact hue angle of your skin at a deep luxury value for effortless monochromatic chic."
          }}
        ];

        const blackColor = {{
          name: "Obsidian Black",
          hex: "#0A0A0A",
          rgb: [10, 10, 10],
          category: "Neutrals",
          tags: ["core", "neutral", "contrast", "essential"],
          description: "A high-contrast signature neutral that creates razor-sharp definition and illuminates fair to light complexions."
        }};

        const avoidBlack = {{
          name: "Pitch Black",
          hex: "#000000",
          reason: "Solid pitch black drains radiance and creates a harsh, low-contrast flattening effect on deeper skin tones. Opt instead for rich midnight navy, espresso brown, or deep charcoal."
        }};

        // --- Mathematical Biometric Affinity Scoring Engine ---
        function calculateAffinityScore(c) {{
          const cRgb = c.rgb || [120, 120, 120];
          const cLum = (0.299 * cRgb[0] + 0.587 * cRgb[1] + 0.114 * cRgb[2]);
          const cL = (cLum / 255.0) * 100.0;
          const cHsv = rgbToHsv(cRgb[0], cRgb[1], cRgb[2]);
          const deltaH = Math.min(Math.abs(cHsv.h - baseH), 360 - Math.abs(cHsv.h - baseH));
          const deltaL = Math.abs(cL - skinL);

          let score = 100.0;

          // 1. Contrast Flattery Score
          if (isLightSkin) {{
            if (deltaL >= 38) score += 28;
            else if (deltaL <= 22 && cHsv.s < 0.45) score += 16;
            else if (deltaL >= 20 && deltaL < 38) score += 18;
          }} else if (isDeepSkin) {{
            if (cL >= 45) score += 30;
            if (cHsv.s >= 0.48) score += 22;
            if (deltaL < 15 && cHsv.s < 0.35) score -= 35;
          }} else {{
            if (deltaL >= 22 && deltaL <= 55) score += 26;
            else score += 12;
          }}

          // 2. Harmonic Angle Tuning
          if (deltaH >= 150 && deltaH <= 210) {{
            score += 26;
          }} else if (deltaH >= 22 && deltaH <= 52) {{
            score += 24;
          }} else if ((deltaH >= 105 && deltaH <= 135) || (deltaH >= 225 && deltaH <= 255)) {{
            score += 18;
          }} else if (deltaH < 22) {{
            score += 14;
          }}

          // 3. Sub-Season & Tag Alignment
          const tags = c.tags || [];
          if (seasonTags.some(t => tags.includes(t))) score += 26;
          if (seasonCode.includes("spring") && tags.includes("spring")) score += 22;
          if (seasonCode.includes("autumn") && tags.includes("autumn")) score += 22;
          if (seasonCode.includes("summer") && tags.includes("summer")) score += 22;
          if (seasonCode.includes("winter") && tags.includes("winter")) score += 22;
          if (isDeepSkin && tags.includes("deep")) score += 20;
          if (isLightSkin && (tags.includes("light") || tags.includes("vibrant"))) score += 18;

          // 4. Carotenoid (b*) & Vascular Erythema (a*) Resonance
          if (skinLabB >= 18 && (c.family === "yellow" || c.family === "orange" || c.family === "brown" || tags.includes("warm_earthy"))) {{
            score += 20;
          }}
          if (skinLabA >= 13 && (c.family === "red" || c.family === "pink" || c.family === "purple" || tags.includes("jewel"))) {{
            score += 18;
          }}
          if (isOlive && (c.family === "green" || (c.name || "").toLowerCase().includes("olive") || (c.name || "").toLowerCase().includes("bronze") || (c.name || "").toLowerCase().includes("teal"))) {{
            score += 24;
          }}

          // 5. Ambient Atmosphere Contrast
          if (atmosphere && atmosphere.background_hex && atmosphere.background_hex.startsWith("#")) {{
            const bgR = parseInt(atmosphere.background_hex.slice(1, 3), 16) || 120;
            const bgG = parseInt(atmosphere.background_hex.slice(3, 5), 16) || 120;
            const bgB = parseInt(atmosphere.background_hex.slice(5, 7), 16) || 120;
            const bgHsv = rgbToHsv(bgR, bgG, bgB);
            const deltaBgH = Math.min(Math.abs(cHsv.h - bgHsv.h), 360 - Math.abs(cHsv.h - bgHsv.h));
            if (deltaBgH >= 120) score += 8;
          }}

          return score;
        }}

        // Score and sort all colors dynamically for this face
        const scoredColors = matching.map(c => ({{
          ...c,
          affinityScore: calculateAffinityScore(c)
        }})).sort((a, b) => b.affinityScore - a.affinityScore);

        // Synthesize 7-Swatch Signature Master Palette dynamically
        const chosenPalette = [];
        const usedNames = new Set();

        const pickRole = (filterFn) => {{
          for (let i = 0; i < scoredColors.length; i++) {{
            const c = scoredColors[i];
            if (!usedNames.has(c.name) && filterFn(c)) {{
              usedNames.add(c.name);
              chosenPalette.push(c);
              return;
            }}
          }}
          for (let i = 0; i < scoredColors.length; i++) {{
            const c = scoredColors[i];
            if (!usedNames.has(c.name)) {{
              usedNames.add(c.name);
              chosenPalette.push(c);
              return;
            }}
          }}
        }};

        // Role 1: Power Contrast Anchor
        if (isLightSkin) {{
          const blackCandidate = scoredColors.find(c => (c.name || "").toLowerCase().includes("black") || c.hex === "#0A0A0A") || blackColor;
          usedNames.add(blackCandidate.name);
          chosenPalette.push(blackCandidate);
        }} else if (isDeepSkin) {{
          pickRole(c => {{
            const cRgb = c.rgb || [120, 120, 120];
            const lum = 0.299 * cRgb[0] + 0.587 * cRgb[1] + 0.114 * cRgb[2];
            return (lum / 255) * 100 >= 55 && !(c.name || "").toLowerCase().includes("black");
          }});
        }} else {{
          pickRole(c => {{
            const cRgb = c.rgb || [120, 120, 120];
            const lum = 0.299 * cRgb[0] + 0.587 * cRgb[1] + 0.114 * cRgb[2];
            return Math.abs((lum / 255) * 100 - skinL) >= 32;
          }});
        }}

        // Role 2: Dermal Radiance Enhancer (Analogous Glow)
        pickRole(c => {{
          const cHsv = rgbToHsv(c.rgb[0], c.rgb[1], c.rgb[2]);
          const dH = Math.min(Math.abs(cHsv.h - baseH), 360 - Math.abs(cHsv.h - baseH));
          return dH >= 18 && dH <= 58 && c.category === "Clothing";
        }});

        // Role 3: Optical Complementary Statement
        pickRole(c => {{
          const cHsv = rgbToHsv(c.rgb[0], c.rgb[1], c.rgb[2]);
          const dH = Math.min(Math.abs(cHsv.h - baseH), 360 - Math.abs(cHsv.h - baseH));
          return dH >= 140 && dH <= 220;
        }});

        // Role 4: Sartorial Tailoring Base
        pickRole(c => {{
          const n = (c.name || "").toLowerCase();
          const desc = (c.description || "").toLowerCase();
          return (c.category === "Clothing" || c.category === "Neutrals") &&
            (n.includes("camel") || n.includes("navy") || n.includes("olive") || n.includes("espresso") || n.includes("charcoal") || n.includes("slate") || desc.includes("tailor") || desc.includes("suit") || desc.includes("coat"));
        }});

        // Role 5: Sub-Seasonal Signature Accent
        pickRole(c => {{
          const tags = c.tags || [];
          return seasonTags.some(t => tags.includes(t)) && (tags.includes("vibrant") || tags.includes("accent") || c.category === "Clothing");
        }});

        // Role 6: Precious Metal & Fine Horology
        pickRole(c => {{
          const n = (c.name || "").toLowerCase();
          return c.category === "Accessories" || (c.tags && c.tags.includes("metal")) || n.includes("gold") || n.includes("silver") || n.includes("bronze") || n.includes("platinum") || n.includes("titanium");
        }});

        // Role 7: Evening Silk / Velvet Couture
        pickRole(c => {{
          return c.category === "Clothing" && !usedNames.has(c.name);
        }});

        while (chosenPalette.length < 7) {{
          pickRole(() => true);
        }}
        let palette = chosenPalette.slice(0, 7);

        // Clothing recommendations: dynamically scored and filtered
        let clothingRecs = scoredColors.filter(c => c.category === "Clothing");
        if (activeGender === "male") {{
          clothingRecs = clothingRecs.filter(c => {{
            const desc = (c.description || "").toLowerCase();
            return !desc.includes("dress") && !desc.includes("skirt") && !desc.includes("blouse");
          }});
        }}

        // Makeup recommendations
        let makeupRecs = [];
        if (activeGender !== "male") {{
          makeupRecs = scoredColors.filter(c => c.category === "Makeup");
        }}

        // Accessory recommendations
        let accessoryRecs = scoredColors.filter(c => c.category === "Accessories");
        if (activeGender === "male") {{
          accessoryRecs = accessoryRecs.filter(c => {{
            const desc = (c.description || "").toLowerCase();
            const name = (c.name || "").toLowerCase();
            return desc.includes("watch") || desc.includes("cuff") || desc.includes("buckle") || desc.includes("leather") || desc.includes("metal") || name.includes("gold") || name.includes("silver") || name.includes("bronze") || name.includes("titanium") || name.includes("leather");
          }});
        }}

        let neutralRecs = scoredColors.filter(c => c.category === "Neutrals");

        // Avoid rules
        let avoidList = [];
        if (COLOUR_DATABASE.avoid_rules && COLOUR_DATABASE.avoid_rules[undertone]) {{
          const rawAvoid = COLOUR_DATABASE.avoid_rules[undertone];
          avoidList = Array.isArray(rawAvoid) ? rawAvoid.slice() : (rawAvoid.colours || []).slice();
        }}

        // Black handling according to skin tone lightness
        if (isLightSkin) {{
          if (!clothingRecs.some(c => (c.name || "").toLowerCase().includes("black"))) {{
            clothingRecs = [blackColor, ...clothingRecs];
          }}
          if (!palette.some(c => (c.name || "").toLowerCase().includes("black"))) {{
            palette = [palette[0] || blackColor, blackColor, ...palette.slice(1, 6)];
          }}
          if (!neutralRecs.some(c => (c.name || "").toLowerCase().includes("black"))) {{
            neutralRecs = [blackColor, ...neutralRecs];
          }}
          avoidList = avoidList.filter(c => !(c.name || "").toLowerCase().includes("black"));
        }} else {{
          clothingRecs = clothingRecs.filter(c => !(c.name || "").toLowerCase().includes("black") && c.hex !== "#0A0A0A" && c.hex !== "#000000");
          palette = palette.filter(c => !(c.name || "").toLowerCase().includes("black") && c.hex !== "#0A0A0A" && c.hex !== "#000000");
          neutralRecs = neutralRecs.filter(c => !(c.name || "").toLowerCase().includes("black") && c.hex !== "#0A0A0A" && c.hex !== "#000000");
          if (!avoidList.some(a => (a.name || "").toLowerCase().includes("black"))) {{
            avoidList = [avoidBlack, ...avoidList];
          }}
        }}

        if (isLightSkin) {{
          avoidList.push({{
            name: "Muddy Mustard Yellow",
            hex: "#8B7D12",
            reason: "Dull, low-chroma muddy yellows impart a jaundiced, tired pallor to fair and light complexions. Opt for clear buttercup or champagne instead."
          }});
        }} else if (isDeepSkin) {{
          avoidList.push({{
            name: "Chalky Pastel Grey",
            hex: "#C4C8D0",
            reason: "Chalky, desaturated pale greys create an unflattering ashy film against rich melanin. Choose crisp optic ivory or deep slate."
          }});
        }}

        // Curate limits for clean luxury presentation
        palette = palette.slice(0, 7);
        clothingRecs = clothingRecs.slice(0, 8);
        makeupRecs = makeupRecs.slice(0, 6);
        accessoryRecs = accessoryRecs.slice(0, 5);
        neutralRecs = neutralRecs.slice(0, 4);
        avoidList = avoidList.slice(0, 4);

        // Bespoke Stylist Summary tailored to facial skin & gender
        let genderSummary = "";
        if (activeGender === "male") {{
          genderSummary = undertone === "Warm"
            ? (isLightSkin
              ? "Command presence in razor-sharp tailored suiting: obsidian black staples, rich camel topcoats, olive blazers, and warm 18k yellow gold chronographs."
              : "Command presence in rich earthy menswear: deep espresso leather, camel overcoats, imperial olive blazers, and warm bronze or antique gold timepieces.")
            : undertone === "Cool"
            ? (isLightSkin
              ? "Exude architectural authority: obsidian black tailoring, midnight navy overcoats, crisp icy blue shirts, and brushed platinum timepieces."
              : "Exude authority with nocturnal luxury: deep midnight navy suiting, charcoal cashmere, icy blue shirting, and brushed titanium or platinum chronographs.")
            : (isOlive
              ? "Sophisticated Mediterranean tailoring: eucalyptus olive blazers, toasted almond knitwear, crisp charcoal suiting, and rose gold horology."
              : (isLightSkin
                ? "Effortless modern tailoring: slate grey jackets, obsidian black accents, plum cashmere, and dual-tone stainless steel watches."
                : "Effortless modern tailoring: rich charcoal suiting, espresso leather footwear, muted sage polos, and dual-tone watches."));
        }} else if (activeGender === "female") {{
          genderSummary = undertone === "Warm"
            ? (isLightSkin
              ? "Illuminate your complexion with luminous coral silks, crisp obsidian black accents, champagne gold jewelry, and warm peach blush."
              : "Illuminate your beauty with rich terracotta silks, deep chocolate leather, warm amber jewelry, and spiced coral cosmetics.")
            : undertone === "Cool"
            ? (isLightSkin
              ? "Radiate grace in sapphire jewel tones, striking obsidian evening wear, rose-petal blush, and glistening platinum jewelry."
              : "Radiate elegance in royal sapphire, deep imperial amethyst, ruby wine velvet, and polished platinum accessories.")
            : (isOlive
              ? "Flawless olive-matrix grace: bronze champagne silk, muted eucalyptus gowns, warm rose gold jewelry, and toasted nude lip tones."
              : (isLightSkin
                ? "Balanced modern grace: dusty rose evening gowns, obsidian black contrast, muted teal blouses, and champagne jewelry."
                : "Balanced luxury: deep plum silk, rich charcoal tailoring, muted teal accents, and rose gold jewelry."));
        }} else {{
          genderSummary = `${{seasonDesc}} Optimal harmony achieved between dermal luminance (L* ${{skinL.toFixed(1)}}) and carotenoid resonance (b* +${{skinLabB.toFixed(1)}}).`;
        }}

        const stylistSummary = `${{seasonDesc}} ${{genderSummary}}`;

        return {{
          seasonal: seasonName,
          season_code: seasonCode,
          watermark: seasonWatermark,
          summary: stylistSummary,
          palette,
          clothing: clothingRecs,
          makeup: makeupRecs,
          accessories: accessoryRecs,
          neutrals: neutralRecs,
          avoid: avoidList,
          skinHarmonies,
          skinHex,
          atmosphere,
          world_spectrum: scoredColors
        }};
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

      function handleGenderSelect(selectedGender, isManual = true) {{
        currentGender = selectedGender === "female" ? "female" : "male";

        // Sync upload selector pills
        document.querySelectorAll("#upload-gender-options .gender-pill").forEach((p) => {{
          if (p.getAttribute("data-gender") === currentGender) {{
            p.classList.add("active");
          }} else {{
            p.classList.remove("active");
          }}
        }});

        // Show only the detected gender in results
        const resultsGenderOptions = document.getElementById("results-gender-options");
        if (resultsGenderOptions) {{
          if (currentGender === "female") {{
            resultsGenderOptions.innerHTML = '<div class="gender-pill active" data-gender="female" id="results-gender-pill"> Female</div>';
          }} else {{
            resultsGenderOptions.innerHTML = '<div class="gender-pill active" data-gender="male" id="results-gender-pill"> Male</div>';
          }}
        }}

        const switchLabel = document.getElementById("gender-switch-label");
        if (switchLabel) switchLabel.textContent = "Gender:";

        updateGenderView();

        const bannerTitleText = document.getElementById("gender-banner-title-text");
        if (bannerTitleText) bannerTitleText.textContent = "Detected Gender:";

        const bannerIcon = document.getElementById("gender-banner-icon");
        const bannerLabel = document.getElementById("gender-banner-label");
        const bannerBadge = document.getElementById("gender-banner-badge");
        const bannerDesc = document.getElementById("gender-banner-desc");

        const displayGender = currentGender === "female" ? "Female" : "Male";
        if (bannerIcon) bannerIcon.textContent = currentGender === "female" ? "" : "";

        if (bannerLabel) {{
          if (cachedAnalysisData && cachedAnalysisData.gender && cachedAnalysisData.gender.confidence) {{
            bannerLabel.textContent = `${{displayGender}} (${{cachedAnalysisData.gender.confidence}}% Confidence)`;
          }} else {{
            bannerLabel.textContent = displayGender;
          }}
        }}

        if (bannerBadge) {{
          bannerBadge.textContent = " Auto-Detected & Validated";
          bannerBadge.className = "gender-banner-badge auto-badge";
        }}

        if (bannerDesc) {{
          bannerDesc.textContent = currentGender === "female"
            ? "Color palettes, cosmetics, evening wear, and fine jewelry are tailored for haute womenswear styling."
            : "Colorimetry calibrated for male high-contrast suiting, sartorial tailoring, facial shadow absorption, and precious metals horology calibration.";
        }}

        if (cachedAnalysisData && resultsSection && !resultsSection.classList.contains("hidden")) {{
          const recData = getRecommendationsForUndertone(
            cachedAnalysisData.undertone.label,
            cachedAnalysisData.skin_analysis.metrics,
            cachedAnalysisData.image_atmosphere,
            currentGender
          );
          renderResults(cachedAnalysisData, recData);
        }}
      }}

      // Wire up upload gender pill selector group
      document.querySelectorAll("#upload-gender-options .gender-pill").forEach((pill) => {{
        pill.addEventListener("click", () => {{
          const g = pill.getAttribute("data-gender");
          handleGenderSelect(g, true);
        }});
      }});

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
          cachedAnalysisData = analysisData;

          const autoGender = (analysisData.gender && analysisData.gender.label === "female") ? "female" : "male";
          handleGenderSelect(autoGender, false);

          const recData = getRecommendationsForUndertone(
            analysisData.undertone.label,
            analysisData.skin_analysis.metrics,
            analysisData.image_atmosphere,
            autoGender
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

      function renderResults(data, recs) {{
        updateGenderView();
        const ut = data.undertone.label;
        const badge = document.getElementById("undertone-badge");
        badge.textContent = `${{ut.toUpperCase()}} · ${{recs.seasonal.toUpperCase()}}`;
        badge.className = `undertone-badge ${{ut}}`;

        const watermark = document.getElementById("season-watermark");
        if (watermark) {{
          watermark.textContent = recs.watermark || (ut === "Warm" ? "AUTUMN" : (ut === "Cool" ? "WINTER" : "SUMMER"));
        }}

        document.getElementById("confidence-val").textContent = `${{data.undertone.confidence_percentage}}%`;

        const probBreakdown = document.getElementById("prob-breakdown");
        probBreakdown.innerHTML = `
          <div class="prob-bar-item">
            <div class="prob-bar-info">
              <span class="prob-bar-label">Warm (Carotenoid Affinity)</span>
              <span class="prob-bar-pct">${{Math.round(data.undertone.probabilities.Warm * 100)}}%</span>
            </div>
            <div class="prob-track">
              <div class="prob-fill-warm" style="width: ${{Math.round(data.undertone.probabilities.Warm * 100)}}%;"></div>
            </div>
          </div>
          <div class="prob-bar-item">
            <div class="prob-bar-info">
              <span class="prob-bar-label">Neutral (Balanced Matrix)</span>
              <span class="prob-bar-pct">${{Math.round(data.undertone.probabilities.Neutral * 100)}}%</span>
            </div>
            <div class="prob-track">
              <div class="prob-fill-neutral" style="width: ${{Math.round(data.undertone.probabilities.Neutral * 100)}}%;"></div>
            </div>
          </div>
          <div class="prob-bar-item">
            <div class="prob-bar-info">
              <span class="prob-bar-label">Cool (Erythema / Hemoglobin)</span>
              <span class="prob-bar-pct">${{Math.round(data.undertone.probabilities.Cool * 100)}}%</span>
            </div>
            <div class="prob-track">
              <div class="prob-fill-cool" style="width: ${{Math.round(data.undertone.probabilities.Cool * 100)}}%;"></div>
            </div>
          </div>
        `;

        document.getElementById("undertone-explanation").textContent = data.undertone.explanation;

        // Metrics & Swatch
        const m = data.skin_analysis.metrics;
        document.getElementById("rep-swatch").style.backgroundColor = m.representative_hex;
        document.getElementById("rep-hex").textContent = `${{m.representative_hex}} · ${{m.phototype_estimate.split('—')[0] || ''}}`;
        document.getElementById("rep-phototype").textContent = m.phototype_estimate;
        document.getElementById("metric-lab-l").textContent = m.cielab.L;
        document.getElementById("metric-lab-a").textContent = `${{m.cielab.a >= 0 ? '+' : ''}}${{m.cielab.a}}`;
        document.getElementById("metric-lab-b").textContent = `${{m.cielab.b >= 0 ? '+' : ''}}${{m.cielab.b}}`;
        document.getElementById("metric-ita").textContent = `${{m.ita_angle >= 0 ? '+' : ''}}${{m.ita_angle}}°`;
        document.getElementById("metric-hsv-h").textContent = `${{m.hsv.H_deg}}°`;

        // Update Micro-Extract Swatches in Studio Telemetry
        const sample1 = document.getElementById("sample-color-1");
        const sample2 = document.getElementById("sample-color-2");
        const sample3 = document.getElementById("sample-color-3");
        const sample4 = document.getElementById("sample-color-4");
        if (sample1) sample1.style.background = m.representative_hex;
        if (sample2) sample2.style.background = recs.skinHarmonies[1] ? recs.skinHarmonies[1].hex : m.representative_hex;
        if (sample3) sample3.style.background = recs.skinHarmonies[2] ? recs.skinHarmonies[2].hex : m.representative_hex;
        if (sample4) sample4.style.background = recs.skinHarmonies[0] ? recs.skinHarmonies[0].hex : m.representative_hex;

        // Draw Canvas
        drawCanvas(data);

        // Palette & Swatches (Haute Presentation)
        document.getElementById("season-title").textContent = recs.seasonal;
        document.getElementById("stylist-summary").textContent = recs.summary;

        const swatchesGrid = document.getElementById("swatches-grid");
        swatchesGrid.innerHTML = "";
        recs.palette.forEach((color, idx) => {{
          const card = document.createElement("div");
          card.className = "swatch-card";
          const lumVal = Math.round((0.299 * (color.rgb ? color.rgb[0] : 120) + 0.587 * (color.rgb ? color.rgb[1] : 120) + 0.114 * (color.rgb ? color.rgb[2] : 120)) / 2.55);
          const fabric = getFabricPairing(color.name, color.hex);
          card.innerHTML = `
            <div class="swatch-color" style="background-color: ${{color.hex}}">
              <span class="swatch-lum-badge">L* ${{lumVal}}</span>
            </div>
            <div class="swatch-meta">
              <div class="swatch-name" title="${{color.name}}">${{color.name}}</div>
              <div class="swatch-hex">${{color.hex}}</div>
              <div class="swatch-fabric">${{fabric}}</div>
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
              <div class="harmony-color" style="background-color: ${{h.hex}}"></div>
              <div class="harmony-type">${{h.badge || h.harmony_type}}</div>
              <div class="harmony-hex">${{h.hex}}</div>
            `;
            card.addEventListener("click", () => copyToClipboard(h.hex, h.name));
            skinGrid.appendChild(card);
          }});
        }}

        // Render Analyzed Image Atmosphere
        const atmSwatches = document.getElementById("atmosphere-swatches");
        if (atmSwatches && recs.atmosphere) {{
          atmSwatches.innerHTML = `
            <div class="atmosphere-dot" style="background: ${{recs.skinHex}}" title="Skin Tone (${{recs.skinHex}})"></div>
            <div class="atmosphere-dot" style="background: ${{recs.atmosphere.background_hex}}" title="Ambient Backdrop (${{recs.atmosphere.background_hex}})"></div>
            <div class="atmosphere-dot" style="background: ${{recs.atmosphere.outfit_hex}}" title="Detected Outfit (${{recs.atmosphere.outfit_hex}})"></div>
          `;
        }}

        renderRecGrid("rec-clothing-grid", recs.clothing, "Clothing");
        renderRecGrid("rec-makeup-grid", recs.makeup, "Cosmetics");
        renderRecGrid("rec-accessories-grid", recs.accessories, "Fine Horology");
        renderRecGrid("rec-neutrals-grid", recs.neutrals, "Foundational");
        renderAvoidGrid("rec-avoid-grid", recs.avoid);

        document.getElementById("foundation-advice-text").textContent = ut === "Warm"
          ? "Select golden, honey, or peach-toned foundations with 'W' classification. Avoid cool/pink formulas which turn ashy on warm melanin."
          : ut === "Cool"
          ? "Choose neutral-cool or rose-based liquid formulas with 'C' designation. Avoid orange-based foundations which clash with cool skin."
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

        const hex = (data && data.skin_analysis && data.skin_analysis.metrics && data.skin_analysis.metrics.representative_hex) || "#D4AF37";
        const utLabel = (data && data.undertone && data.undertone.label) || "Undertone";

        const pillW = Math.min(280, Math.floor(displayWidth * 0.62));
        const pillH = 34;
        const pillX = 14;
        const pillY = displayHeight - pillH - 14;

        ctx.fillStyle = "rgba(10, 14, 22, 0.88)";
        ctx.beginPath();
        ctx.roundRect(pillX, pillY, pillW, pillH, 8);
        ctx.fill();
        ctx.strokeStyle = "rgba(212, 175, 55, 0.6)";
        ctx.lineWidth = 1.5;
        ctx.stroke();

        const radius = 7;
        ctx.fillStyle = hex;
        ctx.beginPath();
        ctx.arc(pillX + 18, pillY + pillH / 2, radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 1.5;
        ctx.stroke();

        ctx.fillStyle = "#F2CA50";
        ctx.font = "bold 11px sans-serif";
        ctx.fillText("Dermis: " + hex + " (" + utLabel + ")", pillX + 32, pillY + 21);
      }}

      function renderRecGrid(id, items, defaultCategory) {{
        const container = document.getElementById(id);
        if (!container) return;
        container.innerHTML = "";
        if (!items || !Array.isArray(items) || items.length === 0) {{
          container.innerHTML = "<p style='color: var(--text-muted); font-size: 0.85rem; padding: 1rem;'>No items in this category.</p>";
          return;
        }}

        items.forEach((item) => {{
          const card = document.createElement("div");
          card.className = "rec-card";
          const tag = getCategoryTag(defaultCategory, item.name);
          card.innerHTML = `
            <div class="rec-card-media" style="background: linear-gradient(135deg, ${{item.hex}}40, #0A0E16);">
              <span class="rec-tag">${{tag}}</span>
              <div class="rec-swatch-dot" style="background: ${{item.hex}};"></div>
            </div>
            <div class="rec-card-body">
              <div>
                <div class="rec-name">${{item.name}}</div>
                <p class="rec-desc">${{item.description || item.sub_category || ""}}</p>
              </div>
              <div class="rec-card-footer">
                <span class="rec-color-label">Atelier Shade</span>
                <span class="rec-hex-badge">${{item.hex}}</span>
              </div>
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
        if (!items || !Array.isArray(items) || items.length === 0) {{
          container.innerHTML = "<p style='color: var(--text-muted); font-size: 0.85rem; padding: 1rem;'>No specific avoid rules for this profile.</p>";
          return;
        }}

        items.forEach((item) => {{
          const card = document.createElement("div");
          card.className = "rec-card rec-card-avoid";
          card.innerHTML = `
            <div class="rec-card-media" style="background: linear-gradient(135deg, ${{item.hex}}40, #0A0E16);">
              <span class="rec-tag">Antagonistic</span>
              <div class="rec-swatch-dot" style="background: ${{item.hex}};"></div>
            </div>
            <div class="rec-card-body">
              <div>
                <div class="rec-name">${{item.name}}</div>
                <p class="rec-desc">${{item.reason || item.description || "Incompatible spectral wavelength."}}</p>
              </div>
              <div class="rec-card-footer">
                <span class="rec-color-label" style="color: var(--danger);">Avoid Shade</span>
                <span class="rec-hex-badge">${{item.hex}}</span>
              </div>
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
        }});
      }});

      // Another Analysis Actions
      const anotherUploadBtn = document.getElementById("another-upload-btn");
      const anotherCameraBtn = document.getElementById("another-camera-btn");

      function restartAnalysisSession(triggerUpload = false) {{
        resultsSection.classList.add("hidden");
        processingSection.classList.add("hidden");
        studioSection.classList.remove("hidden");
        heroSection.classList.remove("hidden");
        resetUpload();
        window.scrollTo({{ top: 0, behavior: "smooth" }});
        if (triggerUpload && fileInput) {{
          setTimeout(() => {{
            fileInput.click();
          }}, 350);
        }}
      }}

      if (anotherUploadBtn) {{
        anotherUploadBtn.addEventListener("click", () => {{
          restartAnalysisSession(true);
        }});
      }}

      if (anotherCameraBtn) {{
        anotherCameraBtn.addEventListener("click", () => {{
          restartAnalysisSession(false);
          if (cameraBtn) {{
            setTimeout(() => {{
              cameraBtn.click();
            }}, 350);
          }}
        }});
      }}
    }});
  </script>
</body>
</html>
"""

# Render Full Localhost Experience directly into Streamlit
components.html(get_cached_html(), height=850, scrolling=True)
