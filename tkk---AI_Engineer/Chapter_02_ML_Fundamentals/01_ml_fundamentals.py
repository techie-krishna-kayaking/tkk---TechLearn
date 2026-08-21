# ============================================================
# CHAPTER 2: ML FUNDAMENTALS
# Practice in: VS Code
# Topics: Core algorithms with intuition + code,
#         all metrics explained, cross-validation,
#         ensemble methods — every concept asked at FAANG
# ============================================================

import numpy as np
import pandas as pd
from sklearn.datasets import make_classification, make_regression
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    mean_squared_error, mean_absolute_error, r2_score
)
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# SECTION 1: Bias-Variance Trade-off — Visualized in Code
# ============================================================

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures

np.random.seed(42)
X_reg, y_reg = make_regression(n_samples=200, n_features=1, noise=20, random_state=42)
X_train, X_test = X_reg[:150], X_reg[150:]
y_train, y_test = y_reg[:150], y_reg[150:]

print("=== BIAS-VARIANCE DEMO ===")
for degree in [1, 5, 15]:
    pipe = Pipeline([
        ('poly', PolynomialFeatures(degree=degree)),
        ('scaler', StandardScaler()),
        ('model', Ridge(alpha=0.01))
    ])
    pipe.fit(X_train, y_train)
    train_mse = mean_squared_error(y_train, pipe.predict(X_train))
    test_mse  = mean_squared_error(y_test,  pipe.predict(X_test))
    label = "UNDERFIT" if degree == 1 else ("OVERFIT" if degree == 15 else "GOOD FIT")
    print(f"  Degree {degree:2d}: Train MSE={train_mse:.1f}, Test MSE={test_mse:.1f}  ← {label}")

# ============================================================
# SECTION 2: Regularization — L1 vs L2 vs ElasticNet
# ============================================================

X_many_feat, y_lasso = make_regression(n_samples=200, n_features=50,
                                        n_informative=5, noise=10, random_state=42)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_many_feat)

print("\n=== REGULARIZATION COMPARISON ===")
for name, model in [
    ("No Reg (OLS)",  Ridge(alpha=0.0001)),
    ("L2 Ridge",      Ridge(alpha=1.0)),
    ("L1 Lasso",      Lasso(alpha=0.1)),
    ("ElasticNet",    ElasticNet(alpha=0.1, l1_ratio=0.5)),
]:
    model.fit(X_scaled, y_lasso)
    coefs = model.coef_
    n_zero = np.sum(np.abs(coefs) < 0.01)
    print(f"  {name:15s}: non-zero weights={50-n_zero:2d}/50, "
          f"max_coef={np.max(np.abs(coefs)):.2f}")
# Lasso → sparsity (feature selection). Ridge → shrinks all. ElasticNet → both.

# ============================================================
# SECTION 3: All Classification Metrics — Explained
# ============================================================

X_clf, y_clf = make_classification(n_samples=1000, n_features=20,
                                    n_informative=10, weights=[0.85, 0.15],  # imbalanced
                                    random_state=42)
X_tr, X_te = X_clf[:800], X_clf[800:]
y_tr, y_te = y_clf[:800], y_clf[800:]

model_clf = GradientBoostingClassifier(n_estimators=100, random_state=42)
model_clf.fit(StandardScaler().fit_transform(X_tr), y_tr)
y_pred      = model_clf.predict(StandardScaler().fit_transform(X_te))
y_pred_prob = model_clf.predict_proba(StandardScaler().fit_transform(X_te))[:, 1]

tn, fp, fn, tp = confusion_matrix(y_te, y_pred).ravel()

print("\n=== CLASSIFICATION METRICS (IMBALANCED DATASET) ===")
print(f"  Confusion Matrix: TP={tp}, TN={tn}, FP={fp}, FN={fn}")
print(f"  Accuracy:  {accuracy_score(y_te, y_pred):.4f}  ← MISLEADING on imbalanced data!")
print(f"  Precision: {precision_score(y_te, y_pred):.4f}  ← Of predicted +, how many are +?")
print(f"  Recall:    {recall_score(y_te, y_pred):.4f}  ← Of actual +, how many caught?")
print(f"  F1 Score:  {f1_score(y_te, y_pred):.4f}  ← Harmonic mean of P and R")
print(f"  AUC-ROC:   {roc_auc_score(y_te, y_pred_prob):.4f}  ← Ranking quality, threshold-free")
print(f"  AUC-PR:    {average_precision_score(y_te, y_pred_prob):.4f}  ← Best for severe imbalance")

# Threshold tuning — lower threshold to improve recall (fraud/cancer use case)
print("\n--- THRESHOLD TUNING DEMO ---")
for threshold in [0.3, 0.5, 0.7]:
    y_custom = (y_pred_prob >= threshold).astype(int)
    p = precision_score(y_te, y_custom, zero_division=0)
    r = recall_score(y_te, y_custom, zero_division=0)
    f = f1_score(y_te, y_custom, zero_division=0)
    print(f"  Threshold={threshold}: Precision={p:.3f}, Recall={r:.3f}, F1={f:.3f}")

# ============================================================
# SECTION 4: Cross-Validation — The Right Way
# ============================================================

print("\n=== CROSS-VALIDATION ===")

# Standard K-Fold (for regression or balanced classification)
kf = KFold(n_splits=5, shuffle=True, random_state=42)
scores_kf = cross_val_score(
    GradientBoostingClassifier(random_state=42),
    X_clf, y_clf, cv=kf, scoring='roc_auc'
)
print(f"  K-Fold AUC:            mean={scores_kf.mean():.4f} ± {scores_kf.std():.4f}")

# Stratified K-Fold (ALWAYS use for classification — preserves class ratio)
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores_skf = cross_val_score(
    GradientBoostingClassifier(random_state=42),
    X_clf, y_clf, cv=skf, scoring='roc_auc'
)
print(f"  Stratified K-Fold AUC: mean={scores_skf.mean():.4f} ± {scores_skf.std():.4f}  ← CORRECT")

# Time-series: use TimeSeriesSplit (no future leakage)
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5)
print("  Time-Series Split: always train on past, test on future → no leakage")

# ============================================================
# SECTION 5: Ensemble Methods — How They Work
# ============================================================

print("\n=== ENSEMBLE METHODS ===")

from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier,
    BaggingClassifier, VotingClassifier, StackingClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

X_ens, y_ens = make_classification(n_samples=1000, n_features=20, random_state=42)
X_tr, X_te, y_tr, y_te = X_ens[:800], X_ens[800:], y_ens[:800], y_ens[800:]

models = {
    "Single Tree":           DecisionTreeClassifier(max_depth=5, random_state=42),
    "Bagging (RF)":          RandomForestClassifier(n_estimators=100, random_state=42),
    "Boosting (GBM)":        GradientBoostingClassifier(n_estimators=100, random_state=42),
    "Voting (hard)":         VotingClassifier(estimators=[
                                 ('lr', LogisticRegression()),
                                 ('rf', RandomForestClassifier(50, random_state=42)),
                                 ('gb', GradientBoostingClassifier(50, random_state=42)),
                             ], voting='soft'),
    "Stacking":              StackingClassifier(
                                 estimators=[
                                     ('rf', RandomForestClassifier(50, random_state=42)),
                                     ('gb', GradientBoostingClassifier(50, random_state=42)),
                                 ],
                                 final_estimator=LogisticRegression(),
                                 cv=5
                             ),
}

for name, model in models.items():
    model.fit(X_tr, y_tr)
    auc = roc_auc_score(y_te, model.predict_proba(X_te)[:, 1])
    print(f"  {name:20s}: AUC={auc:.4f}")

# ============================================================
# SECTION 6: Handling Class Imbalance — All Techniques
# ============================================================

print("\n=== CLASS IMBALANCE HANDLING ===")

from sklearn.utils import resample

# Method 1: Class weights
model_balanced = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
model_balanced.fit(X_tr, y_tr)
print(f"  Class weight='balanced': Recall={recall_score(y_te, model_balanced.predict(X_te)):.4f}")

# Method 2: SMOTE (if imbalanced-learn installed)
# from imblearn.over_sampling import SMOTE
# X_resampled, y_resampled = SMOTE(random_state=42).fit_resample(X_tr, y_tr)

# Method 3: Undersample majority class manually
from sklearn.datasets import make_classification
Xb, yb = make_classification(n_samples=1000, weights=[0.9, 0.1], random_state=42)
minority_idx  = np.where(yb == 1)[0]
majority_idx  = np.where(yb == 0)[0]
majority_down = np.random.choice(majority_idx, len(minority_idx), replace=False)
balanced_idx  = np.concatenate([minority_idx, majority_down])
X_bal, y_bal  = Xb[balanced_idx], yb[balanced_idx]
print(f"  After undersample: class distribution = {np.bincount(y_bal)}")

# ============================================================
# SECTION 7: Feature Importance — Interpreting Models
# ============================================================

print("\n=== FEATURE IMPORTANCE ===")

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_tr, y_tr)

# Built-in: mean decrease in impurity (MDI)
importances = pd.Series(rf.feature_importances_,
                         index=[f"f{i}" for i in range(X_tr.shape[1])])
top5 = importances.nlargest(5)
print("  Top 5 features (MDI):")
for feat, imp in top5.items():
    print(f"    {feat}: {imp:.4f}")

# Permutation importance (more reliable — measures actual impact on metric)
from sklearn.inspection import permutation_importance
perm = permutation_importance(rf, X_te, y_te, n_repeats=10, random_state=42)
perm_series = pd.Series(perm.importances_mean,
                          index=[f"f{i}" for i in range(X_te.shape[1])])
print("  Top 5 features (Permutation):")
for feat, imp in perm_series.nlargest(5).items():
    print(f"    {feat}: {imp:.4f}")

print("\n✅ Chapter 2: ML Fundamentals complete!")
