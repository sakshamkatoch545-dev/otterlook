/**
 * OTTERLOOK AI - Frontend Application Controller
 * Handles image upload, pipeline animations, API communication,
 * landmark canvas overlay, and dynamic palette rendering.
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
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

  // State
  let currentFile = null;
  let currentImageBitmap = null;

  // --- Theme Controller ---
  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    if (themeColorMeta) {
      themeColorMeta.setAttribute("content", theme === "dark" ? "#0B0F17" : "#F8F9FC");
    }
  }

  const savedTheme = localStorage.getItem("otterlook-theme") || "dark";
  applyTheme(savedTheme);

  themeToggleBtn.addEventListener("click", () => {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    applyTheme(newTheme);
    localStorage.setItem("otterlook-theme", newTheme);
  });

  // --- Modal Controller ---
  vivaModalBtn.addEventListener("click", () => vivaModal.classList.remove("hidden"));
  modalCloseBtn.addEventListener("click", () => vivaModal.classList.add("hidden"));
  vivaModal.addEventListener("click", (e) => {
    if (e.target === vivaModal) vivaModal.classList.add("hidden");
  });

  // --- File Upload & Mobile Camera Selfie ---
  if (browseBtn) {
    browseBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      fileInput.click();
    });
  }

  // --- Live Selfie Camera Modal & Stream ---
  const cameraModal = document.getElementById("camera-modal");
  const cameraModalCloseBtn = document.getElementById("camera-modal-close-btn");
  const cameraVideo = document.getElementById("camera-video");
  const cameraCaptureBtn = document.getElementById("camera-capture-btn");
  const cameraFlipBtn = document.getElementById("camera-flip-btn");
  const cameraBtn = document.getElementById("camera-btn");
  const cameraInput = document.getElementById("camera-input");
  let currentStream = null;
  let currentFacingMode = "user";

  async function startCameraStream(facingMode = "user") {
    try {
      if (currentStream) {
        currentStream.getTracks().forEach((t) => t.stop());
      }
      currentFacingMode = facingMode;
      const constraints = {
        video: { facingMode: { ideal: facingMode }, width: { ideal: 1280 }, height: { ideal: 960 } },
        audio: false,
      };
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      currentStream = stream;
      cameraVideo.srcObject = stream;
      await cameraVideo.play();
      cameraModal.classList.remove("hidden");
    } catch (err) {
      console.warn("Webcam stream unavailable, falling back to device camera input:", err);
      if (cameraInput) cameraInput.click();
    }
  }

  function stopCameraStream() {
    if (currentStream) {
      currentStream.getTracks().forEach((t) => t.stop());
      currentStream = null;
    }
    if (cameraModal) cameraModal.classList.add("hidden");
  }

  if (cameraBtn) {
    cameraBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        startCameraStream("user");
      } else if (cameraInput) {
        cameraInput.click();
      }
    });
  }

  if (cameraModalCloseBtn) cameraModalCloseBtn.addEventListener("click", stopCameraStream);
  if (cameraModal) {
    cameraModal.addEventListener("click", (e) => {
      if (e.target === cameraModal) stopCameraStream();
    });
  }

  if (cameraFlipBtn) {
    cameraFlipBtn.addEventListener("click", () => {
      const nextMode = currentFacingMode === "user" ? "environment" : "user";
      startCameraStream(nextMode);
    });
  }

  if (cameraCaptureBtn) {
    cameraCaptureBtn.addEventListener("click", () => {
      if (!cameraVideo || !cameraVideo.videoWidth) return;
      const snapCanvas = document.createElement("canvas");
      snapCanvas.width = cameraVideo.videoWidth;
      snapCanvas.height = cameraVideo.videoHeight;
      const snapCtx = snapCanvas.getContext("2d");
      if (currentFacingMode === "user") {
        snapCtx.translate(snapCanvas.width, 0);
        snapCtx.scale(-1, 1);
      }
      snapCtx.drawImage(cameraVideo, 0, 0);
      snapCanvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], "selfie.jpg", { type: "image/jpeg" });
          handleFileSelection(file);
        }
      }, "image/jpeg", 0.95);
      stopCameraStream();
    });
  }

  if (cameraInput) {
    cameraInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files[0]) {
        handleFileSelection(e.target.files[0]);
      }
    });
  }


  dropZone.addEventListener("click", () => {
    if (!currentFile) fileInput.click();
  });

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-over");
  });

  dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-over"));

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelection(e.target.files[0]);
    }
  });

  removeImgBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    resetUploadState();
  });


  function handleFileSelection(file) {
    if (!file.type.match(/image\/(jpeg|jpg|png|webp)/)) {
      showError("Please upload a valid JPG, JPEG, or PNG image file.");
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      showError("File size exceeds 15MB limit. Please upload a smaller image.");
      return;
    }

    currentFile = file;
    hideError();

    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      uploadPrompt.classList.add("hidden");
      previewBox.classList.remove("hidden");
      analyzeBtn.disabled = false;

      // Load image object for canvas rendering later
      const img = new Image();
      img.src = e.target.result;
      img.onload = () => {
        currentImageBitmap = img;
        // Preliminary quick quality indicator
        showInitialQuality(img.width, img.height);
      };
    };
    reader.readAsDataURL(file);
  }

  function resetUploadState() {
    currentFile = null;
    currentImageBitmap = null;
    fileInput.value = "";
    if (cameraInput) cameraInput.value = "";
    previewImg.src = "";
    uploadPrompt.classList.remove("hidden");
    previewBox.classList.add("hidden");
    analyzeBtn.disabled = true;
    qualityBar.classList.add("hidden");
    hideError();
  }

  function showInitialQuality(w, h) {
    qualityBar.classList.remove("hidden");
    if (w >= 300 && h >= 300) {
      qualityMeter.style.width = "85%";
      qualityStatus.textContent = "Good Resolution";
      qualityStatus.className = "quality-status Good";
      qualityDetails.textContent = `Image dimensions: ${w} × ${h}px • Ready for color analysis`;
    } else {
      qualityMeter.style.width = "45%";
      qualityStatus.textContent = "Low Resolution";
      qualityStatus.className = "quality-status Acceptable";
      qualityDetails.textContent = `Image dimensions: ${w} × ${h}px • High-res portrait recommended`;
    }
  }

  function showError(msg) {
    errorText.textContent = msg;
    errorBanner.classList.remove("hidden");
  }

  function hideError() {
    errorBanner.classList.add("hidden");
  }

  // Cross-platform mobile-friendly copy helper
  function copyToClipboard(text, label) {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(() => {
        showToast(`Copied ${label ? label + ' ' : ''}(${text}) to clipboard!`);
      }).catch(() => {
        fallbackCopyText(text, label);
      });
    } else {
      fallbackCopyText(text, label);
    }
  }

  function fallbackCopyText(text, label) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.left = "-999999px";
    textArea.style.top = "-999999px";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
      document.execCommand("copy");
      showToast(`Copied ${label ? label + ' ' : ''}(${text}) to clipboard!`);
    } catch (err) {
      showToast(`Color code: ${text}`);
    }
    document.body.removeChild(textArea);
  }

  function showToast(msg) {
    toast.textContent = msg;
    toast.classList.remove("hidden");
    setTimeout(() => toast.classList.add("hidden"), 2500);
  }

  // --- Pipeline Stepper Animation ---
  async function animatePipelineSteps() {
    const steps = [
      document.getElementById("step-1"),
      document.getElementById("step-2"),
      document.getElementById("step-3"),
      document.getElementById("step-4"),
      document.getElementById("step-5"),
      document.getElementById("step-6"),
    ];

    steps.forEach((s) => (s.className = "step-item"));

    for (let i = 0; i < steps.length; i++) {
      steps[i].classList.add("active");
      await new Promise((resolve) => setTimeout(resolve, 45));
      steps[i].classList.remove("active");
      steps[i].classList.add("completed");
    }
  }

  // --- Analyze API Execution ---
  analyzeBtn.addEventListener("click", async () => {
    if (!currentFile) return;

    hideError();
    studioSection.classList.add("hidden");
    heroSection.classList.add("hidden");
    processingSection.classList.remove("hidden");
    resultsSection.classList.add("hidden");

    const animationPromise = animatePipelineSteps();

    const formData = new FormData();
    formData.append("file", currentFile);

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      await animationPromise;

      if (!response.ok || !data.success) {
        throw new Error(data.error || "An error occurred during facial color analysis.");
      }

      // Render all results
      renderResults(data);

      processingSection.classList.add("hidden");
      resultsSection.classList.remove("hidden");
      window.scrollTo({ top: 0, behavior: "smooth" });

    } catch (err) {
      processingSection.classList.add("hidden");
      studioSection.classList.remove("hidden");
      heroSection.classList.remove("hidden");
      showError(err.message || "Failed to connect to backend server.");
    }
  });

  // Re-analyze
  reanalyzeBtn.addEventListener("click", () => {
    resultsSection.classList.add("hidden");
    studioSection.classList.remove("hidden");
    heroSection.classList.remove("hidden");
    resetUploadState();
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  // --- Gender / Styling Profile Tracking ---
  let currentGender = "female";
  const uploadGenderOptions = document.getElementById("upload-gender-options");
  if (uploadGenderOptions) {
    uploadGenderOptions.querySelectorAll(".gender-pill").forEach((pill) => {
      pill.addEventListener("click", () => {
        uploadGenderOptions.querySelectorAll(".gender-pill").forEach((p) => p.classList.remove("active"));
        pill.classList.add("active");
        currentGender = pill.getAttribute("data-gender");
        updateGenderView();
      });
    });
  }

  function updateGenderView() {
    const makeupBtn = document.getElementById("tab-btn-makeup");
    if (makeupBtn) {
      if (currentGender === "male") {
        makeupBtn.style.display = "none";
        if (makeupBtn.classList.contains("active")) {
          const clothingBtn = document.querySelector('[data-tab="clothing"]');
          if (clothingBtn) clothingBtn.click();
        }
      } else {
        makeupBtn.style.display = "";
      }
    }
  }

  // --- Render Results ---
  function renderResults(data) {
    updateGenderView();
    const undertone = data.undertone.label;
    const confidencePct = data.undertone.confidence_percentage;

    // 1. Undertone Hero Badge
    const badge = document.getElementById("undertone-badge");
    badge.textContent = undertone.toUpperCase();
    badge.className = `undertone-badge ${undertone}`;

    document.getElementById("confidence-val").textContent = `${confidencePct}%`;
    document.getElementById("confidence-bar").style.width = `${confidencePct}%`;

    // Probability breakdown
    const probBreakdown = document.getElementById("prob-breakdown");
    probBreakdown.innerHTML = "";
    if (data.undertone.probabilities) {
      Object.entries(data.undertone.probabilities).forEach(([cls, prob]) => {
        const span = document.createElement("span");
        span.textContent = `${cls}: ${(prob * 100).toFixed(1)}%`;
        probBreakdown.appendChild(span);
      });
    }

    document.getElementById("undertone-explanation").textContent = data.undertone.explanation;

    // Key factors
    const keyFactorsContainer = document.getElementById("key-factors");
    keyFactorsContainer.innerHTML = "";
    if (data.undertone.key_factors) {
      data.undertone.key_factors.forEach((f) => {
        const div = document.createElement("div");
        div.className = "factor-item";
        div.textContent = f;
        keyFactorsContainer.appendChild(div);
      });
    }

    // 2. Skin Metrics & Color Swatch
    const skinMetrics = data.skin_analysis.metrics;
    document.getElementById("rep-swatch").style.backgroundColor = skinMetrics.representative_hex;
    document.getElementById("rep-hex").textContent = skinMetrics.representative_hex;
    document.getElementById("rep-phototype").textContent = skinMetrics.phototype_estimate;

    document.getElementById("metric-lab-l").textContent = skinMetrics.cielab.L;
    document.getElementById("metric-lab-a").textContent = `${skinMetrics.cielab.a >= 0 ? "+" : ""}${skinMetrics.cielab.a}`;
    document.getElementById("metric-lab-b").textContent = `${skinMetrics.cielab.b >= 0 ? "+" : ""}${skinMetrics.cielab.b}`;
    document.getElementById("metric-ita").textContent = `${skinMetrics.ita_angle >= 0 ? "+" : ""}${skinMetrics.ita_angle}°`;
    document.getElementById("metric-hsv-h").textContent = `${skinMetrics.hsv.H_deg}°`;

    // 3. Draw Autonomous Skin Canvas
    drawFacialLandmarksCanvas(skinMetrics.representative_hex, data.undertone.label);

    // 4. Personalized Core Palette
    document.getElementById("stylist-summary").textContent = data.stylist_summary;
    if (data.seasonal_harmony) {
      document.getElementById("season-title").textContent = data.seasonal_harmony.season_name;
    }

    const swatchesGrid = document.getElementById("swatches-grid");
    swatchesGrid.innerHTML = "";
    data.palette.forEach((color) => {
      const card = document.createElement("div");
      card.className = "swatch-card";
      card.innerHTML = `
        <div class="swatch-color" style="background-color: ${color.hex}"></div>
        <div class="swatch-meta">
          <div class="swatch-name" title="${color.name}">${color.name}</div>
          <div class="swatch-hex">${color.hex}</div>
        </div>
      `;
      card.addEventListener("click", () => {
        copyToClipboard(color.hex, color.name);
      });
      swatchesGrid.appendChild(card);
    });

    // Render Dynamic Skin Harmonies
    const skinBadge = document.getElementById("skin-coords-badge");
    if (skinBadge) skinBadge.textContent = skinMetrics.representative_hex;

    const skinGrid = document.getElementById("skin-harmonies-grid");
    if (skinGrid && data.skin_harmonies) {
      skinGrid.innerHTML = "";
      data.skin_harmonies.forEach((h) => {
        const card = document.createElement("div");
        card.className = "skin-harmony-card";
        card.innerHTML = `
          <div class="skin-harmony-color" style="background-color: ${h.hex}">
            <span class="skin-harmony-badge">${h.badge || "Harmony"}</span>
          </div>
          <div class="skin-harmony-meta">
            <div class="skin-harmony-name" title="${h.name}">${h.name}</div>
            <div class="skin-harmony-hex">${h.hex}</div>
            <div class="skin-harmony-desc">${h.description}</div>
          </div>
        `;
        card.addEventListener("click", () => copyToClipboard(h.hex, h.name));
        skinGrid.appendChild(card);
      });
    }

    // Render Analyzed Image Atmosphere
    const atmSwatches = document.getElementById("atmosphere-swatches");
    if (atmSwatches) {
      atmSwatches.innerHTML = `
        <div class="atmosphere-pill" title="Facial Skin Tone (${skinMetrics.representative_hex})">
          <span class="atmosphere-dot" style="background: ${skinMetrics.representative_hex}"></span>
          <span>Skin ${skinMetrics.representative_hex}</span>
        </div>
      `;
    }

    // 5. Categorized Recommendations
    renderRecGrid("rec-clothing-grid", data.recommendations.clothing);
    renderRecGrid("rec-makeup-grid", data.recommendations.makeup);
    renderRecGrid("rec-accessories-grid", data.recommendations.accessories);
    renderRecGrid("rec-neutrals-grid", data.recommendations.neutrals);
    renderAvoidGrid("rec-avoid-grid", data.less_recommended);

    // 6. World Color Spectrum
    renderWorldSpectrum(data.recommendations.world_spectrum, data.undertone.label);

    document.getElementById("foundation-advice-text").textContent = data.foundation_advice;
  }

  function renderRecGrid(containerId, items) {
    const container = document.getElementById(containerId);
    container.innerHTML = "";
    if (!items || items.length === 0) {
      container.innerHTML = "<p class='text-muted'>No items found for this category.</p>";
      return;
    }

    items.forEach((item) => {
      const card = document.createElement("div");
      card.className = "rec-card";
      card.innerHTML = `
        <div class="rec-color-circle" style="background-color: ${item.hex}"></div>
        <div class="rec-details">
          <div class="rec-name">${item.name}</div>
          <div class="rec-hex">${item.hex}</div>
          <div class="rec-desc">${item.description || item.sub_category || ""}</div>
        </div>
      `;
      card.addEventListener("click", () => {
        copyToClipboard(item.hex, item.name);
      });
      container.appendChild(card);
    });
  }

  function renderAvoidGrid(containerId, items) {
    const container = document.getElementById(containerId);
    container.innerHTML = "";
    if (!items || items.length === 0) {
      container.innerHTML = "<p class='text-muted'>No specific avoid rules for this undertone.</p>";
      return;
    }

    items.forEach((item) => {
      const card = document.createElement("div");
      card.className = "avoid-card";
      card.innerHTML = `
        <div class="avoid-circle" style="background-color: ${item.hex}"></div>
        <div class="avoid-details">
          <div class="avoid-name">${item.name} (${item.hex})</div>
          <div class="avoid-reason">${item.reason}</div>
        </div>
      `;
      container.appendChild(card);
    });
  }

  // --- World Color Spectrum Explorer ---
  let currentWorldFamily = "all";
  let currentWorldSearch = "";
  let cachedWorldColors = [];
  let currentUndertone = "Warm";

  function renderWorldSpectrum(colors, userUndertone) {
    currentUndertone = userUndertone || "Warm";
    const raw = colors || [];
    // Strictly filter to tones that match user undertone so only flattering colors are shown
    cachedWorldColors = raw.filter(c => !c.undertones || c.undertones.includes(currentUndertone));
    applyWorldFilters();
  }

  function applyWorldFilters() {
    const grid = document.getElementById("rec-world-grid");
    const counter = document.getElementById("world-counter");
    if (!grid) return;

    let filtered = cachedWorldColors;
    if (currentWorldFamily !== "all") {
      filtered = filtered.filter(c => c.family === currentWorldFamily);
    }
    if (currentWorldSearch.trim()) {
      const q = currentWorldSearch.toLowerCase().trim();
      filtered = filtered.filter(c => 
        c.name.toLowerCase().includes(q) || 
        c.hex.toLowerCase().includes(q) || 
        (c.tags && c.tags.some(t => t.toLowerCase().includes(q))) ||
        (c.description && c.description.toLowerCase().includes(q))
      );
    }

    if (counter) counter.textContent = `Showing ${filtered.length} of ${cachedWorldColors.length} tones matching your skin`;
    grid.innerHTML = "";

    if (filtered.length === 0) {
      grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 2rem;">No matching tones found for "${currentWorldSearch}" in your flattering palette.</div>`;
      return;
    }

    filtered.forEach((item) => {
      const card = document.createElement("div");
      card.className = "rec-card";
      card.innerHTML = `
        <div class="rec-color-circle" style="background-color: ${item.hex}"></div>
        <div class="rec-details">
          <div class="rec-name">${item.name} <span style="font-size:0.68rem; color:var(--accent-gold); font-weight:700;">✓ Matched</span></div>
          <div class="rec-hex">${item.hex}</div>
          <div class="rec-desc">${item.description || item.family || ""}</div>
        </div>
      `;
      card.addEventListener("click", () => copyToClipboard(item.hex, item.name));
      grid.appendChild(card);
    });
  }

  // Wire up world filter chips and search
  const worldChips = document.querySelectorAll("#world-chips-scroll .world-chip");
  worldChips.forEach(chip => {
    chip.addEventListener("click", () => {
      worldChips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      currentWorldFamily = chip.getAttribute("data-family");
      applyWorldFilters();
    });
  });

  const searchInput = document.getElementById("world-search-input");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      currentWorldSearch = e.target.value;
      applyWorldFilters();
    });
  }

  // --- Canvas Rendering for Autonomous Skin Colorimetry ---
  function drawFacialLandmarksCanvas(skinHex, undertoneLabel) {
    const canvas = document.getElementById("face-canvas");
    const ctx = canvas.getContext("2d");

    if (!currentImageBitmap) return;

    canvas.width = currentImageBitmap.width;
    canvas.height = currentImageBitmap.height;

    // Draw base portrait
    ctx.drawImage(currentImageBitmap, 0, 0, canvas.width, canvas.height);

    // Draw sleek luxury HUD badge
    const hex = skinHex || "#D4AF37";
    const label = undertoneLabel || "Undertone";

    const pillW = Math.max(200, Math.floor(canvas.width * 0.45));
    const pillH = Math.max(34, Math.floor(canvas.height * 0.07));
    const pillX = Math.floor(canvas.width * 0.03);
    const pillY = canvas.height - pillH - Math.floor(canvas.height * 0.03);

    // Glassmorphic pill
    ctx.fillStyle = "rgba(11, 15, 23, 0.85)";
    ctx.beginPath();
    ctx.roundRect(pillX, pillY, pillW, pillH, 8);
    ctx.fill();
    ctx.strokeStyle = "rgba(212, 175, 55, 0.5)";
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Swatch dot
    const radius = Math.max(6, Math.floor(pillH * 0.28));
    ctx.fillStyle = hex;
    ctx.beginPath();
    ctx.arc(pillX + radius + 10, pillY + pillH / 2, radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Text label
    ctx.fillStyle = "#ffffff";
    ctx.font = `bold ${Math.max(11, Math.floor(pillH * 0.38))}px sans-serif`;
    ctx.fillText(`Skin Tone: ${hex} (${label})`, pillX + radius * 2 + 18, pillY + pillH / 2 + 4);
  }

  // --- Tab Navigation with Smooth Scrolling ---
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");
      tabBtns.forEach((b) => b.classList.remove("active"));
      tabContents.forEach((c) => c.classList.remove("active"));

      btn.classList.add("active");
      const content = document.getElementById(`tab-${targetTab}`);
      if (content) content.classList.add("active");

      // Auto scroll selected tab into view on mobile
      btn.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
    });
  });
});
