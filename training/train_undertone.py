"""
ML Training Pipeline for Skin Undertone Classification.
Trains and compares:
1. Logistic Regression
2. Support Vector Classifier (SVM - RBF & Linear)
3. Random Forest Classifier

Saves the best-performing model to models/undertone_model.pkl using joblib.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report

from feature_engineering import FEATURE_COLUMNS

def train_and_compare_models(csv_path: str, output_model_dir: str):
    print("==================================================")
    print("      SKIN UNDERTONE ML TRAINING PIPELINE        ")
    print("==================================================")
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Training dataset not found at {csv_path}. Please run data/generate_dataset.py first.")
        
    df = pd.read_csv(csv_path)
    print(f"Loaded dataset with {len(df)} samples.")
    print(f"Target distribution:\n{df['undertone'].value_counts()}\n")
    
    X = np.asarray(df[FEATURE_COLUMNS].values, dtype=np.float32)
    y = np.asarray(df["undertone"].values, dtype=str)
    
    # 80/20 Stratified Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    models = {
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, C=1.0, random_state=42))
        ]),
        "Support Vector Machine (RBF)": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", SVC(kernel="rbf", C=2.0, gamma="scale", probability=True, random_state=42))
        ]),
        "Support Vector Machine (Linear)": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", SVC(kernel="linear", C=1.0, probability=True, random_state=42))
        ]),
        "Random Forest Classifier": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", RandomForestClassifier(
                n_estimators=150,
                max_depth=10,
                min_samples_split=4,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ))
        ])
    }
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    comparison_results = {}
    
    print("--- 5-Fold Cross Validation Comparison ---")
    for name, pipeline in models.items():
        scoring = ["accuracy", "precision_macro", "recall_macro", "f1_macro"]
        scores = cross_validate(pipeline, X_train, y_train, cv=cv, scoring=scoring, n_jobs=-1)
        
        acc = float(np.mean(scores["test_accuracy"]))
        prec = float(np.mean(scores["test_precision_macro"]))
        rec = float(np.mean(scores["test_recall_macro"]))
        f1 = float(np.mean(scores["test_f1_macro"]))
        
        comparison_results[name] = {
            "cv_accuracy_mean": round(acc, 4),
            "cv_accuracy_std": round(float(np.std(scores["test_accuracy"])), 4),
            "cv_precision_macro": round(prec, 4),
            "cv_recall_macro": round(rec, 4),
            "cv_f1_macro": round(f1, 4)
        }
        print(f"[{name}] Acc: {acc:.4f} (±{np.std(scores['test_accuracy']):.4f}) | F1: {f1:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f}")
    
    # Train each on X_train and evaluate on held-out test set
    print("\n--- Held-Out Test Set Performance (20% Holdout) ---")
    test_evaluations = {}
    best_model_name = None
    best_f1 = -1.0
    fitted_pipelines = {}
    
    for name, pipeline in models.items():
        pipeline.fit(X_train, y_train)
        fitted_pipelines[name] = pipeline
        y_pred = pipeline.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="macro")
        
        test_evaluations[name] = {
            "test_accuracy": round(float(acc), 4),
            "test_precision_macro": round(float(prec), 4),
            "test_recall_macro": round(float(rec), 4),
            "test_f1_macro": round(float(f1), 4),
            "classification_report": classification_report(y_test, y_pred, output_dict=True)
        }
        print(f"[{name}] Test Accuracy: {acc:.4f} | Test F1: {f1:.4f}")
        
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            
    print(f"\n>> Selected Best Performing Model: {best_model_name} (Test F1: {best_f1:.4f})")
    
    # Retrain best pipeline on full dataset for maximum generalization
    best_pipeline = models[best_model_name]
    best_pipeline.fit(X, y)
    
    os.makedirs(output_model_dir, exist_ok=True)
    model_save_path = os.path.join(output_model_dir, "undertone_model.pkl")
    
    # Package model artifact with metadata
    model_artifact = {
        "pipeline": best_pipeline,
        "model_name": best_model_name,
        "classes": list(best_pipeline.classes_),
        "feature_columns": FEATURE_COLUMNS,
        "metrics": test_evaluations[best_model_name],
        "training_samples": len(df)
    }
    
    joblib.dump(model_artifact, model_save_path)
    print(f"Saved best model artifact to: {model_save_path}")
    
    comparison_file = os.path.join(output_model_dir, "model_comparison.json")
    with open(comparison_file, "w") as f:
        json.dump({
            "cross_validation": comparison_results,
            "test_evaluations": test_evaluations,
            "selected_model": best_model_name
        }, f, indent=2)
    print(f"Saved model comparison report to: {comparison_file}")
    
    return model_artifact

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_file = os.path.join(base_dir, "data", "training.csv")
    models_dir = os.path.join(base_dir, "models")
    train_and_compare_models(csv_file, models_dir)
