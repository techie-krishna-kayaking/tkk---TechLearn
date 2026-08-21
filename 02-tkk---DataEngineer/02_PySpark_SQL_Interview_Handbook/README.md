# PySpark SQL vs DataFrame API — Interview Handbook

> The most comprehensive, executable, side-by-side reference for **Spark SQL** and the
> **PySpark DataFrame API**. Built for Data Engineering, Spark, Databricks, Azure/AWS/GCP
> Data Engineer, ETL Developer, and Big Data interviews.

Every single concept in this handbook is shown **twice**:

1. **Spark SQL** (`spark.sql("""...""")`)
2. **Equivalent DataFrame API** (`df.select(...)`, `df.filter(...)`, ...)

This dual approach is exactly what interviewers probe for — "can you do this in *both* SQL
and the DataFrame API?" — and it is how real production codebases are written.

---

## Why this handbook exists

In interviews and on the job you constantly translate between SQL and the DataFrame API.
Most learning resources pick one. This one gives you **both, for every operation**, with:

- Clean, PEP8, heavily commented, **fully executable** code
- The **same datasets** across every file so you can focus on the concept, not the data
- Notes on **interview relevance**, **performance implications**, **common mistakes**, and
  **best practices**

---

## Repository structure

```
PySpark_SQL_vs_DataFrame_API_Interview_Handbook/
│
├── README.md
│
├── datasets/
│      df.csv          # main activity/fitness dataset (has nulls, dates, pipe-delimited tags)
│      df1.csv         # second dataset for union / set operations
│      cust.csv        # customers (for joins)
│      prod.csv        # products / orders (for joins)
│
├── 01_Basics.py                        # Reading, schema, select, sort, filter, columns
├── 02_Filtering_and_String_Functions.py# String & null-handling functions
├── 03_Aggregations_and_GroupBy.py      # sum/avg/count, pivot, cube, rollup, set ops
├── 04_Window_Functions.py              # row_number, rank, lead/lag, running totals
├── 05_Joins.py                         # inner/left/right/full/semi/anti/cross/broadcast
├── 06_Date_and_Time_Functions.py       # date_add, datediff, date_format, extraction
├── 07_Array_Map_Struct.py              # arrays, maps, structs, explode, higher-order
├── 08_DataFrame_Operations.py          # cache, persist, repartition, coalesce, transform
├── 09_File_Formats.py                  # CSV/JSON/Parquet/ORC/Delta, partitioning, bucketing
├── 10_Performance_Optimization.py      # AQE, skew/salting, broadcast, explain plans
├── 11_Advanced_PySpark.py              # UDF, Pandas UDF, RDD, broadcast vars, accumulators
└── 12_Interview_Questions.py           # 150+ Q&A with SQL + PySpark + best practices
```

---

## Prerequisites

- Python 3.8+
- Java 8 / 11 / 17 (required by Spark)
- PySpark

```bash
# Recommended: create a virtual environment first
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate

pip install pyspark
# Optional (only needed for the Delta Lake and Pandas UDF examples):
pip install delta-spark pandas pyarrow
```

> The Delta examples auto-detect whether `delta-spark` is installed and skip gracefully if
> it is not, so the files always run.

---

## How to run

Each file is standalone: it creates its own `SparkSession`, loads the shared datasets, and
prints results. Run any file directly:

```bash
python 01_Basics.py
python 04_Window_Functions.py
python 12_Interview_Questions.py
```

The dataset path is resolved **relative to the script's own location**, so the files run
correctly no matter what directory you launch them from.

---

## The datasets at a glance

### `df.csv` (main)
| column        | type   | notes                                            |
|---------------|--------|--------------------------------------------------|
| id            | int    | primary key                                      |
| name          | string | person name (has duplicates for grouping)        |
| category      | string | `Exercise`, `Diet`, `Sleep`                       |
| activity      | string | e.g. `Running`, `Cycling`                         |
| calories      | int    | **contains NULLs** (great for null handling)      |
| duration_min  | int    | minutes                                           |
| activity_date | string | `yyyy-MM-dd` (cast to date in examples)           |
| city          | string | `New York`, `Chicago`, `Boston`, `Seattle`, ...   |
| tags          | string | **pipe-delimited** (`cardio|outdoor`) for `split` |

### `df1.csv`
Same schema as `df.csv`, used to demonstrate `union`, `intersect`, `except`.

### `cust.csv`
`cust_id, cust_name, city, age, signup_date` — customers.

### `prod.csv`
`order_id, cust_id, product, category, amount, order_date` — orders/products.

> `cust.csv` and `prod.csv` intentionally contain non-matching keys (a customer with no
> orders, an order with no customer) so left/right/full/anti joins produce visible results.

---

## Learning path (Beginner → Senior)

1. **Beginner:** `01` → `02` → `03`
2. **Intermediate:** `04` → `05` → `06` → `07`
3. **Advanced:** `08` → `09`
4. **Senior / Architect:** `10` → `11`
5. **Interview prep:** `12` (revise everything as Q&A)

---

## Conventions used in the code

- Every concept is introduced with a banner comment:

  ```python
  ###########################################################
  # WHERE / filter
  ###########################################################
  ```

- **Spark SQL is always shown first**, then the **DataFrame API** equivalent.
- Comments explain *what* the code does, *why* it matters in interviews, its *performance*
  implications, *common mistakes*, and *best practices*.

Happy learning — and good luck in your interviews!
