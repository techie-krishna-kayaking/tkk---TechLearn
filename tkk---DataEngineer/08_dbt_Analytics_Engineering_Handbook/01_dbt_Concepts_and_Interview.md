# 08 — dbt Analytics Engineering Handbook

> dbt (data build tool) has become standard in modern data stacks. It transforms raw data
> in the warehouse using SQL + version control. Increasingly asked at product companies
> and anywhere with a Snowflake/BigQuery/Databricks warehouse.

---

## 🏗️ What is dbt?

**Interview Q:** *"What is dbt and where does it fit in a data pipeline?"*

dbt is the **T in ELT**. It runs inside the warehouse:
```
Raw (S3/sources) → Load (Fivetran/Airbyte/Glue) → dbt Transform → BI (Looker/Tableau)

dbt does NOT:
  ✗ Extract data from sources
  ✗ Load data to the warehouse
  ✓ Transform data already in the warehouse using SQL
  ✓ Test data quality
  ✓ Document tables
  ✓ Manage dependencies between SQL models
```

---

## 📦 Core Concepts

### Models

A model is a `.sql` file that contains a `SELECT` statement. dbt builds it as a table or view.

```sql
-- models/marts/sales/fct_orders.sql

{{ config(
    materialized="table",
    partition_by={"field": "order_date", "data_type": "date"},
    cluster_by=["customer_id"]
) }}

SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    o.total_amount,
    c.country,
    c.customer_tier
FROM {{ ref("stg_orders") }} o
LEFT JOIN {{ ref("dim_customers") }} c ON o.customer_id = c.customer_id
WHERE o.order_date >= '2023-01-01'
```

**`ref()` function** — the key to dbt.
- Resolves the actual table name in the current target schema
- Creates a **dependency graph** (DAG) automatically
- If `dim_customers` fails, `fct_orders` won't run

---

### Materializations

**Interview Q:** *"What materializations does dbt support? When do you use each?"*

| Materialization | What it does | Use When |
|---|---|---|
| `view` | Creates a view (no data stored) | Simple transformations, always fresh |
| `table` | Full table rebuild every run | Medium data, downstream BI needs speed |
| `incremental` | Only inserts NEW/changed rows | Large tables (avoids full rebuild) |
| `ephemeral` | Inline CTE — no DB object created | Intermediate steps not needed as tables |

**Incremental model (most important):**
```sql
-- models/fct_events.sql

{{ config(materialized="incremental", unique_key="event_id") }}

SELECT
    event_id,
    user_id,
    event_type,
    event_date
FROM {{ source("raw", "events") }}

{% if is_incremental() %}
    -- only include new rows when running incrementally
    WHERE event_date > (SELECT MAX(event_date) FROM {{ this }})
{% endif %}
```

- First run: builds the full table
- Subsequent runs: only processes new rows (much faster)
- `unique_key` → UPDATE existing rows if they match (merge/upsert)
- `{{ this }}` → refers to the current model's table in the DB

---

### Sources

**Interview Q:** *"What is a source in dbt? Why not just use the table name directly?"*

Sources declare raw tables you don't own (loaded by Fivetran, Glue, etc.):

```yaml
# models/sources.yml

version: 2

sources:
  - name: raw_data
    database: analytics          # database / project
    schema: raw                  # schema in warehouse
    tables:
      - name: orders
        description: "Raw orders from transactional DB"
        freshness:
          warn_after: {count: 12, period: hour}    # warn if data is 12h+ old
          error_after: {count: 24, period: hour}   # fail if 24h+ old
        columns:
          - name: order_id
            tests:
              - unique
              - not_null

  - name: stripe
    schema: stripe_raw
    tables:
      - name: payments
```

**Use in models:**
```sql
SELECT * FROM {{ source("raw_data", "orders") }}  -- resolves to analytics.raw.orders
```

Benefits vs hardcoding table names:
- Schema changes in one place (the YAML)
- `dbt source freshness` checks when data was last loaded
- Tests run on source tables too

---

### Tests

**Interview Q:** *"How do you implement data quality in dbt?"*

**Generic tests** (built-in, configured in YAML):
```yaml
# models/schema.yml

models:
  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref("dim_customers")
              field: customer_id      # referential integrity check
      - name: order_status
        tests:
          - accepted_values:
              values: ["pending", "processing", "shipped", "cancelled"]
```

**Singular tests** (custom SQL files in `tests/` folder):
```sql
-- tests/no_negative_amounts.sql
-- Fails if any rows returned (dbt expects 0 rows for a passing test)

SELECT order_id, total_amount
FROM {{ ref("fct_orders") }}
WHERE total_amount < 0
```

**dbt-expectations** (like Great Expectations for dbt):
```yaml
- name: total_amount
  tests:
    - dbt_expectations.expect_column_values_to_be_between:
        min_value: 0
        max_value: 100000
    - dbt_expectations.expect_column_median_to_be_between:
        min_value: 50
        max_value: 500
```

---

### Macros (Jinja Templating)

**Interview Q:** *"What are macros in dbt? Give an example."*

Macros are reusable SQL snippets written in Jinja:

```sql
-- macros/cents_to_dollars.sql

{% macro cents_to_dollars(column_name, scale=2) %}
    ROUND({{ column_name }} / 100, {{ scale }})
{% endmacro %}
```

Used in models:
```sql
SELECT
    order_id,
    {{ cents_to_dollars("amount_cents") }} AS amount_usd
FROM {{ ref("stg_payments") }}
```

**Built-in macros:**
```sql
{{ dbt_utils.date_spine(
    datepart="day",
    start_date="cast('2023-01-01' as date)",
    end_date="current_date"
) }}

{{ dbt_utils.surrogate_key(["order_id", "product_id"]) }}   -- hash key
{{ dbt_utils.pivot("status", ["pending","shipped","cancelled"], agg="count") }}
```

---

### Seeds

CSV files in the `seeds/` folder that dbt loads as tables in the warehouse.

```
seeds/
  country_codes.csv    → dbt seed → warehouse.analytics.country_codes
  product_categories.csv
```

Use for: lookup tables, configuration data, test fixtures.

---

### Snapshots (SCD Type 2)

**Interview Q:** *"How does dbt handle slowly changing dimensions (SCD Type 2)?"*

```sql
-- snapshots/scd_customers.sql

{% snapshot scd_customers %}

{{
    config(
        target_schema="snapshots",
        unique_key="customer_id",
        strategy="timestamp",       # or "check" (for no updated_at column)
        updated_at="updated_at",
    )
}}

SELECT * FROM {{ source("raw", "customers") }}

{% endsnapshot %}
```

dbt adds `dbt_sdc_id`, `dbt_valid_from`, `dbt_valid_to` columns automatically.
Running `dbt snapshot` creates new rows for changed records, closes old rows.

---

### Project Structure (Best Practice)

```
dbt_project/
├── models/
│   ├── staging/          # 1-to-1 with sources, light cleaning, prefix stg_
│   │   ├── stg_orders.sql
│   │   └── stg_customers.sql
│   ├── intermediate/     # business logic, joins (prefix int_)
│   │   └── int_orders_with_customers.sql
│   └── marts/            # final tables for BI consumers
│       ├── sales/
│       │   ├── fct_orders.sql
│       │   └── dim_customers.sql
│       └── finance/
├── seeds/                # static CSV data
├── snapshots/            # SCD Type 2
├── macros/               # reusable SQL snippets
├── tests/                # singular tests (custom SQL)
├── analyses/             # ad-hoc SQL (not compiled to models)
└── dbt_project.yml       # project-level configuration
```

---

## ❓ Top 10 dbt Interview Questions

**Q1: What is the dbt DAG?**
dbt automatically builds a DAG from `ref()` and `source()` dependencies. `dbt run` executes models in topological order. `dbt docs generate` creates a visual lineage graph.

**Q2: How do you run only specific models?**
```bash
dbt run --select fct_orders                   # one model
dbt run --select marts.sales                  # all in a folder
dbt run --select +fct_orders                  # fct_orders and all its ancestors
dbt run --select fct_orders+                  # fct_orders and all its descendants
dbt run --select stg_orders+ --exclude dim_c  # stg_orders+ minus dim_customers
```

**Q3: Incremental vs table materialization — when to switch?**
Start with `view` → if too slow for BI, switch to `table` → if rebuilds take too long (>30 min or data > few hundred GB), switch to `incremental`.

**Q4: How does dbt handle schema changes on incremental models?**
By default, new columns in your SELECT that don't exist in the target table cause an error. Use `on_schema_change='append_new_columns'` to auto-add them, or `sync_all_columns` to add/remove.

**Q5: What is `dbt test` and when does it run?**
`dbt test` runs after `dbt run`. Tests query the data in built models. Failures can be configured to `warn` (continue) or `error` (stop). In CI/CD, tests gate the deployment.

**Q6: How do you document models in dbt?**
Add `description:` in the YAML schema files. `dbt docs generate` creates a static website. `dbt docs serve` opens it in the browser. The docs site shows lineage, column descriptions, test coverage.

**Q7: What is a package in dbt and name three common ones?**
Packages are reusable dbt projects installed via `packages.yml`:
- `dbt-utils` — helper macros (date_spine, surrogate_key, pivot)
- `dbt-expectations` — data quality assertions
- `dbt-audit-helper` — compare two models row-by-row (useful for migrations)

**Q8: What happens when you run `dbt run` in production?**
The scheduler (Airflow, dbt Cloud, GitHub Actions) calls `dbt run`. dbt compiles Jinja → SQL, resolves refs to actual table names, and executes SQL in the warehouse in dependency order. Results (pass/fail) are reported to the metadata layer.

**Q9: How do you implement column-level lineage tracking in dbt?**
dbt's built-in lineage shows model-level dependencies. Column-level lineage requires dbt Cloud's "column-level lineage" feature (paid) or tools like OpenLineage/Marquez integrated via `dbt-openlineage` package.

**Q10: How do you handle sensitive data (PII) in dbt models?**
Tag columns as PII in the YAML (`meta: {pii: true}`). Use masking policies in the warehouse (Snowflake row/column access policies, BigQuery column-level security). dbt can reference these policies via `post-hook`. Limit who can access marts with PII via warehouse RBAC.
