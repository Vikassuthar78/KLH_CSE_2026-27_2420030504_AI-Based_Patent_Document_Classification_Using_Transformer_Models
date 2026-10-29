"""Experiment execution engine for running reproducible patent ML workflows."""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer

from app.config import get_settings
from app.datasets.discovery import discover_datasets
from app.datasets.splitter import create_splits
from app.evaluation.metrics import compute_all_metrics
from app.evaluation.temporal import evaluate_temporal_drift
from app.models.hierarchy_aware import HierarchyAwareClassifier
from app.models.tfidf_baseline import TFIDFBaseline
from app.taxonomy.cpc_tree import CPCTaxonomy
from app.uncertainty.conformal import SplitConformalPredictor

logger = logging.getLogger(__name__)


def run_experiment_pipeline(
    config: Dict[str, Any],
    experiment_id: int,
    progress_callback: Optional[Callable[[float, str], None]] = None,
) -> Dict[str, Any]:
    """Execute complete end-to-end experiment pipeline according to configuration.

    Args:
        config: Experiment parameters
        experiment_id: SQLite experiment entity id
        progress_callback: Optional callback(pct, status_msg)

    Returns:
        Dict with metrics, run_id, figures, and artifact paths.
    """
    settings = get_settings()
    run_id = f"{config.get('type', 'exp')}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

    if progress_callback:
        progress_callback(0.1, "Discovering dataset files...")

    # 1. Discover dataset
    files = discover_datasets(settings.DATASET_ROOT)
    parquet_files = [f.path for f in files if f.format == "parquet"]
    if not parquet_files:
        raise FileNotFoundError(f"No parquet dataset files found under {settings.DATASET_ROOT}")

    if progress_callback:
        progress_callback(0.2, "Loading and sampling dataset...")

    sample_size = int(config.get("sample_size", settings.DEV_SAMPLE_SIZE))
    random_seed = int(config.get("random_seed", settings.RANDOM_SEED))
    np.random.seed(random_seed)

    # Load from first parquet for dev speed
    import pyarrow.parquet as pq

    pf = pq.ParquetFile(parquet_files[0])
    df_raw = pf.read_row_group(0).to_pandas()
    if len(df_raw) > sample_size:
        df = df_raw.sample(n=sample_size, random_state=random_seed).reset_index(drop=True)
    else:
        df = df_raw.copy().reset_index(drop=True)

    # 2. Filter labels
    min_samples = int(config.get("min_samples_per_class", 10))
    df["cpc_list"] = df["cpc_ids"].str.split(",").apply(lambda x: [c.strip() for c in x if c.strip()])

    from collections import Counter

    counts = Counter()
    for cpcs in df["cpc_list"]:
        for c in cpcs:
            counts[c] += 1

    valid_classes = {c for c, cnt in counts.items() if cnt >= min_samples}
    if not valid_classes:
        valid_classes = {c for c, cnt in counts.most_common(10)}

    df["cpc_filtered"] = df["cpc_list"].apply(lambda x: [c for c in x if c in valid_classes])
    df = df[df["cpc_filtered"].apply(len) > 0].reset_index(drop=True)

    mlb = MultiLabelBinarizer(classes=sorted(valid_classes))
    y = mlb.fit_transform(df["cpc_filtered"])
    class_names = mlb.classes_.tolist()

    if progress_callback:
        progress_callback(0.4, "Splitting dataset into train/val/cal/test...")

    # 3. Create splits
    split_strategy = config.get("split_strategy", "random")
    splits = create_splits(
        df,
        strategy=split_strategy,
        temporal_cutoff_year=int(config.get("temporal_cutoff_year", 2012)),
        random_seed=random_seed,
    )
    df_train, df_val, df_cal, df_test = splits["train"], splits["val"], splits["cal"], splits["test"]

    y_train = mlb.transform(df_train["cpc_filtered"])
    y_val = mlb.transform(df_val["cpc_filtered"])
    y_cal = mlb.transform(df_cal["cpc_filtered"])
    y_test = mlb.transform(df_test["cpc_filtered"])

    if progress_callback:
        progress_callback(0.5, f"Training model ({config.get('type', 'baseline')})...")

    # 4. Model selection & training
    exp_type = config.get("type", "baseline")
    t0 = time.time()

    if exp_type == "hierarchy":
        model = HierarchyAwareClassifier(
            base_model=TFIDFBaseline(max_features=int(config.get("max_features", 50000))),
            class_names=class_names,
            hierarchy_penalty=float(config.get("hierarchy_penalty", 0.1)),
        )
        model.train(df_train["text"].tolist(), y_train)
    else:
        # Default baseline
        model = TFIDFBaseline(
            max_features=int(config.get("max_features", 50000)),
            random_seed=random_seed,
        )
        model.train(df_train["text"].tolist(), y_train)

    train_time = time.time() - t0

    if progress_callback:
        progress_callback(0.7, "Evaluating predictions...")

    # 5. Predict on test set
    t_inf = time.time()
    y_pred, y_prob = model.predict(df_test["text"].tolist())
    inf_time = time.time() - t_inf
    latency = (inf_time / max(1, len(df_test))) * 1000

    metrics = compute_all_metrics(
        y_test,
        y_pred,
        y_prob=y_prob,
        class_names=class_names,
        training_time_seconds=train_time,
        inference_latency_ms=latency,
    )
    metrics["run_id"] = run_id
    metrics["sample_size"] = len(df)
    metrics["num_classes"] = len(class_names)

    # 6. Conformal evaluation
    if progress_callback:
        progress_callback(0.8, "Running conformal calibration...")

    target_coverage = float(config.get("target_coverage", 0.90))
    _, cal_probs = model.predict(df_cal["text"].tolist())

    conformal_predictor = SplitConformalPredictor(target_coverage=target_coverage)
    conformal_predictor.calibrate(cal_probs, y_cal)
    pred_sets = conformal_predictor.predict(y_prob)
    conformal_eval = conformal_predictor.evaluate_coverage(pred_sets, y_test)
    metrics["conformal"] = conformal_eval

    # 7. Temporal evaluation if dates available
    if "date" in df_test.columns:
        temporal_eval = evaluate_temporal_drift(df_test, y_test, y_pred)
        metrics["temporal_drift"] = temporal_eval

    if progress_callback:
        progress_callback(0.9, "Generating publication figures and saving artifacts...")

    # 8. Save artifacts and figures
    artifacts_dir = Path(settings.ARTIFACTS_DIR)
    checkpoints_dir = artifacts_dir / "checkpoints"
    figures_dir = artifacts_dir / "figures"
    predictions_dir = artifacts_dir / "predictions"
    metrics_dir = artifacts_dir / "metrics"

    for d in [checkpoints_dir, figures_dir, predictions_dir, metrics_dir]:
        d.mkdir(parents=True, exist_ok=True)

    model_path = checkpoints_dir / f"{run_id}_model.joblib"
    model.save(str(model_path))

    pred_csv_path = predictions_dir / f"{run_id}_predictions.csv"
    pred_df = pd.DataFrame({
        "patent_id": df_test["id"].values,
        "date": df_test["date"].values if "date" in df_test.columns else "N/A",
        "true_labels": [",".join([class_names[j] for j in range(len(class_names)) if y_test[i, j] == 1]) for i in range(len(df_test))],
        "pred_labels": [",".join([class_names[j] for j in range(len(class_names)) if y_pred[i, j] == 1]) for i in range(len(df_test))],
    })
    pred_df.to_csv(pred_csv_path, index=False)

    # Matplotlib figures
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig_manifest = []

    # Figure 1: Metrics summary
    fig, ax = plt.subplots(figsize=(8, 4))
    m_labels = ["Macro F1", "Micro F1", "Macro P", "Macro R"]
    m_vals = [metrics["macro_f1"], metrics["micro_f1"], metrics["macro_precision"], metrics["macro_recall"]]
    ax.bar(m_labels, m_vals, color="#4f46e5")
    ax.set_ylim(0, 1.0)
    ax.set_title(f"Model Performance ({run_id})")
    fig_path = figures_dir / f"{run_id}_metrics.png"
    fig.savefig(str(fig_path), dpi=200, bbox_inches="tight")
    plt.close()
    fig_manifest.append({"name": "metrics", "path": str(fig_path), "caption": "Evaluation metrics summary"})

    if progress_callback:
        progress_callback(1.0, "Experiment completed successfully.")

    return {
        "run_id": run_id,
        "metrics": metrics,
        "model_path": str(model_path),
        "predictions_path": str(pred_csv_path),
        "figures": fig_manifest,
    }

