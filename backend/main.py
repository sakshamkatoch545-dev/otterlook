"""
FastAPI Backend Application for AI-Based Personal Colour Analysis System.
Author: AI Personal Colour Analysis System
"""

import os
import sys
import io
import json
import base64
import logging
import cv2
import numpy as np

# Load .env file for local development (no-op if file doesn't exist)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Ensure root directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional

from backend.utils.image_quality import analyze_image_quality
from backend.vision.face_detection import FaceDetector
from backend.vision.skin_detection import SkinExtractor
from backend.vision.colour_extraction import ColourFeatureExtractor
from backend.ml.predictor import UndertonePredictor
from backend.recommendations.palette_generator import PaletteGenerator
from backend.db import supabase_client

logger = logging.getLogger("otterlook.api")


# Pydantic model for feedback requests
class FeedbackRequest(BaseModel):
    analysis_id: str
    corrected_undertone: str  # "Warm", "Cool", or "Neutral"

app = FastAPI(
    title="AI-Based Personal Colour Analysis API",
    description="Skin undertone classification & personalized colour palette recommendation engine.",
    version="1.0.0"
)

# Enable CORS for frontend flexibility across Streamlit (localhost:8501) and standalone (localhost:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
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

@app.post("/api/detect-face")
async def detect_face(
    request: Request,
    file: Optional[UploadFile] = File(None)
):
    """
    Dedicated endpoint to check if an uploaded image or camera snapshot contains a valid human face
    AND inspects lighting clarity.
    Accepts both multipart upload (file) and JSON with base64 data URL ({image: ...}).
    """
    try:
        image_bgr = None
        if file is not None:
            contents = await file.read()
            if contents:
                nparr = np.frombuffer(contents, np.uint8)
                image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image_bgr is None or image_bgr.size == 0:
            body = await request.body()
            if body:
                try:
                    data = json.loads(body.decode("utf-8"))
                    img_str = data.get("image") or data.get("file")
                    if img_str:
                        if "," in img_str:
                            img_str = img_str.split(",", 1)[1]
                        img_bytes = base64.b64decode(img_str)
                        nparr = np.frombuffer(img_bytes, np.uint8)
                        image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                except Exception:
                    pass

        if image_bgr is None or image_bgr.size == 0:
            return JSONResponse(
                status_code=400,
                content={"has_face": False, "face_count": 0, "lighting_clear": False, "message": "Invalid or unreadable image."}
            )
        
        # 1. Face detection FIRST (YOLO)
        face_res = face_detector.detect_faces(image_bgr)
        if not face_res.get("success") or face_res.get("face_count", 0) == 0:
            return {
                "has_face": False,
                "face_count": 0,
                "lighting_clear": False,
                "bounding_box": None,
                "message": "No human face detected. Please ensure your face is clearly visible."
            }
        
        img_h, img_w = image_bgr.shape[:2]
        bbox = face_res.get("bounding_box")
        pct_bbox = None
        if bbox:
            pct_bbox = {
                "x": bbox[0],
                "y": bbox[1],
                "w": bbox[2],
                "h": bbox[3],
                "pctX": (bbox[0] / img_w) * 100,
                "pctY": (bbox[1] / img_h) * 100,
                "pctW": (bbox[2] / img_w) * 100,
                "pctH": (bbox[3] / img_h) * 100
            }

        # 2. Lighting & Clarity check SECOND
        quality_res = analyze_image_quality(image_bgr)
        lighting_is_clear = bool(quality_res.get("is_valid", True))

        msg = "Face localized and lighting is clear." if lighting_is_clear else f"Face detected, but lighting is not clear: {quality_res.get('message')}"

        return {
            "has_face": True,
            "face_count": face_res.get("face_count", 1),
            "lighting_clear": lighting_is_clear,
            "quality_status": quality_res.get("status", "Good"),
            "quality_message": quality_res.get("message", "Optimal lighting."),
            "bounding_box": pct_bbox,
            "confidence": face_res.get("confidence", 0.9),
            "detector_type": face_res.get("detector_type", "yolo_face"),
            "message": msg
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"has_face": False, "face_count": 0, "lighting_clear": False, "error": str(e)}
        )

@app.post("/api/analyze")
async def analyze_portrait(
    request: Request,
    file: Optional[UploadFile] = File(None),
    gender: Optional[str] = Form("all")
):
    """
    Complete analysis pipeline:
    1. Face detection FIRST (YOLO) - If no face -> Strictly NO output or palettes!
    2. Quality & lighting assessment SECOND - If lighting not clear -> Strictly NO output or palettes!
    3. Multi-region skin sampling (forehead, cheeks, jaw)
    4. Outlier rejection & statistical color feature extraction (RGB, HSV, CIELAB, ITA)
    5. ML undertone classification (Random Forest / SVM)
    6. Personalized palette & style recommendations generation
    """
    image_bgr = None
    user_gender = gender or "all"

    try:
        if file is not None and file.filename:
            if file.content_type not in ALLOWED_MIME_TYPES and not file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported file format. Please upload a JPG, JPEG, or PNG image."
                )
            contents = await file.read()
            if len(contents) > MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="File size exceeds the 15MB limit.")
            nparr = np.frombuffer(contents, np.uint8)
            image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image_bgr is None or image_bgr.size == 0:
            body = await request.body()
            if body:
                try:
                    data = json.loads(body.decode("utf-8"))
                    img_str = data.get("image") or data.get("file")
                    if img_str:
                        if "," in img_str:
                            img_str = img_str.split(",", 1)[1]
                        img_bytes = base64.b64decode(img_str)
                        if len(img_bytes) > MAX_FILE_SIZE:
                            raise HTTPException(status_code=400, detail="File size exceeds the 15MB limit.")
                        nparr = np.frombuffer(img_bytes, np.uint8)
                        image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if data.get("gender"):
                        user_gender = data.get("gender")
                except HTTPException:
                    raise
                except Exception:
                    pass

        if image_bgr is None or image_bgr.size == 0:
            raise HTTPException(status_code=400, detail="Unable to decode image. Please provide a valid JPG or PNG image.")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image upload failed: {str(e)}")

    # Step 1: YOLO Face Detection FIRST (Strict: No face -> No output/palettes!)
    face_result = face_detector.detect_faces(image_bgr)
    if not face_result.get('success') or face_result.get('face_count', 0) == 0:
        return JSONResponse(
            status_code=422,
            content={
                'success': False,
                'stage': 'face_detection',
                'face_count': face_result.get('face_count', 0),
                'error': face_result.get('message') or 'No human face detected in the picture or camera feed. Please position your face clearly in the frame.'
            }
        )

    # Step 2: Quality & Lighting Check SECOND (Strict: Lighting not clear -> No output/palettes!)
    quality_result = analyze_image_quality(image_bgr)
    if not quality_result["is_valid"]:
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "stage": "quality_check",
                "quality": quality_result,
                "error": f"Face detected, but lighting is not clear: {quality_result['message']}. Please use clear, balanced lighting."
            }
        )

    # Step 3: Skin Extraction
    skin_result = skin_extractor.extract_skin_pixels(image_bgr, face_result['regions'])
    if skin_result is None or skin_result.get('total_pixels', 0) < 30:
        bbox = face_result.get('bounding_box')
        skin_result = skin_extractor.extract_skin_pixels_autonomous(image_bgr, bbox)

    if skin_result is None or skin_result.get('total_pixels', 0) < 30:
        return JSONResponse(
            status_code=422,
            content={
                'success': False,
                'stage': 'auto_colour_detection',
                'quality': quality_result,
                'error': 'Could not identify natural skin colour. The image is not clear or does not have proper lighting. Please upload a clear photo with natural lighting.'
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

    sel_gender = (user_gender or "all").lower().strip()
    if sel_gender not in ("male", "female", "all"):
        sel_gender = "all"

    # Step 6: Personalized Palette & Styling Recommendation Engine (Tailored to Selected Gender)
    recommendations_result = palette_generator.generate_recommendations(
        undertone=predicted_undertone,
        skin_metrics=color_features["display_metrics"],
        gender=sel_gender
    )

    # Persist analysis to Supabase (non-blocking, graceful fallback)
    analysis_id = None
    try:
        analysis_id = supabase_client.save_analysis(
            features=color_features["ml_features"],
            predicted_undertone=predicted_undertone,
            confidence=ml_prediction["confidence"],
            quality_score=quality_result["score"]
        )
    except Exception as e:
        logger.error("Supabase save_analysis failed: %s", e)

    # Return comprehensive structured response
    return {
        "success": True,
        "analysis_id": analysis_id,
        "quality": {
            "score": quality_result["score"],
            "status": quality_result["status"],
            "details": quality_result["metrics"]
        },
        "face": {
            "face_count": face_result["face_count"],
            "bounding_box": face_result["bounding_box"],
            "regions": face_result["regions"],
            "has_landmarks": face_result.get("landmarks") is not None,
            "auto_color_spotted": bool(skin_result.get("spotted", True)),
            "representative_hex": skin_result.get("representative_hex")
        },
        "gender": sel_gender,
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

@app.post("/api/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Accepts user corrections to undertone predictions.
    Stores feedback in Supabase for active learning / model retraining.
    """
    valid_undertones = ["Warm", "Cool", "Neutral"]
    corrected = feedback.corrected_undertone.capitalize()
    if corrected not in valid_undertones:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid corrected_undertone. Choose from: {valid_undertones}"
        )

    if not feedback.analysis_id:
        raise HTTPException(status_code=400, detail="analysis_id is required.")

    feedback_id = supabase_client.save_feedback(
        analysis_id=feedback.analysis_id,
        corrected_undertone=corrected
    )

    if feedback_id:
        return {
            "success": True,
            "feedback_id": feedback_id,
            "message": "Thank you for your feedback! It will help improve our model."
        }
    else:
        return {
            "success": False,
            "message": "Feedback storage is currently unavailable. Thank you for trying."
        }


@app.get("/api/db-status")
async def db_status():
    """
    Check whether Supabase is connected and operational.
    """
    return {
        "supabase_connected": supabase_client.is_available(),
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
