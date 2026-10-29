"""Explainability and attribution API endpoints."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.patents import get_inference_model
from app.explainability.attributions import explain_linear_prediction
from app.explainability.faithfulness import compute_faithfulness_metrics

router = APIRouter(prefix="/explainability", tags=["Explainability"])


class ExplainRequest(BaseModel):
    text: str
    target_class_code: Optional[str] = None
    target_class_index: Optional[int] = 0
    top_k: int = 15


@router.get("/methods")
def list_explain_methods() -> Dict[str, List[str]]:
    """List attribution explanation methods."""
    return {"methods": ["Linear Coefficients x TF-IDF", "Gradient x Input", "Integrated Gradients"]}


@router.post("/explain")
def get_explanation(req: ExplainRequest) -> Dict[str, Any]:
    """Compute token-level attribution scores for patent text."""
    model, class_names = get_inference_model()
    if model is None:
        raise HTTPException(status_code=503, detail="No trained model available.")

    target_idx = req.target_class_index or 0
    if req.target_class_code and class_names and req.target_class_code in class_names:
        target_idx = class_names.index(req.target_class_code)

    if hasattr(model, "vectorizer") and hasattr(model, "classifier"):
        res = explain_linear_prediction(
            text=req.text,
            target_class_idx=target_idx,
            vectorizer=model.vectorizer,
            classifier=model.classifier,
            top_k=req.top_k,
        )
        res["target_class_code"] = class_names[target_idx] if class_names and target_idx < len(class_names) else ""
        return res

    raise HTTPException(status_code=400, detail="Current model does not support linear attribution.")


@router.post("/faithfulness")
def evaluate_faithfulness(req: ExplainRequest) -> Dict[str, Any]:
    """Compute Comprehensiveness and Sufficiency metrics for explanation."""
    model, class_names = get_inference_model()
    if model is None:
        raise HTTPException(status_code=503, detail="No model available.")

    target_idx = req.target_class_index or 0
    if req.target_class_code and class_names and req.target_class_code in class_names:
        target_idx = class_names.index(req.target_class_code)

    # Explain first
    explanation = explain_linear_prediction(
        text=req.text,
        target_class_idx=target_idx,
        vectorizer=model.vectorizer,
        classifier=model.classifier,
        top_k=req.top_k,
    )

    def predict_probs(texts: List[str]):
        _, probs = model.predict(texts)
        return probs

    faith = compute_faithfulness_metrics(
        text=req.text,
        tokens=explanation["tokens"],
        scores=explanation["scores"],
        predict_fn=predict_probs,
        target_class_idx=target_idx,
    )
    faith["explanation"] = explanation
    return faith
