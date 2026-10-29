"""Patent classification inference, search, and document upload endpoints."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from pydantic import BaseModel

from app.config import get_settings
from app.datasets.discovery import discover_datasets
from app.models.tfidf_baseline import TFIDFBaseline
from app.taxonomy.cpc_tree import CPCTaxonomy

router = APIRouter(prefix="/patents", tags=["Patents"])


class ClassifyRequest(BaseModel):
    text: str
    model_name: Optional[str] = "baseline"
    top_k: int = 5
    threshold: float = 0.3


# In-memory cached model for fast interactive inference
_cached_inference_model: Optional[Any] = None
_cached_class_names: Optional[List[str]] = None


def get_inference_model():
    """Load latest checkpoint or initialize on sample data."""
    global _cached_inference_model, _cached_class_names
    if _cached_inference_model is None:
        settings = get_settings()
        ckpt_dir = Path(settings.ARTIFACTS_DIR) / "checkpoints"
        models = sorted(ckpt_dir.glob("*.joblib"))
        if models:
            import joblib

            data = joblib.load(str(models[-1]))
            if isinstance(data, dict) and "classifier" in data:
                m = TFIDFBaseline()
                m.vectorizer = data["vectorizer"]
                m.classifier = data["classifier"]
                m.n_classes_ = len(data.get("class_names", []))
                _cached_inference_model = m
                _cached_class_names = data.get("class_names", [])
            else:
                _cached_inference_model = TFIDFBaseline.load(str(models[-1]))
                _cached_class_names = [f"Class_{i}" for i in range(_cached_inference_model.n_classes_)]
        else:
            # Train a quick micro-model on first parquet
            files = discover_datasets(settings.DATASET_ROOT)
            parquets = [f.path for f in files if f.format == "parquet"]
            if parquets:
                import pyarrow.parquet as pq
                from sklearn.preprocessing import MultiLabelBinarizer

                pf = pq.ParquetFile(parquets[0])
                df = pf.read_row_group(0).to_pandas().head(500)
                df["cpc_list"] = df["cpc_ids"].str.split(",").apply(lambda x: [c.strip() for c in x if c.strip()])

                from collections import Counter

                cnts = Counter([c for sub in df["cpc_list"] for c in sub])
                top_codes = [c[0] for c in cnts.most_common(20)]
                df["cpc_filt"] = df["cpc_list"].apply(lambda x: [c for c in x if c in top_codes])
                df = df[df["cpc_filt"].apply(len) > 0]

                mlb = MultiLabelBinarizer(classes=sorted(top_codes))
                y = mlb.fit_transform(df["cpc_filt"])

                m = TFIDFBaseline(max_features=5000)
                m.train(df["text"].tolist(), y)

                _cached_inference_model = m
                _cached_class_names = mlb.classes_.tolist()

    return _cached_inference_model, _cached_class_names


@router.get("/models")
def list_available_models() -> Dict[str, List[str]]:
    """List available model architectures and trained checkpoints."""
    return {"models": ["TF-IDF Baseline", "Hierarchy-Aware Classifier", "Transformer BERT"]}


@router.get("/sample")
def get_sample_patent() -> Dict[str, Any]:
    """Retrieve an actual sample patent record from the offline dataset for demonstration."""
    settings = get_settings()
    files = discover_datasets(settings.DATASET_ROOT)
    parquets = [f.path for f in files if f.format == "parquet"]
    if not parquets:
        return {
            "text": "1. A method of encoding digital media data in a computing environment comprising a processor and a memory, the method comprising: applying a transform to blocks of data; and quantizing the transformed coefficients.",
            "id": "7565018",
            "cpc_ids": "H03M,H04N",
            "date": "2009-07-21",
        }

    import pyarrow.parquet as pq

    pf = pq.ParquetFile(parquets[0])
    df = pf.read_row_group(0).to_pandas().head(1)
    row = df.iloc[0]
    return {
        "text": str(row["text"]),
        "id": str(row["id"]),
        "cpc_ids": str(row["cpc_ids"]),
        "date": str(row["date"]),
    }


@router.post("/classify")
def classify_patent(req: ClassifyRequest) -> Dict[str, Any]:
    """Classify patent text and return top candidate CPC codes with hierarchy paths."""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Patent text cannot be empty.")

    t0 = time.time()
    model, class_names = get_inference_model()
    if model is None:
        raise HTTPException(status_code=503, detail="No trained model available yet. Run baseline experiment first.")

    preds, probs = model.predict([req.text], threshold=req.threshold)
    latency_ms = (time.time() - t0) * 1000

    prob_row = probs[0]
    top_indices = np.argsort(prob_row)[::-1][: req.top_k]

    tax = CPCTaxonomy()
    predictions = []
    for idx in top_indices:
        code = class_names[idx] if class_names and idx < len(class_names) else f"C_{idx}"
        conf = float(prob_row[idx])
        ancestors = tax.get_ancestors(code)
        path = ancestors + [code] if code not in ancestors else ancestors

        predictions.append({
            "code": code,
            "label": f"CPC {code}",
            "confidence": round(conf, 4),
            "hierarchy_path": path,
        })

    return {
        "predictions": predictions,
        "inference_time_ms": round(latency_ms, 2),
        "model_name": req.model_name or "TF-IDF + Logistic Regression",
        "model_type": "multi_label",
    }


@router.get("/search")
def search_patents(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
) -> List[Dict[str, Any]]:
    """Search for patent documents in local dataset containing query."""
    settings = get_settings()
    files = discover_datasets(settings.DATASET_ROOT)
    parquets = [f.path for f in files if f.format == "parquet"]
    if not parquets:
        return []

    import pyarrow.parquet as pq

    pf = pq.ParquetFile(parquets[0])
    df = pf.read_row_group(0).to_pandas()

    q_lower = query.lower()
    matches = df[df["text"].str.lower().str.contains(q_lower, na=False)].head(limit)

    return matches.to_dict(orient="records")


@router.post("/upload")
async def upload_patent_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Parse text from uploaded TXT file."""
    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1", errors="ignore")

    return {
        "filename": file.filename,
        "char_count": len(text),
        "text_preview": text[:500],
        "text": text,
    }
