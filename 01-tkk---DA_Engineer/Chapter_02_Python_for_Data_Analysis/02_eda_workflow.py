# ============================================================
# CHAPTER 2: PYTHON - EDA (Exploratory Data Analysis)
# Practice in: VS Code
# This is what Data Analysts do in every interview case study
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================
# SECTION 1: The EDA Framework (memorize this structure)
# ============================================================
# 1. Load & peek
# 2. Shape, dtypes, nulls
# 3. Descriptive statistics
# 4. Distribution of numerical columns
# 5. Value counts of categorical columns
# 6. Correlations
# 7. Outlier detection
# 8. Key business questions

# ============================================================
# SECTION 2: Full EDA Workflow
# ============================================================

# Simulate e-commerce dataset
np.random.seed(42)
n = 500

df = pd.DataFrame({
    'order_id':   range(1, n + 1),
    'customer_id': np.random.randint(1, 200, n),
    'product_cat': np.random.choice(['Electronics', 'Clothing', 'Food', 'Books', 'Home'], n,
                                     p=[0.3, 0.25, 0.2, 0.15, 0.1]),
    'order_date': pd.date_range('2023-01-01', periods=n, freq='17H'),
    'amount':     np.random.exponential(scale=500, size=n).round(2),
    'discount':   np.random.choice([0, 0.05, 0.10, 0.20], n, p=[0.5, 0.25, 0.15, 0.10]),
    'region':     np.random.choice(['North', 'South', 'East', 'West'], n),
    'returned':   np.random.choice([0, 1], n, p=[0.85, 0.15])
})

# Introduce some nulls for realism
df.loc[np.random.choice(n, 20), 'amount'] = np.nan
df.loc[np.random.choice(n, 10), 'region'] = None

# ---------------------------
# STEP 1: Load & Peek
# ---------------------------
print("Shape:", df.shape)
print("\nFirst 5 rows:")
print(df.head())

# ---------------------------
# STEP 2: Data Types & Nulls
# ---------------------------
print("\n-- Data Types --")
print(df.dtypes)

print("\n-- Null Counts --")
null_summary = pd.DataFrame({
    'null_count': df.isnull().sum(),
    'null_pct':   (df.isnull().sum() / len(df) * 100).round(2)
})
print(null_summary[null_summary.null_count > 0])

# ---------------------------
# STEP 3: Descriptive Stats
# ---------------------------
print("\n-- Numerical Summary --")
print(df.describe().round(2))

print("\n-- Categorical Summary --")
for col in ['product_cat', 'region']:
    print(f"\n{col}:\n{df[col].value_counts()}")

# ---------------------------
# STEP 4: Outlier Detection (IQR method)
# ---------------------------
Q1 = df['amount'].quantile(0.25)
Q3 = df['amount'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers = df[(df['amount'] < lower_bound) | (df['amount'] > upper_bound)]
print(f"\n-- Outliers in 'amount' (IQR method) --")
print(f"  Q1={Q1:.1f}, Q3={Q3:.1f}, IQR={IQR:.1f}")
print(f"  Bounds: [{lower_bound:.1f}, {upper_bound:.1f}]")
print(f"  Outlier count: {len(outliers)} ({len(outliers)/len(df)*100:.1f}%)")

# ---------------------------
# STEP 5: Business Questions
# ---------------------------

# Q1: Revenue by category
df['net_amount'] = df['amount'] * (1 - df['discount'])
cat_revenue = df.groupby('product_cat')['net_amount'].agg(['sum', 'mean', 'count'])
cat_revenue.columns = ['total_revenue', 'avg_order_value', 'order_count']
cat_revenue = cat_revenue.sort_values('total_revenue', ascending=False)
print("\n-- Revenue by Category --")
print(cat_revenue.round(2))

# Q2: Return rate by category
return_rate = df.groupby('product_cat')['returned'].mean().sort_values(ascending=False)
print("\n-- Return Rate by Category --")
print((return_rate * 100).round(2).rename('return_rate_%'))

# Q3: Monthly revenue trend
df['month'] = df['order_date'].dt.to_period('M')
monthly = df.groupby('month')['net_amount'].sum()
print("\n-- Monthly Revenue Trend --")
print(monthly.round(2))

# Q4: Customer segments by spend
customer_total = df.groupby('customer_id')['net_amount'].sum().reset_index()
customer_total.columns = ['customer_id', 'total_spend']
customer_total['segment'] = pd.qcut(
    customer_total['total_spend'],
    q=4,
    labels=['Low', 'Mid', 'High', 'VIP']
)
print("\n-- Customer Segment Distribution --")
print(customer_total['segment'].value_counts())

# ---------------------------
# STEP 6: Correlation Matrix
# ---------------------------
corr = df[['amount', 'discount', 'returned', 'net_amount']].corr().round(3)
print("\n-- Correlation Matrix --")
print(corr)

# ---------------------------
# STEP 7: Visualizations
# ---------------------------

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('E-Commerce EDA Dashboard', fontsize=16, fontweight='bold')

# Plot 1: Revenue by category (bar)
ax1 = axes[0, 0]
cat_revenue['total_revenue'].plot(kind='bar', ax=ax1, color='steelblue')
ax1.set_title('Total Revenue by Category')
ax1.set_xlabel('Category')
ax1.set_ylabel('Revenue ($)')
ax1.tick_params(axis='x', rotation=30)

# Plot 2: Amount distribution (histogram)
ax2 = axes[0, 1]
df['amount'].dropna().plot(kind='hist', bins=30, ax=ax2, color='salmon', edgecolor='white')
ax2.set_title('Order Amount Distribution')
ax2.set_xlabel('Amount ($)')

# Plot 3: Monthly trend (line)
ax3 = axes[1, 0]
monthly.plot(kind='line', ax=ax3, marker='o', color='green')
ax3.set_title('Monthly Revenue Trend')
ax3.set_xlabel('Month')
ax3.set_ylabel('Revenue ($)')
ax3.tick_params(axis='x', rotation=30)

# Plot 4: Return rate by region (bar)
ax4 = axes[1, 1]
region_return = df.groupby('region')['returned'].mean() * 100
region_return.plot(kind='bar', ax=ax4, color='orange')
ax4.set_title('Return Rate by Region (%)')
ax4.set_xlabel('Region')
ax4.set_ylabel('Return Rate %')

plt.tight_layout()
plt.savefig('eda_dashboard.png', dpi=150, bbox_inches='tight')
print("\nChart saved as 'eda_dashboard.png'")
plt.show()
