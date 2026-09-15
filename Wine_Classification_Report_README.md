# Wine Quality Classification — Model Report

## 1. Objective

Predict whether a wine is of **good quality** using its physicochemical properties, framed as a **binary classification problem**. This report covers data preparation, model training, evaluation, and the justification for the final model selection.

**Dataset:** [UCI Wine Quality Dataset](https://archive.ics.uci.edu/dataset/186/wine+quality) (red + white Vinho Verde wine samples)

---

## 2. Data Preparation

1. **Combined** the red (`winequality-red.csv`) and white (`winequality-white.csv`) datasets into a single table, adding a `wine_type` column (0 = red, 1 = white) to preserve that distinction as a feature.
2. **Removed duplicate rows**, resulting in a final dataset of **5,320 samples** across **13 columns** (11 physicochemical features + `wine_type` + `quality`).
3. **Created the binary target** `good_quality`:
   - `1` → `quality >= 7` ("good")
   - `0` → `quality < 7` ("not good")

**Class distribution:**

| Class | Proportion |
|---|---|
| Not good (0) | 81.03% |
| Good (1) | 18.97% |

This is a **moderately imbalanced** classification problem, which directly informed both the model settings (class weighting) and which evaluation metrics matter most (see Section 5).

4. **Train/test split:** 80% train / 20% test, stratified by `good_quality` to preserve the class ratio in both sets.
5. **Feature scaling:** Applied `StandardScaler` to the features for Logistic Regression only (fit on training data, applied to test data). Tree-based models (Decision Tree, Random Forest) used raw, unscaled features since they are not sensitive to feature scale.

---

## 3. Models Trained

Three classifiers were trained and compared:

| Model | Key settings used |
|---|---|
| Logistic Regression | `max_iter=2000`, `class_weight="balanced"`, `random_state=42` |
| Decision Tree | `max_depth=8`, `class_weight="balanced"`, `random_state=42` |
| Random Forest | `n_estimators=300`, `max_depth=12`, `class_weight="balanced"`, `random_state=42` |

### Hyperparameter tuning

**No automated hyperparameter search (e.g. `GridSearchCV` / `RandomizedSearchCV`) was performed in this run.** The values above (`max_depth`, `n_estimators`) were set manually as reasonable starting points to limit overfitting, rather than tuned against a validation set. `class_weight="balanced"` was applied uniformly across all three models to counteract the 81/19 class imbalance — this is a deliberate design choice, not a tuned hyperparameter.

**Suggested next step (not yet done):** run `GridSearchCV` on the Random Forest (the best-performing model) over `n_estimators`, `max_depth`, and `min_samples_leaf`, optimizing for F1-score or ROC-AUC via cross-validation, to see whether performance improves further. This is flagged here as a limitation/future improvement rather than a completed step.

---

## 4. Results

Evaluated on the held-out 20% test set (1,064 samples: 862 "not good", 202 "good"):

| Model | Accuracy | Precision | Recall | F1-score | ROC-AUC |
|---|---|---|---|---|---|
| Logistic Regression | 0.7312 | 0.3950 | 0.7822 | 0.5249 | 0.8166 |
| Decision Tree | 0.7237 | 0.3844 | 0.7574 | 0.5100 | 0.7670 |
| **Random Forest** | **0.8233** | **0.5250** | 0.7277 | **0.6100** | **0.8735** |

### Confusion matrices

**Logistic Regression**
```
[[620 242]
 [ 44 158]]
```

**Decision Tree**
```
[[617 245]
 [ 49 153]]
```

**Random Forest**
```
[[729 133]
 [ 55 147]]
```
(Rows = actual class, columns = predicted class, in order `[not good, good]`)

---

## 5. Evaluation Metrics: Why These Two Matter Most

Given the class imbalance (81% / 19%), **accuracy alone is misleading** — a model predicting "not good" for everything would score ~81% accuracy while being useless. Two metrics were prioritized instead:

- **F1-score** — the harmonic mean of precision and recall. It matters here because we care about both correctly flagging good wines (recall) *and* not over-flagging mediocre wines as good (precision), and F1 penalizes a model that sacrifices one for the other. Random Forest has the best F1 (0.610), indicating the best balance of the two.

- **ROC-AUC** — measures how well the model ranks "good" wines above "not good" ones across *all* possible decision thresholds, independent of class imbalance or a single cutoff choice. Random Forest again leads (0.8735), confirming it produces the most reliable probability ranking of the three models.

---

## 6. Model Justification: Why Random Forest

**Random Forest was selected as the final model.** It outperforms both alternatives on 4 of 5 metrics (Accuracy, Precision, F1-score, ROC-AUC), with only Recall (0.7277) slightly below Logistic Regression's (0.7822).

**Why it performs better:**
- It builds an ensemble of 300 decision trees, each trained on a bootstrapped sample of the data, and averages their votes — this reduces the overfitting and high variance that a single Decision Tree is prone to (visible in the Decision Tree's lower ROC-AUC of 0.767 vs Random Forest's 0.874).
- It captures non-linear relationships and feature interactions that Logistic Regression's linear decision boundary cannot represent.
- Its notably higher precision (0.525 vs ~0.39 for the other two) means far fewer false alarms — of the wines it labels "good," about half actually are, compared to roughly 2-in-5 for the other models.

**Trade-off acknowledged:** Logistic Regression has higher recall (0.782 vs 0.728), meaning it catches slightly more of the truly good wines, at the cost of many more false positives (precision of only 0.395). If the priority were "never miss a good wine, false alarms are acceptable," Logistic Regression would be the more defensible choice. For a **balanced, general-purpose classifier**, Random Forest is the stronger overall model.

---

## 7. Limitations & Future Work

- No formal hyperparameter search was conducted; current settings are reasonable manual defaults, not optimized.
- Cross-validation (e.g. 5-fold) was not used to validate model stability — results reflect a single train/test split.
- Feature importance analysis (Random Forest) could be used to justify feature selection/reduction in a future iteration.
- A cost-sensitive threshold adjustment (rather than the default 0.5 cutoff) could be explored to shift the precision/recall trade-off if a specific business cost were defined for false positives vs false negatives.

---

## 8. Conclusion

Random Forest is the recommended model for this wine quality classification task, offering the best overall balance of accuracy, precision, F1-score, and ranking ability (ROC-AUC), while Logistic Regression remains a reasonable alternative if recall is the top priority.
