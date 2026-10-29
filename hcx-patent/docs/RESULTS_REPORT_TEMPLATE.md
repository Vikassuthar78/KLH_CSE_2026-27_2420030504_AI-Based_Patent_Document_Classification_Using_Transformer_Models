# HCX-Patent Empirical Results Report

*Generated from verified experimental runs only. No synthetic or simulated values.*

## 1. Baseline Experiment Run Summary

| Property | Value |
| :--- | :--- |
| **Model** | TF-IDF + OneVsRest Logistic Regression |
| **Dataset Source** | USPTO-3M Local Parquet (`train-00000-of-00007.parquet`) |
| **Document Split** | 70% Train / 10% Val / 10% Calibration / 10% Test |
| **Leakage Validation** | Passed (Zero document ID overlap across splits) |
| **Features** | Sublinear TF-IDF (1-2 ngrams, max 50,000) |
| **Estimator Count** | 293 independent binary classifiers |

## 2. Experimental Metric Table

| Metric | Empirical Score | Notes |
| :--- | :--- | :--- |
| **Subset Accuracy** | See actual run JSON | Exact match across all multi-labels |
| **Macro Precision** | See actual run JSON | Unweighted mean over classes |
| **Macro Recall** | See actual run JSON | Unweighted mean over classes |
| **Macro F1** | See actual run JSON | Harmonic mean of Macro P and R |
| **Micro F1** | See actual run JSON | Globally aggregated true/false positives |
| **Hamming Loss** | See actual run JSON | Fraction of erroneous labels |
| **Training Time** | Recorded in seconds | CPU multi-threaded execution |
| **Inference Latency** | Recorded in ms/sample | Fast linear classification |

## 3. Publication Figures

1. `artifacts/figures/<run_id>_class_distribution.png`: Frequency distribution of top CPC subclasses.
2. `artifacts/figures/<run_id>_metrics.png`: Grouped performance metrics bar chart.
3. `artifacts/figures/<run_id>_per_class_f1.png`: Per-class F1 distribution histogram.
4. `artifacts/figures/<run_id>_date_distribution.png`: Temporal publication histogram.

