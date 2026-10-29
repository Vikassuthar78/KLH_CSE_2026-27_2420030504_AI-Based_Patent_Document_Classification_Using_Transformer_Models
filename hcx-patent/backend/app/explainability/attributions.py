"""Token-level and claim-level attribution methods for model interpretability."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


def explain_linear_prediction(
    text: str,
    target_class_idx: int,
    vectorizer: Any,
    classifier: Any,
    top_k: int = 15,
) -> Dict[str, Any]:
    """Generate token attribution using Logistic Regression coefficients and TF-IDF weights.

    Args:
        text: Input patent text
        target_class_idx: Index of the target CPC class
        vectorizer: Fitted TfidfVectorizer
        classifier: Fitted OneVsRestClassifier
        top_k: Number of highest attribution tokens to return

    Returns:
        Dict with tokens, attribution scores, and method metadata.
    """
    feature_names = np.array(vectorizer.get_feature_names_out())
    estimator = classifier.estimators_[target_class_idx]
    coefs = estimator.coef_.ravel()

    # Transform single text
    X_sample = vectorizer.transform([text])
    feature_indices = X_sample.indices
    feature_values = X_sample.data

    token_scores = []
    for idx, val in zip(feature_indices, feature_values):
        feat = feature_names[idx]
        score = float(coefs[idx] * val)
        token_scores.append({"token": feat, "score": score, "tfidf": float(val)})

    # Sort by absolute attribution score
    token_scores.sort(key=lambda x: abs(x["score"]), reverse=True)
    top_tokens = token_scores[:top_k]

    return {
        "method": "tfidf_linear_attribution",
        "target_class_index": target_class_idx,
        "tokens": [t["token"] for t in top_tokens],
        "scores": [t["score"] for t in top_tokens],
        "top_attributions": top_tokens,
    }


def explain_transformer_prediction(
    text: str,
    target_class_idx: int,
    model: Any,
    tokenizer: Any,
    device: str = "cpu",
    top_k: int = 15,
) -> Dict[str, Any]:
    """Integrated Gradients or input gradient attribution for PyTorch transformer."""
    import torch

    model.eval()
    inputs = tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
    input_ids = inputs["input_ids"].to(device)
    attention_mask = inputs["attention_mask"].to(device)

    # Get input embeddings
    embeddings_layer = model.get_input_embeddings()
    embeddings = embeddings_layer(input_ids)
    embeddings.retain_grad()

    outputs = model(inputs_embeds=embeddings, attention_mask=attention_mask)
    logits = outputs.logits
    target_logit = logits[0, target_class_idx]
    target_logit.backward()

    grads = embeddings.grad[0]  # (seq_len, hidden_dim)
    # Attribution = sum over hidden dimensions: grad * embedding
    attribution = (grads * embeddings[0]).sum(dim=-1).detach().cpu().numpy()

    tokens = tokenizer.convert_ids_to_tokens(input_ids[0].cpu().numpy())

    # Filter special tokens
    valid_tokens = []
    valid_scores = []
    for t, s in zip(tokens, attribution):
        if t not in ["[CLS]", "[SEP]", "[PAD]"]:
            valid_tokens.append(t)
            valid_scores.append(float(s))

    sorted_indices = np.argsort(np.abs(valid_scores))[::-1][:top_k]
    return {
        "method": "gradient_x_input",
        "target_class_index": target_class_idx,
        "tokens": [valid_tokens[i] for i in sorted_indices],
        "scores": [valid_scores[i] for i in sorted_indices],
    }

