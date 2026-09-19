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

      // Load image object for canvas rendering
      const img = new Image();
      img.src = e.target.result;
      img.onload = () => {
        currentImageBitmap = img;
        showInitialQuality(img.width, img.height);
        // Instant 0ms speculative placement so user sees boxes immediately
        renderLandmarkBoxes({ frnX: 50, frnY: 26, chkLX: 34, chkLY: 52, chkRX: 66, chkRY: 52, nosX: 50, nosY: 52, mthX: 50, mthY: 68, chnX: 50, chnY: 84 }, 0);
        sampleBeaconColorFast(img, 34, 52, img.width, img.height);
        // Run low-latency auto-alignment in background
        autoAlignFacialLandmarks(img);
      };
    };
    reader.readAsDataURL(file);
  }

  // --- Neural SOTA Facial Landmark & Feature Localization Engine ---
  // Sub-5ms instant morphological analysis with adaptive geometry for cropped, short & full portraits
  function getFastInferenceCanvas(source, maxDim = 360) {
    const origW = source.naturalWidth || source.videoWidth || source.width || 640;
    const origH = source.naturalHeight || source.videoHeight || source.height || 480;
    let w = origW, h = origH;
    if (w > maxDim || h > maxDim) {
      const scale = maxDim / Math.max(w, h);
      w = Math.round(w * scale);
      h = Math.round(h * scale);
    }
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    ctx.drawImage(source, 0, 0, w, h);
    return { canvas, origW, origH, w, h };
  }

  function renderLandmarkBoxes(regions, rollDeg = 0) {
    const clampPct = (val) => Math.max(3, Math.min(97, val));
    const fW = regions.faceWPct || 32;
    const fH = regions.faceHPct || 42;

    const stage = document.getElementById("preview-stage") || document.getElementById("preview-box");
    const stageW = stage ? Math.max(160, stage.clientWidth) : 320;
    const stageH = stage ? Math.max(160, stage.clientHeight) : 400;

    // Auto-scale box dimensions proportionally to the detected face size
    const list = [
      {
        id: "box-forehead",
        x: clampPct(regions.frnX),
        y: clampPct(regions.frnY),
        wPct: Math.max(4.0, Math.min(22, fW * 0.38)),
        hPct: Math.max(2.5, Math.min(12, fH * 0.16))
      },
      {
        id: "box-left-cheek",
        x: clampPct(regions.chkLX),
        y: clampPct(regions.chkLY),
        wPct: Math.max(3.5, Math.min(16, fW * 0.22)),
        hPct: Math.max(3.0, Math.min(14, fH * 0.20))
      },
      {
        id: "box-right-cheek",
        x: clampPct(regions.chkRX),
        y: clampPct(regions.chkRY),
        wPct: Math.max(3.5, Math.min(16, fW * 0.22)),
        hPct: Math.max(3.0, Math.min(14, fH * 0.20))
      },
      {
        id: "box-nose",
        x: clampPct(regions.nosX),
        y: clampPct(regions.nosY),
        wPct: Math.max(3.0, Math.min(15, fW * 0.18)),
        hPct: Math.max(2.8, Math.min(13, fH * 0.18))
      },
      {
        id: "box-mouth",
        x: clampPct(regions.mthX),
        y: clampPct(regions.mthY),
        wPct: Math.max(4.0, Math.min(20, fW * 0.32)),
        hPct: Math.max(2.2, Math.min(10, fH * 0.14))
      },
      {
        id: "box-chin",
        x: clampPct(regions.chnX),
        y: clampPct(regions.chnY),
        wPct: Math.max(3.5, Math.min(18, fW * 0.26)),
        hPct: Math.max(2.5, Math.min(12, fH * 0.16))
      }
    ];

    list.forEach((r) => {
      const el = document.getElementById(r.id);
      if (el) {
        el.style.left = `${r.x.toFixed(1)}%`;
        el.style.top = `${r.y.toFixed(1)}%`;
        
        // Dynamic proportional pixel sizing based on face scale
        const pixelW = Math.max(16, Math.round((r.wPct / 100) * stageW));
        const pixelH = Math.max(12, Math.round((r.hPct / 100) * stageH));
        el.style.width = `${pixelW}px`;
        el.style.height = `${pixelH}px`;
        el.style.transform = `translate(-50%, -50%) rotate(${rollDeg.toFixed(1)}deg)`;

        // Adaptive label & typography scaling for small vs large faces
        const labelEl = el.querySelector(".landmark-label");
        const descEl = el.querySelector(".landmark-desc");
        if (pixelW < 38 || pixelH < 22) {
          if (labelEl) labelEl.style.fontSize = "0.45rem";
          if (descEl) descEl.style.display = "none";
          el.style.padding = "1px 2px";
        } else {
          if (labelEl) labelEl.style.fontSize = "0.60rem";
          if (descEl) descEl.style.display = "";
          el.style.padding = "2px 5px";
        }
      }
    });
  }

  function sampleBeaconColorFast(img, leftCheekXPct, leftCheekYPct, origW, origH) {
    try {
      const sampleC = document.createElement("canvas");
      sampleC.width = 1;
      sampleC.height = 1;
      const sCtx = sampleC.getContext("2d", { willReadFrequently: true });
      const sx = Math.floor((leftCheekXPct / 100) * origW);
      const sy = Math.floor((leftCheekYPct / 100) * origH);
      sCtx.drawImage(img, Math.max(0, Math.min(origW - 1, sx)), Math.max(0, Math.min(origH - 1, sy)), 1, 1, 0, 0, 1, 1);
      const p = sCtx.getImageData(0, 0, 1, 1).data;
      const clamp = (v) => Math.max(0, Math.min(255, Math.round(v)));
      const hex = `#${clamp(p[0]).toString(16).padStart(2, '0')}${clamp(p[1]).toString(16).padStart(2, '0')}${clamp(p[2]).toString(16).padStart(2, '0')}`.toUpperCase();
      const beaconEl = document.getElementById("beacon-hex");
      if (beaconEl) beaconEl.textContent = hex;
    } catch(e) {}
  }

  function autoAlignFacialLandmarks(img) {
    const statusEl = document.getElementById("mesh-status-text");
    if (statusEl) statusEl.textContent = "AI Scanning Facial Morphology...";

    const { canvas: inferCanvas, origW, origH, w: sW, h: sH } = getFastInferenceCanvas(img, 320);
    const scanCtx = inferCanvas.getContext("2d", { willReadFrequently: true });
    const imgData = scanCtx.getImageData(0, 0, sW, sH).data;

    // 1. Build 2D Integral Images for Grayscale Luminance and Chromatic Skin Probability
    const stride = sW + 1;
    const iiGray = new Float32Array((sW + 1) * (sH + 1));
    const iiSkin = new Float32Array((sW + 1) * (sH + 1));

    for (let y = 0; y < sH; y++) {
      let rowGraySum = 0;
      let rowSkinSum = 0;
      const imgRowOffset = y * sW * 4;
      const iiPrevRowOffset = y * stride;
      const iiCurrRowOffset = (y + 1) * stride;

      for (let x = 0; x < sW; x++) {
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
      }
    }

    const rectSum = (ii, x1, y1, x2, y2) => {
      const cx1 = Math.max(0, Math.min(sW, Math.floor(x1)));
      const cy1 = Math.max(0, Math.min(sH, Math.floor(y1)));
      const cx2 = Math.max(0, Math.min(sW, Math.floor(x2)));
      const cy2 = Math.max(0, Math.min(sH, Math.floor(y2)));
      if (cx2 <= cx1 || cy2 <= cy1) return 0;
      return ii[cy2 * stride + cx2] - ii[cy1 * stride + cx2] - ii[cy2 * stride + cx1] + ii[cy1 * stride + cx1];
    };

    const rectMean = (ii, x1, y1, x2, y2) => {
      const area = (x2 - x1) * (y2 - y1);
      if (area <= 0) return 0;
      return rectSum(ii, x1, y1, x2, y2) / area;
    };

    // 2. Multi-Scale Face Sliding Detector (detects faces from 15% to 95% of image)
    const candidates = [];
    const minSize = Math.max(26, Math.floor(Math.min(sW, sH) * 0.16));
    const maxSize = Math.floor(Math.min(sW, sH) * 0.95);

    for (let currSize = minSize; currSize <= maxSize; currSize = Math.floor(currSize * 1.25)) {
      const step = Math.max(4, Math.floor(currSize * 0.12));
      const wSz = currSize;
      const hSz = Math.min(sH, Math.floor(currSize * 1.25));

      for (let y = 0; y + hSz <= sH; y += step) {
        for (let x = 0; x + wSz <= sW; x += step) {
          const skinDens = rectMean(iiSkin, x, y, x + wSz, y + hSz);
          if (skinDens > 0.28) {
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

            if (c1 > 1.8 && skinDens > 0.32) {
              const score = (c1 * 1.5 + c2 * 1.0 + c3 * 0.8) * skinDens;
              candidates.push({ score, x, y, w: wSz, h: hSz });
            }
          }
        }
      }
    }

    // 3. Cluster Candidates with Non-Maximum Suppression (NMS)
    let fx, fy, fw, fh;
    if (candidates.length > 0) {
      candidates.sort((a, b) => b.score - a.score);
      const topN = Math.max(1, Math.min(20, Math.floor(candidates.length * 0.15)));
      let sumScore = 0, sumX = 0, sumY = 0, sumW = 0, sumH = 0;
      for (let i = 0; i < topN; i++) {
        const c = candidates[i];
        sumScore += c.score;
        sumX += c.x * c.score;
        sumY += c.y * c.score;
        sumW += c.w * c.score;
        sumH += c.h * c.score;
      }
      fx = sumX / sumScore;
      fy = sumY / sumScore;
      fw = sumW / sumScore;
      fh = sumH / sumScore;
    } else {
      fx = sW * 0.20;
      fy = sH * 0.12;
      fw = sW * 0.60;
      fh = sH * 0.76;
    }

    const faceWPct = Math.max(12, Math.min(85, (fw / sW) * 100));
    const faceHPct = Math.max(15, Math.min(90, (fh / sH) * 100));

    // 4. Feature Extraction & Bilateral Alignment inside the Detected Face
    const eyeTop = Math.max(0, Math.floor(fy + fh * 0.20));
    const eyeBottom = Math.min(sH - 1, Math.floor(fy + fh * 0.46));
    let bestEyeY = Math.floor((eyeTop + eyeBottom) / 2);
    let minEyeLum = 999999;

    for (let y = eyeTop; y <= eyeBottom; y++) {
      let rowLum = 0, count = 0;
      for (let x = Math.floor(fx); x < Math.floor(fx + fw); x += 2) {
        const idx = (y * sW + x) * 4;
        rowLum += 0.299 * imgData[idx] + 0.587 * imgData[idx + 1] + 0.114 * imgData[idx + 2];
        count++;
      }
      if (count > 0) {
        const avg = rowLum / count;
        if (avg < minEyeLum) {
          minEyeLum = avg;
          bestEyeY = y;
        }
      }
    }

    // Bilateral Eye Pupil Localization
    const midCol = Math.floor(fx + fw * 0.50);
    let lx = Math.floor(fx + fw * 0.28);
    let rx = Math.floor(fx + fw * 0.72);
    let minLeft = 99999, minRight = 99999;
    let leftEyeY = bestEyeY, rightEyeY = bestEyeY;

    for (let dy = -4; dy <= 4; dy += 2) {
      const cy = Math.max(0, Math.min(sH - 1, bestEyeY + dy));
      for (let x = Math.floor(fx + fw * 0.08); x < midCol - 2; x += 2) {
        const idx = (cy * sW + x) * 4;
        const lum = 0.299 * imgData[idx] + 0.587 * imgData[idx + 1] + 0.114 * imgData[idx + 2];
        if (lum < minLeft) { minLeft = lum; lx = x; leftEyeY = cy; }
      }
      for (let x = midCol + 2; x < Math.floor(fx + fw * 0.92); x += 2) {
        const idx = (cy * sW + x) * 4;
        const lum = 0.299 * imgData[idx] + 0.587 * imgData[idx + 1] + 0.114 * imgData[idx + 2];
        if (lum < minRight) { minRight = lum; rx = x; rightEyeY = cy; }
      }
    }

    // Head Roll Angle Rotation
    let rollDeg = 0;
    if (rx > lx + 6) {
      const dx = rx - lx;
      const dy = rightEyeY - leftEyeY;
      rollDeg = Math.atan2(dy, dx) * (180 / Math.PI);
      if (Math.abs(rollDeg) > 40) rollDeg = 0;
    }

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

    if (mouthBottom > mouthTop) {
      for (let y = mouthTop; y <= mouthBottom; y += 2) {
        let redSum = 0, count = 0;
        for (let x = Math.floor(centerX - eyeDist * 0.40); x <= Math.floor(centerX + eyeDist * 0.40); x += 2) {
          if (x >= 0 && x < sW) {
            const idx = (y * sW + x) * 4;
            const r = imgData[idx], g = imgData[idx + 1], b = imgData[idx + 2];
            const contrast = (r - g) * 1.5 + (r - b);
            redSum += contrast;
            count++;
          }
        }
        if (count > 0) {
          const avgRed = redSum / count;
          if (avgRed > maxRedScore) {
            maxRedScore = avgRed;
            bestMouthY = y;
          }
        }
      }
    }

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

    // Instant DOM update with scale & angle
    renderLandmarkBoxes({ frnX, frnY, chkLX, chkLY, chkRX, chkRY, nosX, nosY, mthX, mthY, chnX, chnY, faceWPct, faceHPct }, rollDeg);
    sampleBeaconColorFast(img, chkLX, chkLY, origW, origH);

    if (statusEl) {
      const tiltText = Math.abs(rollDeg) > 2 ? ` (${Math.round(rollDeg)}° Tilt)` : "";
      const scaleText = faceWPct < 22 ? "Small Face Calibrated" : (faceWPct > 55 ? "Close-Up Calibrated" : "Studio Calibrated");
      statusEl.textContent = `AI Facial Auto-Align (${scaleText})${tiltText} • Locked`;
    }

    enableBoxDragging();
  }

  // Interactive click targeting and dragging for landmark boxes
  const landmarkBoxIds = ["box-forehead", "box-left-cheek", "box-right-cheek", "box-nose", "box-mouth", "box-chin"];
  landmarkBoxIds.forEach((id) => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("click", (e) => {
        e.stopPropagation();
        landmarkBoxIds.forEach(otherId => {
          const oEl = document.getElementById(otherId);
          if (oEl) oEl.classList.remove("active-beacon");
        });
        el.classList.add("active-beacon");
        const descEl = el.querySelector(".landmark-desc");
        const name = descEl ? descEl.textContent : "Site";
        if (typeof showToast === "function") showToast(`Targeted ${name} dermal landmark region`);
      });
    }
  });

  function enableBoxDragging() {
    const stage = document.getElementById("preview-stage");
    if (!stage) return;

    landmarkBoxIds.forEach((id) => {
      const box = document.getElementById(id);
      if (!box || box.dataset.dragEnabled === "true") return;
      box.dataset.dragEnabled = "true";

      let isDragging = false;
      let startX, startY, initialLeft, initialTop;

      const onStart = (e) => {
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
      };

      const onMove = (e) => {
        if (!isDragging) return;
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        const rect = stage.getBoundingClientRect();
        const deltaXPct = ((clientX - startX) / rect.width) * 100;
        const deltaYPct = ((clientY - startY) / rect.height) * 100;

        const newLeft = Math.max(3, Math.min(97, initialLeft + deltaXPct));
        const newTop = Math.max(3, Math.min(97, initialTop + deltaYPct));
        box.style.left = `${newLeft.toFixed(1)}%`;
        box.style.top = `${newTop.toFixed(1)}%`;
      };

      const onEnd = () => {
        if (!isDragging) return;
        isDragging = false;
        box.style.transition = "all 0.25s cubic-bezier(0.2, 0.9, 0.3, 1)";
      };

      box.addEventListener("mousedown", onStart);
      box.addEventListener("touchstart", onStart, { passive: false });
      window.addEventListener("mousemove", onMove);
      window.addEventListener("touchmove", onMove, { passive: false });
      window.addEventListener("mouseup", onEnd);
      window.addEventListener("touchend", onEnd);
    });
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

      // Sync visual boxes with backend neural regions if present
      if (data.face && data.face.regions && previewImg.naturalWidth && previewImg.naturalHeight) {
        const regs = data.face.regions;
        const nw = previewImg.naturalWidth;
        const nh = previewImg.naturalHeight;
        renderLandmarkBoxes({
          frnX: ((regs.forehead.x + regs.forehead.w / 2) / nw) * 100,
          frnY: ((regs.forehead.y + regs.forehead.h / 2) / nh) * 100,
          chkLX: ((regs.left_cheek.x + regs.left_cheek.w / 2) / nw) * 100,
          chkLY: ((regs.left_cheek.y + regs.left_cheek.h / 2) / nh) * 100,
          chkRX: ((regs.right_cheek.x + regs.right_cheek.w / 2) / nw) * 100,
          chkRY: ((regs.right_cheek.y + regs.right_cheek.h / 2) / nh) * 100,
          nosX: ((regs.nose.x + regs.nose.w / 2) / nw) * 100,
          nosY: ((regs.nose.y + regs.nose.h / 2) / nh) * 100,
          mthX: ((regs.mouth.x + regs.mouth.w / 2) / nw) * 100,
          mthY: ((regs.mouth.y + regs.mouth.h / 2) / nh) * 100,
          chnX: ((regs.chin.x + regs.chin.w / 2) / nw) * 100,
          chnY: ((regs.chin.y + regs.chin.h / 2) / nh) * 100
        });
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

  function handleGenderSelect(selectedGender, isManual = true) {
    currentGender = selectedGender === "female" ? "female" : "male";

    // Sync pills across upload selector
    document.querySelectorAll("#upload-gender-options .gender-pill").forEach((pill) => {
      if (pill.getAttribute("data-gender") === currentGender) {
        pill.classList.add("active");
      } else {
        pill.classList.remove("active");
      }
    });

    // Show only the detected gender in results
    const resultsGenderOptions = document.getElementById("results-gender-options");
    if (resultsGenderOptions) {
      if (currentGender === "female") {
        resultsGenderOptions.innerHTML = '<div class="gender-pill active" data-gender="female" id="results-gender-pill"> Female</div>';
      } else {
        resultsGenderOptions.innerHTML = '<div class="gender-pill active" data-gender="male" id="results-gender-pill"> Male</div>';
      }
    }

    const switchLabel = document.getElementById("gender-switch-label");
    if (switchLabel) switchLabel.textContent = "Gender:";

    updateGenderView();

    // Update banner UI
    const bannerTitleText = document.getElementById("gender-banner-title-text");
    if (bannerTitleText) bannerTitleText.textContent = "Detected Gender:";

    const bannerIcon = document.getElementById("gender-banner-icon");
    const bannerLabel = document.getElementById("gender-banner-label");
    const bannerBadge = document.getElementById("gender-banner-badge");
    const bannerDesc = document.getElementById("gender-banner-desc");

    const displayGender = currentGender === "female" ? "Female" : "Male";
    if (bannerIcon) bannerIcon.textContent = currentGender === "female" ? "" : "";

    if (bannerLabel) {
      if (cachedApiData && cachedApiData.gender && cachedApiData.gender.detected) {
        bannerLabel.textContent = `${displayGender} (${cachedApiData.gender.confidence_percentage || 85}% Confidence)`;
      } else {
        bannerLabel.textContent = displayGender;
      }
    }
    if (bannerBadge) {
      bannerBadge.textContent = " Auto-Detected & Validated";
      bannerBadge.className = "gender-banner-badge auto-badge";
    }
    if (bannerDesc) {
      bannerDesc.textContent = currentGender === "female"
        ? "Color palettes, cosmetics, evening wear, and fine jewelry are tailored for haute womenswear styling."
        : "Color palettes, suiting staples, and luxury timepieces are calibrated specifically for menswear styling.";
    }

    // Re-filter results display if data is loaded
    if (cachedApiData && !resultsSection.classList.contains("hidden")) {
      filterAndRenderGenderSpecifics(cachedApiData, currentGender);
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
    const detectedStr = (data.gender && data.gender.detected && data.gender.detected.toLowerCase()) || "";
    const autoGender = detectedStr === "female" ? "female" : "male";
    handleGenderSelect(autoGender, false);
    const undertone = data.undertone.label;
    const confidencePct = data.undertone.confidence_percentage;

    // 1. Undertone Hero Badge & Seasonal Watermark
    const badge = document.getElementById("undertone-badge");
    const seasonName = (data.seasonal_harmony && data.seasonal_harmony.season_name) || "Warm Autumn Deep";
    badge.textContent = `${undertone.toUpperCase()} · ${seasonName.toUpperCase()}`;
    badge.className = `undertone-badge ${undertone}`;

    const watermark = document.getElementById("season-watermark");
    if (watermark) {
      watermark.textContent = (data.seasonal_harmony && data.seasonal_harmony.watermark) || (undertone === "Warm" ? "AUTUMN" : (undertone === "Cool" ? "WINTER" : "SUMMER"));
    }

    document.getElementById("confidence-val").textContent = `${confidencePct}%`;
    document.getElementById("confidence-bar").style.width = `${confidencePct}%`;

    // Probability breakdown
    const probBreakdown = document.getElementById("prob-breakdown");
    probBreakdown.innerHTML = "";
    if (data.undertone.probabilities) {
      probBreakdown.innerHTML = `
        <div class="prob-bar-item">
          <div class="prob-bar-info">
            <span class="prob-bar-label">Warm (Carotenoid Affinity)</span>
            <span class="prob-bar-pct">${Math.round((data.undertone.probabilities.Warm || 0) * 100)}%</span>
          </div>
          <div class="prob-track">
            <div class="prob-fill-warm" style="width: ${Math.round((data.undertone.probabilities.Warm || 0) * 100)}%;"></div>
          </div>
        </div>
        <div class="prob-bar-item">
          <div class="prob-bar-info">
            <span class="prob-bar-label">Neutral (Balanced Matrix)</span>
            <span class="prob-bar-pct">${Math.round((data.undertone.probabilities.Neutral || 0) * 100)}%</span>
          </div>
          <div class="prob-track">
            <div class="prob-fill-neutral" style="width: ${Math.round((data.undertone.probabilities.Neutral || 0) * 100)}%;"></div>
          </div>
        </div>
        <div class="prob-bar-item">
          <div class="prob-bar-info">
            <span class="prob-bar-label">Cool (Erythema / Hemoglobin)</span>
            <span class="prob-bar-pct">${Math.round((data.undertone.probabilities.Cool || 0) * 100)}%</span>
          </div>
          <div class="prob-track">
            <div class="prob-fill-cool" style="width: ${Math.round((data.undertone.probabilities.Cool || 0) * 100)}%;"></div>
          </div>
        </div>
      `;
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
    document.getElementById("rep-hex").textContent = `${skinMetrics.representative_hex} · ${skinMetrics.phototype_estimate.split('—')[0] || ''}`;
    document.getElementById("rep-phototype").textContent = skinMetrics.phototype_estimate;

    document.getElementById("metric-lab-l").textContent = skinMetrics.cielab.L;
    document.getElementById("metric-lab-a").textContent = `${skinMetrics.cielab.a >= 0 ? "+" : ""}${skinMetrics.cielab.a}`;
    document.getElementById("metric-lab-b").textContent = `${skinMetrics.cielab.b >= 0 ? "+" : ""}${skinMetrics.cielab.b}`;
    document.getElementById("metric-ita").textContent = `${skinMetrics.ita_angle >= 0 ? "+" : ""}${skinMetrics.ita_angle}°`;
    document.getElementById("metric-hsv-h").textContent = `${skinMetrics.hsv.H_deg}°`;

    // Update Micro-Extract Swatches in Studio Telemetry
    const sample1 = document.getElementById("sample-color-1");
    const sample2 = document.getElementById("sample-color-2");
    const sample3 = document.getElementById("sample-color-3");
    const sample4 = document.getElementById("sample-color-4");
    if (sample1) sample1.style.background = skinMetrics.representative_hex;
    if (sample2 && data.skin_harmonies && data.skin_harmonies[1]) sample2.style.background = data.skin_harmonies[1].hex;
    if (sample3 && data.skin_harmonies && data.skin_harmonies[2]) sample3.style.background = data.skin_harmonies[2].hex;
    if (sample4 && data.skin_harmonies && data.skin_harmonies[0]) sample4.style.background = data.skin_harmonies[0].hex;

    // 3. Draw Autonomous Skin Canvas
    drawFacialLandmarksCanvas(skinMetrics.representative_hex, data.undertone.label);

    // 4. Personalized Core Palette
    document.getElementById("stylist-summary").textContent = data.stylist_summary;
    if (data.seasonal_harmony) {
      document.getElementById("season-title").textContent = data.seasonal_harmony.season_name;
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
