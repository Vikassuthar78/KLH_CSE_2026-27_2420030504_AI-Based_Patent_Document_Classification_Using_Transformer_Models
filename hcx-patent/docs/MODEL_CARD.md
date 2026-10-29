# Model Card: HCX-Patent Classifiers

## 1. Classical Baseline: TF-IDF + One-vs-Rest Logistic Regression
- **Architecture**: Sublinear term-frequency inverse-document-frequency vectorizer (unigrams + bigrams, max 50,000 features) coupled with an ensemble of binary $L_2$-regularized Logistic Regression estimators ($C=1.0$).
- **Multi-Label Formulation**: Independent binary cross-entropy minimization across calibrated CPC classes.
- **Hardware Profile**: Pure CPU execution, memory footprint < 1.5 GB RAM.
- **Inference Latency**: ~0.8 - 1.5 ms per document.

## 2. Hierarchy-Aware Model: CPCHierarchyClassifier
- **Architecture**: Base feature representation with parent-child constraint enforcement.
- **Taxonomy Prior**: Subclass predictions $k \in \mathcal{C}_{\text{sub}}$ propagate evidence to ancestor classes $a \in \text{anc}(k)$ ensuring that child activations consistently support parent classes.
- **Evaluation**: Evaluated using both subset exact match, Hamming loss, and hierarchy consistency score.

## 3. Deep Domain Model: PatentBERT Transformer
- **Architecture**: `bert-base-uncased` fine-tuned with binary cross-entropy with logits loss (`BCEWithLogitsLoss`) for multi-label patent categorization.
- **Token Handling**: Chunking and truncation strategy (max sequence length 512).
- **Execution Target**: Designed for CUDA acceleration with automatic CPU fallback for sample development.

## 4. Conformal Quantifier: SplitConformalPredictor
- **Guarantees**: Finite-sample marginal coverage guarantee $P(Y \in \mathcal{C}(X)) \ge 1 - \alpha$.
- **Score Function**: Nonconformity score $s_i = 1 - \hat{P}(Y=y_i \mid X_i)$.
- **Outputs**: Dynamically-sized prediction sets $\mathcal{C}(X) \subseteq \mathcal{Y}$.

