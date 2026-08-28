"""
FastAPI Backend Application for AI-Based Personal Colour Analysis System.
Author: AI Personal Colour Analysis System
"""

import os
import sys
import io
import cv2
import numpy as np

# Ensure backend directory is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from typing import Dict, Any

from utils.image_quality import analyze_image_quality
from vision.face_detection import FaceDetector
from vision.skin_detection import SkinExtractor
from vision.colour_extraction import ColourFeatureExtractor
from ml.predictor import UndertonePredictor
from recommendations.palette_generator import PaletteGenerator

app = FastAPI(
    title="AI-Based Personal Colour Analysis API",
    description="Skin undertone classification & personalized colour palette recommendation engine.",
    version="1.0.0"
)

# Enable CORS for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core pipeline singletons
face_detector = FaceDetector()
skin_extractor = SkinExtractor()
feature_extractor = ColourFeatureExtractor()
undertone_predictor = UndertonePredictor()
palette_generator = PaletteGenerator()

ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint returning system status and model readiness.
    """
    return {
        "status": "healthy",
        "service": "AI Personal Colour Analysis System",
        "version": "1.0.0",
        "model_loaded": undertone_predictor.pipeline is not None,
        "model_name": undertone_predictor.model_name,
        "classes": undertone_predictor.classes
    }

@app.post("/api/analyze")
async def analyze_portrait(file: UploadFile = File(...)):
    """
    Complete analysis pipeline:
    1. Validate image format & dimensions
    2. Quality assessment (blur, brightness, contrast)
    3. Face detection & landmark localization
    4. Multi-region skin sampling (forehead, cheeks, jaw)
    5. Outlier rejection & statistical color feature extraction (RGB, HSV, CIELAB, ITA)
    6. ML undertone classification (Random Forest / SVM)
    7. Personalized palette & style recommendations generation
    """
    if file.content_type not in ALLOWED_MIME_TYPES and not file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a JPG, JPEG, or PNG image."
        )

    try:
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File size exceeds the 15MB limit.")
            
        # Decode image in-memory using OpenCV
        nparr = np.frombuffer(contents, np.uint8)
        image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image_bgr is None or image_bgr.size == 0:
            raise HTTPException(status_code=400, detail="Unable to decode image. The file may be corrupted.")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image upload failed: {str(e)}")

    # Step 1: Image Quality Assessment
    quality_result = analyze_image_quality(image_bgr)
    if not quality_result["is_valid"]:
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "stage": "quality_check",
                "quality": quality_result,
                "error": quality_result["message"]
            }
        )

    # Step 2: Face Detection & Region Localization
    face_result = face_detector.detect_faces(image_bgr)
    if not face_result["success"]:
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "stage": "face_detection",
                "quality": quality_result,
                "error": face_result["message"],
                "face_count": face_result.get("face_count", 0)
            }
        )

    # Step 3: Multi-Region Skin Extraction & Outlier Rejection
    regions = face_result["regions"]
    skin_result = skin_extractor.extract_skin_pixels(image_bgr, regions)
    
    if skin_result["total_pixels"] < 30:
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "stage": "skin_extraction",
                "quality": quality_result,
                "error": "Insufficient clean skin pixels detected. Please ensure your face is well-lit and unobstructed."
            }
        )

    # Step 4: Statistical Color Feature Extraction (RGB, HSV, CIELAB, ITA)
    try:
        color_features = feature_extractor.extract_features(skin_result["pixels_bgr"])
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "stage": "feature_extraction",
                "error": f"Failed to compute color features: {str(e)}"
            }
        )

    # Step 5: ML Undertone Classification
    ml_prediction = undertone_predictor.predict(color_features["ml_features"])
    predicted_undertone = ml_prediction["label"]

    # Step 6: Personalized Palette & Styling Recommendation Engine
    recommendations_result = palette_generator.generate_recommendations(
        undertone=predicted_undertone,
        skin_metrics=color_features["display_metrics"]
    )

    # Return comprehensive structured response
    return {
        "success": True,
        "quality": {
            "score": quality_result["score"],
            "status": quality_result["status"],
            "details": quality_result["metrics"]
        },
        "face": {
            "face_count": face_result["face_count"],
            "bounding_box": face_result["bounding_box"],
            "regions": face_result["regions"],
            "has_landmarks": face_result.get("landmarks") is not None
        },
        "skin_analysis": {
            "total_sampled_pixels": skin_result["total_pixels"],
            "region_samples": skin_result["region_samples"],
            "metrics": color_features["display_metrics"]
        },
        "undertone": {
            "label": ml_prediction["label"],
            "confidence": ml_prediction["confidence"],
            "confidence_percentage": ml_prediction["confidence_percentage"],
            "probabilities": ml_prediction["probabilities"],
            "model_name": ml_prediction["model_name"],
            "explanation": ml_prediction["explanation"],
            "key_factors": ml_prediction["key_factors"]
        },
        "palette": recommendations_result["palette"],
        "recommendations": recommendations_result["recommendations"],
        "less_recommended": recommendations_result["less_recommended"],
        "seasonal_harmony": recommendations_result["seasonal_harmony"],
        "stylist_summary": recommendations_result["stylist_summary"],
        "foundation_advice": recommendations_result["foundation_advice"]
    }

@app.get("/api/palette/{undertone}")
async def get_palette_by_undertone(undertone: str):
    """
    Direct endpoint to fetch styling recommendations for an undertone.
    """
    valid = ["Warm", "Cool", "Neutral"]
    key = undertone.capitalize()
    if key not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid undertone. Choose from: {valid}")
        
    return palette_generator.generate_recommendations(undertone=key)

# Mount Frontend Static Directory
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_dir, "index.html"))
