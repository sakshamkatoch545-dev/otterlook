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
          <span class="brand-sub">Personal Color & Style Analysis</span>
        </div>
      </div>

      <!-- Live Engine Status Hub -->
      <div class="telemetry-hub">
        <span class="telemetry-dot">
          <span class="telemetry-dot-ping"></span>
          <span class="telemetry-dot-core"></span>
        </span>
        <span class="telemetry-text">Auto-Colour Detection Engine Active</span>
        <span class="telemetry-sep">|</span>
        <span class="telemetry-sub">Natural Daylight Standard</span>
      </div>

      <div class="header-actions">
        <button id="viva-modal-btn" class="btn btn-outline" title="About Otterlook AI">
          <span class="material-symbols-outlined" style="font-size: 16px;">help_outline</span>
          <span>How It Works</span>
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
        <span class="material-symbols-outlined" style="font-size: 14px;">palette</span>
        Smart Personal Color Analysis
      </div>
      <h2 class="hero-headline">Find the Colors that <em>Naturally Flatter You</em></h2>
      <p class="hero-description">
        Upload a clear photo taken in natural daylight. Our smart scanner spots your skin tone, checks your lighting, and reveals your personal color season and best outfit shades.
      </p>

      <div class="hero-badges">
        <div class="badge-item">
          <span class="material-symbols-outlined" style="font-size: 14px;">colorize</span>
          Auto-Colour Detection
        </div>
        <div class="badge-item">
          <span class="material-symbols-outlined" style="font-size: 14px;">wb_sunny</span>
          Natural Lighting Check
        </div>
        <div class="badge-item">
          <span class="material-symbols-outlined" style="font-size: 14px;">checkroom</span>
          Personalized Style Guide
        </div>
      </div>
    </section>

    <!-- Studio Photo Upload & Analysis Area -->
    <section class="studio-section">
      <div class="scanner-bento-grid">
        <!-- Left: Upload Viewport Box with Auto-Colour Scanner -->
        <div class="reticle-viewport">
          <!-- 4-Corner Reticles -->
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
              <h3>Upload Your Photo</h3>
              <p>Drag & drop your portrait here, or snap a quick live selfie</p>
              
              <div class="upload-actions">
                <button type="button" class="btn btn-camera" id="camera-btn">
                  <span class="material-symbols-outlined" style="font-size: 16px;">photo_camera</span>
                  Take Live Selfie
                </button>
                <button type="button" class="btn btn-outline" id="browse-btn">
                  <span class="material-symbols-outlined" style="font-size: 16px;">folder_open</span>
                  Browse Files
                </button>
              </div>

              <!-- Quick Demo Studio Portraits -->
              <div class="sample-chips-row">
                <span class="sample-chips-label">Demo Photos:</span>
                <button type="button" class="sample-chip-btn" id="chip-sample-warm" data-sample="/static/assets/samples/sample_warm.jpg">Warm Autumn</button>
                <button type="button" class="sample-chip-btn" id="chip-sample-cool" data-sample="/static/assets/samples/sample_cool.jpg">Cool Summer</button>
                <button type="button" class="sample-chip-btn" id="chip-sample-neutral" data-sample="/static/assets/samples/sample_neutral.jpg">Neutral Spring</button>
              </div>
              
              <span class="file-hint">JPG, PNG, or WebP (max 15MB) • Natural daylight facing a window works best</span>
            </div>

            <!-- Live Preview Box with Auto Colour Detection Overlay -->
            <div class="preview-box hidden" id="preview-box">
              <div class="preview-stage" id="preview-stage">
                <img id="preview-img" src="" alt="Analyzed Photo">
                <button class="remove-btn" id="remove-img-btn" title="Remove image">×</button>
                
                <!-- Auto Colour & Lighting Detection Overlay (Replaces Face Detection Box) -->
                <div class="biometric-overlay" id="biometric-overlay">
                  <div class="viewport-hud">
                    <span class="hud-pill" id="hud-mode-pill">🎨 AUTO COLOUR DETECTION ACTIVE</span>
                    <span class="hud-pill hud-pill-secondary" id="hud-lighting-pill">💡 NATURAL LIGHT SENSOR</span>
                  </div>
                  
                  <!-- Smart Auto-Detected Complexion Badge -->
                  <div class="auto-color-badge-container" id="auto-color-badge-container">
                    <div class="auto-color-badge" id="auto-color-badge">
                      <span class="auto-color-swatch-circle" id="face-box-color-dot" style="background: #C68B59;"></span>
                      <div class="auto-color-badge-info">
                        <span class="auto-color-badge-title" id="auto-color-badge-title">SPOTTING COMPLEXION...</span>
                        <span class="auto-color-badge-hex" id="face-box-hex">CALIBRATING</span>
                      </div>
                      <span class="auto-color-status-tag" id="face-box-sublabel">AUTO SCAN</span>
                    </div>
                  </div>

                  <!-- Reference anchor for backward compatibility -->
                  <div id="box-face" style="display: none;"></div>

                  <!-- Laser Scan Line FX -->
                  <div class="scanline-fx" id="scanline-fx"></div>

                  <!-- Viewport Bottom Dock -->
                  <div class="viewport-dock">
                    <div class="dock-status">
                      <span class="dock-dot" id="dock-dot"></span>
                      <span id="mesh-status-text">Scanning photo lighting and complexion...</span>
                    </div>
                    <span class="hud-pill" id="lighting-status-pill">Checking Lighting...</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Photo Quality & Lighting Bar -->
          <div class="quality-bar hidden" id="quality-bar">
            <div class="quality-header">
              <span class="quality-title">Photo Quality & Lighting Check:</span>
              <span class="quality-status" id="quality-status">Checking Photo...</span>
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

        <!-- Right: Real-time Photo Quality & Lighting Check Card -->
        <div class="telemetry-card">
          <div>
            <div class="telemetry-header">
              <span class="telemetry-title">Photo Check</span>
              <span class="telemetry-grade">High Accuracy</span>
            </div>
            <h3 class="telemetry-headline">Lighting & Clarity Analysis</h3>

            <div class="diagnostic-meters">
              <div class="meter-row">
                <div class="meter-labels">
                  <span class="meter-name">Lighting Quality</span>
                  <span class="meter-val" id="meter-lux-val">Optimal Daylight</span>
                </div>
                <div class="meter-track">
                  <div class="meter-fill" id="meter-lux-fill" style="width: 95%;"></div>
                </div>
              </div>

              <div class="meter-row">
                <div class="meter-labels">
                  <span class="meter-name">Natural Color Balance</span>
                  <span class="meter-val" id="meter-wb-val">Balanced</span>
                </div>
                <div class="meter-track">
                  <div class="meter-fill" id="meter-wb-fill" style="width: 96%;"></div>
                </div>
              </div>

              <div class="meter-row">
                <div class="meter-labels">
                  <span class="meter-name">Image Clarity & Focus</span>
                  <span class="meter-val text-emerald-400" id="meter-snr-val" style="color: #10B981;">Clear & Sharp</span>
                </div>
                <div class="meter-track">
                  <div class="meter-fill meter-fill-green" id="meter-snr-fill" style="width: 95%;"></div>
                </div>
              </div>

              <div class="meter-row">
                <div class="meter-labels">
                  <span class="meter-name">Photo Resolution</span>
                  <span class="meter-val" id="meter-res-val">High Definition</span>
                </div>
                <div class="meter-track">
                  <div class="meter-fill" id="meter-res-fill" style="width: 100%;"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Auto-Detected Complexion Swatches Strip -->
          <div class="micro-samples-strip">
            <div class="micro-samples-title">Auto-Detected Complexion Swatches</div>
            <div class="micro-samples-grid">
              <div class="micro-sample-card">
                <div class="micro-sample-color" id="sample-color-1" style="background: #C68B59;"></div>
                <div class="micro-sample-name">Detected Skin Tone</div>
                <div class="micro-sample-hex" id="sample-hex-1">#C68B59</div>
              </div>
              <div class="micro-sample-card">
                <div class="micro-sample-color" id="sample-color-2" style="background: #BA8152;"></div>
                <div class="micro-sample-name">Upper Face</div>
                <div class="micro-sample-hex" id="sample-hex-2">#BA8152</div>
              </div>
              <div class="micro-sample-card">
                <div class="micro-sample-color" id="sample-color-3" style="background: #D39766;"></div>
                <div class="micro-sample-name">Cheek Tone</div>
                <div class="micro-sample-hex" id="sample-hex-3">#D39766</div>
              </div>
              <div class="micro-sample-card">
                <div class="micro-sample-color" id="sample-color-4" style="background: #BF8555;"></div>
                <div class="micro-sample-name">Lower Face</div>
                <div class="micro-sample-hex" id="sample-hex-4">#BF8555</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Styling Profile Selector -->
      <div class="gender-selector-wrapper">
        <span class="gender-selector-label">Style Recommendations For:</span>
        <div class="gender-options" id="upload-gender-options">
          <button type="button" class="gender-pill active" data-gender="auto">✨ Auto-Detect</button>
          <button type="button" class="gender-pill" data-gender="female">👗 Women's Style</button>
          <button type="button" class="gender-pill" data-gender="male">👔 Men's Style</button>
          <button type="button" class="gender-pill" data-gender="all">👥 All Styles</button>
        </div>
      </div>

      <!-- Primary Analyze CTA -->
      <div class="cta-container">
        <button id="analyze-btn" class="btn btn-primary btn-glow" disabled>
          <span class="material-symbols-outlined" style="font-size: 20px;">play_arrow</span>
          <span>Analyze Undertone & View Palette</span>
        </button>
      </div>
    </section>

    <!-- 6-Phase Glowing Pipeline Stepper -->
    <section class="processing-section hidden" id="processing-section">
      <div class="processing-card">
        <div class="processing-header">
          <div class="processing-title-group">
            <span class="material-symbols-outlined text-primary" style="font-size: 22px;">palette</span>
            <h3 class="processing-title">Analyzing Your Natural Colors...</h3>
          </div>
          <span class="pipeline-timer">Quick Analysis</span>
        </div>

        <div class="pipeline-stepper">
          <!-- Phase 1 -->
          <div class="step-item" id="step-1">
            <div class="step-meta">
              <span class="step-phase">STEP 01</span>
              <span class="material-symbols-outlined step-status-icon">check_circle</span>
            </div>
            <div class="step-label">Lighting Check</div>
            <div class="step-subtext">Daylight Verified</div>
          </div>

          <!-- Phase 2 -->
          <div class="step-item" id="step-2">
            <div class="step-meta">
              <span class="step-phase">STEP 02</span>
              <span class="material-symbols-outlined step-status-icon">check_circle</span>
            </div>
            <div class="step-label">Auto Skin Detection</div>
            <div class="step-subtext">Complexion Spotted</div>
          </div>

          <!-- Phase 3 -->
          <div class="step-item" id="step-3">
            <div class="step-meta">
              <span class="step-phase">STEP 03</span>
              <span class="material-symbols-outlined step-status-icon">check_circle</span>
            </div>
            <div class="step-label">Undertone Analysis</div>
            <div class="step-subtext">Warm vs. Cool</div>
          </div>

          <!-- Phase 4 -->
          <div class="step-item" id="step-4">
            <div class="step-meta">
              <span class="step-phase">STEP 04</span>
              <span class="material-symbols-outlined step-status-icon">check_circle</span>
            </div>
            <div class="step-label">Color Season Match</div>
            <div class="step-subtext">Seasonal Subtype</div>
          </div>

          <!-- Phase 5 -->
          <div class="step-item" id="step-5">
            <div class="step-meta">
              <span class="step-phase">STEP 05</span>
              <span class="material-symbols-outlined step-status-icon">refresh</span>
            </div>
            <div class="step-label">Outfit Color Curation</div>
            <div class="step-subtext">Flattering Shades</div>
          </div>

          <!-- Phase 6 -->
          <div class="step-item" id="step-6">
            <div class="step-meta">
              <span class="step-phase">STEP 06</span>
              <span class="material-symbols-outlined step-status-icon">verified</span>
            </div>
            <div class="step-label">Personal Style Guide</div>
            <div class="step-subtext">Ready to View</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Results Showcase Section -->
    <section class="results-section hidden" id="results-section">
      <!-- Auto-Detected Style Profile Banner -->
      <div class="gender-verdict-banner" id="gender-verdict-banner">
        <div class="gender-banner-left">
          <div class="gender-banner-icon" id="gender-banner-icon"></div>
          <div>
            <div class="gender-banner-title">
              <span id="gender-banner-title-text">Style Profile:</span>
              <strong id="gender-banner-label">All Styles</strong>
              <span class="gender-banner-badge" id="gender-banner-badge"> Verified</span>
            </div>
            <p class="gender-banner-desc" id="gender-banner-desc">
              Your color analysis is personalized for your natural skin undertone and flattering color harmony.
            </p>
          </div>
        </div>
        <div class="gender-banner-controls">
          <span class="gender-switch-label" id="gender-switch-label">Switch Style:</span>
          <div class="gender-options results-gender-options" id="results-gender-options">
            <button type="button" class="gender-pill active" data-gender="female">👗 Women's</button>
            <button type="button" class="gender-pill" data-gender="male">👔 Men's</button>
            <button type="button" class="gender-pill" data-gender="all">👥 All Styles</button>
          </div>
        </div>
      </div>

      <!-- Verdict & Visualizer Grid (Two Columns) -->
      <div class="verdict-grid" id="hud">
        <!-- Left: Seasonal Diagnosis Card -->
        <div class="card verdict-card" id="verdict-card">
          <!-- Seasonal Watermark -->
          <div class="season-watermark" id="season-watermark">AUTUMN</div>

          <div>
            <div class="verdict-header-row">
              <div>
                <span class="card-tag">Your Color Season</span>
                <div class="undertone-badge-wrapper">
                  <h2 class="undertone-badge" id="undertone-badge">WARM AUTUMN</h2>
                </div>
                <div class="verdict-subheadline" id="verdict-subheadline">Warm Earthy Harmony</div>
              </div>
              
              <div class="confidence-score-box">
                <div class="confidence-val" id="confidence-val">94.8%</div>
                <div class="confidence-label">Match Confidence</div>
              </div>
            </div>

            <p class="undertone-explanation" id="undertone-explanation">
              Your natural complexion has rich golden and warm undertones. Earthy colors, terracotta, warm olive, and gold will make your skin look vibrant and healthy.
            </p>

            <!-- Undertone Probability Matrix -->
            <div class="prob-matrix-box">
              <div class="prob-matrix-header">
                <span>Undertone Breakdown</span>
                <span>AI Color Model</span>
              </div>
              <div class="prob-bars-list" id="prob-breakdown">
                <div class="prob-bar-item">
                  <div class="prob-bar-info">
                    <span class="prob-bar-label">Warm (Golden & Peach Tones)</span>
                    <span class="prob-bar-pct">94.8%</span>
                  </div>
                  <div class="prob-track">
                    <div class="prob-fill-warm" style="width: 94.8%;"></div>
                  </div>
                </div>
                <div class="prob-bar-item">
                  <div class="prob-bar-info">
                    <span class="prob-bar-label">Neutral (Balanced Harmony)</span>
                    <span class="prob-bar-pct">4.2%</span>
                  </div>
                  <div class="prob-track">
                    <div class="prob-fill-neutral" style="width: 4.2%;"></div>
                  </div>
                </div>
                <div class="prob-bar-item">
                  <div class="prob-bar-info">
                    <span class="prob-bar-label">Cool (Rosy & Blue Tones)</span>
                    <span class="prob-bar-pct">1.0%</span>
                  </div>
                  <div class="prob-track">
                    <div class="prob-fill-cool" style="width: 1.0%;"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Metrics Row -->
          <div class="micro-metrics-row" id="key-factors">
            <div class="micro-metric-item">
              <div class="micro-metric-val">High</div>
              <div class="micro-metric-label">Golden Warmth</div>
            </div>
            <div class="micro-metric-item">
              <div class="micro-metric-val">Natural</div>
              <div class="micro-metric-label">Rosy Balance</div>
            </div>
            <div class="micro-metric-item">
              <div class="micro-metric-val">Clear</div>
              <div class="micro-metric-label">Depth Level</div>
            </div>
          </div>
        </div>

        <!-- Right: Detected Skin Complexion Card -->
        <div class="card visualizer-card">
          <div class="visualizer-container">
            <div>
              <span class="card-tag">Your Detected Complexion</span>
              <div class="face-canvas-box">
                <canvas id="face-canvas"></canvas>
                <div class="canvas-caption">Auto-Identified Complexion & Lighting Analysis</div>
              </div>
            </div>

            <!-- Representative Skin Swatch -->
            <div class="rep-swatch-box">
              <div class="rep-swatch" id="rep-swatch" style="background: #C68B59;">
                <span class="rep-swatch-tag">Color</span>
              </div>
              <div class="rep-info">
                <span class="rep-label">Your Detected Skin Tone</span>
                <div class="rep-hex" id="rep-hex">#C68B59 · Golden Olive</div>
                <div class="rep-phototype" id="rep-phototype">Medium Golden Complexion</div>
              </div>
            </div>

            <!-- Facial Area Colorimetry Breakdown -->
            <div class="results-areas-strip">
              <div class="results-areas-title">
                <span class="material-symbols-outlined" style="font-size: 14px;">pin_drop</span>
                <span>Analyzed Facial Dermal Regions</span>
              </div>
              <div class="results-areas-grid">
                <div class="results-area-item">
                  <div class="results-area-dot" id="res-area-dot-1" style="background: #C68B59;"></div>
                  <div class="results-area-info">
                    <span class="results-area-label">Core Dermis</span>
                    <span class="results-area-hex" id="res-area-hex-1">#C68B59</span>
                  </div>
                </div>
                <div class="results-area-item">
                  <div class="results-area-dot" id="res-area-dot-2" style="background: #BA8152;"></div>
                  <div class="results-area-info">
                    <span class="results-area-label">Upper Face</span>
                    <span class="results-area-hex" id="res-area-hex-2">#BA8152</span>
                  </div>
                </div>
                <div class="results-area-item">
                  <div class="results-area-dot" id="res-area-dot-3" style="background: #D39766;"></div>
                  <div class="results-area-info">
                    <span class="results-area-label">Cheek Tone</span>
                    <span class="results-area-hex" id="res-area-hex-3">#D39766</span>
                  </div>
                </div>
                <div class="results-area-item">
                  <div class="results-area-dot" id="res-area-dot-4" style="background: #BF8555;"></div>
                  <div class="results-area-info">
                    <span class="results-area-label">Lower Face</span>
                    <span class="results-area-hex" id="res-area-hex-4">#BF8555</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Optical Color Data Table -->
            <div class="color-metrics-table">
              <div class="metric-row">
                <span class="metric-name">Brightness Level (L*)</span>
                <span class="metric-val" id="metric-lab-l">61.4</span>
              </div>
              <div class="metric-row">
                <span class="metric-name">Rosy / Pink Balance (a*)</span>
                <span class="metric-val" id="metric-lab-a">+13.8</span>
              </div>
              <div class="metric-row">
                <span class="metric-name">Golden Warmth (b*)</span>
                <span class="metric-val highlight-metric" id="metric-lab-b">+21.2</span>
              </div>
              <div class="metric-row">
                <span class="metric-name">Complexion Tone Angle</span>
                <span class="metric-val" id="metric-ita">+34.8°</span>
              </div>
              <div class="metric-row">
                <span class="metric-name">Dominant Color Hue</span>
                <span class="metric-val" id="metric-hsv-h">28.4°</span>
              </div>
            </div>

            <div class="visualizer-footer">
              <span>Natural Daylight Standard</span>
              <span>Calibrated Color Harmony</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Signature Curated Palette (7 Master Swatches) -->
      <div class="card palette-showcase-card" id="harmony">
        <div class="palette-header">
          <div>
            <span class="card-tag">Your Color Palette</span>
            <h3 class="palette-title" id="palette-headline">Signature Master Color Swatches</h3>
            <p class="palette-desc" id="stylist-summary">
              Seven flattering shades chosen to harmonize with your natural skin undertone and complexion.
            </p>
            <div class="swatch-tap-hint">
              <span class="material-symbols-outlined" style="font-size: 14px;">content_copy</span>
              <span>Tap any swatch to copy HEX color code</span>
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
            <span>Contrast Level</span>
            <span class="material-symbols-outlined" style="font-size: 18px;">contrast</span>
          </div>
          <h4 class="optical-metric-title">Rich Contrast</h4>
          <p class="optical-metric-desc">
            Pair deeper primary colors with warm neutral highlights to frame your face naturally and cleanly.
          </p>
        </div>

        <div class="optical-metric-card">
          <div class="optical-metric-header">
            <span>Skin Radiance</span>
            <span class="material-symbols-outlined" style="font-size: 18px;">wb_twilight</span>
          </div>
          <h4 class="optical-metric-title">Brings Out Your Warmth</h4>
          <p class="optical-metric-desc">
            Warm earth tones reflect natural daylight onto your face, keeping your complexion looking fresh, bright, and healthy.
          </p>
        </div>

        <div class="optical-metric-card">
          <div class="optical-metric-header">
            <span>Style Recommendations</span>
            <span class="material-symbols-outlined" style="font-size: 18px;">diamond</span>
          </div>
          <h4 class="optical-metric-title">Warm & Earthy Tones</h4>
          <p class="optical-metric-desc">
            Harmonizes best with rich autumnal shades, terracotta, warm neutrals, and warm gold jewelry.
          </p>
        </div>
      </div>


      <!-- Recommendation Categories Tabs -->
      <div class="recommendations-container" id="curations">
        <div class="tab-nav">
          <button class="tab-btn active" data-tab="clothing">👔 Clothes & Outfits</button>
          <button class="tab-btn" data-tab="makeup" id="tab-btn-makeup">💄 Makeup & Lips</button>
          <button class="tab-btn" data-tab="accessories">💍 Jewelry & Metals</button>
          <button class="tab-btn" data-tab="neutrals">🎨 Everyday Neutrals</button>
          <button class="tab-btn tab-btn-avoid" data-tab="avoid">⛔ Colors to Avoid</button>
        </div>

        <div class="tab-content active" id="tab-clothing">
          <div class="rec-grid" id="rec-clothing-grid"></div>
        </div>

        <div class="tab-content" id="tab-makeup">
          <div class="makeup-guide-box" id="foundation-advice-box">
            <div class="guide-icon"></div>
            <div>
              <h4>Foundation & Complexion Tips</h4>
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
              <span>Try Another Photo</span>
            </div>
            <h3 class="another-analysis-title">Analyze Another Photo or Selfie</h3>
            <p class="another-analysis-desc">
              Upload a new photo or take a daylight selfie to test another outfit or lighting.
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
        <h3>Take a Live Selfie</h3>
        <button class="modal-close" id="camera-modal-close-btn">&times;</button>
      </div>
      <div class="camera-video-wrapper">
        <video id="camera-video" playsinline autoplay muted></video>
      </div>
      <div class="camera-controls">
        <button type="button" class="btn btn-outline" id="camera-flip-btn">
          <span class="material-symbols-outlined" style="font-size: 16px;">flip_camera_android</span>
          <span>Flip Camera</span>
        </button>
        <button type="button" class="btn btn-primary" id="camera-capture-btn">
          <span class="material-symbols-outlined" style="font-size: 16px;">photo_camera</span>
          <span>Capture Photo</span>
        </button>
      </div>
      <p class="camera-hint">Position your face in soft, natural daylight so your skin tone is clearly visible.</p>
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
      let currentGender = "auto";
      let userExplicitlyChoseGender = false;
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

      // --- Demo Sample Portrait Quick-Loaders ---
      async function loadSampleUrl(url) {{
        try {{
          const resp = await fetch(url);
          if (!resp.ok) return;
          const blob = await resp.blob();
          const filename = url.split("/").pop() || "sample.jpg";
          const file = new File([blob], filename, {{ type: blob.type || "image/jpeg" }});
          handleFile(file);
        }} catch (e) {{
          console.warn("Failed to load sample portrait:", e);
        }}
      }}

      document.querySelectorAll(".sample-chip-btn").forEach((btn) => {{
        btn.addEventListener("click", (e) => {{
          e.stopPropagation();
          const sampleUrl = btn.getAttribute("data-sample");
          if (sampleUrl) loadSampleUrl(sampleUrl);
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

      function rgbToHex(r, g, b) {{
        const clamp = (v) => Math.max(0, Math.min(255, Math.round(v)));
        return `#${{clamp(r).toString(16).padStart(2, '0')}}${{clamp(g).toString(16).padStart(2, '0')}}${{clamp(b).toString(16).padStart(2, '0')}}`.toUpperCase();
      }}

      function renderFaceBox(face, rollDeg = 0) {{
        // Kept for backward compatibility, box-face is hidden in auto-colour mode
        const el = document.getElementById("box-face");
        if (el) el.style.display = "none";
      }}

      // --- Inclusive Skin Filter across Fitzpatrick Types I to VI ---
      function isSkinPixel(r, g, b) {{
        if (r < 28 || g < 18 || b < 10) return false;
        const maxC = Math.max(r, g, b);
        const minC = Math.min(r, g, b);
        if (maxC - minC < 4) return false;
        if (r < g * 0.88 || r < b * 0.92) return false;

        const yP = 0.299 * r + 0.587 * g + 0.114 * b;
        if (yP < 18 || yP > 252) return false;

        const cr = 0.713 * (r - yP) + 128.0;
        const cb = 0.564 * (b - yP) + 128.0;
        if (cr < 122 || cr > 194 || cb < 64 || cb > 148 || (cr - cb) < 2) return false;

        const delta = maxC - minC;
        const sat = delta / maxC;
        let hue = 0;
        if (delta > 0) {{
          if (maxC === r) hue = ((g - b) / delta) % 6;
          else if (maxC === g) hue = (b - r) / delta + 2;
          else hue = (r - g) / delta + 4;
          hue = (hue * 60 + 360) % 360;
        }}
        return ((hue >= 0 && hue <= 58) || (hue >= 328 && hue <= 360));
      }}

      // --- Unified Anatomical Facial Dermis & Multi-Region Extractor ---
      function extractFacialDermisAndRegions(imgData, w, h) {{
        const candidateSkin = [];
        for (let y = 0; y < h; y += 2) {{
          for (let x = 0; x < w; x += 2) {{
            const idx = (y * w + x) * 4;
            const r = imgData[idx], g = imgData[idx + 1], b = imgData[idx + 2];
            if (isSkinPixel(r, g, b)) {{
              const yP = 0.299 * r + 0.587 * g + 0.114 * b;
              candidateSkin.push({{ r, g, b, lum: yP, x, y }});
            }}
          }}
        }}

        if (candidateSkin.length < 25) {{
          for (let y = Math.floor(h * 0.10); y < Math.floor(h * 0.85); y += 2) {{
            for (let x = Math.floor(w * 0.15); x < Math.floor(w * 0.85); x += 2) {{
              const idx = (y * w + x) * 4;
              const r = imgData[idx], g = imgData[idx + 1], b = imgData[idx + 2];
              if (r > 38 && g > 24 && b > 14 && r >= g && r >= b) {{
                candidateSkin.push({{ r, g, b, lum: 0.299 * r + 0.587 * g + 0.114 * b, x, y }});
              }}
            }}
          }}
        }}

        // Facial skin cluster (focus on head & face, top 80%)
        let faceSkin = candidateSkin.filter(p => p.y < h * 0.80);
        if (faceSkin.length < 20) faceSkin = candidateSkin;

        const xs = faceSkin.map(p => p.x).sort((a, b) => a - b);
        const ys = faceSkin.map(p => p.y).sort((a, b) => a - b);

        const fLeft = xs.length > 0 ? xs[Math.floor(xs.length * 0.08)] : Math.floor(w * 0.2);
        const fRight = xs.length > 0 ? xs[Math.floor(xs.length * 0.92)] : Math.floor(w * 0.8);
        const fTop = ys.length > 0 ? ys[Math.floor(ys.length * 0.04)] : Math.floor(h * 0.1);
        const fBottom = ys.length > 0 ? ys[Math.floor(ys.length * 0.92)] : Math.floor(h * 0.75);

        let fWidth = Math.max(50, fRight - fLeft);
        let fHeight = Math.max(65, fBottom - fTop);
        if (fHeight < fWidth * 1.05) fHeight = Math.round(fWidth * 1.25);
        if (fHeight > fWidth * 1.55) fHeight = Math.round(fWidth * 1.40);
        fHeight = Math.min(fHeight, h - fTop - 2);

        const cx = Math.round(fLeft + fWidth * 0.5);
        const cy = Math.round(fTop + fHeight * 0.48);

        // Circular patch sampling with outlier trimming
        const samplePatch = (targetX, targetY, radius, defR, defG, defB) => {{
          let sR = 0, sG = 0, sB = 0, count = 0;
          const patchPixels = [];
          for (let dy = -radius; dy <= radius; dy += 2) {{
            for (let dx = -radius; dx <= radius; dx += 2) {{
              const px = targetX + dx, py = targetY + dy;
              if (dx * dx + dy * dy <= radius * radius && px >= 0 && px < w && py >= 0 && py < h) {{
                const idx = (py * w + px) * 4;
                const r = imgData[idx], g = imgData[idx + 1], b = imgData[idx + 2];
                const lum = 0.299 * r + 0.587 * g + 0.114 * b;
                if (lum >= 30 && lum <= 248 && r >= g * 0.82 && r >= b * 0.82) {{
                  patchPixels.push({{ r, g, b, lum }});
                }}
              }}
            }}
          }}
          if (patchPixels.length > 4) {{
            patchPixels.sort((a, b) => a.lum - b.lum);
            const lCut = Math.floor(patchPixels.length * 0.15);
            const hCut = Math.max(lCut + 1, Math.floor(patchPixels.length * 0.85));
            for (let i = lCut; i < hCut; i++) {{
              sR += patchPixels[i].r;
              sG += patchPixels[i].g;
              sB += patchPixels[i].b;
              count++;
            }}
          }}
          const finalR = count > 0 ? Math.round(sR / count) : defR;
          const finalG = count > 0 ? Math.round(sG / count) : defG;
          const finalB = count > 0 ? Math.round(sB / count) : defB;
          return {{
            r: finalR, g: finalG, b: finalB,
            hex: rgbToHex(finalR, finalG, finalB),
            x: targetX, y: targetY,
            pctX: (targetX / w) * 100,
            pctY: (targetY / h) * 100,
            count
          }};
        }};

        // Baseline color
        candidateSkin.sort((a, b) => a.lum - b.lum);
        const gLow = Math.floor(candidateSkin.length * 0.15);
        const gHigh = Math.max(gLow + 1, Math.floor(candidateSkin.length * 0.85));
        let baseR = 0, baseG = 0, baseB = 0, baseCount = 0;
        for (let i = gLow; i < gHigh; i++) {{
          baseR += candidateSkin[i].r; baseG += candidateSkin[i].g; baseB += candidateSkin[i].b; baseCount++;
        }}
        const bR = baseCount > 0 ? Math.round(baseR / baseCount) : 190;
        const bG = baseCount > 0 ? Math.round(baseG / baseCount) : 140;
        const bB = baseCount > 0 ? Math.round(baseB / baseCount) : 105;

        const radArea = Math.max(5, Math.round(fWidth * 0.065));

        // 1. Upper Face (Forehead)
        const frnX = cx;
        const frnY = Math.max(4, Math.round(fTop + fHeight * 0.18));
        const forehead = samplePatch(frnX, frnY, radArea, bR, bG, bB);

        // 2. Cheek Tone (Bilateral Average)
        const lChkX = Math.round(fLeft + fWidth * 0.22);
        const rChkX = Math.round(fLeft + fWidth * 0.78);
        const chkY = Math.round(fTop + fHeight * 0.52);
        const leftCheek = samplePatch(lChkX, chkY, radArea, bR, bG, bB);
        const rightCheek = samplePatch(rChkX, chkY, radArea, bR, bG, bB);
        const cheekR = Math.round((leftCheek.r + rightCheek.r) / 2);
        const cheekG = Math.round((leftCheek.g + rightCheek.g) / 2);
        const cheekB = Math.round((leftCheek.b + rightCheek.b) / 2);
        const cheek = {{
          r: cheekR, g: cheekG, b: cheekB,
          hex: rgbToHex(cheekR, cheekG, cheekB),
          x: Math.round(fLeft + fWidth * 0.24), y: chkY,
          pctX: ((fLeft + fWidth * 0.24) / w) * 100,
          pctY: (chkY / h) * 100,
          left: leftCheek, right: rightCheek
        }};

        // 3. Lower Face (Chin)
        const chinX = cx;
        const chinY = Math.min(h - 4, Math.round(fTop + fHeight * 0.84));
        const chin = samplePatch(chinX, chinY, radArea, bR, bG, bB);

        // 4. Overall Detected Core Dermis
        const coreX = cx;
        const coreY = Math.round(fTop + fHeight * 0.44);
        const coreSample = samplePatch(coreX, coreY, Math.round(radArea * 1.2), bR, bG, bB);
        const overallR = Math.round(coreSample.r * 0.6 + bR * 0.4);
        const overallG = Math.round(coreSample.g * 0.6 + bG * 0.4);
        const overallB = Math.round(coreSample.b * 0.6 + bB * 0.4);
        const overall = {{
          r: overallR, g: overallG, b: overallB,
          hex: rgbToHex(overallR, overallG, overallB),
          x: coreX, y: coreY,
          pctX: (coreX / w) * 100,
          pctY: (coreY / h) * 100
        }};

        return {{
          candidateSkin,
          faceBox: {{ x: fLeft, y: fTop, width: fWidth, height: fHeight, cx, cy }},
          areas: {{
            overall,
            forehead,
            cheek,
            chin
          }}
        }};
      }}

      // --- Auto Colour Detection & Lighting Quality Sensor ---
      function checkImageQualityAndAutoColor(img) {{
        const statusEl = document.getElementById("mesh-status-text");
        const lightingPill = document.getElementById("lighting-status-pill");
        const hudLightingPill = document.getElementById("hud-lighting-pill");
        const dockDot = document.getElementById("dock-dot");
        const autoBadgeTitle = document.getElementById("auto-color-badge-title");
        const autoBadgeHex = document.getElementById("face-box-hex");
        const autoBadgeTag = document.getElementById("face-box-sublabel");
        const autoDot = document.getElementById("face-box-color-dot");

        if (statusEl) statusEl.textContent = "Scanning photo lighting and facial regions...";

        const origW = img.naturalWidth || img.width || 320;
        const origH = img.naturalHeight || img.height || 400;

        // Fast sampling canvas
        const sampleW = 280;
        const sampleH = Math.max(140, Math.round((origH / origW) * 280));
        const canvas = document.createElement("canvas");
        canvas.width = sampleW;
        canvas.height = sampleH;
        const ctx = canvas.getContext("2d", {{ willReadFrequently: true }});
        ctx.drawImage(img, 0, 0, sampleW, sampleH);
        const imgData = ctx.getImageData(0, 0, sampleW, sampleH).data;

        // 1. Lighting, Exposure & Clarity metrics
        let totalLum = 0;
        let darkCount = 0;
        let brightCount = 0;
        const totalPixels = sampleW * sampleH;
        const lums = [];

        for (let i = 0; i < imgData.length; i += 4) {{
          const r = imgData[i], g = imgData[i + 1], b = imgData[i + 2];
          const lum = 0.299 * r + 0.587 * g + 0.114 * b;
          totalLum += lum;
          if (lum < 20) darkCount++;
          if (lum > 244) brightCount++;
          if (i % 16 === 0) lums.push(lum);
        }}

        const meanBrightness = totalLum / totalPixels;
        const darkRatio = darkCount / totalPixels;
        const brightRatio = brightCount / totalPixels;

        let lumVarSum = 0;
        for (let l of lums) {{
          const d = l - meanBrightness;
          lumVarSum += d * d;
        }}
        const contrastStd = Math.sqrt(lumVarSum / lums.length);

        // Focus / blur approximation
        let edgeDiffSum = 0;
        let edgeCount = 0;
        for (let y = 1; y < sampleH - 1; y += 3) {{
          for (let x = 1; x < sampleW - 1; x += 3) {{
            const idx = (y * sampleW + x) * 4;
            const c = 0.299 * imgData[idx] + 0.587 * imgData[idx + 1] + 0.114 * imgData[idx + 2];
            const r = 0.299 * imgData[idx + 4] + 0.587 * imgData[idx + 5] + 0.114 * imgData[idx + 6];
            const down = 0.299 * imgData[idx + sampleW * 4] + 0.587 * imgData[idx + sampleW * 4 + 1] + 0.114 * imgData[idx + sampleW * 4 + 2];
            const diff = Math.abs(c - r) + Math.abs(c - down);
            edgeDiffSum += diff * diff;
            edgeCount++;
          }}
        }}
        const blurMetric = edgeCount > 0 ? (edgeDiffSum / edgeCount) : 100;

        // Extract facial dermis and real anatomical regions
        const regionRes = extractFacialDermisAndRegions(imgData, sampleW, sampleH);
        const candidateSkin = regionRes.candidateSkin;
        const areas = regionRes.areas;

        // 3. Check for lighting and clarity issues
        let errorMsg = null;
        if (origW < 140 || origH < 140) {{
          errorMsg = "The image is not clear: Photo resolution is too low. Please upload a higher resolution photo.";
        }} else if (meanBrightness < 38 || darkRatio > 0.42) {{
          errorMsg = "The image is not clear and does not have proper lighting: The photo is too dark. Please take your photo in bright, natural daylight so your skin tone can be identified accurately.";
        }} else if (meanBrightness > 230 || brightRatio > 0.40) {{
          errorMsg = "The image is not clear: Harsh glare or overexposure detected. Please avoid strong camera flash or harsh direct sunlight.";
        }} else if (contrastStd < 14) {{
          errorMsg = "The image is not clear: The photo lacks contrast or has heavy uneven shadows. Please use clear, balanced lighting.";
        }} else if (blurMetric < 12) {{
          errorMsg = "The image is not clear: The photo appears blurry or out of focus. Please ensure the camera is steady and clear.";
        }} else if (candidateSkin.length < 25) {{
          errorMsg = "Could not identify your natural skin colour. The image is not clear or does not have proper lighting. Please upload a clear photo with visible skin complexion in natural lighting.";
        }}

        if (errorMsg) {{
          showError(errorMsg);
          if (qualityBar) qualityBar.classList.remove("hidden");
          if (qualityMeter) {{
            qualityMeter.style.width = "30%";
            qualityMeter.style.background = "#EF4444";
          }}
          if (qualityStatus) {{
            qualityStatus.textContent = "Lighting / Clarity Issue";
            qualityStatus.className = "quality-status Poor";
          }}
          if (qualityDetails) qualityDetails.textContent = errorMsg;

          if (statusEl) statusEl.textContent = "⚠️ Image not clear or poor lighting • Skin colour not spotted";
          if (lightingPill) lightingPill.textContent = "Lighting: Needs Improvement";
          if (hudLightingPill) hudLightingPill.textContent = "⚠️ POOR LIGHTING";
          if (dockDot) dockDot.style.background = "#EF4444";

          if (autoBadgeTitle) autoBadgeTitle.textContent = "SKIN COLOUR NOT SPOTTED";
          if (autoBadgeHex) autoBadgeHex.textContent = "UNCLEAR";
          if (autoBadgeTag) {{
            autoBadgeTag.textContent = "CHECK LIGHTING";
            autoBadgeTag.className = "auto-color-status-tag error";
          }}
          if (autoDot) autoDot.style.backgroundColor = "#64748B";

          analyzeBtn.disabled = true;
          return false;
        }}

        // Success! Dermis color and areas spotted accurately
        hideError();
        const spottedHex = areas.overall.hex;

        // Update Quality Bar: Optimal
        if (qualityBar) qualityBar.classList.remove("hidden");
        if (qualityMeter) {{
          qualityMeter.style.width = "95%";
          qualityMeter.style.background = "#10B981";
        }}
        if (qualityStatus) {{
          qualityStatus.textContent = "Good Lighting & Clear Photo";
          qualityStatus.className = "quality-status Good";
        }}
        if (qualityDetails) {{
          qualityDetails.textContent = `Natural skin tone spotted (${{spottedHex}}) • Lighting is balanced and clear. Ready to proceed!`;
        }}

        // Update HUD & Auto Color Badge
        if (statusEl) statusEl.textContent = `✨ Natural skin colour spotted (${{spottedHex}}) • Lighting is clear`;
        if (lightingPill) lightingPill.textContent = "Lighting: Clear & Balanced";
        if (hudLightingPill) hudLightingPill.textContent = "💡 GOOD LIGHTING";
        if (dockDot) dockDot.style.background = "#10B981";

        if (autoBadgeTitle) autoBadgeTitle.textContent = "SKIN COLOUR SPOTTED";
        if (autoBadgeHex) autoBadgeHex.textContent = spottedHex;
        if (autoBadgeTag) {{
          autoBadgeTag.textContent = "READY TO PROCEED";
          autoBadgeTag.className = "auto-color-status-tag success";
        }}
        if (autoDot) autoDot.style.backgroundColor = spottedHex;

        // Update Telemetry Swatches with REAL anatomical face regions
        const updateSwatch = (colorId, hexId, hex) => {{
          const c = document.getElementById(colorId);
          const h = document.getElementById(hexId);
          if (c) c.style.backgroundColor = hex;
          if (h) h.textContent = hex;
        }};
        updateSwatch("sample-color-1", "sample-hex-1", areas.overall.hex);
        updateSwatch("sample-color-2", "sample-hex-2", areas.forehead.hex);
        updateSwatch("sample-color-3", "sample-hex-3", areas.cheek.hex);
        updateSwatch("sample-color-4", "sample-hex-4", areas.chin.hex);

        // Spotted the colour - proceed!
        analyzeBtn.disabled = false;
        return true;
      }}

      function loadImageFromDataUrl(dataUrl) {{
        currentDataUrl = dataUrl;
        const img = new Image();
        img.onload = () => {{
          currentImageBitmap = img;
          previewImg.src = dataUrl;
          uploadPrompt.classList.add("hidden");
          previewBox.classList.remove("hidden");
          analyzeBtn.disabled = true;
          hideError();
          // Check lighting, clarity, and automatically spot skin colour
          checkImageQualityAndAutoColor(img);
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
        previewBox.classList.remove("hidden");
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

        // Multi-Region Anatomical Skin Extraction
        const regionData = extractFacialDermisAndRegions(imgData, w, h);
        const faceBox = regionData.faceBox;
        const areas = regionData.areas;
        const fLeft = faceBox.x;
        const fTop = faceBox.y;
        const fWidth = faceBox.width;
        const fHeight = faceBox.height;
        const fRight = fLeft + fWidth;
        const fBottom = fTop + fHeight;
        const headCenterX = faceBox.cx;
        const headCenterY = faceBox.cy;

        const mainFaceHex = areas.overall.hex;
        const foreheadHex = areas.forehead.hex;
        const cheekHex = areas.cheek.hex;
        const chinHex = areas.chin.hex;
        const meanR = areas.overall.r;
        const meanG = areas.overall.g;
        const meanB = areas.overall.b;

        const updateMicroSwatch = (idColor, idHex, hex) => {{
          const cEl = document.getElementById(idColor);
          const hEl = document.getElementById(idHex);
          if (cEl) cEl.style.background = hex;
          if (hEl) hEl.textContent = hex;
        }};
        updateMicroSwatch("sample-color-1", "sample-hex-1", mainFaceHex);
        updateMicroSwatch("sample-color-2", "sample-hex-2", foreheadHex);
        updateMicroSwatch("sample-color-3", "sample-hex-3", cheekHex);
        updateMicroSwatch("sample-color-4", "sample-hex-4", chinHex);

        const faceBoxDot = document.getElementById("face-box-color-dot");
        const faceBoxHex = document.getElementById("face-box-hex");
        if (faceBoxDot) faceBoxDot.style.backgroundColor = mainFaceHex;
        if (faceBoxHex) faceBoxHex.textContent = mainFaceHex;

        // Image Atmosphere Sampling
        let bgR = 0, bgG = 0, bgB = 0, bgCount = 0;
        for (let x = 0; x < w; x += 4) {{
          const idxTop = x * 4;
          bgR += imgData[idxTop]; bgG += imgData[idxTop + 1]; bgB += imgData[idxTop + 2];
          bgCount++;
        }}
        const bgHex = rgbToHex(bgR / bgCount, bgG / bgCount, bgB / bgCount);

        let outR = 0, outG = 0, outB = 0, outCount = 0;
        for (let y = Math.floor(h * 0.78); y < h; y += 4) {{
          for (let x = Math.floor(w * 0.25); x < Math.floor(w * 0.75); x += 4) {{
            const idx = (y * w + x) * 4;
            outR += imgData[idx]; outG += imgData[idx + 1]; outB += imgData[idx + 2];
            outCount++;
          }}
        }}
        const outHex = outCount > 0 ? rgbToHex(outR / outCount, outG / outCount, outB / outCount) : "#1E293B";

        // Multi-Factor Balanced Gender Classification
        let scoreMale = 0.0;
        let scoreFemale = 0.0;

        // 1. Mandibular Jaw-to-Cheek Width (Bigonial vs Bizygomatic)
        const jawY = Math.min(h - 1, Math.floor(fTop + fHeight * 0.78));
        const cheekY = Math.min(h - 1, Math.floor(fTop + fHeight * 0.50));
        let jawLeft = headCenterX, jawRight = headCenterX;
        let cheekLeft = headCenterX, cheekRight = headCenterX;
        for (let x = 0; x < w; x += 2) {{
          const idxJ = (jawY * w + x) * 4;
          if (isSkinPixel(imgData[idxJ], imgData[idxJ + 1], imgData[idxJ + 2])) {{
            if (x < jawLeft) jawLeft = x;
            if (x > jawRight) jawRight = x;
          }}
          const idxC = (cheekY * w + x) * 4;
          if (isSkinPixel(imgData[idxC], imgData[idxC + 1], imgData[idxC + 2])) {{
            if (x < cheekLeft) cheekLeft = x;
            if (x > cheekRight) cheekRight = x;
          }}
        }}
        const jawSpan = Math.max(20, jawRight - jawLeft);
        const cheekSpan = Math.max(30, cheekRight - cheekLeft);
        const jawRatio = jawSpan / cheekSpan;

        if (jawRatio > 0.80) {{
          scoreMale += Math.min(2.4, (jawRatio - 0.80) * 8.0 + 0.6);
        }} else if (jawRatio < 0.73) {{
          scoreFemale += Math.min(2.4, (0.73 - jawRatio) * 8.0 + 0.6);
        }}

        // 2. Craniofacial Aspect Ratio
        const faceAspect = fWidth / Math.max(fHeight, 1);
        if (faceAspect > 0.82) {{
          scoreMale += Math.min(1.8, (faceAspect - 0.82) * 6.0 + 0.5);
        }} else if (faceAspect < 0.74) {{
          scoreFemale += Math.min(1.8, (0.74 - faceAspect) * 6.0 + 0.5);
        }}

        // 3. Eyebrow Orbital Arch & Density
        const browY1 = Math.floor(fTop + fHeight * 0.20);
        const browY2 = Math.floor(fTop + fHeight * 0.35);
        const browX1 = Math.floor(headCenterX - fWidth * 0.32);
        const browX2 = Math.floor(headCenterX + fWidth * 0.32);
        let darkBrowPixels = 0, browSumY = 0, totalBrowPixels = 0;
        const meanChkLum = 0.299 * areas.cheek.r + 0.587 * areas.cheek.g + 0.114 * areas.cheek.b;

        for (let y = browY1; y < browY2; y += 2) {{
          for (let x = browX1; x < browX2; x += 2) {{
            if (x >= 0 && x < w && y >= 0 && y < h) {{
              const idx = (y * w + x) * 4;
              const l = 0.299 * imgData[idx] + 0.587 * imgData[idx + 1] + 0.114 * imgData[idx + 2];
              totalBrowPixels++;
              if (l < meanChkLum * 0.62) {{
                darkBrowPixels++;
                browSumY += (y - browY1);
              }}
            }}
          }}
        }}
        if (darkBrowPixels > 6 && totalBrowPixels > 10) {{
          const browRelY = (browSumY / darkBrowPixels) / Math.max(1, browY2 - browY1);
          if (browRelY < 0.44) scoreFemale += 1.3;
          else if (browRelY > 0.56) scoreMale += 1.3;
        }}

        // 4. Lip Mucosa Volume & Relative Chromatic Contrast
        const lipY1 = Math.floor(fTop + fHeight * 0.65);
        const lipY2 = Math.floor(fTop + fHeight * 0.80);
        const lipX1 = Math.floor(headCenterX - fWidth * 0.22);
        const lipX2 = Math.floor(headCenterX + fWidth * 0.22);
        const mouthPixels = [];
        for (let y = lipY1; y < lipY2; y += 2) {{
          for (let x = lipX1; x < lipX2; x += 2) {{
            if (x >= 0 && x < w && y >= 0 && y < h) {{
              const idx = (y * w + x) * 4;
              const r = imgData[idx], g = imgData[idx + 1], b = imgData[idx + 2];
              const redScore = r / Math.max(1, (g + b) / 2);
              mouthPixels.push({{ r, g, b, redScore, y }});
            }}
          }}
        }}
        mouthPixels.sort((a, b) => b.redScore - a.redScore);
        const topLipCut = Math.max(4, Math.floor(mouthPixels.length * 0.28));
        let sumLipR = 0, sumLipG = 0, sumLipB = 0;
        let lipMinY = h, lipMaxY = 0;
        for (let i = 0; i < topLipCut; i++) {{
          sumLipR += mouthPixels[i].r;
          sumLipG += mouthPixels[i].g;
          sumLipB += mouthPixels[i].b;
          if (mouthPixels[i].y < lipMinY) lipMinY = mouthPixels[i].y;
          if (mouthPixels[i].y > lipMaxY) lipMaxY = mouthPixels[i].y;
        }}
        const mLipR = topLipCut > 0 ? sumLipR / topLipCut : 150;
        const mLipG = topLipCut > 0 ? sumLipG / topLipCut : 100;
        const mLipB = topLipCut > 0 ? sumLipB / topLipCut : 95;
        const lipRedRatio = mLipR / Math.max(1, (mLipG + mLipB) / 2);
        const chkRedRatio = areas.cheek.r / Math.max(1, (areas.cheek.g + areas.cheek.b) / 2);
        const lipContrast = lipRedRatio - chkRedRatio;
        const lipThickness = (lipMaxY - lipMinY) / Math.max(1, fHeight);

        if (lipContrast > 0.09 && lipThickness > 0.05) {{
          scoreFemale += Math.min(2.5, (lipContrast - 0.09) * 12.0 + (lipThickness - 0.05) * 14.0 + 0.8);
        }} else if (lipContrast < 0.04) {{
          scoreMale += Math.min(2.0, (0.04 - lipContrast) * 15.0 + 0.6);
        }}

        // 5. Mandibular Follicular Texture & Micro-Variance (Stubble Detection)
        let chinVar = 0, chkVar = 0, chinSampleCount = 0, chkSampleCount = 0;
        const radV = Math.floor(fWidth * 0.08);
        for (let dy = -radV; dy < radV; dy += 2) {{
          for (let dx = -radV; dx < radV; dx += 2) {{
            const cX = headCenterX + dx, cY = areas.chin.y + dy;
            if (cX >= 1 && cX < w - 1 && cY >= 1 && cY < h - 1) {{
              const iC = (cY * w + cX) * 4;
              const iR = (cY * w + cX + 1) * 4;
              const lumC = 0.299 * imgData[iC] + 0.587 * imgData[iC + 1] + 0.114 * imgData[iC + 2];
              const lumR = 0.299 * imgData[iR] + 0.587 * imgData[iR + 1] + 0.114 * imgData[iR + 2];
              chinVar += Math.abs(lumC - lumR);
              chinSampleCount++;
            }}
            const kX = areas.cheek.x + dx, kY = areas.cheek.y + dy;
            if (kX >= 1 && kX < w - 1 && kY >= 1 && kY < h - 1) {{
              const iC = (kY * w + kX) * 4;
              const iR = (kY * w + kX + 1) * 4;
              const lumC = 0.299 * imgData[iC] + 0.587 * imgData[iC + 1] + 0.114 * imgData[iC + 2];
              const lumR = 0.299 * imgData[iR] + 0.587 * imgData[iR + 1] + 0.114 * imgData[iR + 2];
              chkVar += Math.abs(lumC - lumR);
              chkSampleCount++;
            }}
          }}
        }}
        const meanChinGrad = chinSampleCount > 0 ? chinVar / chinSampleCount : 5;
        const meanChkGrad = chkSampleCount > 0 ? chkVar / chkSampleCount : 5;
        const textureRatio = meanChinGrad / Math.max(1, meanChkGrad);

        if (textureRatio > 1.32) {{
          scoreMale += Math.min(2.5, (textureRatio - 1.32) * 3.5 + 0.8);
        }} else if (textureRatio < 1.05) {{
          scoreFemale += Math.min(1.5, (1.05 - textureRatio) * 4.0 + 0.5);
        }}

        // 6. Lateral Hair Volume framing neck & shoulders
        const sideH1 = Math.floor(fTop + fHeight * 0.38);
        const sideH2 = Math.min(h - 1, Math.floor(fTop + fHeight * 1.15));
        const lSideX1 = Math.max(0, Math.floor(fLeft - fWidth * 0.28));
        const lSideX2 = Math.max(0, Math.floor(fLeft - 4));
        const rSideX1 = Math.min(w - 1, Math.floor(fRight + 4));
        const rSideX2 = Math.min(w - 1, Math.floor(fRight + fWidth * 0.28));
        let hairPixels = 0, totalSide = 0;
        const checkHairBand = (x1, x2) => {{
          for (let y = sideH1; y < sideH2; y += 3) {{
            for (let x = x1; x < x2; x += 3) {{
              if (x >= 0 && x < w && y >= 0 && y < h) {{
                const idx = (y * w + x) * 4;
                const r = imgData[idx], g = imgData[idx + 1], b = imgData[idx + 2];
                const lum = 0.299 * r + 0.587 * g + 0.114 * b;
                totalSide++;
                if (lum < 85 || (r > 65 && g > 35 && b < 45 && r > g * 1.25) || (Math.abs(lum - meanChkLum) > 35 && !isSkinPixel(r, g, b))) {{
                  hairPixels++;
                }}
              }}
            }}
          }}
        }};
        checkHairBand(lSideX1, lSideX2);
        checkHairBand(rSideX1, rSideX2);
        const hairRatio = totalSide > 20 ? hairPixels / totalSide : 0;
        if (hairRatio > 0.25) {{
          scoreFemale += Math.min(2.0, (hairRatio - 0.25) * 5.0 + 0.7);
        }} else if (hairRatio < 0.08 && totalSide > 20) {{
          scoreMale += 0.8;
        }}

        // Bayesian Sigmoid Calibration
        const scoreDiff = scoreFemale - scoreMale;
        const pFemale = 1.0 / (1.0 + Math.exp(-scoreDiff * 0.90));
        const pMale = 1.0 - pFemale;
        const detectedGender = pFemale >= 0.50 ? "Female" : "Male";
        const primaryProb = Math.max(pFemale, pMale);
        const genderConfidence = Math.min(98, Math.max(76, Math.round(primaryProb * 100)));

        console.log("[OTTERLOOK GENDER TELEMETRY]", {{
          scoreMale: scoreMale.toFixed(2), scoreFemale: scoreFemale.toFixed(2),
          pFemale: (pFemale * 100).toFixed(1) + "%", pMale: (pMale * 100).toFixed(1) + "%",
          jawRatio: jawRatio.toFixed(2), lipContrast: lipContrast.toFixed(3),
          textureRatio: textureRatio.toFixed(2), detectedGender, confidence: genderConfidence
        }});

        // CIELAB Color Conversion on Core Dermis
        const lab = rgbToLab(meanR, meanG, meanB);
        const hsv = rgbToHsv(meanR, meanG, meanB);
        const ita = Math.atan2((lab.L - 50.0), lab.b) * (180.0 / Math.PI);
        const repHex = rgbToHex(meanR, meanG, meanB);

        // Scientific Chromatic Metrics
        const labHueDeg = (Math.atan2(lab.b, lab.a) * (180.0 / Math.PI) + 360.0) % 360.0;
        const baRatio = lab.b / Math.max(0.5, lab.a);
        const relRB = (meanR - meanB) / Math.max(1.0, meanR + meanG + meanB);
        const grRatio = meanG / Math.max(1.0, meanR);

        // Calibrated Dermatological Undertone Probabilities
        let warmScore = 0.0, coolScore = 0.0, neutralScore = 0.0;

        // 1. Primary Hue Angle & baRatio
        if (baRatio >= 1.22 || labHueDeg >= 53.5) {{
          const delta = Math.min(1.0, Math.max(0, (baRatio - 1.22) / 0.30));
          warmScore += 0.55 + delta * 0.35;
          neutralScore += 0.25 * (1.0 - delta);
          coolScore += 0.05;
        }} else if (baRatio <= 1.02 || labHueDeg <= 46.5) {{
          const delta = Math.min(1.0, Math.max(0, (1.02 - baRatio) / 0.25));
          coolScore += 0.55 + delta * 0.35;
          neutralScore += 0.25 * (1.0 - delta);
          warmScore += 0.05;
        }} else {{
          const t = (baRatio - 1.02) / (1.22 - 1.02);
          neutralScore += 0.65;
          warmScore += t * 0.30;
          coolScore += (1.0 - t) * 0.30;
        }}

        // 2. Subsurface Scattering Vector
        if (relRB >= 0.22) warmScore += 0.25;
        else if (relRB <= 0.13) coolScore += 0.25;
        else neutralScore += 0.25;

        // 3. Olive Melanin Compensation
        const isOlive = (grRatio >= 0.76 && lab.b >= 10.0 && lab.b <= 22.0 && lab.L >= 38.0 && lab.L <= 68.0);
        if (isOlive) {{
          neutralScore += 0.35;
          if (baRatio > 1.12) warmScore += 0.20;
          else coolScore += 0.20;
        }}

        // 4. HSV Hue alignment
        if (hsv.h >= 24 && hsv.h <= 45) warmScore += 0.20;
        else if (hsv.h >= 14 && hsv.h < 24) neutralScore += 0.20;
        else if (hsv.h < 14 || hsv.h > 330) coolScore += 0.20;
        else neutralScore += 0.15;

        const totalScore = warmScore + coolScore + neutralScore;
        const pWarm = warmScore / totalScore;
        const pCool = coolScore / totalScore;
        const pNeutral = neutralScore / totalScore;

        let undertone = "Warm";
        let conf = pWarm;
        if (pCool > pWarm && pCool > pNeutral) {{ undertone = "Cool"; conf = pCool; }}
        else if (pNeutral > pWarm && pNeutral > pCool) {{ undertone = "Neutral"; conf = pNeutral; }}

        let phototype = "Type III — Light-Medium / Golden Sand";
        if (lab.L >= 68.0) phototype = "Type I/II — Fair / Ivory Porcelain";
        else if (lab.L >= 58.0) phototype = isOlive ? "Type III — Golden Olive Mediterranean" : "Type III — Light-Medium / Golden Sand";
        else if (lab.L >= 46.0) phototype = isOlive ? "Type IV — Warm Olive / Honey" : "Type IV — Amber Caramel Melanin";
        else if (lab.L >= 34.0) phototype = "Type V — Deep Bronze / Chestnut";
        else phototype = "Type VI — Deep Melanin / Espresso";

        const explanation = undertone === "Warm"
          ? (isOlive
              ? `Your complexion exhibits a radiant warm-olive signature with golden carotenoid resonance (b* +${{lab.b.toFixed(1)}}) balanced by olive undertones. Earthy terracotta, burnished brass, moss, and warm neutrals illuminate your natural skin depth.`
              : `Your dermal chromatic signature is defined by rich carotenoid undertones paired with golden-yellow spectral resonance (b*/a* = ${{baRatio.toFixed(2)}}). Saturated warm bases, camel, terracotta, and lustrous gold jewelry command natural visual harmony.`)
          : undertone === "Cool"
          ? `Your complexion features cool subcutaneous hemoglobin undertones with low yellow resonance (h° ${{labHueDeg.toFixed(1)}}°). Jewel tones, crisp obsidian black, emerald, royal cobalt, and icy platinum shades provide radiant, flattering definition.`
          : `Your skin displays an exceptional harmonic equilibrium between warm carotenoid and cool hemoglobin pigments (b*/a* = ${{baRatio.toFixed(2)}}). You possess universal versatility across both rich earthy tones and crisp jewel palettes.`;

        return {{
          undertone: {{
            label: undertone,
            confidence_percentage: Math.min(98, Math.max(84, Math.round(conf * 100))),
            probabilities: {{ Warm: pWarm, Neutral: pNeutral, Cool: pCool }},
            explanation,
            key_factors: [
              `CIELAB Chromatic Ratio b*/a* = ${{baRatio.toFixed(2)}} (${{undertone}} Chromatic Axis)`,
              `Color Hue Angle h_ab = ${{labHueDeg.toFixed(1)}}° (${{undertone === 'Warm' ? 'Golden Spectrum' : undertone === 'Cool' ? 'Rosy Spectrum' : 'Balanced Spectrum'}})`,
              `ITA° Typology Angle = ${{ita >= 0 ? '+' : ''}}${{ita.toFixed(1)}}° (${{phototype.split('—')[1] || phototype}})`,
              `Photometric Luminance L* = ${{lab.L.toFixed(1)}} (Calibrated Daylight Standard)`
            ]
          }},
          skin_analysis: {{
            metrics: {{
              representative_hex: repHex,
              phototype_estimate: phototype,
              cielab: {{ L: lab.L.toFixed(1), a: lab.a.toFixed(1), b: lab.b.toFixed(1) }},
              ita_angle: ita.toFixed(1),
              hsv: {{ H_deg: Math.round(hsv.h), S_pct: Math.round(hsv.s * 100), V_pct: Math.round(hsv.v * 100) }},
              is_olive: isOlive
            }},
            areas: {{
              overall: areas.overall,
              forehead: areas.forehead,
              cheek: areas.cheek,
              chin: areas.chin
            }},
            faceBox
          }},
          gender: {{
            label: detectedGender.toLowerCase(),
            detected: detectedGender,
            confidence: genderConfidence,
            probabilities: {{ Male: pMale, Female: pFemale }},
            metrics: {{
              jaw_ratio: jawRatio.toFixed(2),
              aspect_ratio: faceAspect.toFixed(2),
              lip_contrast: lipContrast.toFixed(3),
              texture_ratio: textureRatio.toFixed(2)
            }}
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
        let scoredColors = matching.map(c => ({{
          ...c,
          affinityScore: calculateAffinityScore(c)
        }})).sort((a, b) => b.affinityScore - a.affinityScore);

        if (activeGender === "male") {{
          scoredColors = scoredColors.filter(c => {{
            const cat = (c.category || "").toLowerCase();
            const name = (c.name || "").toLowerCase();
            const desc = (c.description || "").toLowerCase();
            const sub = (c.sub_category || "").toLowerCase();
            return cat !== "makeup" &&
                   !name.includes("lip") &&
                   !name.includes("lipstick") &&
                   !name.includes("gloss") &&
                   !name.includes("blush") &&
                   !name.includes("eyeshadow") &&
                   !name.includes("mascara") &&
                   !desc.includes("lipstick") &&
                   !desc.includes("lip tint") &&
                   !desc.includes("blush") &&
                   !sub.includes("lipstick") &&
                   !sub.includes("blush");
          }});
        }}

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

      function updateGenderView(activeG) {{
        const targetG = (activeG || currentGender || "female").toLowerCase();
        const makeupBtn = document.getElementById("tab-btn-makeup");
        const makeupTab = document.getElementById("tab-makeup");
        const clothingBtn = document.querySelector('[data-tab="clothing"]');
        const clothingTab = document.getElementById("tab-clothing");

        if (targetG === "male") {{
          if (makeupBtn) {{
            makeupBtn.style.display = "none";
            makeupBtn.classList.remove("active");
          }}
          if (makeupTab) {{
            makeupTab.style.display = "none";
            makeupTab.classList.remove("active");
          }}
          if (clothingBtn) clothingBtn.classList.add("active");
          if (clothingTab) {{
            clothingTab.style.display = "";
            clothingTab.classList.add("active");
          }}
        }} else {{
          if (makeupBtn) makeupBtn.style.display = "";
          if (makeupTab && makeupBtn && makeupBtn.classList.contains("active")) {{
            makeupTab.style.display = "";
          }}
        }}
      }}

      function handleGenderSelect(selectedGender, isManual = true) {{
        currentGender = selectedGender;

        // Sync upload selector pills
        document.querySelectorAll("#upload-gender-options .gender-pill").forEach((p) => {{
          p.classList.toggle("active", p.getAttribute("data-gender") === currentGender);
        }});

        // Determine effective gender
        let effectiveGender = currentGender;
        if (effectiveGender === "auto") {{
          effectiveGender = (cachedAnalysisData && cachedAnalysisData.gender && cachedAnalysisData.gender.label)
            ? cachedAnalysisData.gender.label.toLowerCase()
            : "female";
        }}

        // Render interactive style switcher in results banner
        const resultsGenderOptions = document.getElementById("results-gender-options");
        if (resultsGenderOptions) {{
          resultsGenderOptions.innerHTML = `
            <button type="button" class="gender-pill ${{effectiveGender === 'female' ? 'active' : ''}}" data-gender="female">👗 Women's</button>
            <button type="button" class="gender-pill ${{effectiveGender === 'male' ? 'active' : ''}}" data-gender="male">👔 Men's</button>
            <button type="button" class="gender-pill ${{effectiveGender === 'all' ? 'active' : ''}}" data-gender="all">👥 All Styles</button>
          `;
          resultsGenderOptions.querySelectorAll(".gender-pill").forEach((pill) => {{
            pill.addEventListener("click", () => {{
              const g = pill.getAttribute("data-gender");
              handleGenderSelect(g, true);
            }});
          }});
        }}

        const switchLabel = document.getElementById("gender-switch-label");
        if (switchLabel) switchLabel.textContent = "Switch Style:";

        updateGenderView(effectiveGender);

        const bannerTitleText = document.getElementById("gender-banner-title-text");
        if (bannerTitleText) bannerTitleText.textContent = "Style Profile:";

        const bannerIcon = document.getElementById("gender-banner-icon");
        const bannerLabel = document.getElementById("gender-banner-label");
        const bannerBadge = document.getElementById("gender-banner-badge");
        const bannerDesc = document.getElementById("gender-banner-desc");

        const aiDetected = (cachedAnalysisData && cachedAnalysisData.gender && cachedAnalysisData.gender.detected) || "Female";
        const aiConf = (cachedAnalysisData && cachedAnalysisData.gender && cachedAnalysisData.gender.confidence) || 88;

        if (effectiveGender === "female") {{
          if (bannerIcon) bannerIcon.textContent = "👗";
          if (bannerLabel) bannerLabel.textContent = "Women's Style";
          if (bannerBadge) {{
            bannerBadge.textContent = (currentGender === "auto") ? ` Detected: ${{aiDetected}} (${{aiConf}}%)` : " Selected Profile";
            bannerBadge.className = "gender-banner-badge auto-badge";
          }}
          if (bannerDesc) {{
            bannerDesc.textContent = "Color palettes, cosmetics, evening wear, and fine jewelry are tailored for haute womenswear styling.";
          }}
        }} else if (effectiveGender === "male") {{
          if (bannerIcon) bannerIcon.textContent = "👔";
          if (bannerLabel) bannerLabel.textContent = "Men's Style";
          if (bannerBadge) {{
            bannerBadge.textContent = (currentGender === "auto") ? ` Detected: ${{aiDetected}} (${{aiConf}}%)` : " Selected Profile";
            bannerBadge.className = "gender-banner-badge auto-badge";
          }}
          if (bannerDesc) {{
            bannerDesc.textContent = "Colorimetry calibrated for male high-contrast suiting, sartorial tailoring, facial shadow absorption, and precious metals horology calibration.";
          }}
        }} else {{
          if (bannerIcon) bannerIcon.textContent = "👥";
          if (bannerLabel) bannerLabel.textContent = "All Styles (Universal)";
          if (bannerBadge) {{
            bannerBadge.textContent = " Universal Harmony";
            bannerBadge.className = "gender-banner-badge auto-badge";
          }}
          if (bannerDesc) {{
            bannerDesc.textContent = "Comprehensive styling recommendations across tailored suiting, evening wear, cosmetics, and universal color harmonies.";
          }}
        }}

        if (cachedAnalysisData && resultsSection && !resultsSection.classList.contains("hidden")) {{
          const recData = getRecommendationsForUndertone(
            cachedAnalysisData.undertone.label,
            cachedAnalysisData.skin_analysis.metrics,
            cachedAnalysisData.image_atmosphere,
            effectiveGender
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

          let activeProfile = currentGender;
          if (currentGender === "auto") {{
            activeProfile = (analysisData.gender && analysisData.gender.label === "male") ? "male" : "female";
          }}

          handleGenderSelect(currentGender, false);

          const recData = getRecommendationsForUndertone(
            analysisData.undertone.label,
            analysisData.skin_analysis.metrics,
            analysisData.image_atmosphere,
            activeProfile
          );

          renderResults(analysisData, recData);
          updateGenderView(activeProfile);

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

        // Update Micro-Extract Swatches in Studio Telemetry with REAL facial area tones
        const areas = (data && data.skin_analysis && data.skin_analysis.areas) || {{}};
        const overallHex = (areas.overall && areas.overall.hex) || m.representative_hex;
        const foreheadHex = (areas.forehead && areas.forehead.hex) || m.representative_hex;
        const cheekHex = (areas.cheek && areas.cheek.hex) || m.representative_hex;
        const chinHex = (areas.chin && areas.chin.hex) || m.representative_hex;

        const updateMicroSwatch = (idColor, idHex, hex) => {{
          const cEl = document.getElementById(idColor);
          const hEl = document.getElementById(idHex);
          if (cEl) cEl.style.backgroundColor = hex;
          if (hEl) hEl.textContent = hex;
        }};
        updateMicroSwatch("sample-color-1", "sample-hex-1", overallHex);
        updateMicroSwatch("sample-color-2", "sample-hex-2", foreheadHex);
        updateMicroSwatch("sample-color-3", "sample-hex-3", cheekHex);
        updateMicroSwatch("sample-color-4", "sample-hex-4", chinHex);

        // Update the Results Facial Area Breakdown Strip
        const updateResultArea = (dotId, hexId, hex) => {{
          const d = document.getElementById(dotId);
          const h = document.getElementById(hexId);
          if (d) d.style.backgroundColor = hex;
          if (h) h.textContent = hex;
        }};
        updateResultArea("res-area-dot-1", "res-area-hex-1", overallHex);
        updateResultArea("res-area-dot-2", "res-area-hex-2", foreheadHex);
        updateResultArea("res-area-dot-3", "res-area-hex-3", cheekHex);
        updateResultArea("res-area-dot-4", "res-area-hex-4", chinHex);

        // Draw Canvas with Area Pins & Face Boundary
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

        const skinAnalysis = data && data.skin_analysis;
        const metrics = (skinAnalysis && skinAnalysis.metrics) || {{}};
        const areas = (skinAnalysis && skinAnalysis.areas) || {{}};
        const faceBox = (skinAnalysis && skinAnalysis.faceBox) || null;
        const hex = metrics.representative_hex || "#D4AF37";
        const utLabel = (data && data.undertone && data.undertone.label) || "Undertone";

        // 1. Draw Sleek Luxury Gold Face Bounding Oval / Box
        if (faceBox) {{
          const bx = Math.round(faceBox.x * scale);
          const by = Math.round(faceBox.y * scale);
          const bw = Math.round(faceBox.width * scale);
          const bh = Math.round(faceBox.height * scale);

          ctx.save();
          ctx.strokeStyle = "rgba(242, 202, 80, 0.40)";
          ctx.lineWidth = 1.5;
          ctx.setLineDash([4, 4]);
          ctx.beginPath();
          ctx.roundRect(bx, by, bw, bh, 14);
          ctx.stroke();
          ctx.restore();

          // Elegant corner brackets
          const bracketLen = Math.min(20, Math.floor(bw * 0.15));
          ctx.strokeStyle = "#F2CA50";
          ctx.lineWidth = 2.5;

          ctx.beginPath();
          ctx.moveTo(bx, by + bracketLen); ctx.lineTo(bx, by); ctx.lineTo(bx + bracketLen, by);
          ctx.stroke();

          ctx.beginPath();
          ctx.moveTo(bx + bw - bracketLen, by); ctx.lineTo(bx + bw, by); ctx.lineTo(bx + bw, by + bracketLen);
          ctx.stroke();

          ctx.beginPath();
          ctx.moveTo(bx, by + bh - bracketLen); ctx.lineTo(bx, by + bh); ctx.lineTo(bx + bracketLen, by + bh);
          ctx.stroke();

          ctx.beginPath();
          ctx.moveTo(bx + bw - bracketLen, by + bh); ctx.lineTo(bx + bw, by + bh); ctx.lineTo(bx + bw, by + bh - bracketLen);
          ctx.stroke();
        }}

        // 2. Draw Anatomical Target Pins for Facial Areas
        const drawTargetPin = (pt, label, areaHex, isLeft = false) => {{
          if (!pt) return;
          const px = Math.round(pt.x * scale);
          const py = Math.round(pt.y * scale);

          ctx.save();
          ctx.strokeStyle = "rgba(242, 202, 80, 0.75)";
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.arc(px, py, 7, 0, Math.PI * 2);
          ctx.stroke();

          ctx.fillStyle = areaHex;
          ctx.beginPath();
          ctx.arc(px, py, 4.5, 0, Math.PI * 2);
          ctx.fill();
          ctx.strokeStyle = "#FFFFFF";
          ctx.lineWidth = 1;
          ctx.stroke();

          ctx.font = "bold 9px 'JetBrains Mono', monospace";
          const tagText = `${{label}} ${{areaHex}}`;
          const textW = ctx.measureText(tagText).width;
          const tagW = textW + 12;
          const tagH = 18;
          const tagX = isLeft ? Math.max(8, px - tagW - 10) : Math.min(displayWidth - tagW - 8, px + 10);
          const tagY = Math.max(10, Math.min(displayHeight - tagH - 45, py - 9));

          ctx.strokeStyle = "rgba(242, 202, 80, 0.6)";
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(px + (isLeft ? -7 : 7), py);
          ctx.lineTo(tagX + (isLeft ? tagW : 0), tagY + tagH / 2);
          ctx.stroke();

          ctx.fillStyle = "rgba(10, 14, 22, 0.88)";
          ctx.beginPath();
          ctx.roundRect(tagX, tagY, tagW, tagH, 4);
          ctx.fill();
          ctx.strokeStyle = "rgba(212, 175, 55, 0.5)";
          ctx.lineWidth = 1;
          ctx.stroke();

          ctx.fillStyle = "#F8FAFC";
          ctx.fillText(tagText, tagX + 6, tagY + 12.5);
          ctx.restore();
        }};

        if (areas.forehead) drawTargetPin(areas.forehead, "Forehead", areas.forehead.hex, false);
        if (areas.cheek) drawTargetPin(areas.cheek, "Cheek", areas.cheek.hex, true);
        if (areas.chin) drawTargetPin(areas.chin, "Chin", areas.chin.hex, false);

        // 3. Draw Bottom Glassmorphic Summary Bar
        const pillW = Math.min(320, Math.floor(displayWidth * 0.72));
        const pillH = 34;
        const pillX = 14;
        const pillY = displayHeight - pillH - 12;

        ctx.fillStyle = "rgba(10, 14, 22, 0.90)";
        ctx.beginPath();
        ctx.roundRect(pillX, pillY, pillW, pillH, 8);
        ctx.fill();
        ctx.strokeStyle = "rgba(212, 175, 55, 0.7)";
        ctx.lineWidth = 1.5;
        ctx.stroke();

        const radius = 7;
        ctx.fillStyle = hex;
        ctx.beginPath();
        ctx.arc(pillX + 18, pillY + pillH / 2, radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = "#FFFFFF";
        ctx.lineWidth = 1.5;
        ctx.stroke();

        ctx.fillStyle = "#F2CA50";
        ctx.font = "bold 11px sans-serif";
        const genderLabel = (data.gender && data.gender.detected) ? ` • ${{data.gender.detected}}` : '';
        ctx.fillText("Dermis: " + hex + " • " + utLabel + genderLabel, pillX + 32, pillY + 21);
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
