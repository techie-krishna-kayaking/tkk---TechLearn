# ============================================================
# CHAPTER 2: PYTHON FOR DATA ANALYSIS
# Practice in: VS Code (or Databricks notebooks)
# Topics: Pandas data wrangling, real-world data cleaning,
#         NumPy, datetime handling, merge/join operations
# ============================================================

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# SECTION 1: DataFrame Fundamentals (Review / Warmup)
# ============================================================

# Create sample datasets
employees = pd.DataFrame({
    'emp_id':   [1, 2, 3, 4, 5, 6],
    'name':     ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank'],
    'dept':     ['Eng', 'Eng', 'Sales', 'Sales', 'HR', 'HR'],
    'salary':   [90000, 85000, 70000, 75000, 60000, 62000],
    'hire_date':['2018-01-15', '2019-03-10', '2020-06-01', '2017-11-20', '2021-02-28', '2022-08-15'],
    'manager_id': [None, 1, None, 3, None, 5]
})

orders = pd.DataFrame({
    'order_id':    [101, 102, 103, 104, 105, 106, 107],
    'customer_id': [1, 2, 1, 3, 2, 4, 1],
    'order_date':  ['2024-01-10', '2024-01-15', '2024-02-05', '2024-02-20', '2024-03-01', '2024-03-15', '2024-04-02'],
    'amount':      [500, 1200, 800, 300, 950, 1500, 700],
    'region':      ['North', 'South', 'North', 'East', 'South', 'West', 'North']
})

# Convert date columns
employees['hire_date'] = pd.to_datetime(employees['hire_date'])
orders['order_date']   = pd.to_datetime(orders['order_date'])

print("=== Employees ===")
print(employees)
print("\n=== Orders ===")
print(orders)

# ============================================================
# SECTION 2: groupby — the most important Pandas skill
# ============================================================

# Q: Average salary by department
dept_avg = employees.groupby('dept')['salary'].mean().reset_index()
dept_avg.columns = ['dept', 'avg_salary']
print("\n-- Avg Salary by Dept --")
print(dept_avg)

# Q: Multiple aggregations at once
dept_stats = employees.groupby('dept').agg(
    headcount=('emp_id', 'count'),
    avg_salary=('salary', 'mean'),
    max_salary=('salary', 'max'),
    min_salary=('salary', 'min'),
    total_payroll=('salary', 'sum')
).reset_index()
print("\n-- Dept Stats --")
print(dept_stats)

# Q: Orders: revenue by region + month
orders['month'] = orders['order_date'].dt.to_period('M')
monthly_regional = orders.groupby(['region', 'month'])['amount'].sum().reset_index()
print("\n-- Monthly Revenue by Region --")
print(monthly_regional)

# ============================================================
# SECTION 3: Merge / Join Operations (SQL equivalent in Pandas)
# ============================================================

# INNER JOIN — employees with their dept stats
merged = employees.merge(dept_stats[['dept', 'avg_salary']], on='dept', how='left')
merged['vs_dept_avg'] = merged['salary'] - merged['avg_salary']
print("\n-- Employees vs Dept Avg --")
print(merged[['name', 'dept', 'salary', 'avg_salary', 'vs_dept_avg']])

# Self-join — employee + manager name
emp_copy = employees[['emp_id', 'name']].rename(columns={'emp_id': 'manager_id', 'name': 'manager_name'})
with_manager = employees.merge(emp_copy, on='manager_id', how='left')
print("\n-- Employee + Manager --")
print(with_manager[['name', 'dept', 'salary', 'manager_name']])

# ============================================================
# SECTION 4: apply, map, lambda — row-level transformations
# ============================================================

# Q: Classify salary into tiers
def salary_tier(salary):
    if salary >= 85000:
        return 'Senior'
    elif salary >= 70000:
        return 'Mid'
    else:
        return 'Junior'

employees['tier'] = employees['salary'].apply(salary_tier)
# OR using pd.cut (faster):
employees['tier_cut'] = pd.cut(
    employees['salary'],
    bins=[0, 69999, 84999, float('inf')],
    labels=['Junior', 'Mid', 'Senior']
)
print("\n-- Salary Tiers --")
print(employees[['name', 'salary', 'tier', 'tier_cut']])

# Q: Years of experience from hire date
employees['years_exp'] = (pd.Timestamp.today() - employees['hire_date']).dt.days / 365.25
employees['years_exp'] = employees['years_exp'].round(1)

# ============================================================
# SECTION 5: Data Cleaning — Real Interview Scenarios
# ============================================================

# Sample messy data
messy = pd.DataFrame({
    'name':   ['Alice ', ' Bob', 'CHARLIE', 'diana', None, 'Eve'],
    'email':  ['alice@co.com', 'bob@', 'charlie@co.com', None, 'x@y.com', 'eve@co.com'],
    'salary': ['90000', '85,000', '70000', 'N/A', '60000', '62000'],
    'score':  [95, None, 88, 76, None, 91]
})

# Fix name: strip whitespace, title case
messy['name'] = messy['name'].str.strip().str.title()

# Fix salary: remove commas, handle N/A, convert to numeric
messy['salary'] = messy['salary'].replace('N/A', np.nan)
messy['salary'] = messy['salary'].str.replace(',', '').astype(float)

# Handle nulls: fill score with median, drop rows with null name
messy['score'] = messy['score'].fillna(messy['score'].median())
messy = messy.dropna(subset=['name'])

# Validate email
messy['valid_email'] = messy['email'].str.contains(r'^[\w.+-]+@[\w-]+\.\w+$', na=False)

print("\n-- Cleaned Data --")
print(messy)

# ============================================================
# SECTION 6: Pivot Tables — MoM / Cross-tab analysis
# ============================================================

# Pivot: orders amount by region (rows) and month (cols)
orders['month_label'] = orders['order_date'].dt.strftime('%Y-%m')
pivot = orders.pivot_table(
    index='region',
    columns='month_label',
    values='amount',
    aggfunc='sum',
    fill_value=0
)
print("\n-- Revenue Pivot Table --")
print(pivot)

# Cross-tab: order count by region and customer
ctab = pd.crosstab(orders['region'], orders['customer_id'])
print("\n-- Cross-tab: Orders per Region per Customer --")
print(ctab)

# ============================================================
# SECTION 7: Window Functions equivalent in Pandas
# ============================================================

# Q: Rank customers by total spend
customer_spend = orders.groupby('customer_id')['amount'].sum().reset_index()
customer_spend['rank'] = customer_spend['amount'].rank(ascending=False, method='dense').astype(int)
customer_spend = customer_spend.sort_values('rank')
print("\n-- Customer Spend Rank --")
print(customer_spend)

# Q: Running total of orders per customer (sorted by date)
orders_sorted = orders.sort_values(['customer_id', 'order_date'])
orders_sorted['running_total'] = orders_sorted.groupby('customer_id')['amount'].cumsum()
print("\n-- Running Total per Customer --")
print(orders_sorted[['customer_id', 'order_date', 'amount', 'running_total']])

# Q: Month-over-month change in total revenue
monthly_rev = orders.groupby('month_label')['amount'].sum().reset_index()
monthly_rev = monthly_rev.sort_values('month_label')
monthly_rev['prev_month'] = monthly_rev['amount'].shift(1)
monthly_rev['mom_change_pct'] = (
    (monthly_rev['amount'] - monthly_rev['prev_month'])
    / monthly_rev['prev_month'] * 100
).round(2)
print("\n-- MoM Revenue Change --")
print(monthly_rev)
