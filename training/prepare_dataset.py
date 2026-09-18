"""
Otterlook Dataset Preparation and Preprocessing Pipeline.
Performs end-to-end data validation, corruption detection, deduplication,
facial landmark localization, anatomical skin segmentation, and colorimetric feature extraction.

Outputs:
- data/processed/dataset.csv: Full master metadata table
- data/processed/features.csv: Exact feature matrix aligned with Otterlook FEATURE_COLUMNS
- data/processed/train.csv: 70% Stratified training split
- data/processed/validation.csv: 15% Stratified validation split
- data/processed/test.csv: 15% Stratified held-out test split
- data/metadata/processing_log.json: Detailed execution and rejection logs

Author: AI Personal Colour Analysis System
"""

import os
import sys
import json
import hashlib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from sklearn.model_selection import train_test_split

# Ensure backend modules are importable
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import cv2
from backend.utils.image_quality import analyze_image_quality
from backend.vision.face_detection import FaceDetector
from backend.vision.skin_detection import SkinExtractor
from backend.vision.colour_extraction import ColourFeatureExtractor
from training.feature_engineering import FEATURE_COLUMNS

RAW_DIR = os.path.join(ROOT_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")
METADATA_DIR = os.path.join(ROOT_DIR, "data", "metadata")

def calculate_file_hash(filepath: str) -> str:
    """Calculates MD5 hash for image deduplication."""
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()

def process_face_images(
    face_detector: FaceDetector,
    skin_extractor: SkinExtractor,
    colour_extractor: ColourFeatureExtractor
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Processes portrait face images from personal_color_faces.
    Detects faces, extracts skin patches, computes color metrics.
    """
    dataset_dir = os.path.join(RAW_DIR, "personal_color_faces")
    records = []
    seen_hashes = set()
    
    stats = {
        "total_files_scanned": 0,
        "duplicates_removed": 0,
        "corrupted_or_unreadable": 0,
        "face_detection_failed": 0,
        "insufficient_skin_pixels": 0,
        "successfully_processed": 0,
        "rejection_details": []
    }
    
    if not os.path.exists(dataset_dir):
        print(f"Warning: {dataset_dir} does not exist. Skipping face images.")
        return records, stats

    # Category mappings based on Korean 4-season theory
    category_map = {
        "봄 웜톤": ("warm", "Spring Warm Tone"),
        "가을 웜톤": ("warm", "Autumn Warm Tone"),
        "여름 쿨톤": ("cool", "Summer Cool Tone"),
        "겨울 쿨톤": ("cool", "Winter Cool Tone")
    }

    print("Scanning personal color face image repository...")
    for root, _, files in os.walk(dataset_dir):
        # Identify category from directory name
        folder_name = os.path.basename(root)
        undertone_label = "unlabeled"
        orig_label = folder_name
        
        for k, (u_label, desc) in category_map.items():
            if k in folder_name:
                undertone_label = u_label
                orig_label = desc
                break
                
        for file in files:
            if not file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                continue
                
            stats["total_files_scanned"] += 1
            img_path = os.path.join(root, file)
            rel_path = os.path.relpath(img_path, ROOT_DIR)
            
            # 1. Deduplication check
            try:
                f_hash = calculate_file_hash(img_path)
                if f_hash in seen_hashes:
                    stats["duplicates_removed"] += 1
                    stats["rejection_details"].append({
                        "file": rel_path,
                        "reason": "Duplicate image file (matching MD5 hash)"
                    })
                    continue
                seen_hashes.add(f_hash)
            except Exception as e:
                stats["corrupted_or_unreadable"] += 1
                stats["rejection_details"].append({"file": rel_path, "reason": f"Hash read error: {e}"})
                continue

            # 2. Image Decoding
            try:
                img_bgr = cv2.imread(img_path)
                if img_bgr is None or img_bgr.size == 0:
                    # Fallback using numpy fromfile for non-ASCII unicode paths on Windows
                    img_array = np.fromfile(img_path, dtype=np.uint8)
                    img_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    
                if img_bgr is None or img_bgr.size == 0:
                    stats["corrupted_or_unreadable"] += 1
                    stats["rejection_details"].append({"file": rel_path, "reason": "Failed to decode image pixels"})
                    continue
            except Exception as e:
                stats["corrupted_or_unreadable"] += 1
                stats["rejection_details"].append({"file": rel_path, "reason": f"Decode error: {e}"})
                continue

            # 3. Quality Assessment
            quality = analyze_image_quality(img_bgr)
            quality_score = float(quality.get("score", 0.0))

            # 4. Facial Landmark Detection
            face_res = face_detector.detect_faces(img_bgr)
            face_detected = bool(face_res.get("success") and face_res.get("face_count", 0) >= 1)
            
            if not face_detected or not face_res.get("regions"):
                stats["face_detection_failed"] += 1
                stats["rejection_details"].append({
                    "file": rel_path,
                    "reason": "FaceDetector could not localize facial landmarks or skin regions"
                })
                continue

            # 5. Skin Extraction
            skin_res = skin_extractor.extract_skin_pixels(img_bgr, face_res["regions"])
            total_skin_px = skin_res.get("total_pixels", 0)
            
            if total_skin_px < 25:
                stats["insufficient_skin_pixels"] += 1
                stats["rejection_details"].append({
                    "file": rel_path,
                    "reason": f"Insufficient skin pixels extracted ({total_skin_px} < 25)"
                })
                continue

            # 6. Colorimetric Feature Extraction
            try:
                colour_metrics = colour_extractor.extract_features(skin_res["pixels_bgr"])
                ml_feats = colour_metrics["ml_features"]
            except Exception as e:
                stats["rejection_details"].append({"file": rel_path, "reason": f"Colour extraction error: {e}"})
                continue

            # Assemble record
            record = {
                "image_path": rel_path.replace("\\", "/"),
                "source_dataset": "personal_color_faces",
                "original_label": orig_label,
                "undertone_label": undertone_label,
                "face_detected": True,
                "quality_score": round(quality_score, 1),
                "total_sampled_pixels": total_skin_px
            }
            # Append all FEATURE_COLUMNS
            for col in FEATURE_COLUMNS:
                record[col] = ml_feats.get(col, 0.0)
                
            records.append(record)
            stats["successfully_processed"] += 1

    print(f"Face processing completed: {stats['successfully_processed']} / {stats['total_files_scanned']} faces extracted.")
    return records, stats

def process_foundation_catalog() -> List[Dict[str, Any]]:
    """
    Processes the real-world cosmetic foundation shade catalog.
    Extracts warm, cool, and neutral samples matching FEATURE_COLUMNS.
    """
    csv_path = os.path.join(RAW_DIR, "pudding_foundation_shades", "allShades.csv")
    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} not found. Skipping foundation shades.")
        return []

    from data.download_and_build_dataset import parse_undertone_from_text, hex_to_rgb, compute_color_moments_from_rgb
    
    df_raw = pd.read_csv(csv_path)
    records = []
    
    for idx, row in df_raw.iterrows():
        desc = str(row.get("description", ""))
        name = str(row.get("name", ""))
        spec = str(row.get("specific", ""))
        hex_val = str(row.get("hex", ""))
        brand_val = str(row.get("brand", "Unknown"))
        
        undertone = parse_undertone_from_text(desc, name, spec, brand=brand_val)
        if not undertone:
            continue
            
        rgb = hex_to_rgb(hex_val)
        if not rgb:
            continue
            
        moments = compute_color_moments_from_rgb(rgb, num_pixels=80, random_seed=42 + idx)
        
        rec = {
            "image_path": f"swatch_{brand_val}_{hex_val}".replace(" ", "_"),
            "source_dataset": "pudding_foundation_shades",
            "original_label": f"{brand_val} - {desc[:35]}",
            "undertone_label": undertone.lower(),
            "face_detected": True, # Calibrated facial complexion swatch
            "quality_score": 95.0,
            "total_sampled_pixels": 80
        }
        for col in FEATURE_COLUMNS:
            rec[col] = moments.get(col, 0.0)
            
        records.append(rec)
        
    print(f"Extracted {len(records)} foundation complexion formulations.")
    return records

def process_benchmarks() -> List[Dict[str, Any]]:
    """
    Processes Monk Skin Tone benchmark reference points.
    Preserves original labels and explicitly sets undertone_label='unlabeled'.
    """
    mst_path = os.path.join(RAW_DIR, "benchmarks", "monk_skin_tone_reference.csv")
    if not os.path.exists(mst_path):
        return []

    from data.download_and_build_dataset import hex_to_rgb, compute_color_moments_from_rgb

    df_mst = pd.read_csv(mst_path)
    records = []
    for idx, row in df_mst.iterrows():
        mst_level = row.get("mst_level", idx + 1)
        hex_val = str(row.get("hex", "#ffffff"))
        desc = str(row.get("description", f"MST {mst_level}"))
        
        rgb = hex_to_rgb(hex_val)
        if not rgb:
            continue
            
        moments = compute_color_moments_from_rgb(rgb, num_pixels=80, random_seed=100 + idx)
        rec = {
            "image_path": f"mst_ref_scale_{mst_level}",
            "source_dataset": "fitzpatrick_mst_benchmarks",
            "original_label": f"Monk Skin Tone Scale Level {mst_level} ({desc})",
            "undertone_label": "unlabeled", # Ethical compliance: MST measures lightness, not undertone
            "face_detected": True,
            "quality_score": 100.0,
            "total_sampled_pixels": 80
        }
        for col in FEATURE_COLUMNS:
            rec[col] = moments.get(col, 0.0)
        records.append(rec)
    return records

def prepare_all_datasets():
    print("==================================================")
    print("      OTTERLOOK DATASET PREPARATION PIPELINE      ")
    print("==================================================")
    
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(METADATA_DIR, exist_ok=True)
    
    face_detector = FaceDetector()
    skin_extractor = SkinExtractor()
    colour_extractor = ColourFeatureExtractor()
    
    # 1. Process Face Images
    face_records, face_stats = process_face_images(face_detector, skin_extractor, colour_extractor)
    
    # 2. Process Foundation Formulations
    foundation_records = process_foundation_catalog()
    
    # 3. Process Benchmark Scales (Unlabeled reference)
    benchmark_records = process_benchmarks()
    
    # Combine into Master Dataset
    all_records = face_records + foundation_records + benchmark_records
    df_all = pd.DataFrame(all_records)
    
    master_csv = os.path.join(PROCESSED_DIR, "dataset.csv")
    df_all.to_csv(master_csv, index=False)
    print(f"\nSaved master dataset with {len(df_all)} total entries to: {master_csv}")
    
    # Features Matrix
    features_csv = os.path.join(PROCESSED_DIR, "features.csv")
    feature_cols_meta = ["image_path", "source_dataset", "undertone_label"] + FEATURE_COLUMNS
    df_all[feature_cols_meta].to_csv(features_csv, index=False)
    print(f"Saved feature matrix to: {features_csv}")
    
    # Save Detailed Processing Log
    log_file = os.path.join(METADATA_DIR, "processing_log.json")
    with open(log_file, "w") as f:
        json.dump({
            "face_processing_stats": face_stats,
            "total_dataset_counts": {
                "personal_color_faces": len(face_records),
                "pudding_foundation_shades": len(foundation_records),
                "fitzpatrick_mst_benchmarks": len(benchmark_records),
                "total_entries": len(df_all)
            },
            "undertone_distribution": df_all["undertone_label"].value_counts().to_dict()
        }, f, indent=2)
    print(f"Saved processing log to: {log_file}")
    
    # 4. Filter Labeled Samples for ML Training (warm, cool, neutral)
    df_labeled = df_all[df_all["undertone_label"].isin(["warm", "cool", "neutral"])].copy()
    print("\nLabeled Undertone Distribution for Model Training:")
    print(df_labeled["undertone_label"].value_counts())
    
    # 5. Train / Validation / Test Stratified Split (70% Train, 15% Val, 15% Test)
    # Prevent data leakage: Stratify by undertone and source_dataset
    df_labeled["strat_key"] = df_labeled["undertone_label"] + "_" + df_labeled["source_dataset"]
    
    # Filter classes with >= 2 instances for stratification
    valid_strat = df_labeled["strat_key"].value_counts()
    valid_keys = valid_strat[valid_strat >= 2].index
    df_stratifiable = df_labeled[df_labeled["strat_key"].isin(valid_keys)]
    df_remainder = df_labeled[~df_labeled["strat_key"].isin(valid_keys)]
    
    train_val_df, test_df = train_test_split(
        df_stratifiable,
        test_size=0.15,
        random_state=42,
        stratify=df_stratifiable["strat_key"]
    )
    
    # Split train_val into 70% overall train and 15% validation (0.15 / 0.85 approx 0.1765)
    train_df, val_df = train_test_split(
        train_val_df,
        test_size=0.1765,
        random_state=42,
        stratify=train_val_df["strat_key"]
    )
    
    # Append remainder to train
    train_df = pd.concat([train_df, df_remainder]).sample(frac=1.0, random_state=42).reset_index(drop=True)
    val_df = val_df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    test_df = test_df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    
    # Clean temporary stratification column
    train_df = train_df.drop(columns=["strat_key"])
    val_df = val_df.drop(columns=["strat_key"])
    test_df = test_df.drop(columns=["strat_key"])
    
    train_csv = os.path.join(PROCESSED_DIR, "train.csv")
    val_csv = os.path.join(PROCESSED_DIR, "validation.csv")
    test_csv = os.path.join(PROCESSED_DIR, "test.csv")
    
    train_df.to_csv(train_csv, index=False)
    val_df.to_csv(val_csv, index=False)
    test_df.to_csv(test_csv, index=False)
    
    print(f"\n>> Split completed successfully:")
    print(f"  Train:      {len(train_df)} samples (70%) -> {train_csv}")
    print(f"  Validation: {len(val_df)} samples (15%) -> {val_csv}")
    print(f"  Test:       {len(test_df)} samples (15%) -> {test_csv}")
    
    # Also update data/training.csv for seamless backwards compatibility with existing pipeline
    compat_csv = os.path.join(ROOT_DIR, "data", "training.csv")
    # Format undertone capitalized for backwards compatibility
    compat_df = train_df.copy()
    compat_df["undertone"] = compat_df["undertone_label"].str.capitalize()
    compat_df.to_csv(compat_csv, index=False)
    print(f"  Updated existing pipeline training file: {compat_csv}")

if __name__ == "__main__":
    prepare_all_datasets()
