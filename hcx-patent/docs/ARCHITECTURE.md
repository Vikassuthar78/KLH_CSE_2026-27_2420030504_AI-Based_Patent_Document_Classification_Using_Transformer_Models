# HCX-Patent Architecture & System Design

## 1. System Overview

HCX-Patent is a research-grade machine learning and evaluation platform for patent classification under taxonomy evolution, uncertainty quantification, and interpretability requirements.

```
+-----------------------------------------------------------------------------------+
|                                  React Frontend                                   |
| (Overview, DatasetExplorer, ClassificationWorkspace, TaxonomyExplorer, Labs)     |
+-----------------------------------------+-----------------------------------------+
                                          | REST API (FastAPI /api/v1)
+-----------------------------------------v-----------------------------------------+
|                                FastAPI Backend                                    |
|   - Lifespan & CORS Configuration                                                 |
|   - Async Routers: /datasets, /experiments, /patents, /taxonomy, /uncertainty     |
|   - SQLite Persistence & ThreadPool Background Job Manager                        |
+--------+------------------+-------------------+------------------+----------------+
         |                  |                   |                  |
+--------v-------+  +-------v-------+  +--------v-------+  +-------v--------+
|    Datasets    |  |    Models     |  |   Taxonomy     |  |  Uncertainty   |
| - Parquet discovery- TF-IDF Baseline|  | - CPC Tree     |  | - Conformal    |
| - Profiling    |  | - Hierarchical|  | - Ancestor Path|  |   Prediction   |
| - Leak-free    |  | - Transformer |  | - Parent-Child |  | - ECE &        |
|   splitting    |  |   (BERT)      |  |   Validation   |  |   Calibration  |
+--------+-------+  +-------+-------+  +--------+-------+  +-------+--------+
         |                  |                   |                  |
+--------v------------------v-------------------v------------------v----------------+
|                             Local Storage & Artifacts                             |
|   - Offline USPTO-3M Parquet Files (D:\ALT-PROJECT\DATA)                         |
|   - Artifacts: Checkpoints (.joblib), Predictions (.csv), Metrics (.json)         |
|   - Figures (High-DPI PNGs) & SQLite Database (hcx_patent.db)                     |
+-----------------------------------------------------------------------------------+
```

## 2. Core Modules

1. **`app.datasets`**:
   - `discovery.py`: Auto-discovers local partitioned Parquet files.
   - `adapter.py`: Configurable schema mapping to canonical fields (`id`, `text`, `cpc_ids`, `date`).
   - `profiler.py`: Computes null percentages, length distributions, and class frequencies.
   - `validator.py`: Audits for duplicates, empty labels, and corrupted records.
   - `splitter.py`: Random and temporal train/val/cal/test splitting without document identifier leakage.

2. **`app.models`**:
   - `base.py`: Formal `BasePatentClassifier` abstract interface.
   - `tfidf_baseline.py`: Multi-label One-vs-Rest Logistic Regression with sparse sublinear TF-IDF features.
   - `hierarchy_aware.py`: Parent-child constraint propagation and hierarchy-consistent loss.
   - `transformer.py`: Sequence classification with long-text chunking and sigmoid multi-label probabilities.

3. **`app.taxonomy`**:
   - `cpc_tree.py`: CPC hierarchical parser (Section $\to$ Class $\to$ Subclass).
   - `validator.py`: Mathematical consistency checking for predicted multi-label sets.

4. **`app.uncertainty`**:
   - `conformal.py`: Distribution-free split conformal prediction with nonconformity scores $s_i = 1 - \hat{P}(Y=y_i \mid X_i)$.
   - `calibration.py`: Reliability diagram binning and Expected Calibration Error (ECE).

5. **`app.explainability`**:
   - `attributions.py`: Token-level linear coefficient attributions and gradient-based attributions.
   - `faithfulness.py`: Perturbation-based Comprehensiveness and Sufficiency metrics.
   - `stability.py`: Rank-correlation stability under input perturbations.

6. **`app.jobs`**:
   - Thread-pool background job executor with SQLite persistence and real-time percentage progress polling.

