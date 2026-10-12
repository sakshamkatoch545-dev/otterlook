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
  let currentGender = "auto";
  let userExplicitlyChoseGender = false;

  // --- Theme Controller ---
  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    document.body.setAttribute("data-theme", theme);
    if (themeColorMeta) {
      themeColorMeta.setAttribute("content", theme === "dark" ? "#0F131C" : "#F8F9FC");
    }
    try {
      if (window.parent && window.parent.document) {
        window.parent.document.documentElement.setAttribute("data-theme", theme);
        window.parent.document.body.setAttribute("data-theme", theme);
        const pApp = window.parent.document.querySelector(".stApp");
        if (pApp) pApp.style.backgroundColor = theme === "dark" ? "#0F131C" : "#F8F9FC";
      }
    } catch (e) {
      // Ignore cross-origin context
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

  // --- Demo Sample Portrait Quick-Loaders ---
  async function loadSampleUrl(url) {
    try {
      const resp = await fetch(url);
      if (!resp.ok) return;
      const blob = await resp.blob();
      const filename = url.split("/").pop() || "sample.jpg";
      const file = new File([blob], filename, { type: blob.type || "image/jpeg" });
      handleFileSelection(file);
    } catch (e) {
      console.warn("Failed to load sample portrait:", e);
    }
  }

  document.querySelectorAll(".sample-chip-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const sampleUrl = btn.getAttribute("data-sample");
      if (sampleUrl) loadSampleUrl(sampleUrl);
    });
  });

  // Check URL parameter ?sample=warm etc.
  try {
    const urlParams = new URLSearchParams(window.location.search);
    const sampleParam = urlParams.get("sample");
    if (sampleParam) {
      const sampleMap = {
        warm: "/static/assets/samples/sample_warm.jpg",
        cool: "/static/assets/samples/sample_cool.jpg",
        neutral: "/static/assets/samples/sample_neutral.jpg"
      };
      const targetUrl = sampleMap[sampleParam.toLowerCase()];
      if (targetUrl) {
        setTimeout(() => loadSampleUrl(targetUrl), 200);
      }
    }
  } catch(e) {}

  // --- Live Selfie Camera Modal & Stream ---
  const cameraModal = document.getElementById("camera-modal");
  const cameraModalCloseBtn = document.getElementById("camera-modal-close-btn");
  const cameraVideo = document.getElementById("camera-video");
  const cameraCaptureBtn = document.getElementById("camera-capture-btn");
  const cameraFlipBtn = document.getElementById("camera-flip-btn");
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
      analyzeBtn.disabled = true;

      // Load image object for canvas analysis
      const img = new Image();
      img.src = e.target.result;
      img.onload = () => {
        currentImageBitmap = img;
        // Run auto-colour detection & lighting quality check
        checkImageQualityAndAutoColor(img);
      };
    };
    reader.readAsDataURL(file);
  }

  function rgbToHex(r, g, b) {
    const clamp = (v) => Math.max(0, Math.min(255, Math.round(v)));
    return `#${clamp(r).toString(16).padStart(2, '0')}${clamp(g).toString(16).padStart(2, '0')}${clamp(b).toString(16).padStart(2, '0')}`.toUpperCase();
  }

  function renderFaceBox(face, rollDeg = 0) {
    // Kept for backward compatibility, box-face is hidden in auto-colour mode
    const el = document.getElementById("box-face");
    if (el) el.style.display = "none";
  }

  // --- Auto Colour Detection & Lighting Quality Sensor ---
  function checkImageQualityAndAutoColor(img) {
    const statusEl = document.getElementById("mesh-status-text");
    const lightingPill = document.getElementById("lighting-status-pill");
    const hudLightingPill = document.getElementById("hud-lighting-pill");
    const dockDot = document.getElementById("dock-dot");
    const autoBadgeTitle = document.getElementById("auto-color-badge-title");
    const autoBadgeHex = document.getElementById("face-box-hex");
    const autoBadgeTag = document.getElementById("face-box-sublabel");
    const autoDot = document.getElementById("face-box-color-dot");

    if (statusEl) statusEl.textContent = "Scanning photo lighting and complexion...";

    const origW = img.naturalWidth || img.width || 320;
    const origH = img.naturalHeight || img.height || 400;

    // Fast sampling canvas
    const sampleW = 280;
    const sampleH = Math.max(140, Math.round((origH / origW) * 280));
    const canvas = document.createElement("canvas");
    canvas.width = sampleW;
    canvas.height = sampleH;
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    ctx.drawImage(img, 0, 0, sampleW, sampleH);
    const imgData = ctx.getImageData(0, 0, sampleW, sampleH).data;

    // 1. Lighting, Exposure & Clarity metrics
    let totalLum = 0;
    let darkCount = 0;
    let brightCount = 0;
    const totalPixels = sampleW * sampleH;
    const lums = [];

    for (let i = 0; i < imgData.length; i += 4) {
      const r = imgData[i], g = imgData[i + 1], b = imgData[i + 2];
      const lum = 0.299 * r + 0.587 * g + 0.114 * b;
      totalLum += lum;
      if (lum < 22) darkCount++;
      if (lum > 242) brightCount++;
      if (i % 16 === 0) lums.push(lum);
    }

    const meanBrightness = totalLum / totalPixels;
    const darkRatio = darkCount / totalPixels;
    const brightRatio = brightCount / totalPixels;

    let lumVarSum = 0;
    for (let l of lums) {
      const d = l - meanBrightness;
      lumVarSum += d * d;
    }
    const contrastStd = Math.sqrt(lumVarSum / lums.length);

    // Focus / blur approximation
    let edgeDiffSum = 0;
    let edgeCount = 0;
    for (let y = 1; y < sampleH - 1; y += 3) {
      for (let x = 1; x < sampleW - 1; x += 3) {
        const idx = (y * sampleW + x) * 4;
        const c = 0.299 * imgData[idx] + 0.587 * imgData[idx + 1] + 0.114 * imgData[idx + 2];
        const r = 0.299 * imgData[idx + 4] + 0.587 * imgData[idx + 5] + 0.114 * imgData[idx + 6];
        const down = 0.299 * imgData[idx + sampleW * 4] + 0.587 * imgData[idx + sampleW * 4 + 1] + 0.114 * imgData[idx + sampleW * 4 + 2];
        const diff = Math.abs(c - r) + Math.abs(c - down);
        edgeDiffSum += diff * diff;
        edgeCount++;
      }
    }
    const blurMetric = edgeCount > 0 ? (edgeDiffSum / edgeCount) : 100;

    // 2. Candidate skin pixels across full Fitzpatrick range
    const candidateSkin = [];
    for (let y = 0; y < sampleH; y += 2) {
      for (let x = 0; x < sampleW; x += 2) {
        const idx = (y * sampleW + x) * 4;
        const r = imgData[idx], g = imgData[idx + 1], b = imgData[idx + 2];
        const yP = 0.299 * r + 0.587 * g + 0.114 * b;
        const cr = 0.713 * (r - yP) + 128.0;
        const cb = 0.564 * (b - yP) + 128.0;

        const maxC = Math.max(r, g, b), minC = Math.min(r, g, b);
        const delta = maxC - minC;
        const sat = maxC > 0 ? delta / maxC : 0;

        const isYCrCb = (cr >= 126 && cr <= 188 && cb >= 68 && cb <= 142 && (cr - cb) >= 5);
        const isRGB = (r > g && g > b && r > 40 && (r - g) >= 4 && (r - b) >= 7);
        const isSat = (sat >= 0.08 && sat <= 0.78);

        if (isYCrCb && isRGB && isSat) {
          candidateSkin.push({ r, g, b, lum: yP, x, y });
        }
      }
    }

    // 3. Check for lighting and clarity issues
    let errorMsg = null;
    if (origW < 160 || origH < 160) {
      errorMsg = "The image is not clear: Photo resolution is too low. Please upload a higher resolution photo.";
    } else if (meanBrightness < 45 || darkRatio > 0.35) {
      errorMsg = "The image is not clear and does not have proper lighting: The photo is too dark. Please take your photo in bright, natural daylight so your skin tone can be identified accurately.";
    } else if (meanBrightness > 222 || brightRatio > 0.35) {
      errorMsg = "The image is not clear: Harsh glare or overexposure detected. Please avoid strong camera flash or harsh direct sunlight.";
    } else if (contrastStd < 16) {
      errorMsg = "The image is not clear: The photo lacks contrast or has heavy uneven shadows. Please use clear, balanced lighting.";
    } else if (blurMetric < 15) {
      errorMsg = "The image is not clear: The photo appears blurry or out of focus. Please ensure the camera is steady and clear.";
    } else if (candidateSkin.length < 35) {
      errorMsg = "Could not identify your natural skin colour. The image is not clear or does not have proper lighting. Please upload a clear photo with visible skin complexion in natural lighting.";
    }

    if (errorMsg) {
      // Show warning and PREVENT proceeding!
      showError(errorMsg);
      if (qualityBar) qualityBar.classList.remove("hidden");
      if (qualityMeter) {
        qualityMeter.style.width = "30%";
        qualityMeter.style.background = "#EF4444";
      }
      if (qualityStatus) {
        qualityStatus.textContent = "Lighting / Clarity Issue";
        qualityStatus.className = "quality-status Poor";
      }
      if (qualityDetails) qualityDetails.textContent = errorMsg;

      if (statusEl) statusEl.textContent = "⚠️ Image not clear or poor lighting • Skin colour not spotted";
      if (lightingPill) lightingPill.textContent = "Lighting: Needs Improvement";
      if (hudLightingPill) hudLightingPill.textContent = "⚠️ POOR LIGHTING";
      if (dockDot) dockDot.style.background = "#EF4444";

      if (autoBadgeTitle) autoBadgeTitle.textContent = "SKIN COLOUR NOT SPOTTED";
      if (autoBadgeHex) autoBadgeHex.textContent = "UNCLEAR";
      if (autoBadgeTag) {
        autoBadgeTag.textContent = "CHECK LIGHTING";
        autoBadgeTag.className = "auto-color-status-tag error";
      }
      if (autoDot) autoDot.style.backgroundColor = "#64748B";

      analyzeBtn.disabled = true;
      return false;
    }

    // Success! Dermis color spotted accurately
    hideError();
    candidateSkin.sort((a, b) => a.lum - b.lum);
    const lowCut = Math.floor(candidateSkin.length * 0.15);
    const highCut = Math.max(lowCut + 1, Math.floor(candidateSkin.length * 0.85));
    const trimmed = candidateSkin.slice(lowCut, highCut);

    let sumR = 0, sumG = 0, sumB = 0;
    trimmed.forEach((p) => { sumR += p.r; sumG += p.g; sumB += p.b; });
    const spottedR = Math.round(sumR / trimmed.length);
    const spottedG = Math.round(sumG / trimmed.length);
    const spottedB = Math.round(sumB / trimmed.length);
    const spottedHex = rgbToHex(spottedR, spottedG, spottedB);

    // Update Quality Bar: Optimal
    if (qualityBar) qualityBar.classList.remove("hidden");
    if (qualityMeter) {
      qualityMeter.style.width = "95%";
      qualityMeter.style.background = "#10B981";
    }
    if (qualityStatus) {
      qualityStatus.textContent = "Good Lighting & Clear Photo";
      qualityStatus.className = "quality-status Good";
    }
    if (qualityDetails) {
      qualityDetails.textContent = `Natural skin tone spotted (${spottedHex}) • Lighting is balanced and clear. Ready to proceed!`;
    }

    // Update HUD & Auto Color Badge
    if (statusEl) statusEl.textContent = `✨ Natural skin colour spotted (${spottedHex}) • Lighting is clear`;
    if (lightingPill) lightingPill.textContent = "Lighting: Clear & Balanced";
    if (hudLightingPill) hudLightingPill.textContent = "💡 GOOD LIGHTING";
    if (dockDot) dockDot.style.background = "#10B981";

    if (autoBadgeTitle) autoBadgeTitle.textContent = "SKIN COLOUR SPOTTED";
    if (autoBadgeHex) autoBadgeHex.textContent = spottedHex;
    if (autoBadgeTag) {
      autoBadgeTag.textContent = "READY TO PROCEED";
      autoBadgeTag.className = "auto-color-status-tag success";
    }
    if (autoDot) autoDot.style.backgroundColor = spottedHex;

    // Update Telemetry Swatches
    const updateSwatch = (colorId, hexId, hex) => {
      const c = document.getElementById(colorId);
      const h = document.getElementById(hexId);
      if (c) c.style.backgroundColor = hex;
      if (h) h.textContent = hex;
    };
    updateSwatch("sample-color-1", "sample-hex-1", spottedHex);
    updateSwatch("sample-color-2", "sample-hex-2", rgbToHex(Math.min(255, spottedR + 5), Math.min(255, spottedG + 3), Math.max(0, spottedB - 3)));
    updateSwatch("sample-color-3", "sample-hex-3", rgbToHex(Math.max(0, spottedR - 4), Math.max(0, spottedG - 3), Math.min(255, spottedB + 2)));
    updateSwatch("sample-color-4", "sample-hex-4", rgbToHex(Math.max(0, spottedR - 2), Math.max(0, spottedG - 4), Math.max(0, spottedB - 2)));

    // Update Diagnostic Telemetry Meters
    const luxEl = document.getElementById("meter-lux-val");
    if (luxEl) luxEl.textContent = "Optimal Daylight (Clear)";
    const wbEl = document.getElementById("meter-wb-val");
    if (wbEl) wbEl.textContent = "Natural Color Balance";
    const snrEl = document.getElementById("meter-snr-val");
    if (snrEl) snrEl.textContent = "Clear & In Focus";
    const resEl = document.getElementById("meter-res-val");
    if (resEl) resEl.textContent = `${origW} × ${origH}px (Sharp)`;

    // Enable Analyze CTA Button!
    analyzeBtn.disabled = false;
    return true;
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
      await new Promise((resolve) => setTimeout(resolve, 16));
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

      // Sync single face box with backend neural bounding box
      if (data.face && data.face.bounding_box && previewImg.naturalWidth && previewImg.naturalHeight) {
        const [bx, by, bw, bh] = data.face.bounding_box;
        const nw = previewImg.naturalWidth;
        const nh = previewImg.naturalHeight;
        renderFaceBox({
          x: (bx / nw) * 100,
          y: (by / nh) * 100,
          w: (bw / nw) * 100,
          h: (bh / nh) * 100,
          isCenter: false
        }, 0);

        // Lock face box tag to calibrated representative skin color from neural model
        if (data.skin_analysis && data.skin_analysis.metrics) {
          const repHex = data.skin_analysis.metrics.representative_hex;
          const dotEl = document.getElementById("face-box-color-dot");
          const hexEl = document.getElementById("face-box-hex");
          if (dotEl) dotEl.style.backgroundColor = repHex;
          if (hexEl) hexEl.textContent = repHex;
        }
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

  // Re-analyze & Another Analysis Actions
  const anotherUploadBtn = document.getElementById("another-upload-btn");
  const anotherCameraBtn = document.getElementById("another-camera-btn");

  function restartAnalysisSession(triggerUpload = false) {
    resultsSection.classList.add("hidden");
    processingSection.classList.add("hidden");
    studioSection.classList.remove("hidden");
    heroSection.classList.remove("hidden");
    resetUploadState();
    window.scrollTo({ top: 0, behavior: "smooth" });
    if (triggerUpload && fileInput) {
      setTimeout(() => {
        fileInput.click();
      }, 350);
    }
  }

  if (reanalyzeBtn) {
    reanalyzeBtn.addEventListener("click", () => restartAnalysisSession(false));
  }

  if (anotherUploadBtn) {
    anotherUploadBtn.addEventListener("click", () => restartAnalysisSession(true));
  }

  if (anotherCameraBtn) {
    anotherCameraBtn.addEventListener("click", () => {
      restartAnalysisSession(false);
      if (cameraBtn) {
        setTimeout(() => {
          cameraBtn.click();
        }, 350);
      }
    });
  }

  // --- Gender / Styling Profile Tracking ---
  let currentGender = "all";
  let cachedApiData = null;

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

  function getFabricPairing(name, hex) {
    const n = (name || "").toLowerCase();
    if (n.includes("black") || n.includes("obsidian")) return "Super 160s Worsted";
    if (n.includes("gold") || n.includes("champagne") || n.includes("ochre")) return "Sartorial Jacquard";
    if (n.includes("cognac") || n.includes("camel") || n.includes("brown") || n.includes("rust")) return "Cashmere & Wool";
    if (n.includes("olive") || n.includes("spruce") || n.includes("green")) return "Silk Shantung";
    if (n.includes("terracotta") || n.includes("crimson") || n.includes("red")) return "Tuscan Velvet";
    if (n.includes("navy") || n.includes("blue") || n.includes("sapphire")) return "Melton Overcoat";
    return "Fine Knitwear & Silk";
  }

  function getCategoryTag(cat, name) {
    const n = (name || "").toLowerCase();
    if (n.includes("coat") || n.includes("jacket") || n.includes("trench")) return "Outerwear";
    if (n.includes("suit") || n.includes("tuxedo") || n.includes("blazer")) return "Tailored Suiting";
    if (n.includes("shirt") || n.includes("blouse") || n.includes("silk")) return "Shirting & Silk";
    if (n.includes("dress") || n.includes("gown") || n.includes("evening")) return "Formal Eveningwear";
    if (n.includes("watch") || n.includes("gold") || n.includes("silver") || n.includes("bronze")) return "Fine Horology";
    return cat || "Haute Curation";
  }

  function handleGenderSelect(selectedGender, isManual = true) {
    if (isManual) {
      userExplicitlyChoseGender = true;
    }
    currentGender = selectedGender;

    // Sync pills across upload selector
    document.querySelectorAll("#upload-gender-options .gender-pill").forEach((pill) => {
      pill.classList.toggle("active", pill.getAttribute("data-gender") === currentGender);
    });

    // Determine effective gender
    let effectiveGender = currentGender;
    if (effectiveGender === "auto") {
      effectiveGender = (cachedApiData && cachedApiData.gender && cachedApiData.gender.detected)
        ? cachedApiData.gender.detected.toLowerCase()
        : "female";
    }

    // Render interactive style switcher in results banner
    const resultsGenderOptions = document.getElementById("results-gender-options");
    if (resultsGenderOptions) {
      resultsGenderOptions.innerHTML = `
        <button type="button" class="gender-pill ${effectiveGender === 'female' ? 'active' : ''}" data-gender="female">👗 Women's</button>
        <button type="button" class="gender-pill ${effectiveGender === 'male' ? 'active' : ''}" data-gender="male">👔 Men's</button>
        <button type="button" class="gender-pill ${effectiveGender === 'all' ? 'active' : ''}" data-gender="all">👥 All Styles</button>
      `;
      resultsGenderOptions.querySelectorAll(".gender-pill").forEach((pill) => {
        pill.addEventListener("click", () => {
          const g = pill.getAttribute("data-gender");
          handleGenderSelect(g, true);
        });
      });
    }

    const switchLabel = document.getElementById("gender-switch-label");
    if (switchLabel) switchLabel.textContent = "Switch Style:";

    updateGenderView(effectiveGender);

    // Update banner UI
    const bannerTitleText = document.getElementById("gender-banner-title-text");
    if (bannerTitleText) bannerTitleText.textContent = "Style Profile:";

    const bannerIcon = document.getElementById("gender-banner-icon");
    const bannerLabel = document.getElementById("gender-banner-label");
    const bannerBadge = document.getElementById("gender-banner-badge");
    const bannerDesc = document.getElementById("gender-banner-desc");

    const aiDetected = (cachedApiData && cachedApiData.gender && cachedApiData.gender.detected) || "Female";
    const aiConf = (cachedApiData && cachedApiData.gender && (cachedApiData.gender.confidence_percentage || Math.round((cachedApiData.gender.confidence || 0.88) * 100))) || 88;

    if (effectiveGender === "female") {
      if (bannerIcon) bannerIcon.textContent = "👗";
      if (bannerLabel) bannerLabel.textContent = "Women's Style";
      if (bannerBadge) {
        bannerBadge.textContent = (currentGender === "auto") ? ` Detected: ${aiDetected} (${aiConf}%)` : " Selected Profile";
        bannerBadge.className = "gender-banner-badge auto-badge";
      }
      if (bannerDesc) {
        bannerDesc.textContent = "Color palettes, cosmetics, evening wear, and fine jewelry are tailored for haute womenswear styling.";
      }
    } else if (effectiveGender === "male") {
      if (bannerIcon) bannerIcon.textContent = "👔";
      if (bannerLabel) bannerLabel.textContent = "Men's Style";
      if (bannerBadge) {
        bannerBadge.textContent = (currentGender === "auto") ? ` Detected: ${aiDetected} (${aiConf}%)` : " Selected Profile";
        bannerBadge.className = "gender-banner-badge auto-badge";
      }
      if (bannerDesc) {
        bannerDesc.textContent = "Color palettes, suiting staples, and luxury timepieces are calibrated specifically for menswear styling.";
      }
    } else {
      if (bannerIcon) bannerIcon.textContent = "👥";
      if (bannerLabel) bannerLabel.textContent = "All Styles (Universal)";
      if (bannerBadge) {
        bannerBadge.textContent = " Universal Harmony";
        bannerBadge.className = "gender-banner-badge auto-badge";
      }
      if (bannerDesc) {
        bannerDesc.textContent = "Comprehensive styling recommendations across tailored suiting, evening wear, cosmetics, and universal color harmonies.";
      }
    }

    // Re-filter results display if data is loaded
    if (cachedApiData && resultsSection && !resultsSection.classList.contains("hidden")) {
      filterAndRenderGenderSpecifics(cachedApiData, effectiveGender);
    }
  }

  function filterAndRenderGenderSpecifics(data, genderMode) {
    const ut = (data.undertone && data.undertone.label) || "Warm";
    const allMatching = (data.recommendations && data.recommendations.world_spectrum) || [];
    let palette = (data.palette || []).slice();
    const skinMetrics = (data.skin_analysis && data.skin_analysis.metrics) || {};
    const skinL = (skinMetrics.cielab && parseFloat(skinMetrics.cielab.L)) || 60.0;
    const isLightSkin = skinL >= 58.0;

    const blackColor = {
      name: "Obsidian Black",
      hex: "#0A0A0A",
      rgb: [10, 10, 10],
      category: "Neutrals",
      tags: ["core", "neutral", "contrast", "essential"],
      description: "A high-contrast signature neutral that creates razor-sharp definition and illuminates fair to light complexions."
    };

    const avoidBlack = {
      name: "Pitch Black",
      hex: "#000000",
      reason: "Solid pitch black drains radiance and creates a harsh, low-contrast flattening effect on deeper skin tones. Opt instead for rich midnight navy, espresso brown, or deep charcoal."
    };

    let clothingRecs = (data.recommendations && data.recommendations.clothing) || [];
    let makeupRecs = (data.recommendations && data.recommendations.makeup) || [];
    let accessoryRecs = (data.recommendations && data.recommendations.accessories) || [];
    let neutralRecs = (data.recommendations && data.recommendations.neutrals) || [];
    let avoidList = (data.less_recommended || []).slice();
    let stylistSummary = data.stylist_summary || "";

    if (genderMode === "male") {
      const maleTags = ["core", "warm_earthy", "deep", "earthy", "classic", "autumn", "winter"];
      if (allMatching.length > 0) {
        palette = allMatching.filter(c => c.category === "Clothing" || c.category === "Neutrals")
          .slice()
          .sort((a, b) => {
            const aM = (a.tags || []).filter(t => maleTags.includes(t)).length + (["blue", "green", "brown", "metal", "neutral"].includes(a.family) ? 2 : 0);
            const bM = (b.tags || []).filter(t => maleTags.includes(t)).length + (["blue", "green", "brown", "metal", "neutral"].includes(b.family) ? 2 : 0);
            return bM - aM;
          });
      }

      clothingRecs = clothingRecs.filter(c => {
        const desc = (c.description || "").toLowerCase();
        return !desc.includes("dress") && !desc.includes("skirt") && !desc.includes("blouse");
      });

      makeupRecs = [];

      accessoryRecs = accessoryRecs.filter(c => {
        const desc = (c.description || "").toLowerCase();
        const name = (c.name || "").toLowerCase();
        return desc.includes("watch") || desc.includes("cuff") || desc.includes("buckle") || desc.includes("leather") || desc.includes("metal") || name.includes("gold") || name.includes("silver") || name.includes("bronze") || name.includes("titanium") || name.includes("leather");
      });

      stylistSummary = ut === "Warm"
        ? (isLightSkin
          ? "Command presence in rich earthy menswear: tailored camel coats, crisp obsidian black accents, olive blazers, and warm bronze or gold chronographs."
          : "Command presence in rich earthy menswear: tailored camel overcoats, deep olive blazers, rich espresso leather, and warm bronze timepieces (skip pitch black for navy or espresso).")
        : ut === "Cool"
        ? (isLightSkin
          ? "Exude sharp authority with high-contrast masculine neutrals: obsidian black tailoring, midnight navy, crisp icy blue shirts, and brushed platinum timepieces."
          : "Exude sharp authority with rich masculine neutrals: deep midnight navy suiting, charcoal cashmere, icy blue shirting, and brushed platinum or titanium timepieces.")
        : (isLightSkin
          ? "Effortless modern sophistication: slate grey tailoring, obsidian black essentials, rich plum knitwear, and dual-tone stainless steel watches."
          : "Effortless modern sophistication: slate grey tailoring, espresso leather footwear, muted sage polos, and dual-tone stainless steel watches.");

    } else if (genderMode === "female") {
      const femTags = ["core", "vibrant", "accent", "spring", "summer", "jewelry"];
      if (allMatching.length > 0) {
        palette = allMatching.filter(c => c.category === "Clothing" || (c.tags && c.tags.includes("core")))
          .slice()
          .sort((a, b) => {
            const aF = (a.tags || []).filter(t => femTags.includes(t)).length;
            const bF = (b.tags || []).filter(t => femTags.includes(t)).length;
            return bF - aF;
          });
      }

      stylistSummary = ut === "Warm"
        ? (isLightSkin
          ? "Illuminate your beauty with rich terracotta silks, crisp obsidian black contrast, warm golden amber jewelry, and cozy camel outerwear."
          : "Illuminate your beauty with rich terracotta silks, deep chocolate leather, warm golden amber jewelry, and peachy coral cosmetics.")
        : ut === "Cool"
        ? (isLightSkin
          ? "Radiate elegance in sapphire jewel tones, striking obsidian black evening wear, rose-petal blush, and glistening platinum jewelry."
          : "Radiate elegance in deep sapphire jewel tones, rich midnight navy, rose-petal blush, and glistening platinum jewelry.")
        : (isLightSkin
          ? "Flawless grace across dusty rose gowns, obsidian black accents, muted teal blouses, and champagne jewelry."
          : "Flawless grace across dusty rose gowns, deep plum silk, muted teal blouses, and balanced neutral cosmetics.");
    }

    // Black handling according to skin tone lightness
    if (isLightSkin) {
      if (!clothingRecs.some(c => (c.name || "").toLowerCase().includes("black"))) {
        clothingRecs = [blackColor, ...clothingRecs];
      }
      if (!palette.some(c => (c.name || "").toLowerCase().includes("black"))) {
        palette = [palette[0] || blackColor, blackColor, ...palette.slice(1)];
      }
      if (!neutralRecs.some(c => (c.name || "").toLowerCase().includes("black"))) {
        neutralRecs = [blackColor, ...neutralRecs];
      }
      avoidList = avoidList.filter(c => !(c.name || "").toLowerCase().includes("black"));
    } else {
      clothingRecs = clothingRecs.filter(c => !(c.name || "").toLowerCase().includes("black") && c.hex !== "#0A0A0A" && c.hex !== "#000000");
      palette = palette.filter(c => !(c.name || "").toLowerCase().includes("black") && c.hex !== "#0A0A0A" && c.hex !== "#000000");
      neutralRecs = neutralRecs.filter(c => !(c.name || "").toLowerCase().includes("black") && c.hex !== "#0A0A0A" && c.hex !== "#000000");
      if (!avoidList.some(a => (a.name || "").toLowerCase().includes("black"))) {
        avoidList = [avoidBlack, ...avoidList];
      }
    }

    // Curate: Show ONLY the most flattering, essential items (clean, luxury presentation)
    palette = palette.slice(0, 7);
    clothingRecs = clothingRecs.slice(0, 8);
    makeupRecs = makeupRecs.slice(0, 6);
    accessoryRecs = accessoryRecs.slice(0, 5);
    neutralRecs = neutralRecs.slice(0, 4);
    avoidList = avoidList.slice(0, 4);

    const summaryElem = document.getElementById("stylist-summary");
    if (summaryElem) summaryElem.textContent = stylistSummary;

    // Render palette
    const swatchesGrid = document.getElementById("swatches-grid");
    if (swatchesGrid && palette.length > 0) {
      swatchesGrid.innerHTML = "";
      palette.forEach((color) => {
        const card = document.createElement("div");
        card.className = "swatch-card";
        const lumVal = Math.round((0.299 * (color.rgb ? color.rgb[0] : 120) + 0.587 * (color.rgb ? color.rgb[1] : 120) + 0.114 * (color.rgb ? color.rgb[2] : 120)) / 2.55);
        const fabric = getFabricPairing(color.name, color.hex);
        card.innerHTML = `
          <div class="swatch-color" style="background-color: ${color.hex}">
            <span class="swatch-lum-badge">L* ${lumVal}</span>
          </div>
          <div class="swatch-meta">
            <div class="swatch-name" title="${color.name}">${color.name}</div>
            <div class="swatch-hex">${color.hex}</div>
            <div class="swatch-fabric">${fabric}</div>
          </div>
        `;
        card.addEventListener("click", () => copyToClipboard(color.hex, color.name));
        swatchesGrid.appendChild(card);
      });
    }

    renderRecGrid("rec-clothing-grid", clothingRecs, "Clothing");
    renderRecGrid("rec-makeup-grid", makeupRecs, "Cosmetics");
    renderRecGrid("rec-accessories-grid", accessoryRecs, "Fine Horology");
    renderRecGrid("rec-neutrals-grid", neutralRecs, "Foundational");
    renderAvoidGrid("rec-avoid-grid", avoidList);
  }

  // Wire up upload gender pill selector group
  document.querySelectorAll("#upload-gender-options .gender-pill").forEach((pill) => {
    pill.addEventListener("click", () => {
      const g = pill.getAttribute("data-gender");
      handleGenderSelect(g, true);
    });
  });

  // --- Render Results ---
  function renderResults(data) {
    cachedApiData = data;

    // Auto-detect gender from API response and apply styling profile
    handleGenderSelect(currentGender, false);
    const undertone = data.undertone.label;
    const confidencePct = data.undertone.confidence_percentage;

    // 1. Undertone Hero Badge & Seasonal Watermark
    const badge = document.getElementById("undertone-badge");
    const seasonName = (data.seasonal_harmony && data.seasonal_harmony.season_name) || "Warm Autumn Deep";
    if (badge) {
      badge.textContent = `${undertone.toUpperCase()} · ${seasonName.toUpperCase()}`;
      badge.className = `undertone-badge ${undertone}`;
    }

    const watermark = document.getElementById("season-watermark");
    if (watermark) {
      watermark.textContent = (data.seasonal_harmony && data.seasonal_harmony.watermark) || (undertone === "Warm" ? "AUTUMN" : (undertone === "Cool" ? "WINTER" : "SUMMER"));
    }

    const confVal = document.getElementById("confidence-val");
    if (confVal) confVal.textContent = `${confidencePct}%`;

    const confBar = document.getElementById("confidence-bar");
    if (confBar) confBar.style.width = `${confidencePct}%`;

    // Probability breakdown
    const probBreakdown = document.getElementById("prob-breakdown");
    if (probBreakdown && data.undertone.probabilities) {
      probBreakdown.innerHTML = `
        <div class="prob-bar-item">
          <div class="prob-bar-info">
            <span class="prob-bar-label">Warm (Golden & Peach Tones)</span>
            <span class="prob-bar-pct">${Math.round((data.undertone.probabilities.Warm || 0) * 100)}%</span>
          </div>
          <div class="prob-track">
            <div class="prob-fill-warm" style="width: ${Math.round((data.undertone.probabilities.Warm || 0) * 100)}%;"></div>
          </div>
        </div>
        <div class="prob-bar-item">
          <div class="prob-bar-info">
            <span class="prob-bar-label">Neutral (Balanced Harmony)</span>
            <span class="prob-bar-pct">${Math.round((data.undertone.probabilities.Neutral || 0) * 100)}%</span>
          </div>
          <div class="prob-track">
            <div class="prob-fill-neutral" style="width: ${Math.round((data.undertone.probabilities.Neutral || 0) * 100)}%;"></div>
          </div>
        </div>
        <div class="prob-bar-item">
          <div class="prob-bar-info">
            <span class="prob-bar-label">Cool (Rosy & Blue Tones)</span>
            <span class="prob-bar-pct">${Math.round((data.undertone.probabilities.Cool || 0) * 100)}%</span>
          </div>
          <div class="prob-track">
            <div class="prob-fill-cool" style="width: ${Math.round((data.undertone.probabilities.Cool || 0) * 100)}%;"></div>
          </div>
        </div>
      `;
    }

    const underExpl = document.getElementById("undertone-explanation");
    if (underExpl) underExpl.textContent = data.undertone.explanation;

    // Key factors
    const keyFactorsContainer = document.getElementById("key-factors");
    if (keyFactorsContainer && data.undertone.key_factors) {
      keyFactorsContainer.innerHTML = "";
      data.undertone.key_factors.forEach((f) => {
        const div = document.createElement("div");
        div.className = "factor-item";
        div.textContent = f;
        keyFactorsContainer.appendChild(div);
      });
    }

    // 2. Skin Metrics & Color Swatch
    const skinMetrics = data.skin_analysis.metrics;
    const repSwatch = document.getElementById("rep-swatch");
    if (repSwatch) repSwatch.style.backgroundColor = skinMetrics.representative_hex;
    const repHex = document.getElementById("rep-hex");
    if (repHex) repHex.textContent = `${skinMetrics.representative_hex} · ${(skinMetrics.phototype_estimate || '').split('—')[0] || ''}`;
    const repPhototype = document.getElementById("rep-phototype");
    if (repPhototype) repPhototype.textContent = skinMetrics.phototype_estimate || '';

    const labLEl = document.getElementById("metric-lab-l");
    if (labLEl) labLEl.textContent = skinMetrics.cielab ? skinMetrics.cielab.L : '';
    const labAEl = document.getElementById("metric-lab-a");
    if (labAEl) labAEl.textContent = skinMetrics.cielab ? `${skinMetrics.cielab.a >= 0 ? "+" : ""}${skinMetrics.cielab.a}` : '';
    const labBEl = document.getElementById("metric-lab-b");
    if (labBEl) labBEl.textContent = skinMetrics.cielab ? `${skinMetrics.cielab.b >= 0 ? "+" : ""}${skinMetrics.cielab.b}` : '';
    const itaEl = document.getElementById("metric-ita");
    if (itaEl) itaEl.textContent = skinMetrics.ita_angle !== undefined ? `${skinMetrics.ita_angle >= 0 ? "+" : ""}${skinMetrics.ita_angle}°` : '';
    const hsvEl = document.getElementById("metric-hsv-h");
    if (hsvEl) hsvEl.textContent = skinMetrics.hsv ? `${skinMetrics.hsv.H_deg}°` : '';

    // Update Micro-Extract Swatches in Studio Telemetry
    const sample1 = document.getElementById("sample-color-1");
    const sample2 = document.getElementById("sample-color-2");
    const sample3 = document.getElementById("sample-color-3");
    const sample4 = document.getElementById("sample-color-4");
    const hex1 = document.getElementById("sample-hex-1");
    const hex2 = document.getElementById("sample-hex-2");
    const hex3 = document.getElementById("sample-hex-3");
    const hex4 = document.getElementById("sample-hex-4");

    if (sample1) sample1.style.background = skinMetrics.representative_hex;
    if (hex1) hex1.textContent = skinMetrics.representative_hex;

    const hexVal2 = (data.skin_harmonies && data.skin_harmonies[1]) ? data.skin_harmonies[1].hex : skinMetrics.representative_hex;
    const hexVal3 = (data.skin_harmonies && data.skin_harmonies[2]) ? data.skin_harmonies[2].hex : skinMetrics.representative_hex;
    const hexVal4 = (data.skin_harmonies && data.skin_harmonies[0]) ? data.skin_harmonies[0].hex : skinMetrics.representative_hex;

    if (sample2) sample2.style.background = hexVal2;
    if (hex2) hex2.textContent = hexVal2;
    if (sample3) sample3.style.background = hexVal3;
    if (hex3) hex3.textContent = hexVal3;
    if (sample4) sample4.style.background = hexVal4;
    if (hex4) hex4.textContent = hexVal4;

    // 3. Draw Autonomous Skin Canvas
    drawFacialLandmarksCanvas(skinMetrics.representative_hex, data.undertone.label);

    // 4. Personalized Core Palette
    const stylistSummaryEl = document.getElementById("stylist-summary");
    if (stylistSummaryEl) stylistSummaryEl.textContent = data.stylist_summary || "";
    if (data.seasonal_harmony) {
      const seasonTitleEl = document.getElementById("season-title");
      if (seasonTitleEl) seasonTitleEl.textContent = data.seasonal_harmony.season_name || "";
    }

    const swatchesGridMain = document.getElementById("swatches-grid");
    swatchesGridMain.innerHTML = "";
    (data.palette || []).forEach((color) => {
      const card = document.createElement("div");
      card.className = "swatch-card";
      const lumVal = Math.round((0.299 * (color.rgb ? color.rgb[0] : 120) + 0.587 * (color.rgb ? color.rgb[1] : 120) + 0.114 * (color.rgb ? color.rgb[2] : 120)) / 2.55);
      const fabric = getFabricPairing(color.name, color.hex);
      card.innerHTML = `
        <div class="swatch-color" style="background-color: ${color.hex}">
          <span class="swatch-lum-badge">L* ${lumVal}</span>
        </div>
        <div class="swatch-meta">
          <div class="swatch-name" title="${color.name}">${color.name}</div>
          <div class="swatch-hex">${color.hex}</div>
          <div class="swatch-fabric">${fabric}</div>
        </div>
      `;
      card.addEventListener("click", () => {
        copyToClipboard(color.hex, color.name);
      });
      swatchesGridMain.appendChild(card);
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
          <div class="harmony-color" style="background-color: ${h.hex}"></div>
          <div class="harmony-type">${h.badge || h.harmony_type || "Harmony"}</div>
          <div class="harmony-hex">${h.hex}</div>
        `;
        card.addEventListener("click", () => copyToClipboard(h.hex, h.name));
        skinGrid.appendChild(card);
      });
    }

    // Render Analyzed Image Atmosphere
    const atmSwatches = document.getElementById("atmosphere-swatches");
    if (atmSwatches) {
      atmSwatches.innerHTML = `
        <div class="atmosphere-dot" style="background: ${skinMetrics.representative_hex}" title="Skin Tone (${skinMetrics.representative_hex})"></div>
      `;
    }

    // 5. Categorized Recommendations
    renderRecGrid("rec-clothing-grid", data.recommendations.clothing, "Clothing");
    renderRecGrid("rec-makeup-grid", data.recommendations.makeup, "Cosmetics");
    renderRecGrid("rec-accessories-grid", data.recommendations.accessories, "Fine Horology");
    renderRecGrid("rec-neutrals-grid", data.recommendations.neutrals, "Foundational");
    renderAvoidGrid("rec-avoid-grid", data.less_recommended);

    document.getElementById("foundation-advice-text").textContent = data.foundation_advice;
  }

  function renderRecGrid(containerId, items, defaultCategory) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = "";
    if (!items || items.length === 0) {
      container.innerHTML = "<p style='color: var(--text-muted); font-size: 0.85rem; padding: 1rem;'>No items found for this category.</p>";
      return;
    }

    items.forEach((item) => {
      const card = document.createElement("div");
      card.className = "rec-card";
      const tag = getCategoryTag(defaultCategory, item.name);
      card.innerHTML = `
        <div class="rec-card-media" style="background: linear-gradient(135deg, ${item.hex}40, #0A0E16);">
          <span class="rec-tag">${tag}</span>
          <div class="rec-swatch-dot" style="background: ${item.hex};"></div>
        </div>
        <div class="rec-card-body">
          <div>
            <div class="rec-name">${item.name}</div>
            <p class="rec-desc">${item.description || item.sub_category || ""}</p>
          </div>
          <div class="rec-card-footer">
            <span class="rec-color-label">Atelier Shade</span>
            <span class="rec-hex-badge">${item.hex}</span>
          </div>
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
    if (!container) return;
    container.innerHTML = "";
    if (!items || items.length === 0) {
      container.innerHTML = "<p style='color: var(--text-muted); font-size: 0.85rem; padding: 1rem;'>No specific avoid rules for this undertone.</p>";
      return;
    }

    items.forEach((item) => {
      const card = document.createElement("div");
      card.className = "rec-card rec-card-avoid";
      card.innerHTML = `
        <div class="rec-card-media" style="background: linear-gradient(135deg, ${item.hex}40, #0A0E16);">
          <span class="rec-tag">Antagonistic</span>
          <div class="rec-swatch-dot" style="background: ${item.hex};"></div>
        </div>
        <div class="rec-card-body">
          <div>
            <div class="rec-name">${item.name}</div>
            <p class="rec-desc">${item.reason || item.description || "Incompatible spectral wavelength."}</p>
          </div>
          <div class="rec-card-footer">
            <span class="rec-color-label" style="color: var(--danger);">Avoid Shade</span>
            <span class="rec-hex-badge">${item.hex}</span>
          </div>
        </div>
      `;
      container.appendChild(card);
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
  
  // Global restrictions to disable copy, cut, paste and context menu
  document.addEventListener('copy', (e) => e.preventDefault());
  document.addEventListener('cut', (e) => e.preventDefault());
  document.addEventListener('paste', (e) => e.preventDefault());
  document.addEventListener('contextmenu', (e) => e.preventDefault());
});
