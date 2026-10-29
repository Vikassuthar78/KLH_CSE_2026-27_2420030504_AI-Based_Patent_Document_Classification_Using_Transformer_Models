"""
Tests for ML models, metrics, and evaluation
"""
import sys
from pathlib import Path

import pytest
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


class TestMetrics:
    """Tests for evaluation metrics."""

    def test_compute_all_metrics(self):
        """Test that all expected metrics are computed."""
        from app.evaluation.metrics import compute_all_metrics
        
        np.random.seed(42)
        n_samples, n_classes = 50, 5
        y_true = np.random.randint(0, 2, (n_samples, n_classes))
        y_pred = np.random.randint(0, 2, (n_samples, n_classes))
        y_prob = np.random.rand(n_samples, n_classes)
        
        metrics = compute_all_metrics(y_true, y_pred, y_prob)
        
        assert "macro_f1" in metrics
        assert "micro_f1" in metrics
        assert "macro_precision" in metrics
        assert "macro_recall" in metrics
        assert "micro_precision" in metrics
        assert "micro_recall" in metrics
        assert "hamming_loss" in metrics
        
        # All metrics should be between 0 and 1
        for key in ["macro_f1", "micro_f1", "macro_precision", "macro_recall", "hamming_loss"]:
            assert 0.0 <= metrics[key] <= 1.0, f"{key} = {metrics[key]} is out of range"

    def test_perfect_predictions(self):
        """Test metrics with perfect predictions."""
        from app.evaluation.metrics import compute_all_metrics
        
        y_true = np.array([[1, 0, 1], [0, 1, 0], [1, 1, 0]])
        y_pred = y_true.copy()
        
        metrics = compute_all_metrics(y_true, y_pred)
        assert metrics["micro_f1"] == 1.0
        assert metrics["macro_f1"] == 1.0
        assert metrics["hamming_loss"] == 0.0

    def test_per_class_metrics(self):
        """Test per-class metric computation."""
        from app.evaluation.metrics import compute_all_metrics
        
        y_true = np.array([[1, 0], [0, 1], [1, 1], [0, 0]])
        y_pred = np.array([[1, 0], [0, 1], [1, 0], [0, 0]])
        
        metrics = compute_all_metrics(y_true, y_pred, class_names=["A", "B"])
        assert "per_class" in metrics
        assert len(metrics["per_class"]) == 2


class TestTFIDFBaseline:
    """Tests for TF-IDF + Logistic Regression baseline."""

    def test_train_and_predict(self, sample_texts, sample_labels):
        """Test training and prediction pipeline."""
        from app.models.tfidf_baseline import TFIDFBaseline
        
        mlb = MultiLabelBinarizer()
        y_bin = mlb.fit_transform(sample_labels)
        
        model = TFIDFBaseline(max_features=1000)
        model.train(sample_texts, y_bin)
        
        predictions, probabilities = model.predict(sample_texts[:2])
        assert predictions.shape[0] == 2
        assert predictions.shape[1] == y_bin.shape[1]
        assert probabilities.shape == predictions.shape

    def test_save_and_load(self, sample_texts, sample_labels, temp_dir):
        """Test model save/load cycle."""
        from app.models.tfidf_baseline import TFIDFBaseline
        
        mlb = MultiLabelBinarizer()
        y_bin = mlb.fit_transform(sample_labels)
        
        model = TFIDFBaseline(max_features=1000)
        model.train(sample_texts, y_bin)
        
        save_path = temp_dir / "model"
        model.save(str(save_path))
        
        loaded = TFIDFBaseline.load(str(save_path))
        preds1, _ = model.predict(sample_texts[:1])
        preds2, _ = loaded.predict(sample_texts[:1])
        np.testing.assert_array_equal(preds1, preds2)

    def test_empty_text_handling(self):
        """Test handling of empty or very short texts."""
        from app.models.tfidf_baseline import TFIDFBaseline
        
        texts = ["Normal patent text about methods", "", "Another valid text"]
        labels = np.array([[1, 0], [0, 1], [1, 1]])
        
        model = TFIDFBaseline(max_features=100)
        # Should not crash on empty texts
        model.train(texts, labels)
        preds, _ = model.predict(["test text"])
        assert preds.shape[0] == 1


class TestConformalPrediction:
    """Tests for conformal prediction."""

    def test_basic_conformal(self):
        """Test basic split conformal prediction."""
        from app.uncertainty.conformal import SplitConformalPredictor
        
        np.random.seed(42)
        n_cal, n_test, n_classes = 200, 50, 5
        
        # Generate calibration scores
        cal_probs = np.random.rand(n_cal, n_classes)
        cal_probs = cal_probs / cal_probs.sum(axis=1, keepdims=True)
        cal_labels = np.eye(n_classes)[np.random.randint(0, n_classes, n_cal)]
        
        test_probs = np.random.rand(n_test, n_classes)
        test_probs = test_probs / test_probs.sum(axis=1, keepdims=True)
        
        predictor = SplitConformalPredictor(target_coverage=0.9)
        predictor.calibrate(cal_probs, cal_labels)
        
        pred_sets = predictor.predict(test_probs)
        assert len(pred_sets) == n_test
        assert all(isinstance(s, (list, np.ndarray)) for s in pred_sets)

    def test_coverage_approximate(self):
        """Test that empirical coverage is approximately at target."""
        from app.uncertainty.conformal import SplitConformalPredictor
        
        np.random.seed(42)
        n = 1000
        n_classes = 10
        
        # Generate well-calibrated scores
        true_classes = np.random.randint(0, n_classes, n)
        probs = np.random.dirichlet(np.ones(n_classes), n)
        # Make true class more likely
        for i in range(n):
            probs[i, true_classes[i]] += 1.0
        probs = probs / probs.sum(axis=1, keepdims=True)
        
        labels = np.eye(n_classes)[true_classes]
        
        # Split into cal and test
        cal_probs, test_probs = probs[:500], probs[500:]
        cal_labels, test_labels = labels[:500], labels[500:]
        test_true = true_classes[500:]
        
        predictor = SplitConformalPredictor(target_coverage=0.9)
        predictor.calibrate(cal_probs, cal_labels)
        
        pred_sets = predictor.predict(test_probs)
        
        # Check coverage
        covered = sum(1 for i, ps in enumerate(pred_sets) if test_true[i] in ps)
        coverage = covered / len(pred_sets)
        
        # Coverage should be >= target - some slack for finite sample
        assert coverage >= 0.85, f"Coverage {coverage:.3f} too low"


class TestTaxonomy:
    """Tests for CPC taxonomy handling."""

    def test_build_hierarchy(self):
        """Test CPC hierarchy building from codes."""
        from app.taxonomy.cpc_tree import CPCTaxonomy
        
        codes = ["A01H", "A01B", "A61K", "G06F", "G06Q", "H01L", "H04N"]
        taxonomy = CPCTaxonomy()
        taxonomy.build_from_codes(codes)
        
        tree = taxonomy.get_tree()
        # Should have sections A, G, H
        section_codes = [n["code"] for n in tree]
        assert "A" in section_codes
        assert "G" in section_codes
        assert "H" in section_codes

    def test_get_ancestors(self):
        """Test getting ancestor codes."""
        from app.taxonomy.cpc_tree import CPCTaxonomy
        
        taxonomy = CPCTaxonomy()
        ancestors = taxonomy.get_ancestors("A01H")
        assert "A" in ancestors
        assert "A01" in ancestors

    def test_validate_parent_child(self):
        """Test parent-child validation."""
        from app.taxonomy.cpc_tree import CPCTaxonomy
        
        taxonomy = CPCTaxonomy()
        assert taxonomy.is_valid_parent_child("A", "A01")
        assert taxonomy.is_valid_parent_child("A01", "A01H")
        assert not taxonomy.is_valid_parent_child("A", "G06")
        assert not taxonomy.is_valid_parent_child("B01", "A01H")

