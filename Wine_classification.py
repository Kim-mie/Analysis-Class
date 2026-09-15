"""
Wine Quality Classification
Dataset: UCI Wine Quality (https://archive.ics.uci.edu/dataset/186/wine+quality)
Task: Binary classification -> "good" wine (quality >= 7) vs "not good" (quality < 7)
Models: Logistic Regression, Decision Tree, Random Forest
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report, roc_curve
)
import matplotlib

import matplotlib.pyplot as plt
import seaborn as sns

RANDOM_STATE = 42

# ---------------------------------------------------------------
# 1. Load & combine data
# ---------------------------------------------------------------
red = pd.read_csv("winequality-red.csv", sep=";")
white = pd.read_csv("winequality-white.csv", sep=";")
red["wine_type"] = 0   # red = 0
white["wine_type"] = 1  # white = 1
df = pd.concat([red, white], axis=0, ignore_index=True)
df = df.drop_duplicates().reset_index(drop=True)

print("Combined dataset shape:", df.shape)
print(df["quality"].value_counts().sort_index())

# ---------------------------------------------------------------
# 2. Create binary classification target
#    "good" wine = quality >= 7, "not good" = quality < 7
# ---------------------------------------------------------------
df["good_quality"] = (df["quality"] >= 7).astype(int)
print("\nClass balance (good_quality):")
print(df["good_quality"].value_counts(normalize=True))

X = df.drop(columns=["quality", "good_quality"])
y = df["good_quality"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
)

# Scale features (needed for Logistic Regression; harmless for trees)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ---------------------------------------------------------------
# 3. Train models
# ---------------------------------------------------------------
models = {
    "Logistic Regression": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE),
    "Decision Tree": DecisionTreeClassifier(max_depth=8, class_weight="balanced", random_state=RANDOM_STATE),
    "Random Forest": RandomForestClassifier(n_estimators=300, max_depth=12, class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1),
}

results = []
roc_data = {}
fitted = {}

for name, model in models.items():
    if name == "Logistic Regression":
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        y_proba = model.predict_proba(X_test_scaled)[:, 1]
    else:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

    fitted[name] = model

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    cm = confusion_matrix(y_test, y_pred)

    fpr, tpr, _ = roc_curve(y_test, y_proba)
    roc_data[name] = (fpr, tpr, auc)

    results.append({
        "Model": name,
        "Accuracy": acc,
        "Precision": prec,
        "Recall": rec,
        "F1-score": f1,
        "ROC-AUC": auc,
    })

    print(f"\n===== {name} =====")
    print(f"Accuracy : {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall   : {rec:.4f}")
    print(f"F1-score : {f1:.4f}")
    print(f"ROC-AUC  : {auc:.4f}")
    print("Confusion Matrix:\n", cm)
    print(classification_report(y_test, y_pred, target_names=["not good", "good"]))

results_df = pd.DataFrame(results).set_index("Model").round(4)
print("\n\n===== SUMMARY TABLE =====")
print(results_df)
results_df.to_csv("model_comparison_results.csv")

# ---------------------------------------------------------------
# 4. Plots: metric comparison bar chart, ROC curves, confusion matrices
# ---------------------------------------------------------------
sns.set_style("whitegrid")

# Metric comparison bar chart
fig, ax = plt.subplots(figsize=(10, 6))
results_df.plot(kind="bar", ax=ax)
ax.set_title("Model Performance Comparison - Wine Quality Classification")
ax.set_ylabel("Score")
ax.set_ylim(0, 1.05)
ax.legend(loc="lower right")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("metric_comparison.png", dpi=150)
plt.close()

# ROC curves
fig, ax = plt.subplots(figsize=(7, 6))
for name, (fpr, tpr, auc) in roc_data.items():
    ax.plot(fpr, tpr, label=f"{name} (AUC = {auc:.3f})")
ax.plot([0, 1], [0, 1], "k--", label="Random guess")
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.set_title("ROC Curves")
ax.legend(loc="lower right")
plt.tight_layout()
plt.savefig("roc_curves.png", dpi=150)
plt.close()

# Confusion matrices grid
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
for ax, (name, model) in zip(axes, fitted.items()):
    if name == "Logistic Regression":
        y_pred = model.predict(X_test_scaled)
    else:
        y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
                xticklabels=["not good", "good"], yticklabels=["not good", "good"])
    ax.set_title(name)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
plt.tight_layout()
plt.savefig("confusion_matrices.png", dpi=150)
plt.close()

# Feature importance (Random Forest)
rf = fitted["Random Forest"]
importances = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(8, 6))
importances.plot(kind="barh", ax=ax, color="teal")
ax.invert_yaxis()
ax.set_title("Random Forest Feature Importances")
plt.tight_layout()
plt.savefig("feature_importance.png", dpi=150)
plt.close()

print("\nSaved plots: metric_comparison.png, roc_curves.png, confusion_matrices.png, feature_importance.png")
print("\nTop features by RF importance:")
print(importances.head(6))