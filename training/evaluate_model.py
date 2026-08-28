"""
Model Evaluation and Diagnostics Script.
Computes comprehensive classification metrics:
- Accuracy, Macro/Weighted Precision, Recall, F1-Score
- Confusion Matrix
- Per-class classification breakdown (Warm, Cool, Neutral)
- Feature Importance Analysis (for tree ensembles / linear weights)
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

from feature_engineering import FEATURE_COLUMNS

def evaluate_saved_model(csv_path: str, model_path: str, report_out_path: str):
    print("==================================================")
    print("        UNDERTONE MODEL EVALUATION REPORT         ")
    print("==================================================")
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model artifact not found at {model_path}. Train model first.")
        
    artifact = joblib.load(model_path)
    pipeline = artifact["pipeline"]
    model_name = artifact["model_name"]
    classes = artifact["classes"]
    
    df = pd.read_csv(csv_path)
    X = np.asarray(df[FEATURE_COLUMNS].values, dtype=np.float32)
    y_true = np.asarray(df["undertone"].values, dtype=str)
    
    y_pred = pipeline.predict(X)
    y_proba = pipeline.predict_proba(X)
    
    acc = accuracy_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    report_dict = classification_report(y_true, y_pred, target_names=classes, output_dict=True)
    
    print(f"Model Architecture: {model_name}")
    print(f"Total Evaluated Samples: {len(df)}")
    print(f"Overall Accuracy: {acc * 100:.2f}%\n")
    print("--- Detailed Classification Report ---")
    print(classification_report(y_true, y_pred, target_names=classes))
    
    print("--- Confusion Matrix ---")
    print(f"Classes: {classes}")
    for i, row in enumerate(cm):
        print(f"  {classes[i]:<10}: {row}")
        
    # Feature importance analysis if Random Forest
    clf = pipeline.named_steps["clf"]
    feature_importance_list = []
    if hasattr(clf, "feature_importances_"):
        importances = clf.feature_importances_
        indices = np.argsort(importances)[::-1]
        print("\n--- Top Feature Importances ---")
        for i in range(min(10, len(indices))):
            idx = indices[i]
            feat_name = FEATURE_COLUMNS[idx]
            imp_val = float(importances[idx])
            feature_importance_list.append({"feature": feat_name, "importance": round(imp_val, 4)})
            print(f"  {i+1:2d}. {feat_name:<16}: {imp_val:.4f}")
            
    eval_summary = {
        "model_name": model_name,
        "classes": classes,
        "total_samples": len(df),
        "overall_accuracy": round(float(acc), 4),
        "confusion_matrix": {
            "labels": classes,
            "matrix": cm.tolist()
        },
        "per_class_metrics": report_dict,
        "top_features": feature_importance_list
    }
    
    with open(report_out_path, "w") as f:
        json.dump(eval_summary, f, indent=2)
        
    print(f"\nSaved evaluation summary to: {report_out_path}")
    return eval_summary

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_file = os.path.join(base_dir, "data", "training.csv")
    model_file = os.path.join(base_dir, "models", "undertone_model.pkl")
    report_file = os.path.join(base_dir, "models", "evaluation_report.json")
    evaluate_saved_model(csv_file, model_file, report_file)
