/**
 * OTTERLOOK AI - Frontend Application Controller
 * Handles image upload, pipeline animations, API communication,
 * landmark canvas overlay, and dynamic palette rendering.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Origin-aware API endpoint builder: prefers same-origin /api/* in production
  // and falls back to local FastAPI (8000) when running under file:// or Streamlit (8501)
  function buildApiEndpoints(path) {
    const cleanPath = path.startsWith("/") ? path : `/${path}`;
    const isLocalNonApiOrigin =
      window.location.protocol === "file:" ||
      window.location.protocol === "about:" ||
      window.location.port === "8501" ||
      ((window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") &&
        window.location.port !== "8000");
    if (isLocalNonApiOrigin) {
      return [
        `http://127.0.0.1:8000${cleanPath}`,
        `http://localhost:8000${cleanPath}`,
        cleanPath
      ];
    }
    return [cleanPath];
  }

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
  const errorActionBtns = document.getElementById("error-action-btns");
  const bannerCameraBtn = document.getElementById("banner-camera-btn");
  const bannerUploadBtn = document.getElementById("banner-upload-btn");
  const noFaceOverlay = document.getElementById("no-face-overlay");
  const overlayCameraBtn = document.getElementById("overlay-camera-btn");
  const overlayUploadBtn = document.getElementById("overlay-upload-btn");

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
  let currentGender = "all";
  let selectedGenderMode = "all";
  let currentClothingType = "all";
  let currentWeather = "all";
  let cachedApiData = null;

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
  let uploadGenerationId = 0;
  let faceCheckAbortController = null;
  let cameraMeterInterval = null;
  let originalUploadedFile = null;
  let originalImageBitmap = null;
  let detectedFacesList = [];
  let selectedFaceIndex = 0;
  let isAutoCroppedPortrait = false;

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

      // Start live brightness guidance meter while camera is open
      if (cameraMeterInterval) clearInterval(cameraMeterInterval);
      const liveMeterEl = document.getElementById("camera-live-meter");
      const meterCanvas = document.createElement("canvas");
      meterCanvas.width = 64;
      meterCanvas.height = 48;
      const meterCtx = meterCanvas.getContext("2d", { willReadFrequently: true });
      cameraMeterInterval = setInterval(() => {
        if (!cameraVideo || !cameraVideo.videoWidth || !liveMeterEl) return;
        meterCtx.drawImage(cameraVideo, 0, 0, 64, 48);
        const px = meterCtx.getImageData(16, 8, 32, 32).data;
        let sum = 0;
        for (let i = 0; i < px.length; i += 4) {
          sum += 0.299 * px[i] + 0.587 * px[i + 1] + 0.114 * px[i + 2];
        }
        const avg = sum / (px.length / 4);
        if (avg < 55) {
          liveMeterEl.textContent = "Too Dark • Move toward daylight";
          liveMeterEl.className = "camera-live-meter warn";
        } else if (avg > 215) {
          liveMeterEl.textContent = "Too Bright / Glare • Soften light";
          liveMeterEl.className = "camera-live-meter warn";
        } else {
          liveMeterEl.textContent = "Optimal Daylight • Center face in oval";
          liveMeterEl.className = "camera-live-meter good";
        }
      }, 400);
    } catch (err) {
      console.warn("Webcam stream unavailable, falling back to device camera input:", err);
      if (cameraInput) cameraInput.click();
    }
  }

  function stopCameraStream() {
    if (cameraMeterInterval) {
      clearInterval(cameraMeterInterval);
      cameraMeterInterval = null;
    }
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
    cameraCaptureBtn.addEventListener("click", async () => {
      if (!cameraVideo || !cameraVideo.videoWidth) return;
      const ovalEl = document.querySelector(".camera-face-oval");

      // Compute oval geometry normalized to video frame (0..1) BEFORE closing camera modal
      let ovalCx = 0.5, ovalCy = 0.5, ovalW = 0.56, ovalH = 0.74;
      if (ovalEl) {
        const vRect = cameraVideo.getBoundingClientRect();
        const oRect = ovalEl.getBoundingClientRect();
        if (vRect.width > 0 && vRect.height > 0 && oRect.width > 0 && oRect.height > 0) {
          ovalCx = ((oRect.left + oRect.width / 2) - vRect.left) / vRect.width;
          ovalCy = ((oRect.top + oRect.height / 2) - vRect.top) / vRect.height;
          ovalW = oRect.width / vRect.width;
          ovalH = oRect.height / vRect.height;
        }
      }

      const snapCanvas = document.createElement("canvas");
      snapCanvas.width = cameraVideo.videoWidth;
      snapCanvas.height = cameraVideo.videoHeight;
      const snapCtx = snapCanvas.getContext("2d");
      if (currentFacingMode === "user") {
        snapCtx.translate(snapCanvas.width, 0);
        snapCtx.scale(-1, 1);
      }
      snapCtx.drawImage(cameraVideo, 0, 0);

      // 1. Click/capture the picture first and close the camera modal
      const snapDataUrl = snapCanvas.toDataURL("image/jpeg", 0.92);
      stopCameraStream();

      hideError();
      previewImg.src = snapDataUrl;
      uploadPrompt.classList.add("hidden");
      previewBox.classList.remove("hidden");
      analyzeBtn.disabled = true;
      currentFile = null;

      const snapImg = new Image();
      snapImg.src = snapDataUrl;
      await new Promise((resolve) => {
        snapImg.onload = resolve;
        snapImg.onerror = resolve;
      });

      // 2. Determine whether a face fits inside the oval
      const detRes = await verifyHumanFaceWithYOLO(snapImg, uploadGenerationId);
      if (detRes && !detRes.networkError) {
        const allFaces = (detRes.faces && detRes.faces.length)
          ? detRes.faces
          : (detRes.bounding_box ? [detRes.bounding_box] : []);

        const inOvalFaces = allFaces
          .map((f) => {
            const fcx = (f.pctX + f.pctW / 2) / 100;
            const fcy = (f.pctY + f.pctH / 2) / 100;
            const fw = f.pctW / 100;
            const fh = f.pctH / 100;
            const rx = Math.max(0.15, ovalW * 0.5);
            const ry = Math.max(0.15, ovalH * 0.5);
            const dist2 = Math.pow((fcx - ovalCx) / rx, 2) + Math.pow((fcy - ovalCy) / ry, 2);
            const fitsSize = fw >= ovalW * 0.25 && fh >= ovalH * 0.22;
            return { face: f, dist2, inside: dist2 <= 1.1 && fitsSize };
          })
          .filter((item) => item.inside)
          .sort((a, b) => a.dist2 - b.dist2);

        if (inOvalFaces.length === 0) {
          analyzeBtn.disabled = true;
          currentFile = null;
          showError("⚠️ Face is not inside the oval. Please put your face inside the oval and capture again.", true);
          return;
        }

        // 3. Only keep & analyze the face inside the oval (even when multiple faces appear)
        const targetFace = inOvalFaces[0].face;
        const cropped = await cropPortraitAroundFace(snapImg, targetFace);
        if (cropped && cropped.file) {
          handleFileSelection(cropped.file);
          return;
        }
      }

      // Offline fallback if /api/detect-face was unreachable
      snapCanvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], "selfie.jpg", { type: "image/jpeg" });
          handleFileSelection(file);
        }
      }, "image/jpeg", 0.92);
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


  async function handleFileSelection(file) {
    if (!file.type.match(/image\/(jpeg|jpg|png|webp)/)) {
      showError("Please upload a valid JPG, JPEG, or PNG image file.");
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      showError("File size exceeds 15MB limit. Please upload a smaller image.");
      return;
    }

    const genId = ++uploadGenerationId;
    if (faceCheckAbortController) {
      try { faceCheckAbortController.abort(); } catch (e) {}
    }

    hideError();

    // Normalize EXIF orientation and downscale oversized mobile photos (> 1600px)
    let normalizedFile = file;
    let previewDataUrl = null;
    try {
      if (typeof createImageBitmap === "function") {
        const bmp = await createImageBitmap(file);
        const maxSide = 900;
        const origMax = Math.max(bmp.width, bmp.height);
        if (origMax > maxSide || file.size > 900 * 1024) {
          const scale = origMax > maxSide ? (maxSide / origMax) : 1;
          const nw = Math.max(100, Math.round(bmp.width * scale));
          const nh = Math.max(100, Math.round(bmp.height * scale));
          const c = document.createElement("canvas");
          c.width = nw;
          c.height = nh;
          c.getContext("2d").drawImage(bmp, 0, 0, nw, nh);
          const blob = await new Promise((resolve) => c.toBlob(resolve, "image/jpeg", 0.86));
          if (blob) {
            normalizedFile = new File([blob], (file.name || "portrait").replace(/\.[^.]+$/, "") + ".jpg", { type: "image/jpeg" });
            previewDataUrl = c.toDataURL("image/jpeg", 0.86);
          }
        }
        bmp.close();
      }
    } catch (normErr) {
      console.warn("Client resize/EXIF normalization skipped:", normErr);
    }

    if (genId !== uploadGenerationId) return;
    currentFile = normalizedFile;
    originalUploadedFile = normalizedFile;
    detectedFacesList = [];
    selectedFaceIndex = 0;
    isAutoCroppedPortrait = false;
    const autoBar = document.getElementById("face-autoselect-bar");
    if (autoBar) autoBar.classList.add("hidden");

    const loadPreviewAndVerify = (dataUrl) => {
      if (genId !== uploadGenerationId) return;
      previewImg.src = dataUrl;
      uploadPrompt.classList.add("hidden");
      previewBox.classList.remove("hidden");
      analyzeBtn.disabled = true;

      const img = new Image();
      img.src = dataUrl;
      img.onload = () => {
        if (genId !== uploadGenerationId) return;
        currentImageBitmap = img;
        originalImageBitmap = img;
        checkImageQualityAndAutoColor(img, genId, false);
      };
    };

    if (previewDataUrl) {
      loadPreviewAndVerify(previewDataUrl);
    } else {
      const reader = new FileReader();
      reader.onload = (e) => loadPreviewAndVerify(e.target.result);
      reader.readAsDataURL(normalizedFile);
    }
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

  // --- Inclusive Skin Filter across Fitzpatrick Types I to VI ---
  function isSkinPixel(r, g, b) {
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
    if (delta > 0) {
      if (maxC === r) hue = ((g - b) / delta) % 6;
      else if (maxC === g) hue = (b - r) / delta + 2;
      else hue = (r - g) / delta + 4;
      hue = (hue * 60 + 360) % 360;
    }
    return ((hue >= 0 && hue <= 58) || (hue >= 328 && hue <= 360));
  }

  // --- Unified Anatomical Facial Dermis & Multi-Region Extractor ---
  function extractFacialDermisAndRegions(imgData, w, h) {
    const candidateSkin = [];
    for (let y = 0; y < h; y += 2) {
      for (let x = 0; x < w; x += 2) {
        const idx = (y * w + x) * 4;
        const r = imgData[idx], g = imgData[idx + 1], b = imgData[idx + 2];
        if (isSkinPixel(r, g, b)) {
          const yP = 0.299 * r + 0.587 * g + 0.114 * b;
          candidateSkin.push({ r, g, b, lum: yP, x, y });
        }
      }
    }

    if (candidateSkin.length < 40) {
      for (let y = Math.floor(h * 0.10); y < Math.floor(h * 0.85); y += 2) {
        for (let x = Math.floor(w * 0.15); x < Math.floor(w * 0.85); x += 2) {
          const idx = (y * w + x) * 4;
          const r = imgData[idx], g = imgData[idx + 1], b = imgData[idx + 2];
          if (r > 38 && g > 24 && b > 14 && r >= g && r >= b) {
            candidateSkin.push({ r, g, b, lum: 0.299 * r + 0.587 * g + 0.114 * b, x, y });
          }
        }
      }
    }

    // 2. PRIMARY FACE DENSITY PEAK FINDER
    // Locates the subject's face center even when other people or arms are in frame
    const cellStep = Math.max(8, Math.round(Math.min(w, h) * 0.05));
    let bestScore = -1;
    let peakX = Math.round(w * 0.5);
    let peakY = Math.round(h * 0.42);

    const searchRad = Math.max(30, Math.round(Math.min(w, h) * 0.20));
    const searchRadSq = searchRad * searchRad;

    const minGridX = Math.floor(w * 0.22);
    const maxGridX = Math.floor(w * 0.78);
    const minGridY = Math.floor(h * 0.18);
    const maxGridY = Math.floor(h * 0.68);

    for (let gy = minGridY; gy <= maxGridY; gy += cellStep) {
      for (let gx = minGridX; gx <= maxGridX; gx += cellStep) {
        const dxNorm = (gx - w * 0.5) / (w * 0.28);
        const dyNorm = (gy - h * 0.42) / (h * 0.26);
        const centrality = Math.exp(-0.5 * (dxNorm * dxNorm + dyNorm * dyNorm));

        let count = 0;
        for (let i = 0; i < candidateSkin.length; i++) {
          const p = candidateSkin[i];
          const dX = p.x - gx;
          const dY = p.y - gy;
          if (dX * dX + dY * dY <= searchRadSq) {
            count++;
          }
        }

        const score = count * (0.35 + 0.65 * centrality);
        if (score > bestScore) {
          bestScore = score;
          peakX = gx;
          peakY = gy;
        }
      }
    }

    // 3. ISOLATE PRIMARY FACE CLUSTER
    // Excludes background bystanders, arms, hands, desk
    const clusterRadX = Math.max(36, Math.min(Math.round(w * 0.24), Math.round(searchRad * 1.05)));
    const clusterRadY = Math.max(48, Math.min(Math.round(h * 0.32), Math.round(searchRad * 1.35)));

    let faceSkin = candidateSkin.filter(p => 
      Math.abs(p.x - peakX) <= clusterRadX && 
      Math.abs(p.y - peakY) <= clusterRadY
    );
    if (faceSkin.length < 15) {
      faceSkin = candidateSkin.filter(p => 
        Math.abs(p.x - peakX) <= clusterRadX * 1.3 && 
        Math.abs(p.y - peakY) <= clusterRadY * 1.3
      );
    }
    if (faceSkin.length < 10) faceSkin = candidateSkin;

    // 4. PRECISE ANATOMICAL BOUNDING BOX & CHIN ANCHOR
    const xs = faceSkin.map(p => p.x).sort((a, b) => a - b);
    const ys = faceSkin.map(p => p.y).sort((a, b) => a - b);

    const p10X = xs[Math.floor(xs.length * 0.10)];
    const p90X = xs[Math.floor(xs.length * 0.90)];
    // Lowest robust skin pixels on the primary face correspond anatomically to the chin tip (mentalis)
    const chinY = ys[Math.floor(ys.length * 0.90)];

    let rawW = Math.max(45, p90X - p10X);
    let fWidth = Math.max(Math.round(w * 0.20), Math.min(Math.round(w * 0.46), Math.round(rawW * 1.12)));
    
    const cx = xs[Math.floor(xs.length * 0.5)];
    let fLeft = Math.round(cx - fWidth * 0.5);
    if (fLeft < 2) fLeft = 2;
    if (fLeft + fWidth > w - 2) fLeft = Math.max(2, w - fWidth - 2);
    fWidth = Math.min(fWidth, w - fLeft - 2);

    // Human craniofacial proportion: Face Height is 1.34x Bizygomatic Width
    let fHeight = Math.round(fWidth * 1.34);
    
    // Anatomical Chin Anchor: face top aligned upwards from chin landmark
    let fTop = Math.max(2, chinY - fHeight);
    if (fTop + fHeight > h - 2) {
      fHeight = h - fTop - 2;
    }
    const cy = Math.round(fTop + fHeight * 0.5);

    // Circular patch sampling with outlier trimming
    const samplePatch = (targetX, targetY, radius, defR, defG, defB) => {
      let sR = 0, sG = 0, sB = 0, count = 0;
      const patchPixels = [];
      for (let dy = -radius; dy <= radius; dy += 2) {
        for (let dx = -radius; dx <= radius; dx += 2) {
          const px = targetX + dx, py = targetY + dy;
          if (dx * dx + dy * dy <= radius * radius && px >= 0 && px < w && py >= 0 && py < h) {
            const idx = (py * w + px) * 4;
            const r = imgData[idx], g = imgData[idx + 1], b = imgData[idx + 2];
            const lum = 0.299 * r + 0.587 * g + 0.114 * b;
            if (lum >= 30 && lum <= 248 && r >= g * 0.80 && r >= b * 0.80) {
              patchPixels.push({ r, g, b, lum });
            }
          }
        }
      }
      if (patchPixels.length > 4) {
        patchPixels.sort((a, b) => a.lum - b.lum);
        const lCut = Math.floor(patchPixels.length * 0.15);
        const hCut = Math.max(lCut + 1, Math.floor(patchPixels.length * 0.85));
        for (let i = lCut; i < hCut; i++) {
          sR += patchPixels[i].r;
          sG += patchPixels[i].g;
          sB += patchPixels[i].b;
          count++;
        }
      }
      const finalR = count > 0 ? Math.round(sR / count) : defR;
      const finalG = count > 0 ? Math.round(sG / count) : defG;
      const finalB = count > 0 ? Math.round(sB / count) : defB;
      return {
        r: finalR, g: finalG, b: finalB,
        hex: rgbToHex(finalR, finalG, finalB),
        x: targetX, y: targetY,
        pctX: (targetX / w) * 100,
        pctY: (targetY / h) * 100,
        count
      };
    };

    // Baseline color from primary face
    faceSkin.sort((a, b) => a.lum - b.lum);
    const gLow = Math.floor(faceSkin.length * 0.15);
    const gHigh = Math.max(gLow + 1, Math.floor(faceSkin.length * 0.85));
    let baseR = 0, baseG = 0, baseB = 0, baseCount = 0;
    for (let i = gLow; i < gHigh; i++) {
      baseR += faceSkin[i].r; baseG += faceSkin[i].g; baseB += faceSkin[i].b; baseCount++;
    }
    const bR = baseCount > 0 ? Math.round(baseR / baseCount) : 190;
    const bG = baseCount > 0 ? Math.round(baseG / baseCount) : 140;
    const bB = baseCount > 0 ? Math.round(baseB / baseCount) : 105;

    const radArea = Math.max(5, Math.round(fWidth * 0.055));

    // 5. ADAPTIVE FOREHEAD LOCALIZATION (AVOID HAIR / BANGS)
    // Midline scan down hair part to locate exposed glabella / forehead
    let bestFrnY = Math.round(fTop + fHeight * 0.20);
    let bestFrnSkinCount = -1;
    const frnScanMin = Math.round(fTop + fHeight * 0.10);
    const frnScanMax = Math.round(fTop + fHeight * 0.32);

    for (let candY = frnScanMin; candY <= frnScanMax; candY += 2) {
      let candSkinCount = 0;
      let candLumSum = 0;
      let candTotal = 0;
      for (let dy = -4; dy <= 4; dy += 2) {
        for (let dx = -4; dx <= 4; dx += 2) {
          const px = cx + dx, py = candY + dy;
          if (px >= 0 && px < w && py >= 0 && py < h) {
            const idx = (py * w + px) * 4;
            const r = imgData[idx], g = imgData[idx + 1], b = imgData[idx + 2];
            const lum = 0.299 * r + 0.587 * g + 0.114 * b;
            candTotal++;
            candLumSum += lum;
            if (isSkinPixel(r, g, b) && lum >= 48) {
              candSkinCount++;
            }
          }
        }
      }
      const avgLum = candTotal > 0 ? candLumSum / candTotal : 0;
      const score = candSkinCount * (avgLum >= 50 ? 1.5 : 0.4);
      if (score > bestFrnSkinCount) {
        bestFrnSkinCount = score;
        bestFrnY = candY;
      }
    }
    const forehead = samplePatch(cx, bestFrnY, radArea, bR, bG, bB);

    // 6. BILATERAL ZYGOMATIC CHEEKS (BOUND TO PRIMARY FACE)
    const nomLX = Math.round(cx - fWidth * 0.23);
    const nomRX = Math.round(cx + fWidth * 0.23);
    const nomChkY = Math.round(fTop + fHeight * 0.53);

    const refineCheek = (nomX, nomY) => {
      let bestX = nomX, bestY = nomY, bestScore = -1;
      for (let dy = -6; dy <= 6; dy += 3) {
        for (let dx = -6; dx <= 6; dx += 3) {
          const sX = nomX + dx, sY = nomY + dy;
          let validCount = 0;
          for (let r = 0; r < 4; r++) {
            const px = sX + (r % 2 === 0 ? 2 : -2);
            const py = sY + (r < 2 ? 2 : -2);
            if (px >= 0 && px < w && py >= 0 && py < h) {
              const idx = (py * w + px) * 4;
              if (isSkinPixel(imgData[idx], imgData[idx+1], imgData[idx+2])) validCount++;
            }
          }
          if (validCount > bestScore) {
            bestScore = validCount;
            bestX = sX;
            bestY = sY;
          }
        }
      }
      return samplePatch(bestX, bestY, radArea, bR, bG, bB);
    };

    const leftCheek = refineCheek(nomLX, nomChkY);
    const rightCheek = refineCheek(nomRX, nomChkY);
    const cheekR = Math.round((leftCheek.r + rightCheek.r) / 2);
    const cheekG = Math.round((leftCheek.g + rightCheek.g) / 2);
    const cheekB = Math.round((leftCheek.b + rightCheek.b) / 2);
    const cheek = {
      r: cheekR, g: cheekG, b: cheekB,
      hex: rgbToHex(cheekR, cheekG, cheekB),
      x: leftCheek.x, y: leftCheek.y,
      pctX: (leftCheek.x / w) * 100,
      pctY: (leftCheek.y / h) * 100,
      left: leftCheek, right: rightCheek
    };

    // 7. CHIN / JAW LOCALIZATION
    const chin = samplePatch(cx, chinY, radArea, bR, bG, bB);

    // 8. OVERALL DETECTED CORE DERMIS
    const coreX = cx;
    const coreY = Math.round(fTop + fHeight * 0.44);
    const coreSample = samplePatch(coreX, coreY, Math.round(radArea * 1.2), bR, bG, bB);
    const overallR = Math.round(coreSample.r * 0.6 + bR * 0.4);
    const overallG = Math.round(coreSample.g * 0.6 + bG * 0.4);
    const overallB = Math.round(coreSample.b * 0.6 + bB * 0.4);
    const overall = {
      r: overallR, g: overallG, b: overallB,
      hex: rgbToHex(overallR, overallG, overallB),
      x: coreX, y: coreY,
      pctX: (coreX / w) * 100,
      pctY: (coreY / h) * 100
    };

    return {
      candidateSkin,
      faceBox: {
        x: fLeft, y: fTop, width: fWidth, height: fHeight, cx, cy,
        pctX: (fLeft / w) * 100, pctY: (fTop / h) * 100,
        pctW: (fWidth / w) * 100, pctH: (fHeight / h) * 100
      },
      areas: {
        overall,
        forehead,
        cheek,
        chin
      }
    };
  }

  // Neural Human Face Verification via backend YOLO / MediaPipe model
  async function verifyHumanFaceWithYOLO(img, genId = uploadGenerationId) {
    const maxDim = 800;
    let w = img.naturalWidth || img.width || 640;
    let h = img.naturalHeight || img.height || 480;
    if (w > maxDim || h > maxDim) {
      const sc = maxDim / Math.max(w, h);
      w = Math.round(w * sc);
      h = Math.round(h * sc);
    }
    // Minimum size guard
    w = Math.max(w, 100);
    h = Math.max(h, 100);

    const tempCanvas = document.createElement("canvas");
    tempCanvas.width = w;
    tempCanvas.height = h;
    const tCtx = tempCanvas.getContext("2d");
    tCtx.drawImage(img, 0, 0, w, h);

    const dataUrl = tempCanvas.toDataURL("image/jpeg", 0.92);
    const endpoints = buildApiEndpoints("/api/detect-face");
    faceCheckAbortController = new AbortController();
    const sharedSignal = faceCheckAbortController.signal;

    // 1. Try JSON payload with reliable timeout (4000ms)
    let backendAvailable = false;
    for (let ep of endpoints) {
      if (genId !== uploadGenerationId) return null;
      try {
        const controller = new AbortController();
        const onParentAbort = () => controller.abort();
        sharedSignal.addEventListener("abort", onParentAbort, { once: true });
        const tid = setTimeout(() => controller.abort(), 15000);
        const res = await fetch(ep, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ image: dataUrl }),
          signal: controller.signal
        });
        clearTimeout(tid);
        sharedSignal.removeEventListener("abort", onParentAbort);
        backendAvailable = true;
        if (res.ok) {
          const resJson = await res.json();
          console.log("[FaceCheck] Backend responded:", ep, resJson);
          return resJson;
        }
        if (res.status === 422) {
          const resJson = await res.json().catch(() => ({}));
          return { has_face: false, face_count: 0, message: resJson.error || "No human face detected." };
        }
      } catch (err) {
        if (sharedSignal.aborted) return null;
        console.warn("[FaceCheck] Fast JSON attempt failed on", ep, err.name);
      }
    }

    // 2. Try multipart FormData only if backend seemed partially available
    if (backendAvailable) {
      try {
        const blob = await new Promise((resolve) => tempCanvas.toBlob(resolve, "image/jpeg", 0.85));
        if (blob) {
          const fd = new FormData();
          fd.append("file", blob, "face_check.jpg");
          for (let ep of endpoints) {
            try {
              const controller = new AbortController();
              const tid = setTimeout(() => controller.abort(), 4000);
              const res = await fetch(ep, { method: "POST", body: fd, signal: controller.signal });
              clearTimeout(tid);
              if (res.ok) {
                const resJson = await res.json();
                return resJson;
              }
            } catch (err) {}
          }
        }
      } catch (blobErr) {}
    }

    // 3. Backend unreachable — check Native Browser FaceDetector API (Chrome / Edge / Android)
    if (typeof window !== "undefined" && "FaceDetector" in window) {
      try {
        const detector = new window.FaceDetector({ fastMode: true, maxDetectedFaces: 1 });
        const nativeFaces = await detector.detect(img);
        if (nativeFaces && nativeFaces.length > 0) {
          const nb = nativeFaces[0].boundingBox;
          const nw = img.naturalWidth || img.width || 640;
          const nh = img.naturalHeight || img.height || 480;
          console.log("[FaceCheck] Native browser FaceDetector found face:", nb);
          return {
            has_face: true,
            face_count: nativeFaces.length,
            lighting_clear: true,
            confidence: 0.95,
            detector_type: "native_face_detector",
            bounding_box: {
              x: nb.x, y: nb.y, w: nb.width, h: nb.height,
              pctX: (nb.x / nw) * 100, pctY: (nb.y / nh) * 100,
              pctW: (nb.width / nw) * 100, pctH: (nb.height / nh) * 100
            },
            message: "Face localized via Neural Face Detector."
          };
        } else {
          return {
            has_face: false,
            face_count: 0,
            lighting_clear: false,
            message: "No human face detected. Please position your face clearly in the frame."
          };
        }
      } catch (nativeErr) {
        console.warn("[FaceCheck] Native FaceDetector error:", nativeErr);
      }
    }

    // 4. Algorithmic biometric fallback
    console.warn("[FaceCheck] Backend unreachable — running algorithmic biometric check");
    try {
      const fbW = 200, fbH = 200;
      const fbCanvas = document.createElement("canvas");
      fbCanvas.width = fbW; fbCanvas.height = fbH;
      const fbCtx = fbCanvas.getContext("2d");
      fbCtx.drawImage(img, 0, 0, fbW, fbH);
      const fbData = fbCtx.getImageData(0, 0, fbW, fbH).data;

      let totalLum = 0, totalSkin = 0;
      let skinXSum = 0, skinYSum = 0;
      let minX = fbW, maxX = 0, minY = fbH, maxY = 0;
      const totalPixels = fbW * fbH;
      const lums = [];

      for (let i = 0; i < fbData.length; i += 4) {
        const r = fbData[i], g = fbData[i + 1], b = fbData[i + 2];
        const lum = 0.299 * r + 0.587 * g + 0.114 * b;
        totalLum += lum;
        if (i % 16 === 0) lums.push(lum);

        if (isSkinPixel(r, g, b)) {
          const pxIdx = i / 4;
          const pxX = pxIdx % fbW;
          const pxY = Math.floor(pxIdx / fbW);
          // Focus on head/face upper 85% region
          if (pxY < fbH * 0.85) {
            totalSkin++;
            skinXSum += pxX;
            skinYSum += pxY;
            if (pxX < minX) minX = pxX;
            if (pxX > maxX) maxX = pxX;
            if (pxY < minY) minY = pxY;
            if (pxY > maxY) maxY = pxY;
          }
        }
      }

      // Check pixel variance to reject uniform/flat/blank images
      const meanLum = totalLum / totalPixels;
      let lumVar = 0;
      for (let l of lums) {
        const d = l - meanLum;
        lumVar += d * d;
      }
      lumVar = lumVar / lums.length;
      if (lumVar < 18) {
        return {
          has_face: false,
          face_count: 0,
          message: "No human face detected. Image is completely uniform or blank."
        };
      }

      const clusterW = Math.max(0, maxX - minX);
      const clusterH = Math.max(0, maxY - minY);
      const clusterArea = clusterW * clusterH;

      // Real human face in portrait/selfie mode takes up a concentrated, distinct region
      // Reject if skin cluster is too small, absent, or diffuse pattern (curtains/walls)
      if (totalSkin < 160 || clusterW < 30 || clusterH < 35 || clusterArea < 1200) {
        return {
          has_face: false,
          face_count: 0,
          message: "No human face detected. Please ensure your face is clearly visible."
        };
      }

      const aspect = clusterH / clusterW;
      if (aspect < 0.60 || aspect > 2.4) {
        return {
          has_face: false,
          face_count: 0,
          message: "No human face detected. Object shape does not match a human face."
        };
      }

      const clusterDensity = totalSkin / clusterArea;
      // In real human faces, skin pixels form a coherent cluster (density >= 0.16)
      // Diffuse patterns (curtains, wallpapers, textures) have low cluster density (< 0.08)
      if (clusterDensity < 0.16) {
        return {
          has_face: false,
          face_count: 0,
          message: "No human face detected. Detected texture does not match a human face."
        };
      }

      const cx = (skinXSum / totalSkin) / fbW;
      const cy = (skinYSum / totalSkin) / fbH;
      // Centrality check: face center of mass should be reasonably positioned
      if (cx >= 0.15 && cx <= 0.85 && cy >= 0.10 && cy <= 0.82) {
        return {
          has_face: true,
          face_count: 1,
          lighting_clear: true,
          confidence: 0.80,
          detector_type: "biometric_fallback",
          message: "Face verified (local biometric detector)."
        };
      }

      return {
        has_face: false,
        face_count: 0,
        message: "No human face detected. Please position your face closer to the center."
      };
    } catch (fbErr) {
      console.error("[FaceCheck] Fallback error:", fbErr);
    }

    return { has_face: false, message: "No human face detected. Please check your image." };
  }

  // --- Auto Colour Detection & Lighting Quality Sensor ---
  // Exact user logic:
  // If face detected -> check lighting:
  //   elif lighting not clear -> NO palettes, show lighting alert
  //   otherwise -> show palettes and enable analysis
  // Else (no face detected) -> NO palettes, show no face alert
  function cropPortraitAroundFace(sourceImg, faceBoxPct) {
    return new Promise((resolve) => {
      if (!sourceImg || !faceBoxPct) return resolve(null);
      const origW = sourceImg.naturalWidth || sourceImg.width || 640;
      const origH = sourceImg.naturalHeight || sourceImg.height || 480;

      const bx = faceBoxPct.pctX !== undefined ? (faceBoxPct.pctX / 100) * origW : (faceBoxPct.x || 0);
      const by = faceBoxPct.pctY !== undefined ? (faceBoxPct.pctY / 100) * origH : (faceBoxPct.y || 0);
      const bw = faceBoxPct.pctW !== undefined ? (faceBoxPct.pctW / 100) * origW : (faceBoxPct.w || origW * 0.5);
      const bh = faceBoxPct.pctH !== undefined ? (faceBoxPct.pctH / 100) * origH : (faceBoxPct.h || origH * 0.5);

      // Padded portrait framing (headroom + cheeks + jawline/neck)
      const x1 = Math.max(0, Math.floor(bx - bw * 0.35));
      const y1 = Math.max(0, Math.floor(by - bh * 0.45));
      const x2 = Math.min(origW, Math.ceil(bx + bw + bw * 0.35));
      const y2 = Math.min(origH, Math.ceil(by + bh + bh * 0.55));
      const cw = Math.max(160, x2 - x1);
      const ch = Math.max(160, y2 - y1);

      // Keep crisp portrait dimensions between 520px and 1200px so HUD overlays never overlap
      const maxDim = Math.max(cw, ch);
      const scale = maxDim > 1200 ? (1200 / maxDim) : (maxDim < 520 ? (520 / maxDim) : 1);
      const outW = Math.max(240, Math.round(cw * scale));
      const outH = Math.max(240, Math.round(ch * scale));

      const c = document.createElement("canvas");
      c.width = outW;
      c.height = outH;
      c.getContext("2d").drawImage(sourceImg, x1, y1, cw, ch, 0, 0, outW, outH);
      const dataUrl = c.toDataURL("image/jpeg", 0.95);
      c.toBlob((blob) => {
        if (!blob) return resolve(null);
        const file = new File([blob], "portrait_autoselect.jpg", { type: "image/jpeg" });
        resolve({ file, dataUrl });
      }, "image/jpeg", 0.95);
    });
  }

  function renderFaceAutoSelectBar(faces, activeIdx, isCropped, showToggle) {
    let bar = document.getElementById("face-autoselect-bar");
    if (!bar && qualityBar && qualityBar.parentNode) {
      bar = document.createElement("div");
      bar.id = "face-autoselect-bar";
      bar.className = "face-autoselect-bar hidden";
      qualityBar.parentNode.insertBefore(bar, qualityBar);
    }
    if (!bar) return;

    if (!faces || faces.length === 0 || !showToggle) {
      bar.classList.add("hidden");
      return;
    }

    const labelText = isCropped
      ? "Auto-focused on primary face"
      : "Viewing full uploaded photo";

    const chipsHtml = `<button type="button" class="face-chip-btn" id="toggle-full-photo-btn">${isCropped ? "Use Full Photo" : "Auto-Focus Face"}</button>`;

    bar.innerHTML = `
      <span class="face-autoselect-label">🎯 ${labelText}</span>
      <div class="face-autoselect-actions">${chipsHtml}</div>
    `;
    bar.classList.remove("hidden");

    const toggleBtn = document.getElementById("toggle-full-photo-btn");
    if (toggleBtn && originalImageBitmap && originalUploadedFile) {
      toggleBtn.addEventListener("click", async () => {
        if (isAutoCroppedPortrait) {
          isAutoCroppedPortrait = false;
          currentFile = originalUploadedFile;
          currentImageBitmap = originalImageBitmap;
          previewImg.src = originalImageBitmap.src;
          checkImageQualityAndAutoColor(originalImageBitmap, uploadGenerationId, true);
        } else if (detectedFacesList[selectedFaceIndex]) {
          const cropped = await cropPortraitAroundFace(originalImageBitmap, detectedFacesList[selectedFaceIndex]);
          if (!cropped) return;
          isAutoCroppedPortrait = true;
          currentFile = cropped.file;
          previewImg.src = cropped.dataUrl;
          const nextImg = new Image();
          nextImg.src = cropped.dataUrl;
          nextImg.onload = () => {
            currentImageBitmap = nextImg;
            checkImageQualityAndAutoColor(nextImg, uploadGenerationId, true);
          };
        }
      });
    }
  }

  async function checkImageQualityAndAutoColor(img, genId = uploadGenerationId, skipAutoCrop = false) {
    const statusEl = document.getElementById("mesh-status-text");
    const lightingPill = document.getElementById("lighting-status-pill");
    const hudLightingPill = document.getElementById("hud-lighting-pill");
    const dockDot = document.getElementById("dock-dot");
    const autoBadgeTitle = document.getElementById("auto-color-badge-title");
    const autoBadgeHex = document.getElementById("face-box-hex");
    const autoBadgeTag = document.getElementById("face-box-sublabel");
    const autoDot = document.getElementById("face-box-color-dot");
    const faceBoxEl = document.getElementById("preview-face-box");

    if (statusEl) statusEl.textContent = "Checking photo lighting and complexion...";
    if (faceBoxEl) faceBoxEl.classList.add("hidden");
    analyzeBtn.disabled = true;

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
      if (lum < 20) darkCount++;
      if (lum > 244) brightCount++;
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

    // 1. Verify real human face via YOLO detector
    const yoloResult = await verifyHumanFaceWithYOLO(img, genId);
    if (genId !== uploadGenerationId) return false;

    // CONDITION 1: NO HUMAN FACE DETECTED -> STRICTLY NO PALETTES, NO OUTPUT!
    if (!yoloResult || !yoloResult.has_face) {
      isFaceVerified = false;
      const failMsg = (yoloResult && yoloResult.message) || "No human face detected. Please position your face clearly in the camera frame.";
      showError(failMsg, true);

      if (faceBoxEl) faceBoxEl.classList.add("hidden");
      analyzeBtn.disabled = true;
      // Hide any previously visible results — strictly no output
      if (resultsSection) resultsSection.classList.add("hidden");
      const navHomeBtnEl = document.getElementById("nav-home-btn");
      if (navHomeBtnEl) navHomeBtnEl.classList.add("hidden");

      if (qualityBar) qualityBar.classList.remove("hidden");
      if (qualityMeter) {
        qualityMeter.style.width = "15%";
        qualityMeter.style.background = "#EF4444";
      }
      if (qualityStatus) {
        qualityStatus.textContent = "No Human Face";
        qualityStatus.className = "quality-status Poor";
      }
      if (qualityDetails) qualityDetails.textContent = failMsg;

      if (statusEl) statusEl.textContent = "⚠️ No human face detected • Please show a human face";
      if (lightingPill) lightingPill.textContent = "Subject: No Human Face";
      if (hudLightingPill) hudLightingPill.textContent = "⚠️ NO FACE DETECTED";
      if (dockDot) dockDot.style.background = "#EF4444";

      if (autoBadgeTitle) autoBadgeTitle.textContent = "NO HUMAN FACE DETECTED";
      if (autoBadgeHex) autoBadgeHex.textContent = "NO FACE";
      if (autoBadgeTag) {
        autoBadgeTag.textContent = "NOT RECOGNIZED";
        autoBadgeTag.className = "auto-color-status-tag error";
      }
      if (autoDot) autoDot.style.backgroundColor = "#64748B";

      return false;
    }

    isFaceVerified = true;

    // CONDITION 2: FACE IS DETECTED! Auto-select & focus if wide/group photo, then check face-scoped lighting
    const yoloBbox = yoloResult.bounding_box;
    if (!skipAutoCrop) {
      detectedFacesList = (yoloResult.faces && yoloResult.faces.length)
        ? yoloResult.faces
        : (yoloBbox ? [yoloBbox] : []);
      selectedFaceIndex = 0;

      const faceAreaPct = yoloBbox && yoloBbox.pctW && yoloBbox.pctH ? (yoloBbox.pctW * yoloBbox.pctH) : 10000;
      const shouldAutoCrop = Boolean(yoloBbox) && (faceAreaPct < 3500 || detectedFacesList.length > 1);
      if (shouldAutoCrop && originalImageBitmap) {
        const cropped = await cropPortraitAroundFace(originalImageBitmap, detectedFacesList[0]);
        if (genId !== uploadGenerationId) return false;
        if (cropped) {
          isAutoCroppedPortrait = true;
          currentFile = cropped.file;
          previewImg.src = cropped.dataUrl;
          const croppedImg = new Image();
          croppedImg.src = cropped.dataUrl;
          await new Promise((resolve) => {
            croppedImg.onload = resolve;
            croppedImg.onerror = resolve;
          });
          if (genId !== uploadGenerationId) return false;
          currentImageBitmap = croppedImg;
          return checkImageQualityAndAutoColor(croppedImg, genId, true);
        }
      } else {
        isAutoCroppedPortrait = false;
      }
    }

    const canToggleFocus = Boolean(originalImageBitmap && detectedFacesList.length > 0 && (
      isAutoCroppedPortrait ||
      detectedFacesList.length > 1 ||
      (yoloBbox && yoloBbox.pctW && yoloBbox.pctH && (yoloBbox.pctW * yoloBbox.pctH) < 3500)
    ));
    renderFaceAutoSelectBar(detectedFacesList, selectedFaceIndex, isAutoCroppedPortrait, canToggleFocus);

    const regionRes = extractFacialDermisAndRegions(imgData, sampleW, sampleH);
    const areas = regionRes.areas;
    lastExtractedAreas = areas;
    lastExtractedFaceBox = yoloBbox || regionRes.faceBox;

    // Recompute face-scoped brightness/contrast inside detected face ROI so dark/bright backgrounds don't trigger false rejections
    let evalBrightness = meanBrightness;
    let evalDarkRatio = darkRatio;
    let evalBrightRatio = brightRatio;
    let evalContrastStd = contrastStd;
    if (yoloBbox && yoloBbox.pctW > 0 && yoloBbox.pctH > 0) {
      const fx1 = Math.max(0, Math.floor((yoloBbox.pctX / 100) * sampleW));
      const fy1 = Math.max(0, Math.floor((yoloBbox.pctY / 100) * sampleH));
      const fx2 = Math.min(sampleW, Math.ceil(((yoloBbox.pctX + yoloBbox.pctW) / 100) * sampleW));
      const fy2 = Math.min(sampleH, Math.ceil(((yoloBbox.pctY + yoloBbox.pctH) / 100) * sampleH));
      if ((fx2 - fx1) >= 20 && (fy2 - fy1) >= 20) {
        let fSum = 0, fDark = 0, fBright = 0, fCount = 0;
        const fLums = [];
        for (let py = fy1; py < fy2; py++) {
          for (let px = fx1; px < fx2; px++) {
            const pIdx = (py * sampleW + px) * 4;
            const fl = 0.299 * imgData[pIdx] + 0.587 * imgData[pIdx + 1] + 0.114 * imgData[pIdx + 2];
            fSum += fl;
            if (fl < 20) fDark++;
            if (fl > 244) fBright++;
            if (fCount % 4 === 0) fLums.push(fl);
            fCount++;
          }
        }
        if (fCount > 0) {
          evalBrightness = fSum / fCount;
          evalDarkRatio = fDark / fCount;
          evalBrightRatio = fBright / fCount;
          let fv = 0;
          for (const l of fLums) fv += (l - evalBrightness) ** 2;
          evalContrastStd = Math.sqrt(fv / Math.max(1, fLums.length));
        }
      }
    }

    let lightingError = null;
    if (yoloResult.lighting_clear === false && yoloResult.quality_message) {
      lightingError = "Face detected, but lighting is not clear: " + yoloResult.quality_message;
    } else if (origW < 140 || origH < 140) {
      lightingError = "Face detected, but photo resolution is too low. Please upload a higher resolution photo.";
    } else if (evalBrightness < 35 || evalDarkRatio > 0.45) {
      lightingError = "Face detected, but lighting is not clear: The photo is too dark. Please take your photo in bright, natural daylight.";
    } else if (evalBrightness > 235 || evalBrightRatio > 0.40) {
      lightingError = "Face detected, but lighting is not clear: Harsh glare or overexposure detected. Please avoid direct bright flash.";
    } else if (evalContrastStd < 13) {
      lightingError = "Face detected, but lighting is not clear: Uneven shadows or low contrast. Please use clear, balanced lighting.";
    } else if (blurMetric < 10) {
      lightingError = "Face detected, but image is not clear: Photo appears blurry or out of focus. Please ensure camera is steady.";
    }

    if (lightingError) {
      showError(lightingError);
      if (faceBoxEl) faceBoxEl.classList.add("hidden");
      analyzeBtn.disabled = true;

      if (qualityBar) qualityBar.classList.remove("hidden");
      if (qualityMeter) {
        qualityMeter.style.width = "35%";
        qualityMeter.style.background = "#F59E0B";
      }
      if (qualityStatus) {
        qualityStatus.textContent = "Lighting Not Clear";
        qualityStatus.className = "quality-status Poor";
      }
      if (qualityDetails) qualityDetails.textContent = lightingError;

      if (statusEl) statusEl.textContent = "⚠️ Face detected, but lighting is not clear • Adjust lighting";
      if (lightingPill) lightingPill.textContent = "Lighting: Not Clear";
      if (hudLightingPill) hudLightingPill.textContent = "⚠️ LIGHTING NOT CLEAR";
      if (dockDot) dockDot.style.background = "#F59E0B";

      if (autoBadgeTitle) autoBadgeTitle.textContent = "LIGHTING NOT CLEAR";
      if (autoBadgeHex) autoBadgeHex.textContent = "UNCLEAR";
      if (autoBadgeTag) {
        autoBadgeTag.textContent = "IMPROVE LIGHTING";
        autoBadgeTag.className = "auto-color-status-tag error";
      }
      if (autoDot) autoDot.style.backgroundColor = "#F59E0B";

      return false;
    }

    // CONDITION 3: OTHERWISE (Face Detected AND Lighting is Clear) -> PALETTES & OUTPUT!
    hideError();
    const spottedHex = areas.overall.hex;

    // Render sleek Auto-Selector Box around the detected face (aligned to rendered image rect)
    if (faceBoxEl) {
      const boxToRender = yoloBbox || regionRes.faceBox;
      if (boxToRender && previewImg && previewImg.naturalWidth && previewImg.naturalHeight) {
        const positionBox = () => {
          const overlay = document.getElementById("face-regions-overlay");
          if (!overlay || !previewImg.clientWidth || !previewImg.clientHeight) return;
          const oRect = overlay.getBoundingClientRect();
          const iRect = previewImg.getBoundingClientRect();
          const natRatio = previewImg.naturalWidth / previewImg.naturalHeight;
          const renRatio = iRect.width / iRect.height;
          let drawW = iRect.width, drawH = iRect.height, offX = 0, offY = 0;
          if (natRatio > renRatio) {
            drawH = iRect.width / natRatio;
            offY = (iRect.height - drawH) / 2;
          } else {
            drawW = iRect.height * natRatio;
            offX = (iRect.width - drawW) / 2;
          }
          const baseLeft = (iRect.left - oRect.left) + offX;
          const baseTop = (iRect.top - oRect.top) + offY;
          const px = boxToRender.pctX !== undefined ? boxToRender.pctX : 25;
          const py = boxToRender.pctY !== undefined ? boxToRender.pctY : 15;
          const pw = boxToRender.pctW !== undefined ? boxToRender.pctW : 50;
          const ph = boxToRender.pctH !== undefined ? boxToRender.pctH : 65;

          faceBoxEl.style.left = `${baseLeft + (px / 100) * drawW}px`;
          faceBoxEl.style.top = `${baseTop + (py / 100) * drawH}px`;
          faceBoxEl.style.width = `${(pw / 100) * drawW}px`;
          faceBoxEl.style.height = `${(ph / 100) * drawH}px`;
          faceBoxEl.style.display = "block";
          faceBoxEl.classList.remove("hidden");

          const tagEl = document.getElementById("preview-face-box-tag");
          if (tagEl) {
            tagEl.textContent = detectedFacesList.length > 1
              ? `AUTO-SELECTED FACE ${selectedFaceIndex + 1}`
              : "AUTO-SELECTED FACE";
          }
        };
        positionBox();
        requestAnimationFrame(positionBox);
      } else {
        faceBoxEl.classList.add("hidden");
      }
    }

    // Update Quality Bar: Optimal
    if (qualityBar) qualityBar.classList.remove("hidden");
    if (qualityMeter) {
      qualityMeter.style.width = "95%";
      qualityMeter.style.background = "#10B981";
    }
    if (qualityStatus) {
      qualityStatus.textContent = "Good Lighting & Face Verified";
      qualityStatus.className = "quality-status Good";
    }
    if (qualityDetails) {
      qualityDetails.textContent = `Face localized & natural dermis spotted (${spottedHex}) • Lighting is clear. Ready to unlock palettes!`;
    }

    // Update HUD & Auto Color Badge with Complexion
    if (statusEl) statusEl.textContent = `✨ Face verified & lighting is clear (${spottedHex}) • Ready to analyze!`;
    if (lightingPill) lightingPill.textContent = "Lighting: Clear & Balanced";
    if (hudLightingPill) hudLightingPill.textContent = "💡 NATURAL LIGHT SENSOR • OPTIMAL";
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
    updateSwatch("sample-color-1", "sample-hex-1", areas.overall.hex);
    updateSwatch("sample-color-2", "sample-hex-2", areas.forehead.hex);
    updateSwatch("sample-color-3", "sample-hex-3", areas.cheek.hex);
    updateSwatch("sample-color-4", "sample-hex-4", areas.chin.hex);

    // Spotted the colour and verified lighting - unlock Palettes & Output!
    analyzeBtn.disabled = false;
    return true;
  }

    function resetUploadState() {
    isFaceVerified = false;
    currentFile = null;
    currentImageBitmap = null;
    originalUploadedFile = null;
    originalImageBitmap = null;
    detectedFacesList = [];
    selectedFaceIndex = 0;
    isAutoCroppedPortrait = false;
    const autoBar = document.getElementById("face-autoselect-bar");
    if (autoBar) autoBar.classList.add("hidden");
    fileInput.value = "";
    if (cameraInput) cameraInput.value = "";
    previewImg.src = "";
    previewImg.removeAttribute("src");
    uploadPrompt.classList.remove("hidden");
    previewBox.classList.add("hidden");
    analyzeBtn.disabled = true;
    hideError();
    const faceBoxEl = document.getElementById("preview-face-box");
    if (faceBoxEl) faceBoxEl.classList.add("hidden");
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

  function triggerCameraCapture() {
    hideError();
    if (cameraBtn) {
      cameraBtn.click();
    } else if (cameraInput) {
      cameraInput.click();
    }
  }

  function triggerFileUpload() {
    hideError();
    if (fileInput) {
      fileInput.click();
    }
  }

  if (overlayCameraBtn) overlayCameraBtn.addEventListener("click", triggerCameraCapture);
  if (bannerCameraBtn) bannerCameraBtn.addEventListener("click", triggerCameraCapture);
  if (overlayUploadBtn) overlayUploadBtn.addEventListener("click", triggerFileUpload);
  if (bannerUploadBtn) bannerUploadBtn.addEventListener("click", triggerFileUpload);

  function showError(msg, isNoFace = false) {
    errorText.textContent = msg;
    errorBanner.classList.remove("hidden");
    if (isNoFace) {
      if (errorActionBtns) errorActionBtns.classList.remove("hidden");
      if (noFaceOverlay) noFaceOverlay.classList.remove("hidden");
    } else {
      if (errorActionBtns) errorActionBtns.classList.add("hidden");
      if (noFaceOverlay) noFaceOverlay.classList.add("hidden");
    }
  }

  function hideError() {
    errorBanner.classList.add("hidden");
    if (errorActionBtns) errorActionBtns.classList.add("hidden");
    if (noFaceOverlay) noFaceOverlay.classList.add("hidden");
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
    if (!currentFile && !currentImageBitmap) return;

    if (!isFaceVerified) {
      showError("Cannot analyze: No human face detected in the picture. Please position your face clearly in the camera frame.");
      if (resultsSection) resultsSection.classList.add("hidden");
      analyzeBtn.disabled = true;
      return;
    }

    hideError();
    studioSection.classList.add("hidden");
    heroSection.classList.add("hidden");
    processingSection.classList.remove("hidden");
    resultsSection.classList.add("hidden");

    const animationPromise = animatePipelineSteps();

    const analyzeEndpoints = buildApiEndpoints("/api/analyze");

    try {
      let data = null;
      let lastError = null;

      // 1. Try FormData first
      if (currentFile) {
        const formData = new FormData();
        formData.append("file", currentFile);
        formData.append("gender", selectedGenderMode || currentGender || "all");
        formData.append("clothing_type", currentClothingType || "all");
        formData.append("weather", currentWeather || "all");

        for (let ep of analyzeEndpoints) {
          try {
            const controller = new AbortController();
            const tid = setTimeout(() => controller.abort(), 28000);
            const response = await fetch(ep, {
              method: "POST",
              body: formData,
              signal: controller.signal
            });
            clearTimeout(tid);

            if (response.ok) {
              data = await response.json();
              break;
            } else if (response.status === 422) {
              const errData = await response.json().catch(() => ({}));
              const valErr = new Error(errData.error || "No human face detected. Cannot analyze.");
              valErr.isValidationError = true;
              throw valErr;
            }
          } catch (netErr) {
            if (netErr.isValidationError || (netErr.message && netErr.message.includes("No human face"))) {
              throw netErr;
            }
            lastError = netErr;
          }
        }
      }

      // 2. If FormData failed or image is dataUrl, try JSON payload
      if (!data && previewImg && previewImg.src && previewImg.src.startsWith("data:")) {
        for (let ep of analyzeEndpoints) {
          try {
            const controller = new AbortController();
            const tid = setTimeout(() => controller.abort(), 28000);
            const response = await fetch(ep, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                image: previewImg.src,
                gender: selectedGenderMode || currentGender || "all",
                clothing_type: currentClothingType || "all",
                weather: currentWeather || "all"
              }),
              signal: controller.signal
            });
            clearTimeout(tid);

            if (response.ok) {
              data = await response.json();
              break;
            } else if (response.status === 422) {
              const errData = await response.json().catch(() => ({}));
              const valErr = new Error(errData.error || "No human face detected. Cannot analyze.");
              valErr.isValidationError = true;
              throw valErr;
            }
          } catch (netErr) {
            if (netErr.isValidationError || (netErr.message && netErr.message.includes("No human face"))) {
              throw netErr;
            }
            lastError = netErr;
          }
        }
      }

      await animationPromise;

      if (!data || (!data.success && !data.undertone)) {
        throw new Error(
          (lastError && lastError.message) ||
          "Failed to analyze image. Please ensure a clear human face is visible."
        );
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
      const navHomeBtnEl = document.getElementById("nav-home-btn");
      if (navHomeBtnEl) navHomeBtnEl.classList.remove("hidden");
      window.scrollTo({ top: 0, behavior: "smooth" });

    } catch (err) {
      processingSection.classList.add("hidden");
      studioSection.classList.remove("hidden");
      heroSection.classList.remove("hidden");
      const navHomeBtnEl = document.getElementById("nav-home-btn");
      if (navHomeBtnEl) navHomeBtnEl.classList.add("hidden");
      showError(err.message || "Failed to connect to backend server.");
    }
  });

  // Re-analyze & Another Analysis Actions
  const anotherUploadBtn = document.getElementById("another-upload-btn");
  const anotherCameraBtn = document.getElementById("another-camera-btn");
  const navHomeBtn = document.getElementById("nav-home-btn");
  const resultsHomeBtn = document.getElementById("results-home-btn");
  const anotherHomeBtn = document.getElementById("another-home-btn");

  function returnToHomePage() {
    resultsSection.classList.add("hidden");
    processingSection.classList.add("hidden");
    studioSection.classList.remove("hidden");
    heroSection.classList.remove("hidden");
    if (navHomeBtn) navHomeBtn.classList.add("hidden");
    resetUploadState();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  if (navHomeBtn) navHomeBtn.addEventListener("click", returnToHomePage);
  if (resultsHomeBtn) resultsHomeBtn.addEventListener("click", returnToHomePage);
  if (anotherHomeBtn) anotherHomeBtn.addEventListener("click", returnToHomePage);

  function restartAnalysisSession(triggerUpload = false) {
    resultsSection.classList.add("hidden");
    processingSection.classList.add("hidden");
    studioSection.classList.remove("hidden");
    heroSection.classList.remove("hidden");
    if (navHomeBtn) navHomeBtn.classList.add("hidden");
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
  function updateGenderView(activeG) {
    const targetG = (activeG || currentGender || "female").toLowerCase();
    const makeupBtn = document.getElementById("tab-btn-makeup");
    const makeupTab = document.getElementById("tab-makeup");
    const clothingBtn = document.querySelector('[data-tab="clothing"]');
    const clothingTab = document.getElementById("tab-clothing");

    if (targetG === "male") {
      if (makeupBtn) {
        makeupBtn.style.display = "none";
        makeupBtn.classList.remove("active");
      }
      if (makeupTab) {
        makeupTab.style.display = "none";
        makeupTab.classList.remove("active");
      }
      if (clothingBtn) clothingBtn.classList.add("active");
      if (clothingTab) {
        clothingTab.style.display = "";
        clothingTab.classList.add("active");
      }
    } else {
      if (makeupBtn) makeupBtn.style.display = "";
      if (makeupTab && makeupBtn && makeupBtn.classList.contains("active")) {
        makeupTab.style.display = "";
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
    const rawMode = (selectedGender === "female" || selectedGender === "all") ? selectedGender : "male";
    if (isManual) {
      selectedGenderMode = rawMode;
    }

    let wasAutoDetected = !isManual || rawMode === "all";
    let effectiveGender = rawMode;

    if (
      rawMode === "all" &&
      cachedApiData &&
      cachedApiData.detected_gender &&
      (cachedApiData.detected_gender.gender === "male" || cachedApiData.detected_gender.gender === "female")
    ) {
      effectiveGender = cachedApiData.detected_gender.gender;
      wasAutoDetected = true;
    }

    currentGender = effectiveGender;

    // Sync pills across upload selector using the user-chosen mode (so "All Styles" stays selected)
    document.querySelectorAll("#upload-gender-options .gender-pill").forEach((pill) => {
      pill.classList.toggle("active", pill.getAttribute("data-gender") === selectedGenderMode);
    });

    // Sync pills across results outfit studio
    document.querySelectorAll("#results-gender-options .gender-filter-pill").forEach((pill) => {
      pill.classList.toggle("active", pill.getAttribute("data-gender") === selectedGenderMode);
    });

    const switchLabel = document.getElementById("gender-switch-label");
    if (switchLabel) switchLabel.style.display = "none";
    const bannerControls = document.querySelector(".gender-banner-controls");
    if (bannerControls) bannerControls.style.display = "none";

    updateGenderView(effectiveGender);

    // Update banner UI
    const bannerTitleText = document.getElementById("gender-banner-title-text");
    if (bannerTitleText) bannerTitleText.textContent = "Style Profile:";

    const bannerIcon = document.getElementById("gender-banner-icon");
    const bannerLabel = document.getElementById("gender-banner-label");
    const bannerBadge = document.getElementById("gender-banner-badge");
    const bannerDesc = document.getElementById("gender-banner-desc");
    const autoConf = cachedApiData && cachedApiData.detected_gender && cachedApiData.detected_gender.confidence_percentage;
    const badgeText = wasAutoDetected
      ? (autoConf ? `Auto-Detected · ${autoConf}%` : "Auto-Detected")
      : "Selected Profile";

    if (effectiveGender === "female") {
      if (bannerIcon) bannerIcon.textContent = "👗";
      if (bannerLabel) bannerLabel.textContent = "Women's Style";
      if (bannerBadge) {
        bannerBadge.textContent = badgeText;
        bannerBadge.className = "gender-banner-badge auto-badge";
      }
      if (bannerDesc) {
        bannerDesc.textContent = "Color palettes, cosmetics, evening wear, and fine jewelry are tailored for haute womenswear styling.";
      }
    } else if (effectiveGender === "male") {
      if (bannerIcon) bannerIcon.textContent = "👔";
      if (bannerLabel) bannerLabel.textContent = "Men's Style";
      if (bannerBadge) {
        bannerBadge.textContent = badgeText;
        bannerBadge.className = "gender-banner-badge auto-badge";
      }
      if (bannerDesc) {
        bannerDesc.textContent = "Color palettes, suiting staples, and luxury timepieces are calibrated specifically for menswear styling.";
      }
    } else {
      if (bannerIcon) bannerIcon.textContent = "👥";
      if (bannerLabel) bannerLabel.textContent = "Universal Harmony Profile";
      if (bannerBadge) {
        bannerBadge.textContent = "Universal Harmony";
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
        palette = allMatching.filter(c => {
          const cat = (c.category || "").toLowerCase();
          const name = (c.name || "").toLowerCase();
          const desc = (c.description || "").toLowerCase();
          return (cat === "Clothing" || cat === "Neutrals") &&
                 !name.includes("lip") &&
                 !name.includes("lipstick") &&
                 !name.includes("gloss") &&
                 !name.includes("blush") &&
                 !name.includes("eyeshadow") &&
                 !desc.includes("lipstick");
        })
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

  // Wire up upload clothing type & weather pre-select pills
  document.querySelectorAll("#upload-clothing-options .style-pill").forEach((pill) => {
    pill.addEventListener("click", () => {
      document.querySelectorAll("#upload-clothing-options .style-pill").forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");
      currentClothingType = pill.getAttribute("data-type") || "all";
      document.querySelectorAll("#results-clothing-options .filter-pill").forEach((p) => {
        p.classList.toggle("active", p.getAttribute("data-type") === currentClothingType);
      });
    });
  });

  document.querySelectorAll("#upload-weather-options .weather-pill").forEach((pill) => {
    pill.addEventListener("click", () => {
      document.querySelectorAll("#upload-weather-options .weather-pill").forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");
      currentWeather = pill.getAttribute("data-weather") || "all";
      document.querySelectorAll("#results-weather-options .weather-filter-pill").forEach((p) => {
        p.classList.toggle("active", p.getAttribute("data-weather") === currentWeather);
      });
    });
  });

  // Wire up results outfit studio live filter pills
  document.querySelectorAll("#results-clothing-options .filter-pill").forEach((pill) => {
    pill.addEventListener("click", () => {
      document.querySelectorAll("#results-clothing-options .filter-pill").forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");
      currentClothingType = pill.getAttribute("data-type") || "all";
      document.querySelectorAll("#upload-clothing-options .style-pill").forEach((p) => {
        p.classList.toggle("active", p.getAttribute("data-type") === currentClothingType);
      });
      fetchOrUpdateOutfits();
    });
  });

  document.querySelectorAll("#results-weather-options .weather-filter-pill").forEach((pill) => {
    pill.addEventListener("click", () => {
      document.querySelectorAll("#results-weather-options .weather-filter-pill").forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");
      currentWeather = pill.getAttribute("data-weather") || "all";
      document.querySelectorAll("#upload-weather-options .weather-pill").forEach((p) => {
        p.classList.toggle("active", p.getAttribute("data-weather") === currentWeather);
      });
      fetchOrUpdateOutfits();
    });
  });

  document.querySelectorAll("#results-gender-options .gender-filter-pill").forEach((pill) => {
    pill.addEventListener("click", () => {
      const g = pill.getAttribute("data-gender");
      handleGenderSelect(g, true);
      fetchOrUpdateOutfits();
    });
  });

  // --- Render Results ---
  function renderResults(data) {
    cachedApiData = data;
    resetFeedbackWidget(data);

    // Auto-detect gender from API response when "All Styles" was chosen, otherwise apply selected profile
    const wasAllSelected = selectedGenderMode === "all" || (data && data.requested_gender === "all");
    if (wasAllSelected) {
      selectedGenderMode = "all";
      handleGenderSelect("all", false);
    } else {
      const targetG = (data && data.gender) || selectedGenderMode;
      selectedGenderMode = (targetG === "female" || targetG === "all") ? targetG : "male";
      handleGenderSelect(selectedGenderMode, true);
    }
    const rawUt = (data && data.undertone && (data.undertone.label || data.undertone)) || "Neutral";
    const undertone = typeof rawUt === "string" ? rawUt : (rawUt.label || "Neutral");
    const utStr = String(undertone || "Neutral");
    const confidencePct = (data && data.undertone && data.undertone.confidence_percentage) !== undefined ? data.undertone.confidence_percentage : 94;

    // 0. Biometric Face Recognition Status Badge
    let recBadge = document.getElementById("face-recognition-badge");
    if (!recBadge) {
      recBadge = document.createElement("div");
      recBadge.id = "face-recognition-badge";
      recBadge.className = "face-recognition-badge";
      const resultsContainer =
        document.querySelector("#results-section .results-top-bar") ||
        document.querySelector(".results-header") ||
        document.querySelector(".undertone-hero") ||
        document.getElementById("results-section");
      if (resultsContainer) resultsContainer.appendChild(recBadge);
    }
    if (recBadge && data && data.recognition) {
      const pid = data.recognition.profile_id || "";
      const forgetHtml = pid
        ? ` <button type="button" class="forget-profile-btn" data-profile-id="${pid}" title="Delete this face profile from database memory">Forget Profile</button>`
        : "";
      if (data.recognition.is_recognized) {
        recBadge.innerHTML = `<span class="rec-icon">⚡</span> <strong>Recognized Client Profile</strong> · Loaded your calibrated signature colorimetry (${data.recognition.similarity}% match)${forgetHtml}`;
        recBadge.className = "face-recognition-badge recognized";
        recBadge.style.display = "inline-flex";
        showToast(`Welcome back! Restored your calibrated signature profile (${data.recognition.similarity}% match).`);
      } else {
        recBadge.innerHTML = `<span class="rec-icon">✨</span> <strong>New Face Profile Registered</strong> · Unique colorimetry calibrated and saved to database memory${forgetHtml}`;
        recBadge.className = "face-recognition-badge new-profile";
        recBadge.style.display = "inline-flex";
      }
      const forgetBtn = recBadge.querySelector(".forget-profile-btn");
      if (forgetBtn) {
        forgetBtn.addEventListener("click", async () => {
          const id = forgetBtn.getAttribute("data-profile-id");
          if (!id) return;
          forgetBtn.disabled = true;
          forgetBtn.textContent = "Removing...";
          for (const ep of buildApiEndpoints(`/api/face-profile/${encodeURIComponent(id)}`)) {
            try {
              const res = await fetch(ep, { method: "DELETE" });
              if (res.ok) {
                recBadge.innerHTML = `<span class="rec-icon">🗑️</span> <strong>Profile Removed</strong> · Your facial biometric memory was erased from the database.`;
                recBadge.className = "face-recognition-badge new-profile";
                showToast("Biometric face profile deleted from database.");
                return;
              }
            } catch (e) {}
          }
          forgetBtn.disabled = false;
          forgetBtn.textContent = "Forget Profile";
          showToast("Could not remove profile right now.");
        });
      }
    }

    // 1. Undertone Hero Badge & Seasonal Watermark
    const badge = document.getElementById("undertone-badge");
    const seasonName = (data && data.seasonal_harmony && data.seasonal_harmony.season_name) || "Warm Autumn Deep";
    const seasonStr = String(seasonName || "Warm Autumn Deep");
    if (badge) {
      badge.textContent = `${utStr.toUpperCase()} · ${seasonStr.toUpperCase()}`;
      badge.className = `undertone-badge ${utStr}`;
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
    if (repHex) repHex.textContent = (skinMetrics.phototype_estimate || "Natural Skin Tone").split("—")[0].trim();
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

    // Update Micro-Extract Swatches in Studio Telemetry & Results Area Strip
    const regSamples = (data.skin_analysis && data.skin_analysis.region_samples) || {};
    const repSkinHex = skinMetrics.representative_hex;
    const areas = (data.skin_analysis && data.skin_analysis.areas) || lastExtractedAreas || {};

    const coreHex = (areas.overall && areas.overall.hex) || repSkinHex;
    const foreheadHex = (areas.forehead && areas.forehead.hex) || (regSamples.forehead && regSamples.forehead.hex) || repSkinHex;
    const cheekHex = (areas.cheek && areas.cheek.hex) || (regSamples.left_cheek && regSamples.left_cheek.hex) || (regSamples.right_cheek && regSamples.right_cheek.hex) || repSkinHex;
    const chinHex = (areas.chin && areas.chin.hex) || (regSamples.chin && regSamples.chin.hex) || repSkinHex;

    const updateAreaItem = (colorId, hexId, hex) => {
      const c = document.getElementById(colorId);
      const h = document.getElementById(hexId);
      if (c) c.style.backgroundColor = hex;
      if (h) h.textContent = hex;
    };

    // Studio telemetry swatches
    updateAreaItem("sample-color-1", "sample-hex-1", coreHex);
    updateAreaItem("sample-color-2", "sample-hex-2", foreheadHex);
    updateAreaItem("sample-color-3", "sample-hex-3", cheekHex);
    updateAreaItem("sample-color-4", "sample-hex-4", chinHex);

    // Results card facial areas strip
    updateAreaItem("res-area-dot-1", "res-area-hex-1", coreHex);
    updateAreaItem("res-area-dot-2", "res-area-hex-2", foreheadHex);
    updateAreaItem("res-area-dot-3", "res-area-hex-3", cheekHex);
    updateAreaItem("res-area-dot-4", "res-area-hex-4", chinHex);

    // 3. Draw Autonomous Skin Canvas
    drawFacialLandmarksCanvas(skinMetrics.representative_hex, data.undertone.label, data);

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


    // 5. Categorized Recommendations
    renderRecGrid("rec-clothing-grid", data.recommendations.clothing, "Clothing");
    renderRecGrid("rec-makeup-grid", data.recommendations.makeup, "Cosmetics");
    renderRecGrid("rec-accessories-grid", data.recommendations.accessories, "Fine Horology");
    renderRecGrid("rec-neutrals-grid", data.recommendations.neutrals, "Foundational");
    renderAvoidGrid("rec-avoid-grid", data.less_recommended);

    document.getElementById("foundation-advice-text").textContent = data.foundation_advice;

    // 6. Bespoke 3 to 4 Curated Outfit Lookbooks
    if (data.outfits && data.outfits.length > 0) {
      renderCuratedOutfits(data.outfits);
    } else {
      fetchOrUpdateOutfits();
    }
  }

  // --- Render 3 to 4 Complete Curated Outfits ---
  function renderCuratedOutfits(outfits) {
    const grid = document.getElementById("outfit-looks-grid");
    if (!grid) return;
    grid.innerHTML = "";

    if (!outfits || outfits.length === 0) {
      grid.innerHTML = `<p style="grid-column: 1 / -1; color: var(--text-muted); text-align: center; padding: 2.5rem; background: rgba(255,255,255,0.02); border-radius: var(--radius-md);">No curated outfits found for this specific combination. Try adjusting the clothing or weather filters above.</p>`;
      return;
    }

    outfits.forEach((look, idx) => {
      const card = document.createElement("div");
      card.className = "outfit-look-card";
      card.id = `outfit-card-${look.look_id || idx + 1}`;

      const upper = look.upper || {};
      const bottom = look.bottom || {};
      const shoes = look.shoes || {};
      const jewellery = look.jewellery || {};
      const isFemale = jewellery.type === "female";

      // Build jewellery & accessories HTML
      let jewelleryHTML = "";
      if (isFemale) {
        const neck = jewellery.necklace || {};
        const ear = jewellery.earrings || {};
        const lip = jewellery.lipstick_tint || {};
        jewelleryHTML = `
          <div class="jewellery-subgrid">
            <div class="jewellery-item-chip">
              <span class="jewel-icon-tag">NECKLACE</span>
              <span><strong>${neck.name || "Statement Collar"}</strong> · ${neck.metal || "18k Warm Gold"}</span>
            </div>
            <div class="jewellery-item-chip">
              <span class="jewel-icon-tag">EARRINGS</span>
              <span><strong>${ear.name || "Sculptural Drops"}</strong> · ${ear.metal || "Fine Precious Metal"}</span>
            </div>
            <div class="jewellery-item-chip" style="background: rgba(225, 29, 72, 0.08); border: 1px solid rgba(225, 29, 72, 0.2);">
              <span class="piece-color-dot" style="width: 14px; height: 14px; background: ${lip.color_hex || '#C25D4E'}; margin: 0;"></span>
              <span class="jewel-icon-tag" style="background: rgba(225, 29, 72, 0.2); color: #FB7185;">LIP TINT</span>
              <span><strong>${lip.name || "Velvet Lip Tint"}</strong> · <i>${lip.finish || "Velvet Stained Satin"}</i></span>
            </div>
          </div>
        `;
      } else {
        const ring = jewellery.rings || {};
        const ear = jewellery.earrings || {};
        const watch = jewellery.watch || {};
        jewelleryHTML = `
          <div class="jewellery-subgrid">
            <div class="jewellery-item-chip">
              <span class="jewel-icon-tag">RING</span>
              <span><strong>${ring.name || "Signet Ring"}</strong> · ${ring.metal || "18k Brushed Gold"}</span>
            </div>
            <div class="jewellery-item-chip">
              <span class="jewel-icon-tag">EARRING</span>
              <span><strong>${ear.name || "Minimalist Stud"}</strong> · ${ear.metal || "Brushed Metal / Obsidian"}</span>
            </div>
            <div class="jewellery-item-chip">
              <span class="jewel-icon-tag">WATCH</span>
              <span><strong>${watch.name || "Horology"}</strong> · ${watch.dial || "Sunburst Dial"}</span>
            </div>
          </div>
        `;
      }

      card.innerHTML = `
        <div class="look-header-badge-row">
          <div class="look-meta-tags">
            <span class="look-number-badge">LOOK 0${look.look_number || idx + 1}</span>
            <span class="look-tag-chip">${look.clothing_type || "Styling"}</span>
            <span class="look-tag-chip">${look.weather || "All-Season"}</span>
            <span class="look-tag-chip">${look.gender || "Wardrobe"}</span>
          </div>
          <div class="look-harmony-badge">
            <span class="material-symbols-outlined" style="font-size: 15px;">verified</span>
            <span>${look.harmony_score || 96.5}% Match</span>
          </div>
        </div>

        <h4 class="look-card-title">${look.title || `Look ${idx + 1}`}</h4>
        <p class="look-card-concept">${look.concept || "Harmonized palette styling formulated for your natural complexion."}</p>

        <!-- Vector Visual Flat-Lay of the Clothes -->
        <div class="outfit-visual-container" id="visual-container-${look.look_number || idx + 1}">
          ${look.svg_illustration || ""}
        </div>

        <!-- Detailed Garment Components Breakdown -->
        <div class="outfit-pieces-list">
          <!-- Upperwear -->
          <div class="piece-row">
            <div class="piece-color-dot" style="background: ${upper.color_hex || '#D4AF37'};"></div>
            <div class="piece-info">
              <div class="piece-meta-top">
                <span class="piece-category">${upper.category || "Upperwear / Top"}</span>
                <span class="piece-hex">${upper.color_hex || ""}</span>
              </div>
              <div class="piece-name">${upper.name}</div>
              <div class="piece-subtext"><strong>Color:</strong> ${upper.color_name} • <strong>Fabric:</strong> ${upper.fabric || "Premium Weave"} • <strong>Cut:</strong> ${upper.silhouette || "Tailored"}</div>
              <div class="piece-tip">💡 ${upper.styling_tip || ""}</div>
            </div>
          </div>

          <!-- Bottomwear -->
          <div class="piece-row">
            <div class="piece-color-dot" style="background: ${bottom.color_hex || '#1E293B'};"></div>
            <div class="piece-info">
              <div class="piece-meta-top">
                <span class="piece-category">${bottom.category || "Bottomwear"}</span>
                <span class="piece-hex">${bottom.color_hex || ""}</span>
              </div>
              <div class="piece-name">${bottom.name}</div>
              <div class="piece-subtext"><strong>Color:</strong> ${bottom.color_name} • <strong>Fabric:</strong> ${bottom.fabric || "Structured Weave"} • <strong>Silhouette:</strong> ${bottom.silhouette || "Classic"}</div>
              <div class="piece-tip">💡 ${bottom.styling_tip || ""}</div>
            </div>
          </div>

          <!-- Shoes -->
          <div class="piece-row">
            <div class="piece-color-dot" style="background: ${shoes.color_hex || '#475569'};"></div>
            <div class="piece-info">
              <div class="piece-meta-top">
                <span class="piece-category">${shoes.category || "Footwear / Shoes"}</span>
                <span class="piece-hex">${shoes.color_hex || ""}</span>
              </div>
              <div class="piece-name">${shoes.name}</div>
              <div class="piece-subtext"><strong>Color:</strong> ${shoes.color_name} • <strong>Material:</strong> ${shoes.material || "Fine Leather"}</div>
              <div class="piece-tip">💡 ${shoes.styling_tip || ""}</div>
            </div>
          </div>

          <!-- Jewellery & Beauty -->
          <div class="piece-row">
            <div class="piece-color-dot" style="background: ${isFemale ? (jewellery.lipstick_tint?.color_hex || '#D4AF37') : (jewellery.rings?.accent_hex || '#D4AF37')};"></div>
            <div class="piece-info">
              <div class="piece-meta-top">
                <span class="piece-category">${isFemale ? "Fine Jewellery & Lip Tint" : "Fine Horology & Men's Jewellery"}</span>
                <span class="piece-hex">${isFemale ? (jewellery.lipstick_tint?.color_hex || "") : (jewellery.rings?.accent_hex || "")}</span>
              </div>
              ${jewelleryHTML}
              <div class="piece-tip">💡 ${jewellery.styling_tip || ""}</div>
            </div>
          </div>
        </div>

        <!-- Action Footer -->
        <div class="outfit-card-footer">
          <button type="button" class="btn-download-outfit" data-look="${look.look_number || idx + 1}">
            <span class="material-symbols-outlined" style="font-size: 16px;">download</span>
            <span>Download Lookboard (PNG)</span>
          </button>
          <button type="button" class="btn-copy-look" data-look="${look.look_number || idx + 1}">
            <span class="material-symbols-outlined" style="font-size: 16px;">content_copy</span>
            <span>Copy Specs</span>
          </button>
        </div>
      `;

      // Wire up Download PNG
      const dlBtn = card.querySelector(".btn-download-outfit");
      if (dlBtn) {
        dlBtn.addEventListener("click", () => {
          const svgEl = card.querySelector(".outfit-flatlay-svg");
          downloadOutfitAsPNG(look.look_number || idx + 1, svgEl, look.title);
        });
      }

      // Wire up Copy Specs
      const cpBtn = card.querySelector(".btn-copy-look");
      if (cpBtn) {
        cpBtn.addEventListener("click", () => {
          const jText = isFemale
            ? `Necklace: ${jewellery.necklace?.name || 'N/A'}, Earrings: ${jewellery.earrings?.name || 'N/A'}, Lip Tint: ${jewellery.lipstick_tint?.name || 'N/A'} (${jewellery.lipstick_tint?.color_hex || ''})`
            : `Ring: ${jewellery.rings?.name || 'N/A'}, Earrings: ${jewellery.earrings?.name || 'N/A'}, Watch: ${jewellery.watch?.name || 'N/A'}`;
          const text = `${look.title} (${look.clothing_type} • ${look.weather})\n` +
            `Upper: ${upper.name} (${upper.color_name} - ${upper.color_hex})\n` +
            `Bottom: ${bottom.name} (${bottom.color_name} - ${bottom.color_hex})\n` +
            `Shoes: ${shoes.name} (${shoes.color_name} - ${shoes.color_hex})\n` +
            `Jewellery & Accessories: ${jText}`;
          navigator.clipboard.writeText(text).then(() => {
            showToast("Copied outfit ensemble specs to clipboard!");
          }).catch(() => {
            showToast("Copied to clipboard!");
          });
        });
      }

      grid.appendChild(card);
    });
  }

  // --- Dynamic Live Outfit Re-generation on Filter Changes ---
  async function fetchOrUpdateOutfits() {
    if (!cachedApiData) return;
    const grid = document.getElementById("outfit-looks-grid");
    if (grid) {
      grid.style.opacity = "0.5";
      grid.style.pointerEvents = "none";
    }
    try {
      const rawUt = (cachedApiData.undertone && (cachedApiData.undertone.label || cachedApiData.undertone)) || "Warm";
      const utStr = typeof rawUt === "string" ? rawUt : (rawUt.label || "Warm");
      const repHex = (cachedApiData.skin_analysis && cachedApiData.skin_analysis.metrics && cachedApiData.skin_analysis.metrics.representative_hex) || "#C68B59";
      
      const payload = {
        undertone: utStr,
        palette: cachedApiData.palette || [],
        clothing_type: currentClothingType,
        weather: currentWeather,
        gender: currentGender,
        skin_hex: repHex
      };

      let res = null;
      for (const ep of buildApiEndpoints("/api/generate-outfits")) {
        try {
          res = await fetch(ep, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });
          if (res.ok) break;
        } catch (e) {}
      }

      if (res && res.ok) {
        const data = await res.json();
        if (data.outfits) {
          cachedApiData.outfits = data.outfits;
          renderCuratedOutfits(data.outfits);
        }
      }
    } catch (e) {
      console.warn("Failed to update outfits:", e);
    } finally {
      if (grid) {
        grid.style.opacity = "1";
        grid.style.pointerEvents = "auto";
      }
    }
  }

  // --- Export Outfit Lookboard as High-Res PNG Image ---
  function downloadOutfitAsPNG(lookNumber, svgElement, title) {
    if (!svgElement) return;
    try {
      const svgString = new XMLSerializer().serializeToString(svgElement);
      const svgBlob = new Blob([svgString], { type: "image/svg+xml;charset=utf-8" });
      const URL = window.URL || window.webkitURL || window;
      const blobURL = URL.createObjectURL(svgBlob);
      const image = new Image();

      image.onload = () => {
        const canvas = document.createElement("canvas");
        const vb = svgElement.viewBox && svgElement.viewBox.baseVal;
        const vbW = (vb && vb.width) || 660;
        const vbH = (vb && vb.height) || 840;
        // Ultra-crisp 2x Stitch Retina canvas (1320 x 1680)
        canvas.width = vbW * 2;
        canvas.height = vbH * 2;
        const ctx = canvas.getContext("2d");
        const isLight = document.documentElement.getAttribute("data-theme") === "light";
        ctx.fillStyle = isLight ? "#FFFFFF" : "#0B0E17";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
        URL.revokeObjectURL(blobURL);

        canvas.toBlob((pngBlob) => {
          if (!pngBlob) return;
          const a = document.createElement("a");
          const safeTitle = (title || `Look_${lookNumber}`).replace(/[^a-zA-Z0-9_-]/g, "_");
          a.download = `Otterlook_${safeTitle}_Outfit_Board.png`;
          a.href = URL.createObjectURL(pngBlob);
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          showToast(`Exported Look 0${lookNumber} high-res outfit board!`);
        }, "image/png", 0.95);
      };
      image.src = blobURL;
    } catch (err) {
      console.warn("PNG download fallback:", err);
      showToast("Downloading SVG vector outfit lookboard...");
      const svgBlob = new Blob([new XMLSerializer().serializeToString(svgElement)], { type: "image/svg+xml" });
      const a = document.createElement("a");
      a.download = `Otterlook_Look_${lookNumber}_Outfit_Board.svg`;
      a.href = URL.createObjectURL(svgBlob);
      a.click();
    }
  }

  function renderRecGrid(containerId, items, defaultCategory) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = "";
    if (!items || items.length === 0) {
      container.innerHTML = "<p style='color: var(--text-muted); font-size: 0.85rem; padding: 1rem;'>No items found for this category.</p>";
      return;
    }

    items.forEach((item, idx) => {
      const card = document.createElement("div");
      card.className = "rec-card";
      card.style.animationDelay = `${idx * 40}ms`;
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

  // --- Canvas Rendering for Autonomous Skin Colorimetry & Facial Areas ---
  function drawFacialLandmarksCanvas(skinHex, undertoneLabel, data) {
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
    const areas = (skinAnalysis && skinAnalysis.areas) || lastExtractedAreas || {};
    let faceBox = (skinAnalysis && skinAnalysis.faceBox) || lastExtractedFaceBox || null;

    if (!faceBox && data && data.face && data.face.bounding_box) {
      const [bx, by, bw, bh] = data.face.bounding_box;
      faceBox = { x: bx, y: by, width: bw, height: bh };
    }

    const hex = skinHex || "#D4AF37";
    const label = undertoneLabel || "Undertone";
    const detectedGender = (data && data.gender && (data.gender.detected || data.gender.label)) || "Natural";

    // Face bounding box, region marks, and bottom summary bar removed for a clean portrait presentation
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

  // --- Active Learning / Feedback Widget Logic ---
  const feedbackWidget = document.getElementById("feedback-widget");
  const feedbackConfirmBtn = document.getElementById("feedback-confirm-btn");
  const feedbackStatus = document.getElementById("feedback-status");
  const feedbackChips = document.querySelectorAll(".feedback-chip");

  function resetFeedbackWidget(data) {
    if (!feedbackWidget) return;
    if (feedbackStatus) {
      feedbackStatus.classList.add("hidden");
      feedbackStatus.className = "feedback-status hidden";
      feedbackStatus.textContent = "";
    }
    if (feedbackConfirmBtn) {
      feedbackConfirmBtn.disabled = false;
    }
    feedbackChips.forEach((chip) => {
      chip.disabled = false;
      chip.classList.remove("active");
    });
  }

  async function handleFeedbackSubmission(correctedUndertone) {
    if (!cachedApiData || !cachedApiData.analysis_id) {
      if (feedbackStatus) {
        feedbackStatus.textContent = "Analysis ID unavailable. Feedback requires database connection.";
        feedbackStatus.className = "feedback-status error";
        feedbackStatus.classList.remove("hidden");
      }
      return;
    }

    if (feedbackConfirmBtn) feedbackConfirmBtn.disabled = true;
    feedbackChips.forEach((chip) => (chip.disabled = true));

    try {
      let resp = null;
      for (const ep of buildApiEndpoints("/api/feedback")) {
        try {
          resp = await fetch(ep, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              analysis_id: cachedApiData.analysis_id,
              corrected_undertone: correctedUndertone,
            }),
          });
          if (resp.ok) break;
        } catch (e) {}
      }
      if (!resp) throw new Error("Feedback endpoint unreachable.");

      const resData = await resp.json();
      if (resp.ok && resData.success) {
        if (feedbackStatus) {
          feedbackStatus.innerHTML = `<span class="material-symbols-outlined" style="font-size: 16px;">check</span> Feedback recorded (${correctedUndertone}). Thank you for helping refine the model!`;
          feedbackStatus.className = "feedback-status";
          feedbackStatus.classList.remove("hidden");
        }
      } else {
        throw new Error(resData.detail || resData.error || "Failed to save feedback.");
      }
    } catch (err) {
      if (feedbackStatus) {
        feedbackStatus.textContent = err.message || "Could not submit feedback.";
        feedbackStatus.className = "feedback-status error";
        feedbackStatus.classList.remove("hidden");
      }
      if (feedbackConfirmBtn) feedbackConfirmBtn.disabled = false;
      feedbackChips.forEach((chip) => (chip.disabled = false));
    }
  }

  if (feedbackConfirmBtn) {
    feedbackConfirmBtn.addEventListener("click", () => {
      const currentLabel = (cachedApiData && cachedApiData.undertone && cachedApiData.undertone.label) || "Warm";
      handleFeedbackSubmission(currentLabel);
    });
  }

  feedbackChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      feedbackChips.forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      const chosen = chip.getAttribute("data-undertone");
      if (chosen) handleFeedbackSubmission(chosen);
    });
  });

  // --- Google Material Design 3 Ripple Interaction Engine ---
  function triggerMaterialRipple(event, targetElement) {
    const rect = targetElement.getBoundingClientRect();
    const circle = document.createElement("span");
    const diameter = Math.max(rect.width, rect.height);
    const radius = diameter / 2;
    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${event.clientX - rect.left - radius}px`;
    circle.style.top = `${event.clientY - rect.top - radius}px`;
    circle.classList.add("m3-ripple");
    const existingRipple = targetElement.querySelector(".m3-ripple");
    if (existingRipple) existingRipple.remove();
    targetElement.appendChild(circle);
    setTimeout(() => {
      if (circle && circle.parentNode) circle.remove();
    }, 600);
  }

  document.addEventListener("pointerdown", (e) => {
    const interactiveTarget = e.target.closest(".btn, .tab-btn, .swatch-card, .skin-harmony-card, .rec-card, .feedback-chip, .theme-toggle");
    if (interactiveTarget) {
      triggerMaterialRipple(e, interactiveTarget);
    }
  });

  // --- Google Cloud Console OAuth & Limited-Character Login Gate ---
  (async function initAuthLogin() {
    const loginPage = document.getElementById("auth-login-page");
    const googleContainer = document.getElementById("google-signin-container");
    const quickForm = document.getElementById("quick-login-form");
    const nameInput = document.getElementById("login-name-input");
    const charCountEl = document.getElementById("login-char-count");
    const loginErrorEl = document.getElementById("auth-login-error");
    const userChip = document.getElementById("header-user-chip");
    const userNameEl = document.getElementById("header-user-name");
    const logoutBtn = document.getElementById("logout-btn");
    const STORAGE_KEY = "otterlook_user_v1";

    const applySession = (user) => {
      if (!user || !user.name) {
        if (loginPage) loginPage.classList.remove("hidden");
        if (userChip) userChip.classList.add("hidden");
        return;
      }
      const cleanName = String(user.name).trim().slice(0, 16);
      if (userNameEl) userNameEl.textContent = cleanName;
      if (userChip) userChip.classList.remove("hidden");
      if (loginPage) loginPage.classList.add("hidden");
    };

    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
      applySession(saved);
    } catch (_) {
      applySession(null);
    }

    if (nameInput && charCountEl) {
      nameInput.addEventListener("input", () => {
        if (nameInput.value.length > 16) nameInput.value = nameInput.value.slice(0, 16);
        charCountEl.textContent = `${nameInput.value.length}/16`;
      });
    }

    if (quickForm && nameInput) {
      quickForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const val = nameInput.value.trim().slice(0, 16);
        if (val.length < 2) {
          if (loginErrorEl) {
            loginErrorEl.textContent = "Enter 2–16 characters.";
            loginErrorEl.classList.remove("hidden");
          }
          return;
        }
        const user = { name: val, provider: "name" };
        try { localStorage.setItem(STORAGE_KEY, JSON.stringify(user)); } catch (_) {}
        if (loginErrorEl) loginErrorEl.classList.add("hidden");
        applySession(user);
      });
    }

    if (logoutBtn) {
      logoutBtn.addEventListener("click", () => {
        try { localStorage.removeItem(STORAGE_KEY); } catch (_) {}
        if (nameInput) nameInput.value = "";
        if (charCountEl) charCountEl.textContent = "0/16";
        applySession(null);
      });
    }

    // Load Google Cloud Console OAuth Client ID from backend
    try {
      let cfg = null;
      for (const ep of buildApiEndpoints("/api/auth/config")) {
        try {
          const r = await fetch(ep);
          if (r.ok) { cfg = await r.json(); break; }
        } catch (_) {}
      }
      if (cfg && cfg.google_enabled && cfg.google_client_id && googleContainer) {
        const renderGsi = () => {
          if (!window.google || !window.google.accounts || !window.google.accounts.id) return false;
          window.google.accounts.id.initialize({
            client_id: cfg.google_client_id,
            callback: async (response) => {
              try {
                let authData = null;
                for (const ep of buildApiEndpoints("/api/auth/google")) {
                  try {
                    const r = await fetch(ep, {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({ credential: response.credential }),
                    });
                    if (r.ok) { authData = await r.json(); break; }
                  } catch (_) {}
                }
                if (authData && authData.success && authData.user) {
                  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(authData.user)); } catch (_) {}
                  applySession(authData.user);
                } else if (loginErrorEl) {
                  loginErrorEl.textContent = "Google sign-in failed.";
                  loginErrorEl.classList.remove("hidden");
                }
              } catch (_) {}
            },
          });
          window.google.accounts.id.renderButton(googleContainer, {
            theme: "filled_black",
            size: "large",
            shape: "pill",
            width: 280,
          });
          return true;
        };
        if (!renderGsi()) {
          const gsiTimer = setInterval(() => {
            if (renderGsi()) clearInterval(gsiTimer);
          }, 250);
          setTimeout(() => clearInterval(gsiTimer), 6000);
        }
      } else if (googleContainer) {
        googleContainer.style.display = "none";
      }
    } catch (_) {}
  })();

  // Global restrictions to disable copy, cut, paste and context menu
  document.addEventListener('copy', (e) => e.preventDefault());
  document.addEventListener('cut', (e) => e.preventDefault());
  document.addEventListener('paste', (e) => e.preventDefault());
  document.addEventListener('contextmenu', (e) => e.preventDefault());
});
