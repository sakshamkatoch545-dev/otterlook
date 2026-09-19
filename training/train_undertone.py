"""
ML Training & Comparison Pipeline for Skin Undertone Classification.
Trains and compares:
1. Logistic Regression (balanced)
2. Support Vector Classifier (SVM - RBF Kernel)
3. Support Vector Classifier (SVM - Linear Kernel)
4. Random Forest Classifier (balanced)

Uses verified Train / Validation / Test splits with Stratified K-Fold cross validation.
Saves the best-performing model to models/undertone_model.pkl using joblib.

Author: AI Personal Colour Analysis System
"""

import os
import json
import joblib
import warnings
import numpy as np
import pandas as pd
from typing import Optional, Dict, Any
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report

warnings.filterwarnings("ignore")

from feature_engineering import FEATURE_COLUMNS

def train_and_compare_models(
    train_csv: str,
    val_csv: Optional[str] = None,
    test_csv: Optional[str] = None,
    output_model_dir: Optional[str] = None,
    results_dir: Optional[str] = None
) -> Dict[str, Any]:
    print("==================================================")
    print("      SKIN UNDERTONE ML TRAINING PIPELINE        ")
    print("==================================================")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if output_model_dir is None:
        output_model_dir = os.path.join(base_dir, "models")
    if results_dir is None:
        results_dir = os.path.join(base_dir, "results")
        
    os.makedirs(output_model_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    if not os.path.exists(train_csv):
        raise FileNotFoundError(f"Training dataset not found at {train_csv}.")

    df_train = pd.read_csv(train_csv)
    
    # Identify target column
    target_col = "undertone_label" if "undertone_label" in df_train.columns else "undertone"
    
    # Capitalize for standard Otterlook classes: Warm, Cool, Neutral
    df_train["target"] = df_train[target_col].astype(str).str.capitalize()
    df_train = df_train[df_train["target"].isin(["Warm", "Cool", "Neutral"])].copy()
    
    print(f"Loaded training split: {len(df_train)} samples.")
    print(f"Target distribution:\n{df_train['target'].value_counts()}\n")

    X_train = np.asarray(df_train[FEATURE_COLUMNS].values, dtype=np.float32)
    y_train = np.asarray(df_train["target"].values, dtype=str)

    # Load validation split if available
    if val_csv and os.path.exists(val_csv):
        df_val = pd.read_csv(val_csv)
        val_target_col = "undertone_label" if "undertone_label" in df_val.columns else "undertone"
        df_val["target"] = df_val[val_target_col].astype(str).str.capitalize()
        df_val = df_val[df_val["target"].isin(["Warm", "Cool", "Neutral"])].copy()
        X_val = np.asarray(df_val[FEATURE_COLUMNS].values, dtype=np.float32)
        y_val = np.asarray(df_val["target"].values, dtype=str)
        print(f"Loaded validation split: {len(df_val)} samples.")
    else:
        X_val, y_val = None, None

    # Load test split if available
    if test_csv and os.path.exists(test_csv):
        df_test = pd.read_csv(test_csv)
        test_target_col = "undertone_label" if "undertone_label" in df_test.columns else "undertone"
        df_test["target"] = df_test[test_target_col].astype(str).str.capitalize()
        df_test = df_test[df_test["target"].isin(["Warm", "Cool", "Neutral"])].copy()
        X_test = np.asarray(df_test[FEATURE_COLUMNS].values, dtype=np.float32)
        y_test = np.asarray(df_test["target"].values, dtype=str)
        print(f"Loaded held-out test split: {len(df_test)} samples.\n")
    else:
        X_test, y_test = None, None

    models = {
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, C=1.0, class_weight="balanced", random_state=42))
        ]),
        "Support Vector Machine (RBF)": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", SVC(kernel="rbf", C=2.0, gamma="scale", probability=True, class_weight="balanced", random_state=42))
        ]),
        "Support Vector Machine (Linear)": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", SVC(kernel="linear", C=1.0, probability=True, class_weight="balanced", random_state=42))
        ]),
        "Random Forest Classifier": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", RandomForestClassifier(
                n_estimators=1000,
                max_depth=None,
                min_samples_split=2,
                min_samples_leaf=1,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1
            ))
        ])
    }

    # 5-Fold Cross Validation on Training set
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    comparison_results = {}

    print("--- 5-Fold Stratified Cross Validation on Training Data ---")
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

    # Evaluate on Validation Set
    val_evaluations = {}
    best_model_name = None
    best_f1 = -1.0
    fitted_pipelines = {}

    eval_X = X_val if X_val is not None else X_train
    eval_y = y_val if y_val is not None else y_train
    eval_name = "Validation Set" if X_val is not None else "Training Set"

    print(f"\n--- Model Selection on {eval_name} ---")
    for name, pipeline in models.items():
        pipeline.fit(X_train, y_train)
        fitted_pipelines[name] = pipeline
        y_pred = pipeline.predict(eval_X)

        acc = accuracy_score(eval_y, y_pred)
        prec, rec, f1, _ = precision_recall_fscore_support(eval_y, y_pred, average="macro")

        val_evaluations[name] = {
            "accuracy": round(float(acc), 4),
            "precision_macro": round(float(prec), 4),
            "recall_macro": round(float(rec), 4),
            "f1_macro": round(float(f1), 4),
            "classification_report": classification_report(eval_y, y_pred, output_dict=True)
        }
        print(f"[{name}] {eval_name} Accuracy: {acc:.4f} | F1: {f1:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f}")

        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name

    print(f"\n>> Selected Best Performing Architecture: {best_model_name} (F1: {best_f1:.4f})")

    # Final unbiased evaluation on held-out Test set
    test_metrics = {}
    if X_test is not None:
        best_pipe = fitted_pipelines[best_model_name]
        y_test_pred = best_pipe.predict(X_test)
        t_acc = accuracy_score(y_test, y_test_pred)
        t_prec, t_rec, t_f1, _ = precision_recall_fscore_support(y_test, y_test_pred, average="macro")
        test_metrics = {
            "test_accuracy": round(float(t_acc), 4),
            "test_precision_macro": round(float(t_prec), 4),
            "test_recall_macro": round(float(t_rec), 4),
            "test_f1_macro": round(float(t_f1), 4),
            "classification_report": classification_report(y_test, y_test_pred, output_dict=True)
        }
        print("\n--- Unbiased Held-Out Test Set Performance ---")
        print(f"[{best_model_name}] Test Accuracy: {t_acc:.4f} | Test F1: {t_f1:.4f} | Prec: {t_prec:.4f} | Rec: {t_rec:.4f}")
        print("\nDetailed Test Report:")
        print(classification_report(y_test, y_test_pred))

    # Fit best model on Train + Validation combined for deployment
    if X_val is not None:
        X_full_train = np.vstack([X_train, X_val])
        y_full_train = np.concatenate([y_train, y_val])
    else:
        X_full_train = X_train
        y_full_train = y_train

    final_pipeline = models[best_model_name]
    final_pipeline.fit(X_full_train, y_full_train)

    # Save model artifact
    model_save_path = os.path.join(output_model_dir, "undertone_model.pkl")
    model_artifact = {
        "pipeline": final_pipeline,
        "model_name": best_model_name,
        "classes": list(final_pipeline.classes_),
        "feature_columns": FEATURE_COLUMNS,
        "metrics": test_metrics or val_evaluations[best_model_name],
        "training_samples": len(X_full_train)
    }

    joblib.dump(model_artifact, model_save_path)
    print(f"\n>> Saved production model artifact to: {model_save_path}")

    # Save evaluation reports in models/ and results/
    comparison_payload = {
        "cross_validation": comparison_results,
        "validation_evaluations": val_evaluations,
        "test_evaluations": test_metrics,
        "selected_model": best_model_name,
        "training_samples": len(X_full_train)
    }

    for target_dir in [output_model_dir, results_dir]:
        out_f = os.path.join(target_dir, "model_comparison.json")
        with open(out_f, "w") as f:
            json.dump(comparison_payload, f, indent=2)

    print(f"Saved model comparison reports to: {results_dir}/model_comparison.json")
    return model_artifact

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    train_f = os.path.join(base_dir, "data", "processed", "train.csv")
    val_f = os.path.join(base_dir, "data", "processed", "validation.csv")
    test_f = os.path.join(base_dir, "data", "processed", "test.csv")
    
    # Fallback to data/training.csv if processed files not found
    if not os.path.exists(train_f):
        train_f = os.path.join(base_dir, "data", "training.csv")
        val_f = None
        test_f = None
        
    train_and_compare_models(train_f, val_f, test_f)
