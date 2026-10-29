# HCX-Patent: Hierarchical, Explainable, and Uncertainty-Aware Patent Classification Platform

HCX-Patent is a research-grade platform designed to evaluate and enhance patent classification through:
1. **Hierarchical Consistency**: Enforcing Cooperative Patent Classification (CPC) taxonomy constraints.
2. **Explainability**: Generating token-level attribution with perturbation faithfulness verification.
3. **Uncertainty Quantification**: Split conformal prediction sets with guaranteed finite-sample coverage.
4. **Temporal Drift Analysis**: Tracking classification decay across publication cohorts.

---

## 1. Local Dataset Structure

The platform reads directly from your offline USPTO-3M corpus located at:
`D:\ALT-PROJECT\DATA`

```
D:\ALT-PROJECT\DATA\
  ├── train-00000-of-00007.parquet (456,909 rows, 191 MB)
  ├── train-00001-of-00007.parquet (456,909 rows, 191 MB)
  ├── train-00002-of-00007.parquet (456,909 rows, 191 MB)
  ├── train-00003-of-00007.parquet (456,909 rows, 191 MB)
  ├── train-00004-of-00007.parquet (456,908 rows, 191 MB)
  ├── train-00005-of-00007.parquet (456,908 rows, 191 MB)
  └── train-00006-of-00007.parquet (456,908 rows, 191 MB)
  Total: 3,198,360 patent records
```

Discovered Schema:
- `id` (string): Patent publication identifier.
- `date` (string, YYYY-MM-DD): Publication / grant date.
- `cpc_ids` (string): Multi-label comma-separated CPC subclass codes (e.g. `A01H,C11D,Y10S`).
- `text` (string): Full patent claims and abstract text.

---

## 2. Quick Launch Commands (Windows / PowerShell)

### Prerequisites
- Python 3.11+
- Node.js v18+ & npm

### Terminal 1: Launch Backend API
```powershell
cd D:\ALT-PROJECT\hcx-patent\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The FastAPI backend and Swagger documentation will be live at:
- API Base: `http://127.0.0.1:8000`
- Interactive Swagger Docs: `http://127.0.0.1:8000/docs`

### Terminal 2: Launch React Frontend
```powershell
cd D:\ALT-PROJECT\hcx-patent\frontend
npm run dev
```
The Research Dashboard will be accessible at:
- Web UI: `http://localhost:5173` (or `http://localhost:3000`)

---

## 3. Running Verification Tests

Run the complete 33-test suite covering dataset discovery, leakage tests, ML models, conformal predictors, and API endpoints:

```powershell
cd D:\ALT-PROJECT
python -m pytest hcx-patent/tests/ -v
```

---

## 4. Running the Classical Baseline Experiment

To execute a complete, reproducible multi-label baseline experiment on a 10,000 record development sample:

```powershell
python D:\ALT-PROJECT\hcx-patent\scripts\run_baseline_experiment.py
```

Artifacts generated:
- Model checkpoint: `artifacts/checkpoints/<run_id>_model.joblib`
- Evaluation metrics: `artifacts/metrics/<run_id>_metrics.json`
- Test predictions: `artifacts/predictions/<run_id>_predictions.csv`
- Split manifest: `data/splits/<run_id>_split_manifest.json`
- High-DPI Publication figures: `artifacts/figures/<run_id>_*.png`

---

## 5. Frontend Pages & Workflows

1. **Research Overview (`/`)**: High-level telemetry, dataset health status, hardware capabilities, and latest experiment metrics.
2. **Dataset Explorer (`/dataset`)**: Partition explorer, quality audit reports, CPC class distributions, and paginated records preview.
3. **Classification Workspace (`/classify`)**: Interactive multi-label inference, latency metrics, and hierarchical taxonomy path tracking.
4. **CPC Taxonomy Explorer (`/taxonomy`)**: Search and interactive Section $\to$ Class $\to$ Subclass tree navigation.
5. **Explainability Laboratory (`/explainability`)**: Token-level attribution, positive/negative evidence highlighting, and perturbation faithfulness tests.
6. **Uncertainty Laboratory (`/uncertainty`)**: Dynamic target coverage slider ($1 - \alpha$), empirical conformal coverage checks, and reliability calibration diagrams.
7. **Drift Analysis (`/drift`)**: Chronological cohort evaluations across the 2004–2015 publication timeline.
8. **Experiment Center (`/experiments`)**: Full pipeline orchestration, background job tracking, side-by-side run comparisons, and CSV/JSON downloads.

