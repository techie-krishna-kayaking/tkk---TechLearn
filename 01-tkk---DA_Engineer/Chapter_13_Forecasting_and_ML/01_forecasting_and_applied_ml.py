# ============================================================
# CHAPTER 13: FORECASTING & APPLIED ML FOR ANALYSTS
# Practice in: VS Code (Python)
# At 10 YOE, "analyst" roles at product companies expect you to
# forecast, model churn/propensity, and explain DRIVERS — not just
# describe the past. This is the analytics-vs-data-science overlap
# that unlocks the 75-80 LPA band.
# ============================================================

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (roc_auc_score, classification_report,
                             mean_absolute_error, confusion_matrix)
from sklearn.preprocessing import StandardScaler

rng = np.random.default_rng(7)

# ============================================================
# SECTION 1: FORECASTING — THE ANALYST'S BREAD & BUTTER
# ------------------------------------------------------------
# You WILL be asked "forecast next quarter's orders." Frameworks:
#   - Baselines first: naive (last value), seasonal naive, moving avg.
#   - Classical: Holt-Winters (trend + seasonality), SARIMA.
#   - ML: Prophet, LightGBM on lag features.
#   - ALWAYS beat the naive baseline or your model is worthless.
# Evaluate with a TIME-BASED split (never random) + MAPE/MAE.
# ============================================================

# Build a daily series with trend + weekly seasonality + noise
days = pd.date_range("2023-01-01", periods=730, freq="D")
t = np.arange(len(days))
trend = 500 + 0.8 * t
weekly = 60 * np.sin(2 * np.pi * t / 7)
orders = trend + weekly + rng.normal(0, 25, len(days))
ts = pd.Series(orders, index=days, name="orders")

# --- Baselines (compute these BEFORE any fancy model) ---
horizon = 28
train, test = ts.iloc[:-horizon], ts.iloc[-horizon:]

naive = np.repeat(train.iloc[-1], horizon)                 # last value
seasonal_naive = train.iloc[-7:].values.tolist() * (horizon // 7 + 1)
seasonal_naive = np.array(seasonal_naive[:horizon])        # same weekday LW

print("=== FORECASTING BASELINES (beat these!) ===")
print(f"Naive          MAE: {mean_absolute_error(test, naive):.1f}")
print(f"Seasonal-naive MAE: {mean_absolute_error(test, seasonal_naive):.1f}")

# --- Holt-Winters (trend + seasonality), no heavy deps ---
try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    hw = ExponentialSmoothing(train, trend="add",
                              seasonal="add", seasonal_periods=7).fit()
    hw_fc = hw.forecast(horizon)
    print(f"Holt-Winters   MAE: {mean_absolute_error(test, hw_fc):.1f}")
except Exception as e:
    print(f"(statsmodels not available: {e})")

def mape(y, yhat):
    return np.mean(np.abs((y - yhat) / y)) * 100
print(f"Seasonal-naive MAPE: {mape(test.values, seasonal_naive):.1f}%\n")
# INTERVIEW LINE: "I always report error vs a naive baseline and use
# a time-based holdout. A model that can't beat seasonal-naive isn't
# worth the complexity or the maintenance cost."


# ============================================================
# SECTION 2: CHURN / PROPENSITY MODEL (most-asked analyst ML task)
# ------------------------------------------------------------
# Predict P(churn) so the business can target retention. Analysts
# are judged on: right target definition, leakage avoidance,
# threshold choice tied to $ , and DRIVER interpretation.
# ============================================================

n = 8000
recency = rng.exponential(20, n)          # days since last order
frequency = rng.poisson(6, n)             # orders in window
tenure = rng.gamma(2, 30, n)
support_tickets = rng.poisson(0.5, n)
# True churn driven by high recency, low frequency, more tickets
logit = -1.5 + 0.06 * recency - 0.15 * frequency + 0.4 * support_tickets
p_churn = 1 / (1 + np.exp(-logit))
churn = rng.binomial(1, p_churn)

X = pd.DataFrame({"recency": recency, "frequency": frequency,
                  "tenure": tenure, "support_tickets": support_tickets})
y = churn
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25,
                                          random_state=1, stratify=y)

# Scale for the linear model (interpretable coefficients)
scaler = StandardScaler().fit(X_tr)
logit_model = LogisticRegression(max_iter=1000).fit(
    scaler.transform(X_tr), y_tr)
gbm = GradientBoostingClassifier(random_state=1).fit(X_tr, y_tr)

auc_logit = roc_auc_score(y_te, logit_model.predict_proba(
    scaler.transform(X_te))[:, 1])
auc_gbm = roc_auc_score(y_te, gbm.predict_proba(X_te)[:, 1])
print("=== CHURN MODEL ===")
print(f"Logistic Regression AUC: {auc_logit:.3f}")
print(f"Gradient Boosting   AUC: {auc_gbm:.3f}")

# DRIVERS (this is what the business actually wants)
coef = pd.Series(logit_model.coef_[0], index=X.columns).sort_values()
print("\nStandardized drivers (log-odds per 1 SD):")
print(coef.round(3).to_string())
print("Positive => raises churn risk. Recency & tickets are levers.\n")
# INTERVIEW LINE: "AUC tells me ranking quality, but the business
# needs the DRIVERS and a threshold. I'd calibrate probabilities and
# pick a cutoff where (save rate x margin) > (contact cost)."


# ============================================================
# SECTION 3: THRESHOLD CHOICE = A BUSINESS DECISION, NOT 0.5
# ------------------------------------------------------------
# Tie the cutoff to economics, not a default. Show this table.
# ============================================================
proba = gbm.predict_proba(X_te)[:, 1]
save_value = 800     # ₹ margin saved if we retain a true churner
contact_cost = 50    # ₹ cost to contact one flagged user
print("=== THRESHOLD -> EXPECTED VALUE ===")
best = (None, -1e18)
for thr in [0.2, 0.3, 0.4, 0.5, 0.6]:
    flag = proba >= thr
    tp = np.sum(flag & (y_te == 1))
    fp = np.sum(flag & (y_te == 0))
    ev = tp * save_value - (tp + fp) * contact_cost
    if ev > best[1]:
        best = (thr, ev)
    print(f"thr={thr:.1f}  flagged={flag.sum():4d}  TP={tp:4d}  "
          f"FP={fp:4d}  EV=₹{ev:,.0f}")
print(f"-> Pick threshold {best[0]} (max EV ₹{best[1]:,.0f}).\n")


# ============================================================
# SECTION 4: DRIVER / KEY-DRIVER ANALYSIS (regression for "why")
# ------------------------------------------------------------
# "NPS dropped — what's driving it?" Use a regression and read the
# standardized coefficients as relative importance. Communicate in
# business terms, not p-values.
# ============================================================
m = 3000
delivery_speed = rng.normal(0, 1, m)
price_fairness = rng.normal(0, 1, m)
app_quality = rng.normal(0, 1, m)
nps = (2.0 * delivery_speed + 1.2 * price_fairness
       + 0.6 * app_quality + rng.normal(0, 1, m))
D = pd.DataFrame({"delivery_speed": delivery_speed,
                  "price_fairness": price_fairness,
                  "app_quality": app_quality})
lr = LinearRegression().fit(D, nps)
drivers = pd.Series(lr.coef_, index=D.columns).sort_values(ascending=False)
print("=== KEY-DRIVER ANALYSIS (NPS) ===")
print(drivers.round(2).to_string())
print("Delivery speed is the top lever — invest there first.\n")


# ============================================================
# SECTION 5: MODEL EVALUATION LITERACY (traps interviewers probe)
# ------------------------------------------------------------
# - Data LEAKAGE: never use post-outcome features (e.g. 'cancellation
#   reason' to predict cancellation). #1 way models look 'too good'.
# - Class IMBALANCE: accuracy is useless at 2% churn; use AUC/PR-AUC,
#   recall@budget, and calibration.
# - Time leakage: split by TIME for anything temporal.
# - Overfitting: gap between train and validation; use CV.
# - Correlation of features (multicollinearity) inflates/flips signs.
# - Business metric > ML metric: optimize EV/₹, not AUC in a vacuum.
# ============================================================


# ============================================================
# WHAT TO SAY WHEN ASKED "WOULD YOU USE ML HERE?"
# ------------------------------------------------------------
# "First a baseline and the simplest model that answers the
#  business question. I add complexity only if it beats the
#  baseline on a time-honest holdout AND the lift is worth the
#  maintenance. I always translate the model into a decision:
#  a threshold, a driver, or a forecast with a confidence range."
# ============================================================

if __name__ == "__main__":
    print("Chapter 13 complete: forecasting + churn + drivers ready.")
