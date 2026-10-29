# HCX-Patent: AI-Based Patent Document Classification Using Transformer Models

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2+-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Tests](https://img.shields.io/badge/Pytest-33%20Passed%20(100%25)-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](#6-testing--validation)

**Hierarchical, Explainable, and Uncertainty-Aware Patent Classification under Taxonomy Drift**

*KL Deemed to be University — Department of Computer Science & Engineering*  
*Project ID: 2420030504*

[Research Paper (PDF)](docs/ALT_PAPER.pdf) • [Documentation (PDF)](docs/ALT_DOCUMENTATION_FINAL.pdf) • [Presentation Slides (PPTX)](docs/AI_Patent_Classification_Presentation%20%20Final%20Review-%201,2,3.pptx) • [Interactive Web UI](#5-quickstart-guide)

</div>

---

## 1. Executive Summary & Research Motivation

Classifying patent documents into standardized patent taxonomies (e.g., the **Cooperative Patent Classification [CPC]**) represents one of the most demanding tasks in natural language processing. Real-world patent examination faces four critical limitations:
1. **Taxonomy Inconsistency**: Standard flat classifiers assign subclasses that violate parent Section/Class constraints.
2. **Black-box Predictions**: Lack of faithful claim-level attribution impedes patent attorney and examiner review.
3. **Overconfidence & Miscalibration**: Deep models output point predictions without rigorous risk quantification.
4. **Temporal & Taxonomy Drift**: As novel technologies emerge, classification accuracy decays across chronological patent cohorts.

**HCX-Patent** addresses these challenges through a unified research and production platform evaluating **3.19 million USPTO patents** with:
- **Hierarchy-Aware Ensembles**: Constrained hierarchical decoding enforcing Section $\to$ Class $\to$ Subclass validity.
- **Claim-Level Explainability**: Token-level Integrated Gradients with perturbation faithfulness verification.
- **Split Conformal Prediction**: Distribution-free prediction sets guaranteeing statistical coverage ($1 - \alpha$).
- **Taxonomy Drift Auditing**: Evaluation across publication cohorts (2004–2015) to detect vocabulary decay and class shifts.

---

## 2. Key Research Results

Evaluated across multi-label patent classifications from the offline **USPTO-3M** dataset:

| Metric | Baseline TF-IDF (Flat) | HCX-Patent (Hierarchy-Aware) | Improvement / Significance |
|:---|:---:|:---:|:---:|
| **Top-1 Subclass Accuracy** | 71.4% | **82.5%** | **+11.1%** |
| **Top-3 Subclass Accuracy** | 86.2% | **94.5%** | **+8.3%** |
| **Section Top-1 Accuracy** | 68.9% | **77.3%** | **+8.4%** |
| **Hierarchy Consistency Violation Rate** | 14.8% | **0.00%** | **100% Constraint Compliance** |
| **Conformal Prediction Empirical Coverage** | 89.2% | **97.4%** | **Guaranteed $(\ge 95\%)$** |
| **Average Prediction Set Size** | 7.6 classes | **4.08 classes** | **46.3% Set Size Efficiency** |
| **Inference Latency (CPU)** | 42 ms | **35 ms** | Real-time capable |

*Detailed LaTeX tables, ablation studies, and high-DPI figures are available in [`docs/ALT_PAPER.pdf`](docs/ALT_PAPER.pdf) and [`hcx-patent/docs/paper_tables.tex`](hcx-patent/docs/paper_tables.tex).*

---

## 3. Platform Architecture

```
                                      ┌───────────────────────────────────────────────┐
                                      │           Offline USPTO-3M Dataset            │
                                      │  (3.19M Parquet records, 8 CPC Sections)      │
                                      └──────────────────────┬────────────────────────┘
                                                             │
                                                             ▼
                                      ┌───────────────────────────────────────────────┐
                                      │      Dataset Ingestion & Quality Profiler     │
                                      │   (Chunked Polars/Pandas, Leakage Shield)    │
                                      └──────────────────────┬────────────────────────┘
                                                             │
                              ┌──────────────────────────────┼──────────────────────────────┐
                              │                              │                              │
                              ▼                              ▼                              ▼
                 ┌─────────────────────────┐   ┌───────────────────────────┐   ┌─────────────────────────┐
                 │  Hierarchy Classifier   │   │  Split Conformal Engine   │   │  Explainability Engine  │
                 │   Multi-stage Section   │   │  Non-conformity scoring   │   │  Claim token salience   │
                 │  -> Class -> Subclass   │   │  Finite-sample coverage   │   │  Perturbation verify    │
                 └────────────┬────────────┘   └─────────────┬─────────────┘   └────────────┬────────────┘
                              │                              │                              │
                              └──────────────────────────────┼──────────────────────────────┘
                                                             │
                                                             ▼
                                      ┌───────────────────────────────────────────────┐
                                      │              FastAPI Backend REST             │
                                      │    (Async Endpoints, SQLite, Background Jobs) │
                                      └──────────────────────┬────────────────────────┘
                                                             │ JSON REST API
                                                             ▼
                                      ┌───────────────────────────────────────────────┐
                                      │      HCX Research Dashboard (React + Vite)    │
                                      │   8 Academic Modules • Recharts Data Studio   │
                                      └───────────────────────────────────────────────┘
```

---

## 4. Full-Stack Feature Modules

The web dashboard is organized into 8 scientific workspaces:

1. **Research Overview (`/`)**: Real-time telemetry, dataset discovery summary, hardware capability stats, and active experiment KPIs.
2. **Dataset Explorer (`/dataset`)**: Multi-partition browser for the 7 USPTO-3M chunks, missing-value audits, publication year histograms, and CPC frequency bars.
3. **Classification Workspace (`/classify`)**: Interactive patent text input with live hierarchical candidate predictions, confidence scores, and taxonomy path visualization.
4. **CPC Taxonomy Explorer (`/taxonomy`)**: Interactive tree browser across all 8 CPC Sections (A through H, Y), drilling down to Classes and Subclasses with official definitions.
5. **Explainability Laboratory (`/explainability`)**: Claim-level token attribution with positive/negative evidence highlighting and perturbation faithfulness tests.
6. **Uncertainty Laboratory (`/uncertainty`)**: Target coverage calibration slider ($1 - \alpha$), empirical coverage verification, prediction set size distribution, and calibration curves.
7. **Drift Analysis (`/drift`)**: Longitudinal cohort analysis comparing 2004–2015 patent distributions, measuring vocabulary shift and performance degradation.
8. **Experiment Center (`/experiments`)**: Interactive experiment runner, baseline vs. hierarchy model comparison, run history, and JSON/CSV artifact exports.

---

## 5. Quickstart Guide

### Prerequisites
- **Python**: 3.11 or higher
- **Node.js**: v18 or higher (with `npm`)
- **OS**: Windows 10/11, Linux, or macOS (CPU-first execution; optional CUDA acceleration)

### Step 1: Clone the Repository
```bash
git clone https://github.com/Vikassuthar78/KLH_CSE_2026-27_2420030504_AI-Based_Patent_Document_Classification_Using_Transformer_Models.git
cd KLH_CSE_2026-27_2420030504_AI-Based_Patent_Document_Classification_Using_Transformer_Models
```

### Step 2: Backend Setup & Launch
```powershell
# Navigate to backend directory
cd hcx-patent\backend

# Install Python dependencies
pip install -r requirements.txt

# Launch FastAPI server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- **API Base**: `http://127.0.0.1:8000`
- **Swagger Documentation**: `http://127.0.0.1:8000/docs`

### Step 3: Frontend Setup & Launch
```powershell
# In a new terminal, navigate to frontend directory
cd hcx-patent\frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
- **Web UI**: Open `http://localhost:5173` (or `http://localhost:3000`) in your browser.

---

## 6. Testing & Validation

The platform includes a comprehensive automated test suite with **33 unit and integration tests** verifying:
- Dataset discovery, chunked loading, and schema verification.
- Temporal split integrity and patent-family leakage prevention.
- Multi-label classification models and hierarchical decoders.
- Split conformal prediction coverage guarantees.
- FastAPI REST endpoints and background job managers.

Run all tests from the repository root:
```powershell
python -m pytest hcx-patent/tests/ -v
```

**Results:**
```text
============================= 33 passed in 10.42s =============================
- tests/test_datasets.py: 14 passed (100%)
- tests/test_models.py:   11 passed (100%)
- tests/test_api.py:       8 passed (100%)
```

---

## 7. Experiment Reproduction Scripts

Reproduce the research findings locally using the provided standalone scripts:

### A. Run Classical Multi-Label Baseline
```powershell
python hcx-patent\scripts\run_baseline_experiment.py
```
*Generates checkpoints, evaluation metrics, conformal calibration, and test set predictions.*

### B. Train Hierarchy-Aware High-Accuracy Model
```powershell
python hcx-patent\scripts\train_high_accuracy_model.py
```
*Trains Section and Subclass classifiers, enforces tree constraints, and records metrics in the SQLite database.*

### C. Generate Publication LaTeX Tables & Figures
```powershell
python hcx-patent\scripts\generate_paper_tables.py
```
*Outputs publication-ready LaTeX tables to `hcx-patent/docs/paper_tables.tex`.*

---

## 8. Repository Structure

```
├── .gitignore                     # Excludes large raw data (DATA/*.parquet), binaries, and caches
├── README.md                      # Primary project documentation
├── docs/
│   ├── ALT_PAPER.pdf              # Full academic research paper
│   ├── ALT_DOCUMENTATION_FINAL.pdf# Comprehensive project report & specifications
│   └── AI_Patent_Classification_Presentation  Final Review- 1,2,3.pptx # Defense slides
└── hcx-patent/
    ├── backend/
    │   ├── app/
    │   │   ├── api/               # FastAPI route controllers (patents, datasets, experiments, etc.)
    │   │   ├── core/              # Database engine, security, logging
    │   │   ├── datasets/          # USPTO-3M adapter, chunk profiler, leakage-free splitter
    │   │   ├── evaluation/        # Hierarchical metrics, temporal drift evaluators
    │   │   ├── explainability/    # Token attribution, stability & faithfulness checks
    │   │   ├── models/            # TF-IDF baseline, hierarchy-aware classifier, transformer wrapper
    │   │   ├── schemas/           # Pydantic validation schemas
    │   │   ├── taxonomy/          # CPC taxonomy tree navigation & validation
    │   │   └── uncertainty/       # Split conformal predictor, calibration diagnostics
    │   ├── pyproject.toml         # Python build configuration
    │   └── requirements.txt       # Pinned backend dependencies
    ├── configs/
    │   ├── dataset_config.yaml    # Column mapping & dataset thresholds
    │   └── experiment_configs.yaml# Hyperparameters & split definitions
    ├── docs/
    │   ├── ARCHITECTURE.md        # Technical architecture details
    │   ├── DATASET_CARD.md        # USPTO-3M dataset card
    │   ├── MODEL_CARD.md          # Model cards for deployed classifiers
    │   ├── EXPERIMENT_PROTOCOL.md # Reproducibility guidelines
    │   └── paper_tables.tex       # Generated LaTeX publication tables
    ├── frontend/
    │   ├── src/
    │   │   ├── api/               # Typed Axios API clients
    │   │   ├── charts/            # Recharts research visualizers (Drift, Calibration, Coverage, etc.)
    │   │   ├── components/        # Reusable UI cards, tables, modal, layout
    │   │   ├── pages/             # 8 scientific dashboard pages
    │   │   └── types/             # TypeScript interface definitions
    │   ├── package.json           # Frontend dependencies
    │   ├── tailwind.config.js     # Tailwind CSS theme
    │   └── vite.config.ts         # Vite bundler config
    ├── scripts/                   # Automated training, evaluation, and packaging scripts
    └── tests/                     # 33 comprehensive Pytest test cases
```

---

## 9. Academic Deliverables & Citation

If you use this codebase or research in your academic work, please refer to the project documentation:

```bibtex
@misc{suthar2026hcxpatent,
  author       = {Vikas Suthar},
  title        = {HCX-Patent: Hierarchical, Explainable, and Uncertainty-Aware Patent Classification under Taxonomy Drift},
  year         = {2026},
  institution  = {KL Deemed to be University},
  department   = {Department of Computer Science and Engineering},
  note         = {Project ID: 2420030504}
}
```

---

## 10. License

This research prototype is developed for academic evaluation under the MIT License.
The USPTO patent dataset consists of public domain documents provided by the United States Patent and Trademark Office.
