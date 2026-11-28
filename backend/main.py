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

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request, Response, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from backend.utils.image_quality import analyze_image_quality
from backend.vision.face_detection import FaceDetector
from backend.vision.gender_detection import GenderDetector
from backend.vision.skin_detection import SkinExtractor
from backend.vision.colour_extraction import ColourFeatureExtractor
from backend.ml.predictor import UndertonePredictor
from backend.recommendations.palette_generator import PaletteGenerator
from backend.recommendations.outfit_synthesizer import (
    generate_curated_outfits,
    CLOTHING_TYPES,
    WEATHER_TYPES
)
from backend.vision.face_biometrics import extract_face_embedding
from backend.db.face_memory import face_memory_db
from backend.db import neon_client as db_client

logger = logging.getLogger("otterlook.api")


# Pydantic models
class FeedbackRequest(BaseModel):
    analysis_id: str
    corrected_undertone: str  # "Warm", "Cool", or "Neutral"


class GenerateOutfitsRequest(BaseModel):
    undertone: str = "Warm"
    palette: Optional[List[Dict[str, Any]]] = None
    clothing_type: str = "all"
    weather: str = "all"
    gender: str = "all"
    skin_hex: Optional[str] = "#C68B59"


class GoogleAuthRequest(BaseModel):
    credential: str

app = FastAPI(
    title="AI-Based Personal Colour Analysis API",
    description="Skin undertone classification & personalized colour palette recommendation engine.",
    version="1.0.0"
)

# Enable CORS for frontend flexibility across Streamlit (localhost:8501) and standalone (localhost:8000)
_raw_origins = os.environ.get("ALLOWED_ORIGINS", "*").strip()
_allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()] if _raw_origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.middleware("http")
async def add_pna_and_cors_headers(request: Request, call_next):
    if request.method == "OPTIONS":
        response = Response(status_code=200)
    else:
        response = await call_next(request)
    req_origin = request.headers.get("origin")
    if _allowed_origins == ["*"]:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Private-Network"] = "true"
    elif req_origin and req_origin in _allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = req_origin
        response.headers["Vary"] = "Origin"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# Initialize core pipeline singletons
face_detector = FaceDetector()
gender_detector = GenderDetector()
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
                if len(contents) > MAX_FILE_SIZE:
                    return JSONResponse(
                        status_code=400,
                        content={"has_face": False, "face_count": 0, "lighting_clear": False, "message": "File size exceeds the 15MB limit."}
                    )
                nparr = np.frombuffer(contents, np.uint8)
                image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image_bgr is None or image_bgr.size == 0:
            body = await request.body()
            if body:
                if len(body) > MAX_FILE_SIZE * 2:
                    return JSONResponse(
                        status_code=400,
                        content={"has_face": False, "face_count": 0, "lighting_clear": False, "message": "Payload exceeds size limit."}
                    )
                try:
                    data = json.loads(body.decode("utf-8"))
                    img_str = data.get("image") or data.get("file")
                    if img_str:
                        if "," in img_str:
                            img_str = img_str.split(",", 1)[1]
                        img_bytes = base64.b64decode(img_str)
                        if len(img_bytes) > MAX_FILE_SIZE:
                            return JSONResponse(
                                status_code=400,
                                content={"has_face": False, "face_count": 0, "lighting_clear": False, "message": "File size exceeds the 15MB limit."}
                            )
                        nparr = np.frombuffer(img_bytes, np.uint8)
                        image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                except Exception:
                    pass

        if image_bgr is None or image_bgr.size == 0:
            return JSONResponse(
                status_code=400,
                content={"has_face": False, "face_count": 0, "lighting_clear": False, "message": "Invalid or unreadable image."}
            )
        
        # 1. Human Face Detection FIRST (fast bbox-only pass for /api/detect-face)
        face_res = face_detector.detect_faces(image_bgr, extract_landmarks=False)
        if not face_res.get("success") or face_res.get("face_count", 0) == 0:
            return {
                "has_face": False,
                "face_count": 0,
                "lighting_clear": False,
                "bounding_box": None,
                "message": face_res.get("message") or "No human face detected. Please ensure your face is clearly visible."
            }
        
        img_h, img_w = image_bgr.shape[:2]
        bbox = face_res.get("bounding_box")
        def _to_pct_box(b):
            return {
                "x": b[0],
                "y": b[1],
                "w": b[2],
                "h": b[3],
                "pctX": (b[0] / img_w) * 100,
                "pctY": (b[1] / img_h) * 100,
                "pctW": (b[2] / img_w) * 100,
                "pctH": (b[3] / img_h) * 100
            }
        pct_bbox = _to_pct_box(bbox) if bbox else None
        raw_faces = face_res.get("all_faces") or ([bbox] if bbox else [])
        faces_list = [_to_pct_box(fb) for fb in raw_faces]

        # 2. Lighting & Clarity check SECOND (scoped to selected face ROI)
        quality_res = analyze_image_quality(image_bgr, bbox=bbox)
        lighting_is_clear = bool(quality_res.get("is_valid", True))

        msg = "Face localized and lighting is clear." if lighting_is_clear else f"Face detected, but lighting is not clear: {quality_res.get('message')}"

        return {
            "has_face": True,
            "face_count": face_res.get("face_count", len(faces_list) or 1),
            "lighting_clear": lighting_is_clear,
            "quality_status": quality_res.get("status", "Good"),
            "quality_message": quality_res.get("message", "Optimal lighting."),
            "bounding_box": pct_bbox,
            "faces": faces_list,
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
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    gender: Optional[str] = Form("all"),
    clothing_type: Optional[str] = Form("all"),
    weather: Optional[str] = Form("all")
):
    """
    Complete analysis pipeline:
    1. Face detection FIRST (YOLO) - If no face -> Strictly NO output or palettes!
    2. Quality & lighting assessment SECOND - If lighting not clear -> Strictly NO output or palettes!
    3. Multi-region skin sampling (forehead, cheeks, jaw)
    4. Outlier rejection & statistical color feature extraction (RGB, HSV, CIELAB, ITA)
    5. ML undertone classification (Random Forest / SVM)
    6. Personalized palette & style recommendations generation
    7. Synthesize 3 to 4 complete styled looks (Upper, Bottom, Shoes, Jewellery & Makeup)
    """
    image_bgr = None
    user_gender = gender or "all"
    user_clothing_type = clothing_type or "all"
    user_weather = weather or "all"

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
                    if data.get("clothing_type"):
                        user_clothing_type = data.get("clothing_type")
                    if data.get("weather"):
                        user_weather = data.get("weather")
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

    # Step 2: Quality & Lighting Check SECOND (scoped to detected face ROI)
    quality_result = analyze_image_quality(image_bgr, bbox=face_result.get("bounding_box"))
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

    # Step 4b: Extract Facial Biometric Embedding & Check Face Memory Database
    bbox = face_result.get("bounding_box") or [0, 0, image_bgr.shape[1], image_bgr.shape[0]]
    landmarks = face_result.get("landmarks")
    face_embedding = extract_face_embedding(
        image_bgr=image_bgr,
        bbox=bbox,
        landmarks=landmarks,
        skin_result=skin_result
    )

    recognized_profile = None
    similarity_score = 0.0
    saved_face_id = None
    match_result = face_memory_db.find_matching_profile(face_embedding, threshold=0.82)
    if match_result is not None:
        recognized_profile, similarity_score = match_result
        background_tasks.add_task(face_memory_db.touch_profile, recognized_profile["face_id"], face_embedding)
        saved_face_id = recognized_profile["face_id"]
        logger.info("Recognized returning face %s (similarity: %.1f%%)", saved_face_id, similarity_score * 100)

    sel_gender = (user_gender or "all").lower().strip()
    if sel_gender not in ("male", "female", "all"):
        sel_gender = "all"

    if sel_gender == "all":
        detected_gender_info = gender_detector.detect_gender(image_bgr, bbox)
        effective_gender = detected_gender_info["gender"]
    else:
        detected_gender_info = {
            "gender": sel_gender,
            "label": "Women's Style" if sel_gender == "female" else "Men's Style",
            "confidence": 1.0,
            "confidence_percentage": 100.0,
            "auto_detected": False,
        }
        effective_gender = sel_gender

    if recognized_profile is not None:
        # Recognized returning face: retrieve the exact same calibrated signature palette and answers!
        predicted_undertone = recognized_profile["undertone"]
        conf_val = float(recognized_profile["confidence"])
        saved_probs = recognized_profile.get("probabilities")
        if not saved_probs or not isinstance(saved_probs, dict):
            rem = max(0.0, 1.0 - conf_val)
            saved_probs = {
                cls: (round(conf_val, 4) if cls == predicted_undertone else round(rem / 2.0, 4))
                for cls in ("Warm", "Neutral", "Cool")
            }
        ml_prediction = {
            "label": predicted_undertone,
            "confidence": conf_val,
            "confidence_percentage": round(conf_val * 100, 1),
            "probabilities": saved_probs,
            "model_name": "Biometric Memory Signature",
            "explanation": f"Recognized returning face profile ({round(similarity_score * 100, 1)}% biometric confidence). Loaded your calibrated signature colorimetry.",
            "key_factors": ["Biometric facial landmark match", "Dermal colorimetry signature alignment", "Consistent spectral profile"]
        }

        # Generate styling with saved palette and harmonies
        recommendations_result = palette_generator.generate_recommendations(
            undertone=predicted_undertone,
            skin_metrics=color_features["display_metrics"],
            gender=effective_gender,
            face_embedding=face_embedding
        )
        if recognized_profile.get("palette"):
            recommendations_result["palette"] = recognized_profile["palette"]
        if recognized_profile.get("skin_harmonies"):
            recommendations_result["skin_harmonies"] = recognized_profile["skin_harmonies"]

        rep_skin_hex = recognized_profile.get("skin_hex") or color_features["display_metrics"].get("representative_hex") or "#C68B59"

        saved_outfits = recognized_profile.get("curated_outfits")
        expected_panel = "UPPERWEAR / BLOUSE" if effective_gender == "female" else "UPPERWEAR / SHIRT"
        has_current_lookboard = (
            isinstance(saved_outfits, list)
            and len(saved_outfits) > 0
            and expected_panel in (saved_outfits[0].get("svg") or "")
        )
        if (
            has_current_lookboard
            and user_clothing_type == "all"
            and user_weather == "all"
            and recognized_profile.get("gender") == effective_gender
        ):
            curated_outfits = saved_outfits
        else:
            curated_outfits = generate_curated_outfits(
                undertone=predicted_undertone,
                palette=recommendations_result.get("palette", []),
                clothing_type=user_clothing_type,
                weather=user_weather,
                gender=effective_gender,
                skin_hex=rep_skin_hex
            )
    else:
        # Step 5: New Face ML Undertone Classification
        ml_prediction = undertone_predictor.predict(color_features["ml_features"])
        predicted_undertone = ml_prediction["label"]

        # Step 6: Personalized Differentiated Palette (unique to this distinct face)
        recommendations_result = palette_generator.generate_recommendations(
            undertone=predicted_undertone,
            skin_metrics=color_features["display_metrics"],
            gender=effective_gender,
            face_embedding=face_embedding
        )

        # Step 7: Synthesize 3 to 4 Curated Outfit Looks
        rep_skin_hex = color_features["display_metrics"].get("representative_hex") or skin_result.get("representative_hex") or "#C68B59"
        curated_outfits = generate_curated_outfits(
            undertone=predicted_undertone,
            palette=recommendations_result.get("palette", []),
            clothing_type=user_clothing_type,
            weather=user_weather,
            gender=effective_gender,
            skin_hex=rep_skin_hex
        )

        # Register and save this new face profile into persistent database
        saved_face_id = face_memory_db.save_profile(
            embedding=face_embedding,
            undertone=predicted_undertone,
            confidence=ml_prediction["confidence"],
            palette=recommendations_result.get("palette", []),
            skin_metrics=color_features["display_metrics"],
            gender=effective_gender,
            skin_hex=rep_skin_hex,
            skin_harmonies=recommendations_result.get("skin_harmonies", []),
            curated_outfits=curated_outfits,
            probabilities=ml_prediction.get("probabilities")
        )
        logger.info("Registered new distinct face profile %s into database.", saved_face_id)

    recognition_info = {
        "is_recognized": recognized_profile is not None,
        "profile_id": saved_face_id,
        "similarity": round(similarity_score * 100, 1) if recognized_profile else 100.0,
        "detection_count": (recognized_profile["detection_count"] + 1) if recognized_profile else 1,
        "first_seen": recognized_profile["created_at"] if recognized_profile else "Just now",
        "message": (
            f"✓ Recognized Returning Client ({round(similarity_score * 100, 1)}% biometric match) • Loaded your calibrated signature profile"
            if recognized_profile else
            "✓ Calibrated new unique facial colorimetry • Saved profile to database memory"
        )
    }

    # Persist analysis to Neon Postgres in background so response returns immediately
    import uuid as _uuid
    analysis_id = str(_uuid.uuid4())
    if db_client.is_available():
        background_tasks.add_task(
            db_client.save_analysis,
            features=color_features["ml_features"],
            predicted_undertone=predicted_undertone,
            confidence=ml_prediction["confidence"],
            quality_score=quality_result["score"],
            analysis_id=analysis_id,
        )

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
            "representative_hex": rep_skin_hex
        },
        "gender": effective_gender,
        "requested_gender": sel_gender,
        "detected_gender": detected_gender_info,
        "clothing_type": user_clothing_type,
        "weather": user_weather,
        "clothing_types": CLOTHING_TYPES,
        "weather_types": WEATHER_TYPES,
        "skin_analysis": {
            "total_sampled_pixels": skin_result["total_pixels"],
            "region_samples": skin_result["region_samples"],
            "areas": {
                "overall": {"hex": rep_skin_hex, "label": "Core Dermis"},
                "forehead": {"hex": (skin_result.get("region_samples") or {}).get("forehead", {}).get("hex") or rep_skin_hex, "label": "Upper Face"},
                "cheek": {"hex": (skin_result.get("region_samples") or {}).get("left_cheek", {}).get("hex") or (skin_result.get("region_samples") or {}).get("right_cheek", {}).get("hex") or rep_skin_hex, "label": "Cheek Tone"},
                "chin": {"hex": (skin_result.get("region_samples") or {}).get("chin", {}).get("hex") or rep_skin_hex, "label": "Lower Face"}
            },
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
        "foundation_advice": recommendations_result["foundation_advice"],
        "outfits": curated_outfits,
        "recognition": recognition_info
    }

@app.get("/api/wardrobe-filters")
async def get_wardrobe_filters():
    """Returns available clothing types, weather conditions, and styling options."""
    return {
        "success": True,
        "clothing_types": CLOTHING_TYPES,
        "weather_types": WEATHER_TYPES,
        "genders": [
            {"id": "male", "label": "Men's Style", "jewellery_focus": "Rings, Earrings, Watches, Chains"},
            {"id": "female", "label": "Women's Style", "jewellery_focus": "Necklaces, Earrings, Lip Tints, Rings"},
            {"id": "all", "label": "All Styles", "jewellery_focus": "Curated Ensemble"}
        ]
    }

@app.post("/api/generate-outfits")
async def generate_outfits_endpoint(payload: GenerateOutfitsRequest):
    """
    Dynamically generates 3 to 4 tailored outfit looks for upper, bottom, shoes, jewellery & makeup
    harmonized with the user's analyzed colour palette, chosen clothing style, weather, and gender.
    Allows instant filter adjustments without re-uploading the photo.
    """
    try:
        palette = payload.palette or []
        if not palette:
            rec = palette_generator.generate_recommendations(
                undertone=payload.undertone,
                gender=payload.gender
            )
            palette = rec.get("palette", [])

        outfits = generate_curated_outfits(
            undertone=payload.undertone,
            palette=palette,
            clothing_type=payload.clothing_type,
            weather=payload.weather,
            gender=payload.gender,
            skin_hex=payload.skin_hex or "#C68B59"
        )

        return {
            "success": True,
            "clothing_type": payload.clothing_type,
            "weather": payload.weather,
            "gender": payload.gender,
            "clothing_types": CLOTHING_TYPES,
            "weather_types": WEATHER_TYPES,
            "outfits": outfits
        }
    except Exception as e:
        logger.error("Dynamic outfit generation failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to generate outfits: {str(e)}")

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

    feedback_id = db_client.save_feedback(
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
    Check whether Neon Postgres is connected and operational.
    """
    return {
        "database_connected": db_client.is_available(),
        "database_provider": "neon_postgres",
        "face_memory": face_memory_db.get_stats(),
    }


@app.get("/api/auth/config")
async def auth_config():
    """
    Returns public Google Cloud Console OAuth 2.0 Client ID configuration.
    """
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    return {
        "google_enabled": bool(client_id),
        "google_client_id": client_id,
        "max_name_chars": 16,
    }


@app.post("/api/auth/google")
async def verify_google_login(payload: GoogleAuthRequest):
    """
    Verifies a Google Identity Services ID token against Google's tokeninfo endpoint
    and the configured GOOGLE_CLIENT_ID from Google Cloud Console.
    """
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    if not client_id:
        raise HTTPException(
            status_code=503,
            detail="Google Cloud Console authentication is not configured (missing GOOGLE_CLIENT_ID)."
        )
    token = (payload.credential or "").strip()
    if not token:
        raise HTTPException(status_code=400, detail="Missing Google ID token.")

    try:
        import httpx
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": token},
            )
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid Google token.")
        info = resp.json()
        if info.get("aud") != client_id:
            raise HTTPException(status_code=401, detail="Google token client mismatch.")

        raw_name = (info.get("name") or info.get("given_name") or info.get("email") or "User").strip()
        short_name = raw_name[:16]
        return {
            "success": True,
            "user": {
                "name": short_name,
                "email": info.get("email", ""),
                "picture": info.get("picture", ""),
                "provider": "google",
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Google token verification failed: %s", exc)
        raise HTTPException(status_code=401, detail="Google authentication failed.")


@app.delete("/api/face-profile/{face_id}")
async def delete_face_profile(face_id: str):
    """
    Deletes a stored biometric face profile from the face memory database.
    """
    deleted = face_memory_db.delete_profile(face_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Face profile not found.")
    return {"success": True, "deleted_face_id": face_id}


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
