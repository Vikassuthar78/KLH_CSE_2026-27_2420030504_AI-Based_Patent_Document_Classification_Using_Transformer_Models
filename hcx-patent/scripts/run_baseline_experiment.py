"""
HCX-Patent: Run the first baseline experiment
This script trains a TF-IDF + Logistic Regression baseline on a development sample.
"""
import os
import sys
import time
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

import numpy as np

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


def main():
    print("=" * 70)
    print("HCX-Patent: Baseline Experiment (TF-IDF + Logistic Regression)")
    print("=" * 70)
    print()
    
    # Configuration
    DATASET_ROOT = os.environ.get("DATASET_ROOT", r"D:\ALT-PROJECT\DATA")
    PROJECT_ROOT = os.environ.get("PROJECT_ROOT", str(Path(__file__).parent.parent))
    SAMPLE_SIZE = int(os.environ.get("DEV_SAMPLE_SIZE", "10000"))
    RANDOM_SEED = int(os.environ.get("RANDOM_SEED", "42"))
    MIN_SAMPLES_PER_CLASS = 10
    MAX_FEATURES = 50000
    
    artifacts_dir = Path(PROJECT_ROOT) / "artifacts"
    metrics_dir = artifacts_dir / "metrics"
    checkpoints_dir = artifacts_dir / "checkpoints"
    predictions_dir = artifacts_dir / "predictions"
    figures_dir = artifacts_dir / "figures"
    
    for d in [metrics_dir, checkpoints_dir, predictions_dir, figures_dir]:
        d.mkdir(parents=True, exist_ok=True)
    
    run_id = f"baseline_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    print(f"Run ID: {run_id}")
    print(f"Dataset root: {DATASET_ROOT}")
    print(f"Sample size: {SAMPLE_SIZE}")
    print(f"Random seed: {RANDOM_SEED}")
    print()
    
    np.random.seed(RANDOM_SEED)
    
    # Step 1: Load data
    print("[1/6] Loading dataset sample...")
    t0 = time.time()
    
    import pyarrow.parquet as pq
    import pandas as pd
    from glob import glob
    
    files = sorted(glob(os.path.join(DATASET_ROOT, "train-*.parquet")))
    if not files:
        print("ERROR: No parquet files found!")
        sys.exit(1)
    
    print(f"  Found {len(files)} parquet files")
    
    # Read from first file for dev sample
    pf = pq.ParquetFile(files[0])
    df_full = pf.read().to_pandas()
    
    if len(df_full) > SAMPLE_SIZE:
        df = df_full.sample(n=SAMPLE_SIZE, random_state=RANDOM_SEED).reset_index(drop=True)
    else:
        df = df_full
    
    load_time = time.time() - t0
    print(f"  Loaded {len(df)} records in {load_time:.1f}s")
    print()
    
    # Step 2: Parse labels and filter rare classes
    print("[2/6] Processing labels...")
    from sklearn.preprocessing import MultiLabelBinarizer
    
    # Parse CPC codes
    df["cpc_list"] = df["cpc_ids"].str.split(",").apply(lambda x: [c.strip() for c in x if c.strip()])
    
    # Count class frequencies
    from collections import Counter
    class_counts = Counter()
    for cpcs in df["cpc_list"]:
        for c in cpcs:
            class_counts[c] += 1
    
    # Filter rare classes
    valid_classes = {c for c, cnt in class_counts.items() if cnt >= MIN_SAMPLES_PER_CLASS}
    print(f"  Total unique CPC codes: {len(class_counts)}")
    print(f"  Classes with >= {MIN_SAMPLES_PER_CLASS} samples: {len(valid_classes)}")
    
    # Filter labels to valid classes only
    df["cpc_filtered"] = df["cpc_list"].apply(lambda x: [c for c in x if c in valid_classes])
    
    # Remove records with no valid labels
    df = df[df["cpc_filtered"].apply(len) > 0].reset_index(drop=True)
    print(f"  Records after filtering: {len(df)}")
    
    # Binarize labels
    mlb = MultiLabelBinarizer(classes=sorted(valid_classes))
    y = mlb.fit_transform(df["cpc_filtered"])
    class_names = mlb.classes_.tolist()
    print(f"  Label matrix shape: {y.shape}")
    print()
    
    # Step 3: Split data
    print("[3/6] Creating train/val/cal/test splits...")
    from sklearn.model_selection import train_test_split
    
    indices = np.arange(len(df))
    # 70% train, 30% rest
    train_idx, rest_idx = train_test_split(indices, test_size=0.3, random_state=RANDOM_SEED)
    # Split rest into val (1/3), cal (1/3), test (1/3) of 30% = 10% each
    val_idx, cal_test_idx = train_test_split(rest_idx, test_size=2/3, random_state=RANDOM_SEED)
    cal_idx, test_idx = train_test_split(cal_test_idx, test_size=0.5, random_state=RANDOM_SEED)
    
    print(f"  Train: {len(train_idx)}, Val: {len(val_idx)}, Cal: {len(cal_idx)}, Test: {len(test_idx)}")
    
    # Verify no leakage
    all_ids = [set(df.iloc[idx]["id"].values) for idx in [train_idx, val_idx, cal_idx, test_idx]]
    for i in range(len(all_ids)):
        for j in range(i+1, len(all_ids)):
            overlap = all_ids[i] & all_ids[j]
            assert len(overlap) == 0, f"Leakage detected between splits {i} and {j}"
    print("  No data leakage between splits [OK]")
    
    texts_train = df.iloc[train_idx]["text"].tolist()
    texts_val = df.iloc[val_idx]["text"].tolist()
    texts_cal = df.iloc[cal_idx]["text"].tolist()
    texts_test = df.iloc[test_idx]["text"].tolist()
    
    y_train = y[train_idx]
    y_val = y[val_idx]
    y_cal = y[cal_idx]
    y_test = y[test_idx]
    print()
    
    # Step 4: Train TF-IDF + LogReg
    print("[4/6] Training TF-IDF + Logistic Regression...")
    t_train_start = time.time()
    
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.multiclass import OneVsRestClassifier
    from sklearn.linear_model import LogisticRegression
    
    vectorizer = TfidfVectorizer(
        max_features=MAX_FEATURES,
        ngram_range=(1, 2),
        sublinear_tf=True,
        strip_accents="unicode",
        min_df=2
    )
    
    X_train = vectorizer.fit_transform(texts_train)
    X_val = vectorizer.transform(texts_val)
    X_cal = vectorizer.transform(texts_cal)
    X_test = vectorizer.transform(texts_test)
    
    print(f"  TF-IDF matrix: {X_train.shape}", flush=True)
    
    classifier = OneVsRestClassifier(
        LogisticRegression(C=1.0, max_iter=200, solver="liblinear"),
        n_jobs=-1
    )
    classifier.fit(X_train, y_train)
    
    training_time = time.time() - t_train_start
    print(f"  Training completed in {training_time:.1f}s")
    print()
    
    # Step 5: Evaluate
    print("[5/6] Evaluating on test set...")
    t_infer_start = time.time()
    
    y_pred = classifier.predict(X_test)
    inference_time = time.time() - t_infer_start
    inference_latency_ms = (inference_time / len(test_idx)) * 1000
    
    # Try to get probabilities
    try:
        y_prob = np.column_stack([e.predict_proba(X_test)[:, 1] for e in classifier.estimators_])
    except Exception:
        y_prob = None
    
    from sklearn.metrics import (
        accuracy_score, f1_score, precision_score, recall_score,
        hamming_loss, classification_report
    )
    
    metrics = {
        "run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset": "USPTO-3M",
        "sample_size": len(df),
        "num_classes": len(class_names),
        "train_size": len(train_idx),
        "val_size": len(val_idx),
        "cal_size": len(cal_idx),
        "test_size": len(test_idx),
        "model_type": "tfidf_logreg",
        "max_features": MAX_FEATURES,
        "random_seed": RANDOM_SEED,
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "macro_precision": float(precision_score(y_test, y_pred, average="macro", zero_division=0)),
        "macro_recall": float(recall_score(y_test, y_pred, average="macro", zero_division=0)),
        "macro_f1": float(f1_score(y_test, y_pred, average="macro", zero_division=0)),
        "micro_precision": float(precision_score(y_test, y_pred, average="micro", zero_division=0)),
        "micro_recall": float(recall_score(y_test, y_pred, average="micro", zero_division=0)),
        "micro_f1": float(f1_score(y_test, y_pred, average="micro", zero_division=0)),
        "hamming_loss": float(hamming_loss(y_test, y_pred)),
        "training_time_seconds": round(training_time, 2),
        "inference_time_seconds": round(inference_time, 4),
        "inference_latency_ms": round(inference_latency_ms, 4),
    }
    
    # Per-class metrics
    per_class = {}
    for i, cls_name in enumerate(class_names):
        if y_test[:, i].sum() > 0 or y_pred[:, i].sum() > 0:
            per_class[cls_name] = {
                "precision": float(precision_score(y_test[:, i], y_pred[:, i], zero_division=0)),
                "recall": float(recall_score(y_test[:, i], y_pred[:, i], zero_division=0)),
                "f1": float(f1_score(y_test[:, i], y_pred[:, i], zero_division=0)),
                "support": int(y_test[:, i].sum()),
            }
    metrics["per_class"] = per_class
    
    print(f"  Results:")
    print(f"    Accuracy (subset):   {metrics['accuracy']:.4f}")
    print(f"    Macro Precision:     {metrics['macro_precision']:.4f}")
    print(f"    Macro Recall:        {metrics['macro_recall']:.4f}")
    print(f"    Macro F1:            {metrics['macro_f1']:.4f}")
    print(f"    Micro Precision:     {metrics['micro_precision']:.4f}")
    print(f"    Micro Recall:        {metrics['micro_recall']:.4f}")
    print(f"    Micro F1:            {metrics['micro_f1']:.4f}")
    print(f"    Hamming Loss:        {metrics['hamming_loss']:.4f}")
    print(f"    Training Time:       {metrics['training_time_seconds']:.1f}s")
    print(f"    Inference Latency:   {metrics['inference_latency_ms']:.2f}ms/sample")
    print()
    
    # Step 6: Save artifacts
    print("[6/6] Saving artifacts...")
    
    # Save metrics
    metrics_path = metrics_dir / f"{run_id}_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"  Metrics: {metrics_path}")
    
    # Save model
    import joblib
    model_path = checkpoints_dir / f"{run_id}_model.joblib"
    joblib.dump({
        "vectorizer": vectorizer,
        "classifier": classifier,
        "mlb": mlb,
        "class_names": class_names,
        "config": {
            "max_features": MAX_FEATURES,
            "random_seed": RANDOM_SEED,
            "sample_size": len(df),
        }
    }, str(model_path))
    print(f"  Model: {model_path}")
    
    # Save predictions
    pred_df = pd.DataFrame({
        "patent_id": df.iloc[test_idx]["id"].values,
        "true_labels": [",".join([class_names[j] for j in range(len(class_names)) if y_test[i, j] == 1]) for i in range(len(test_idx))],
        "pred_labels": [",".join([class_names[j] for j in range(len(class_names)) if y_pred[i, j] == 1]) for i in range(len(test_idx))],
    })
    preds_path = predictions_dir / f"{run_id}_predictions.csv"
    pred_df.to_csv(preds_path, index=False)
    print(f"  Predictions: {preds_path}")
    
    # Save split manifest
    split_manifest = {
        "run_id": run_id,
        "train_ids": df.iloc[train_idx]["id"].tolist(),
        "val_ids": df.iloc[val_idx]["id"].tolist(),
        "cal_ids": df.iloc[cal_idx]["id"].tolist(),
        "test_ids": df.iloc[test_idx]["id"].tolist(),
    }
    splits_dir = Path(PROJECT_ROOT) / "data" / "splits"
    splits_dir.mkdir(parents=True, exist_ok=True)
    split_path = splits_dir / f"{run_id}_split_manifest.json"
    with open(split_path, "w") as f:
        json.dump(split_manifest, f)
    print(f"  Split manifest: {split_path}")
    
    # Generate figures
    print()
    print("  Generating figures...")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    
    # Figure 1: Class distribution (top 30)
    fig, ax = plt.subplots(figsize=(14, 6))
    top_classes = sorted(class_counts.items(), key=lambda x: -x[1])[:30]
    codes = [c[0] for c in top_classes]
    counts = [c[1] for c in top_classes]
    ax.barh(codes[::-1], counts[::-1], color="#4f46e5")
    ax.set_xlabel("Count")
    ax.set_title(f"Top 30 CPC Class Distribution (n={len(df)})")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    fig.savefig(str(figures_dir / f"{run_id}_class_distribution.png"), dpi=300, bbox_inches="tight")
    plt.close()
    
    # Figure 2: Metric comparison bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    metric_names = ["Macro P", "Macro R", "Macro F1", "Micro P", "Micro R", "Micro F1"]
    metric_vals = [
        metrics["macro_precision"], metrics["macro_recall"], metrics["macro_f1"],
        metrics["micro_precision"], metrics["micro_recall"], metrics["micro_f1"]
    ]
    bars = ax.bar(metric_names, metric_vals, color=["#4f46e5", "#4f46e5", "#4f46e5", "#06b6d4", "#06b6d4", "#06b6d4"])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title(f"TF-IDF + LogReg Baseline Metrics (n={len(df)})")
    for bar, val in zip(bars, metric_vals):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02, f"{val:.3f}", ha='center', va='bottom', fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    fig.savefig(str(figures_dir / f"{run_id}_metrics.png"), dpi=300, bbox_inches="tight")
    plt.close()
    
    # Figure 3: Per-class F1 distribution
    if per_class:
        f1_vals = [v["f1"] for v in per_class.values() if v["support"] > 0]
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(f1_vals, bins=20, color="#4f46e5", edgecolor="white", alpha=0.8)
        ax.axvline(np.mean(f1_vals), color="red", linestyle="--", label=f"Mean: {np.mean(f1_vals):.3f}")
        ax.set_xlabel("F1 Score")
        ax.set_ylabel("Number of Classes")
        ax.set_title("Per-Class F1 Score Distribution")
        ax.legend()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()
        fig.savefig(str(figures_dir / f"{run_id}_per_class_f1.png"), dpi=300, bbox_inches="tight")
        plt.close()
    
    # Figure 4: Date distribution
    dates = pd.to_datetime(df["date"], errors="coerce")
    years = dates.dt.year.dropna().astype(int)
    fig, ax = plt.subplots(figsize=(10, 5))
    year_counts = years.value_counts().sort_index()
    ax.bar(year_counts.index, year_counts.values, color="#4f46e5")
    ax.set_xlabel("Publication Year")
    ax.set_ylabel("Count")
    ax.set_title(f"Patent Publication Year Distribution (n={len(df)})")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    fig.savefig(str(figures_dir / f"{run_id}_date_distribution.png"), dpi=300, bbox_inches="tight")
    plt.close()
    
    print(f"  Figures saved to {figures_dir}")
    
    # Save figure manifest
    figure_manifest = {
        "run_id": run_id,
        "figures": [
            {"name": "class_distribution", "path": str(figures_dir / f"{run_id}_class_distribution.png"), "caption": "Top 30 CPC class frequency distribution"},
            {"name": "metrics", "path": str(figures_dir / f"{run_id}_metrics.png"), "caption": "Baseline model classification metrics"},
            {"name": "per_class_f1", "path": str(figures_dir / f"{run_id}_per_class_f1.png"), "caption": "Distribution of per-class F1 scores"},
            {"name": "date_distribution", "path": str(figures_dir / f"{run_id}_date_distribution.png"), "caption": "Patent publication year distribution"},
        ]
    }
    with open(figures_dir / f"{run_id}_manifest.json", "w") as f:
        json.dump(figure_manifest, f, indent=2)
    
    print()
    print("=" * 70)
    print("EXPERIMENT COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print(f"  Run ID:    {run_id}")
    print(f"  Macro F1:  {metrics['macro_f1']:.4f}")
    print(f"  Micro F1:  {metrics['micro_f1']:.4f}")
    print(f"  Metrics:   {metrics_path}")
    print(f"  Model:     {model_path}")
    print()
    
    return metrics


if __name__ == "__main__":
    main()

