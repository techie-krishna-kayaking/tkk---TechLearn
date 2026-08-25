# ============================================================
# CHAPTER 10: CAUSAL INFERENCE (Beyond Basic A/B)
# Practice in: VS Code (Python)
# This is the #1 differentiator for SENIOR / STAFF DA at
# Google, Meta, Uber, Netflix, Booking, DoorDash, Swiggy.
# Basic A/B testing is table stakes. THIS gets you to 75-80 LPA.
# ============================================================

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

rng = np.random.default_rng(42)

# ============================================================
# WHY THIS CHAPTER MATTERS
# ------------------------------------------------------------
# Interviewers separate mid-level from senior with ONE theme:
#   "You can't run a clean A/B test here. Now what?"
# Answer: variance reduction, quasi-experiments, and causal
# estimation. Correlation != causation is a junior answer.
# Senior answer = "here is the identification strategy."
# ============================================================


# ============================================================
# SECTION 1: CUPED (Variance Reduction) — asked at Microsoft/Meta
# ------------------------------------------------------------
# Problem: A/B test is underpowered. You need a smaller MDE
#          without more traffic or longer runtime.
# Idea: Use a PRE-EXPERIMENT covariate (e.g. user's spend the
#       week before) to remove known variance from the metric.
#       Y_adj = Y - theta * (X - E[X]),  theta = cov(X,Y)/var(X)
# Result: same unbiased treatment effect, 20-50% less variance
#         => 20-50% less traffic needed. Huge for senior roles.
# ============================================================

def cuped_adjust(y, x_pre):
    """Return CUPED-adjusted metric using a pre-period covariate."""
    theta = np.cov(x_pre, y, ddof=1)[0, 1] / np.var(x_pre, ddof=1)
    return y - theta * (x_pre - x_pre.mean()), theta

# Simulate: pre-period spend correlates with in-experiment spend
n = 5000
pre_spend = rng.gamma(shape=2.0, scale=50, size=n)
noise = rng.normal(0, 40, n)
assign = rng.integers(0, 2, n)              # 0=control, 1=treatment
true_effect = 5.0                            # treatment adds 5 units
y = 0.7 * pre_spend + true_effect * assign + noise

y_adj, theta = cuped_adjust(y, pre_spend)

def effect_and_se(metric, assign):
    t = metric[assign == 1]; c = metric[assign == 0]
    eff = t.mean() - c.mean()
    se = np.sqrt(t.var(ddof=1)/len(t) + c.var(ddof=1)/len(c))
    return eff, se

eff_raw, se_raw = effect_and_se(y, assign)
eff_cuped, se_cuped = effect_and_se(y_adj, assign)
print("=== CUPED ===")
print(f"theta                : {theta:.3f}")
print(f"Raw   effect {eff_raw:6.2f}  SE {se_raw:.3f}")
print(f"CUPED effect {eff_cuped:6.2f}  SE {se_cuped:.3f}")
print(f"Variance reduction   : {(1 - (se_cuped/se_raw)**2)*100:.1f}%  "
      f"=> ~{(1 - (se_cuped/se_raw)**2)*100:.0f}% less traffic needed\n")
# INTERVIEW LINE: "CUPED keeps the estimate unbiased because the
# covariate is measured PRE-treatment, so it cannot be affected by
# the treatment. We only strip out pre-existing variance."


# ============================================================
# SECTION 2: DIFFERENCE-IN-DIFFERENCES (DiD)
# ------------------------------------------------------------
# Use when: you CANNOT randomize (e.g. a feature/price rolled
#           out to one city, one market, one platform).
# Identifies effect by comparing the CHANGE in treated group vs
# the CHANGE in a control group over the same period.
# KEY ASSUMPTION: parallel trends (both groups would have moved
#                 the same way absent treatment). Always test it.
# ============================================================

# Panel: cities A,B (treated after t=6), C,D (control), 12 periods
periods = np.arange(12)
rows = []
for city, treated in [("A", 1), ("B", 1), ("C", 0), ("D", 0)]:
    base = rng.normal(100, 5)
    for t in periods:
        trend = 2 * t                              # common time trend
        post = 1 if t >= 6 else 0
        effect = 15 if (treated and post) else 0   # true lift = 15
        gmv = base + trend + effect + rng.normal(0, 3)
        rows.append((city, t, treated, post, gmv))
did = pd.DataFrame(rows, columns=["city", "t", "treated", "post", "gmv"])

# DiD via regression: gmv ~ treated + post + treated:post
# The interaction coefficient IS the causal effect.
model = smf.ols("gmv ~ treated + post + treated:post", data=did).fit()
print("=== DIFFERENCE-IN-DIFFERENCES ===")
print(f"Estimated treatment effect (interaction): "
      f"{model.params['treated:post']:.2f}  (true = 15)")
print(f"p-value: {model.pvalues['treated:post']:.4f}\n")
# INTERVIEW LINE: "DiD controls for (a) fixed differences between
# groups and (b) common time shocks. It fails if trends diverge
# for reasons other than treatment — so I'd plot pre-period trends."


# ============================================================
# SECTION 3: SEQUENTIAL TESTING (Stop peeking safely)
# ------------------------------------------------------------
# Problem: PMs peek daily and stop when p<0.05 => false positive
#          rate explodes to 20-30%, not 5%.
# Fixes senior candidates mention:
#   1) Fixed-horizon test — commit to n up front (classic).
#   2) Always-Valid p-values / mSPRT (Optimizely, Netflix).
#   3) Group Sequential (O'Brien-Fleming alpha spending).
# Below: a simple alpha-spending style guardrail demo.
# ============================================================

def obrien_fleming_bounds(looks, alpha=0.05):
    """Approx two-sided z-boundaries for K interim looks."""
    k = np.arange(1, looks + 1)
    frac = k / looks
    z_final = stats.norm.ppf(1 - alpha / 2)
    # O'Brien-Fleming: spend little early, most at the end
    return z_final / np.sqrt(frac)

print("=== SEQUENTIAL TESTING (O'Brien-Fleming z-bounds) ===")
for looks in (2, 4):
    b = obrien_fleming_bounds(looks)
    print(f"{looks} looks -> reject if |z| exceeds: "
          f"{np.round(b, 2)}")
print("Naive |z|>1.96 at every look inflates alpha to ~20-30%.\n")
# INTERVIEW LINE: "Peeking is a multiple-comparisons problem. I'd
# either fix the horizon, or use an always-valid / group-sequential
# method that spends alpha across looks."


# ============================================================
# SECTION 4: SWITCHBACK EXPERIMENTS
# ------------------------------------------------------------
# Use when: marketplace / network effects break unit-level A/B.
#   (Uber surge, DoorDash dispatch, Swiggy delivery allocation)
# You randomize TIME x REGION cells to treatment/control instead
# of users, because one user's treatment leaks onto others.
# ============================================================

# Randomize each (region, 30-min window) cell to T or C
regions = ["north", "south", "east", "west"]
windows = pd.date_range("2024-06-01", periods=48, freq="30min")
sw = pd.DataFrame(
    [(r, w) for r in regions for w in windows],
    columns=["region", "window"]
)
sw["treatment"] = rng.integers(0, 2, len(sw))
# Effect: treatment reduces ETA by ~1.5 min
sw["eta_min"] = 12 - 1.5 * sw["treatment"] + rng.normal(0, 2, len(sw))

# Cluster-robust comparison (cluster = region) — never use naive t-test
eff = smf.ols("eta_min ~ treatment", data=sw).fit(
    cov_type="cluster", cov_kwds={"groups": sw["region"]})
print("=== SWITCHBACK EXPERIMENT ===")
print(f"ETA effect: {eff.params['treatment']:.2f} min "
      f"(true = -1.5), cluster-robust p={eff.pvalues['treatment']:.4f}")
print("Randomize time x region cells; cluster SEs by region.\n")
# INTERVIEW LINE: "Unit-level randomization violates SUTVA in a
# marketplace. Switchbacks randomize time-region blocks so supply
# and demand see a consistent condition within a window."


# ============================================================
# SECTION 5: PROPENSITY SCORE MATCHING (Observational data)
# ------------------------------------------------------------
# Use when: no experiment at all — only logs. Users self-select
#           into a feature. Naive comparison = selection bias.
# Fit P(treat | covariates), then compare treated vs control users
# with SIMILAR propensity (matching / IPW). Reduces confounding.
# ============================================================

m = 4000
age = rng.normal(35, 8, m)
tenure = rng.gamma(2, 20, m)
# Heavier users self-select into the feature (confounding!)
logit = -6 + 0.05 * age + 0.02 * tenure
p_treat = 1 / (1 + np.exp(-logit))
treat = rng.binomial(1, p_treat)
# True effect = +8 on retention score; confounders also raise it
retention = 40 + 0.3 * age + 0.1 * tenure + 8 * treat + rng.normal(0, 5, m)
obs = pd.DataFrame({"age": age, "tenure": tenure,
                    "treat": treat, "retention": retention})

naive = obs.loc[obs.treat == 1, "retention"].mean() - \
        obs.loc[obs.treat == 0, "retention"].mean()

# Estimate propensity, then Inverse Propensity Weighting (IPW)
ps_model = smf.logit("treat ~ age + tenure", data=obs).fit(disp=0)
obs["ps"] = ps_model.predict(obs)
obs["w"] = np.where(obs.treat == 1, 1 / obs.ps, 1 / (1 - obs.ps))
ipw = (np.average(obs.loc[obs.treat == 1, "retention"],
                  weights=obs.loc[obs.treat == 1, "w"]) -
       np.average(obs.loc[obs.treat == 0, "retention"],
                  weights=obs.loc[obs.treat == 0, "w"]))
print("=== PROPENSITY SCORE / IPW ===")
print(f"Naive (biased) effect : {naive:.2f}")
print(f"IPW adjusted effect   : {ipw:.2f}   (true = 8)")
print("Adjusting for confounders removes selection bias.\n")
# INTERVIEW LINE: "Observational data has confounding. I model the
# treatment assignment, then reweight/match so treated and control
# are comparable on observed covariates. Caveat: unobserved
# confounders still bias us — that's the key limitation."


# ============================================================
# SECTION 6: WHICH METHOD? (Decision framework — say this out loud)
# ------------------------------------------------------------
# Can you randomize users cleanly?           -> A/B test (+ CUPED)
# Underpowered / need less traffic?          -> CUPED / stratification
# Network/marketplace spillover?             -> Switchback / cluster A/B
# Rolled out by geo/time, no control arm?    -> DiD / Synthetic Control
# Only observational logs, self-selection?   -> PSM / IPW / DoubleML
# A threshold/cutoff assigns treatment?      -> Regression Discontinuity
# An instrument nudges adoption?             -> Instrumental Variables
#
# Golden closing line for any causal question:
# "State the estimand, the identification strategy, the key
#  assumption, and how I'd stress-test that assumption."
# ============================================================

if __name__ == "__main__":
    print("Chapter 10 complete: you can now handle any 'we can't "
          "run a clean A/B test' senior interview question.")
