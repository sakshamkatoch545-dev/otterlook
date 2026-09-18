"""
Model Evaluation and Diagnostics Script.
Computes comprehensive classification metrics:
- Accuracy, Macro/Weighted Precision, Recall, F1-Score
- Confusion Matrix
- Per-class classification breakdown (Warm, Cool, Neutral)
- Feature Importance Analysis (for tree ensembles / linear weights)
- Saves output reports to results/ and models/

Author: AI Personal Colour Analysis System
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

from feature_engineering import FEATURE_COLUMNS

def evaluate_saved_model(csv_path: str, model_path: str, report_out_path: str, results_dir: str = None):
    print("==================================================")
    print("        UNDERTONE MODEL EVALUATION REPORT         ")
    print("==================================================")
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model artifact not found at {model_path}. Train model first.")
        
    artifact = joblib.load(model_path)
    pipeline = artifact["pipeline"]
    model_name = artifact["model_name"]
    classes = [str(c) for c in artifact["classes"]]
    
    df = pd.read_csv(csv_path)
    
    target_col = "undertone_label" if "undertone_label" in df.columns else "undertone"
    df["target"] = df[target_col].astype(str).str.capitalize()
    df = df[df["target"].isin(classes)].copy()
    
    X = np.asarray(df[FEATURE_COLUMNS].values, dtype=np.float32)
    y_true = np.asarray(df["target"].values, dtype=str)
    
    y_pred = pipeline.predict(X)
    
    acc = accuracy_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    report_dict = classification_report(y_true, y_pred, target_names=classes, output_dict=True)
    
    print(f"Model Architecture: {model_name}")
    print(f"Evaluated File: {csv_path}")
    print(f"Total Evaluated Samples: {len(df)}")
    print(f"Overall Accuracy: {acc * 100:.2f}%\n")
    print("--- Detailed Classification Report ---")
    print(classification_report(y_true, y_pred, target_names=classes))
    
    print("--- Confusion Matrix ---")
    print(f"Classes: {classes}")
    for i, row in enumerate(cm):
        print(f"  {classes[i]:<10}: {row}")
        
    # Feature importance analysis if Random Forest
    feature_importance_list = []
    if "clf" in pipeline.named_steps:
        clf = pipeline.named_steps["clf"]
        if hasattr(clf, "feature_importances_"):
            importances = clf.feature_importances_
            indices = np.argsort(importances)[::-1]
            print("\n--- Top Feature Importances ---")
            for idx in indices[:10]:
                feat_name = FEATURE_COLUMNS[idx]
                feat_score = float(importances[idx])
                feature_importance_list.append({"feature": feat_name, "importance": round(feat_score, 4)})
                print(f"  {feat_name:<15}: {feat_score:.4f}")
                
    evaluation_summary = {
        "model_name": model_name,
        "evaluated_dataset": os.path.basename(csv_path),
        "total_samples": len(df),
        "overall_accuracy": round(float(acc), 4),
        "macro_avg": report_dict["macro avg"],
        "weighted_avg": report_dict["weighted avg"],
        "per_class": {c: report_dict[c] for c in classes if c in report_dict},
        "confusion_matrix": {classes[i]: cm[i].tolist() for i in range(len(classes))},
        "top_features": feature_importance_list
    }
    
    os.makedirs(os.path.dirname(report_out_path), exist_ok=True)
    with open(report_out_path, "w") as f:
        json.dump(evaluation_summary, f, indent=2)
    print(f"\nSaved evaluation summary to: {report_out_path}")
    
    if results_dir:
        os.makedirs(results_dir, exist_ok=True)
        results_report_path = os.path.join(results_dir, "evaluation_report.json")
        with open(results_report_path, "w") as f:
            json.dump(evaluation_summary, f, indent=2)
        print(f"Saved duplicate evaluation summary to: {results_report_path}")

    return evaluation_summary

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Default to evaluating on held-out test split
    test_csv = os.path.join(base_dir, "data", "processed", "test.csv")
    if not os.path.exists(test_csv):
        test_csv = os.path.join(base_dir, "data", "training.csv")
        
    model_file = os.path.join(base_dir, "models", "undertone_model.pkl")
    report_file = os.path.join(base_dir, "models", "evaluation_report.json")
    results_dir = os.path.join(base_dir, "results")
    
    evaluate_saved_model(test_csv, model_file, report_file, results_dir)
