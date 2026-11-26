"""
Otterlook AI - Streamlit Application
Serves the unified frontend/ UI (identical to Vercel and FastAPI localhost:8000)
and ensures the FastAPI backend is running on 127.0.0.1:8000.
"""

import os
import re
import streamlit as st
import streamlit.components.v1 as components

# Page Configuration
st.set_page_config(
    page_title="OTTERLOOK AI — Atelier de Colorimétrie & Haute Vision",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit default chrome & margins for a 100% full-screen experience
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


def _ensure_backend_server():
    """Ensure the Otterlook FastAPI backend runs in background on 127.0.0.1:8000."""
    import subprocess, sys, urllib.request, time
    try:
        urllib.request.urlopen("http://127.0.0.1:8000/api/health", timeout=0.8)
        return
    except Exception:
        pass

    root_dir = os.path.dirname(os.path.abspath(__file__))
    subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "warning"],
        cwd=root_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    for _ in range(8):
        time.sleep(0.5)
        try:
            urllib.request.urlopen("http://127.0.0.1:8000/api/health", timeout=0.8)
            return
        except Exception:
            pass


_ensure_backend_server()


def get_cached_html():
    """Load and bundle frontend/index.html, style.css, and script.js as a single unified UI."""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(root_dir, "frontend")

    with open(os.path.join(frontend_dir, "index.html"), "r", encoding="utf-8") as f:
        html_content = f.read()

    with open(os.path.join(frontend_dir, "style.css"), "r", encoding="utf-8") as f:
        css_content = f.read()

    with open(os.path.join(frontend_dir, "script.js"), "r", encoding="utf-8") as f:
        js_content = f.read()

    iframe_overrides = "\nhtml, body { overflow-x: hidden; overflow-y: auto !important; height: auto !important; }\n"
    html_content = re.sub(
        r'<link\s+rel="stylesheet"\s+href="/static/style\.css[^"]*">',
        lambda _: f"<style>\n{css_content}{iframe_overrides}</style>",
        html_content
    )
    html_content = re.sub(
        r'<script\s+src="/static/script\.js[^"]*"></script>',
        lambda _: f"<script>\n{js_content}\n</script>",
        html_content
    )
    # Route static asset fetches (demo portraits) to local FastAPI server
    html_content = html_content.replace('"/static/assets/', '"http://127.0.0.1:8000/static/assets/')
    return html_content


components.html(get_cached_html(), height=850, scrolling=True)
