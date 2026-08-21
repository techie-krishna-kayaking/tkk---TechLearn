# ============================================================
# CHAPTER 3: STATISTICS & A/B TESTING
# Practice in: VS Code (Python)
# Topics asked at: Google, Meta, Amazon, Flipkart, Uber, Swiggy
# ============================================================

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# SECTION 1: Key Distributions (Know these cold!)
# ============================================================

# NORMAL distribution — used for large samples, CLT
# BINOMIAL  — yes/no events (click or not, convert or not)
# POISSON   — count of events in fixed time (orders per hour)
# UNIFORM   — equal probability

# ============================================================
# SECTION 2: Central Limit Theorem (CLT)
# ============================================================
# "Sample means follow a normal distribution regardless of
#  the underlying population distribution — given large n"
# THIS is why t-tests and z-tests work!

# Demonstrate CLT
population = np.random.exponential(scale=10, size=100000)  # skewed population

sample_means = []
for _ in range(1000):
    sample = np.random.choice(population, size=50)
    sample_means.append(np.mean(sample))

print(f"Population mean:      {np.mean(population):.2f}")
print(f"Mean of sample means: {np.mean(sample_means):.2f}  (should be ~equal)")
print(f"Population skewness:  {stats.skew(population):.2f}")
print(f"Sample means skewness:{stats.skew(sample_means):.2f} (should be ~0, normal)")

# ============================================================
# SECTION 3: Hypothesis Testing Framework
# ============================================================
# ALWAYS follow this structure in interviews:
#
# Step 1: State null (H0) and alternative (H1) hypothesis
# Step 2: Choose significance level (alpha = 0.05 typically)
# Step 3: Choose the right test
# Step 4: Calculate test statistic and p-value
# Step 5: Reject or fail to reject H0
# Step 6: Business conclusion

# ============================================================
# SECTION 4: A/B Testing — The Core DA Interview Topic
# ============================================================

# Simulate A/B test data
np.random.seed(42)
n_control   = 5000
n_treatment = 5000

# Conversion rates: control=10%, treatment=12%
control_conversions   = np.random.binomial(1, 0.10, n_control)
treatment_conversions = np.random.binomial(1, 0.12, n_treatment)

control_rate   = control_conversions.mean()
treatment_rate = treatment_conversions.mean()
lift           = (treatment_rate - control_rate) / control_rate * 100

print("\n=== A/B TEST RESULTS ===")
print(f"Control   Conversion Rate: {control_rate:.4f} ({control_rate*100:.2f}%)")
print(f"Treatment Conversion Rate: {treatment_rate:.4f} ({treatment_rate*100:.2f}%)")
print(f"Lift: {lift:.2f}%")

# Two-proportion Z-test
p_pool = (control_conversions.sum() + treatment_conversions.sum()) / (n_control + n_treatment)
se = np.sqrt(p_pool * (1 - p_pool) * (1/n_control + 1/n_treatment))
z_stat = (treatment_rate - control_rate) / se
p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))  # two-tailed

print(f"\nZ-statistic: {z_stat:.4f}")
print(f"P-value:     {p_value:.4f}")
print(f"Alpha:       0.05")
print(f"\nConclusion: {'REJECT H0 — Treatment is statistically significant!' if p_value < 0.05 else 'FAIL TO REJECT H0 — Not significant'}")

# Alternative: scipy chi2_contingency for conversion
contingency = np.array([
    [control_conversions.sum(),   n_control   - control_conversions.sum()],
    [treatment_conversions.sum(), n_treatment - treatment_conversions.sum()]
])
chi2, p_chi2, dof, expected = stats.chi2_contingency(contingency)
print(f"\nChi-square test p-value: {p_chi2:.4f}  (same conclusion)")

# ============================================================
# SECTION 5: T-Test (Continuous metric A/B)
# ============================================================

# Simulate revenue per user (continuous metric)
control_revenue   = np.random.normal(loc=50,  scale=20, size=n_control)
treatment_revenue = np.random.normal(loc=54,  scale=20, size=n_treatment)

t_stat, p_value_t = stats.ttest_ind(control_revenue, treatment_revenue)
print("\n=== T-TEST (Revenue per User) ===")
print(f"Control mean:   ${control_revenue.mean():.2f}")
print(f"Treatment mean: ${treatment_revenue.mean():.2f}")
print(f"T-statistic:    {t_stat:.4f}")
print(f"P-value:        {p_value_t:.4f}")
print(f"Conclusion: {'Significant difference!' if p_value_t < 0.05 else 'Not significant'}")

# ============================================================
# SECTION 6: Statistical Power & Sample Size
# ============================================================
# "How many users do I need in my A/B test?"

from math import ceil, sqrt

def sample_size_proportion(p1, p2, alpha=0.05, power=0.80):
    """Calculate required sample size per group for proportion test"""
    z_alpha = stats.norm.ppf(1 - alpha / 2)   # 1.96 for alpha=0.05
    z_beta  = stats.norm.ppf(power)            # 0.84 for power=0.80

    p_bar = (p1 + p2) / 2
    n = (z_alpha * sqrt(2 * p_bar * (1 - p_bar)) +
         z_beta  * sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p2 - p1) ** 2
    return ceil(n)

n_required = sample_size_proportion(p1=0.10, p2=0.12)  # 10% → 12% lift
print(f"\n=== SAMPLE SIZE CALCULATOR ===")
print(f"To detect 10% → 12% conversion lift:")
print(f"Required sample size per group: {n_required:,}")
print(f"Total sample needed: {n_required * 2:,}")

# ============================================================
# SECTION 7: Common Statistical Interview Q&As
# ============================================================

# Q1: What is p-value?
# A: Probability of observing test results at least as extreme
#    as the actual results, assuming H0 is true.
#    p < 0.05 → result is unlikely due to chance → reject H0

# Q2: Type 1 vs Type 2 Error
# Type 1 (False Positive): Reject H0 when it's actually true  → controlled by alpha
# Type 2 (False Negative): Fail to reject H0 when it's false  → controlled by beta/power

# Q3: What if p-value = 0.04? Is your test significant?
# → Yes, if alpha=0.05. But ALSO check effect size!
# → A tiny difference can be statistically significant with large n
# → Practical significance (effect size) matters too

# Q4: What is statistical power?
# Power = 1 - beta = probability of correctly detecting a true effect
# Typically set to 0.80 (80%)

# Q5: When to use t-test vs z-test?
# z-test: large samples (n > 30), known population std deviation
# t-test: small samples OR unknown population std deviation (most cases)

# ============================================================
# SECTION 8: Confidence Intervals
# ============================================================

# 95% CI for treatment conversion rate
n_t       = n_treatment
conv_t    = treatment_conversions.sum()
rate_t    = conv_t / n_t
z         = 1.96
margin    = z * sqrt(rate_t * (1 - rate_t) / n_t)
ci_lower  = rate_t - margin
ci_upper  = rate_t + margin

print(f"\n=== 95% CONFIDENCE INTERVAL ===")
print(f"Treatment conversion: {rate_t:.4f}")
print(f"95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")
print(f"Interpretation: We are 95% confident the true conversion rate")
print(f"                lies between {ci_lower*100:.2f}% and {ci_upper*100:.2f}%")

# ============================================================
# SECTION 9: Common A/B Test Pitfalls (Know These!)
# ============================================================
"""
1. PEEKING: Looking at results before experiment ends and stopping early
   → Inflates false positive rate. Use sequential testing or fix end date.

2. NOVELTY EFFECT: Users behave differently because it's new
   → Run test long enough (usually 2 weeks minimum)

3. NETWORK EFFECTS / INTERFERENCE: Users in control interact with treatment
   → Use cluster-level randomization

4. MULTIPLE TESTING: Running many simultaneous tests
   → Apply Bonferroni correction: alpha_adjusted = alpha / n_tests

5. SAMPLE RATIO MISMATCH (SRM): Actual split ≠ intended split
   → Run chi-square test on group sizes — if p < 0.05, something's wrong

6. SURVIVORSHIP BIAS: Analyzing only users who completed action
   → Always analyze at assignment level, not action level
"""

print("\n✅ Chapter 3: Statistics & A/B Testing complete!")
