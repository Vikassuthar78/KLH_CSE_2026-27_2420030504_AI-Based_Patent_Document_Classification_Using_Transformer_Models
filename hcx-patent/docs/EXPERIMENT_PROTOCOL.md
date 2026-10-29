# HCX-Patent Research Experiment Protocol

## 1. Research Hypotheses Under Evaluation

1. **H1 (Hierarchical Consistency)**: Explicit taxonomy priors reduce hierarchical constraint violations compared to unconstrained flat multi-label baselines without compromising macro-F1.
2. **H2 (Faithfulness & Stability)**: Input gradient and linear coefficient token attributions achieve higher Comprehensiveness ($P(x) - P(x \setminus S)$) than random or attention-weight baselines.
3. **H3 (Conformal Coverage)**: Split conformal prediction produces calibrated prediction sets that meet empirical target coverage ($1 - \alpha$) on independent test sets under exchangeability.
4. **H4 (Temporal Drift Degradation)**: Chronologically separated evaluation cohorts (e.g. 2004 vs 2014) experience measurable performance decay ($\Delta \text{Macro-F1}$) due to language and patent terminology evolution.

## 2. Evaluation Metrics

- **Subset Accuracy (Exact Match)**: $\frac{1}{N} \sum_{i=1}^N \mathbb{I}(\mathbf{y}_i = \mathbf{\hat{y}}_i)$
- **Hamming Loss**: $\frac{1}{N \cdot C} \sum_{i=1}^N \sum_{c=1}^C \mathbb{I}(y_{ic} \neq \hat{y}_{ic})$
- **Macro Precision, Recall, F1**: Unweighted arithmetic mean across all active CPC classes.
- **Micro Precision, Recall, F1**: Aggregate true-positive, false-positive, and false-negative pooling.
- **Expected Calibration Error (ECE)**: $\sum_{m=1}^M \frac{|B_m|}{N} |\text{acc}(B_m) - \text{conf}(B_m)|$
- **Empirical Conformal Coverage**: $\frac{1}{N_{\text{test}}} \sum_{i=1}^{N_{\text{test}}} \mathbb{I}(\mathbf{y}_i \in \mathcal{C}(\mathbf{x}_i))$
- **Average Prediction Set Size**: $\frac{1}{N_{\text{test}}} \sum_{i=1}^{N_{\text{test}}} |\mathcal{C}(\mathbf{x}_i)|$

