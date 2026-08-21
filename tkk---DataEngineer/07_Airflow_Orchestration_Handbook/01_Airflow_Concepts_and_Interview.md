# 07 — Airflow & Orchestration Handbook
# Comprehensive Guide + Interview Q&A

> Airflow is the most widely used data pipeline orchestrator. Every data engineering
> role that isn't fully on Databricks Workflows or cloud-native (Step Functions, ADF)
> will ask Airflow questions. Know it well.

---

## 🏗️ Airflow Architecture

```
Webserver      → UI for monitoring, triggering, viewing DAGs and logs
Scheduler      → parses DAGs, creates DAG runs, queues task instances
Executor       → runs tasks (LocalExecutor, CeleryExecutor, KubernetesExecutor)
Workers        → processes that actually execute the tasks (for Celery/K8s)
Metadata DB    → stores DAG state, task instances, logs (PostgreSQL recommended)
DAG Bag        → folder of .py files the scheduler parses (~/airflow/dags/)
```

---

## 📊 Core Concepts

### DAG (Directed Acyclic Graph)

**Interview Q:** *"What is a DAG in Airflow?"*

A DAG is a Python object that defines:
- The **tasks** in your pipeline
- The **dependencies** between tasks (A must complete before B starts)
- **Schedule** (how often to run)
- **Configuration** (start_date, retries, timeout)

"Directed" = has direction (A→B). "Acyclic" = no cycles (no A→B→A).

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "data-team",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email": ["alerts@company.com"],
}

with DAG(
    dag_id="sales_pipeline",
    default_args=default_args,
    schedule_interval="0 6 * * *",    # daily at 6 AM (cron)
    start_date=datetime(2024, 1, 1),  # when backfilling starts from
    catchup=False,                    # don't backfill past runs
    tags=["sales", "production"],
    max_active_runs=1,                # only one run at a time
) as dag:
    pass
```

---

### Tasks & Operators

**Interview Q:** *"What is the difference between a Task and an Operator?"*

- **Operator** = a class that defines WHAT to do (BashOperator, PythonOperator, SparkSubmitOperator)
- **Task** = an INSTANCE of an operator with a specific `task_id`
- **Task Instance** = a specific run of a task on a specific date

**Most common operators:**
```python
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator     # placeholder (was DummyOperator)
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

extract = PythonOperator(
    task_id="extract_data",
    python_callable=my_extract_function,
    op_kwargs={"source": "s3://bucket/data/"},
)

transform = BashOperator(
    task_id="run_dbt",
    bash_command="dbt run --models sales_mart",
)

load = DatabricksRunNowOperator(
    task_id="run_notebook",
    job_id=12345,   # Databricks job ID
)

# Task dependency syntax
extract >> transform >> load       # sequential
extract >> [transform, load]       # fan-out
[extract, validate] >> transform   # fan-in
```

---

### Schedule Interval (Cron)

**Interview Q:** *"How do you schedule a DAG in Airflow? What is cron?"*

```python
# Cron format: minute  hour  day  month  weekday
schedule_interval = "0 6 * * *"     # daily at 6:00 AM
schedule_interval = "0 */4 * * *"   # every 4 hours
schedule_interval = "0 0 * * MON"   # every Monday at midnight
schedule_interval = "0 0 1 * *"     # 1st of every month

# Airflow presets (shortcuts)
"@daily"    # = "0 0 * * *"
"@hourly"   # = "0 * * * *"
"@weekly"   # = "0 0 * * 0"
"@monthly"  # = "0 0 1 * *"
"@once"     # run once only
None        # manual trigger only
```

**Dataset-driven scheduling (Airflow 2.4+):**
```python
# Trigger DAG B when DAG A produces a dataset
from airflow.datasets import Dataset

my_dataset = Dataset("s3://bucket/processed/sales/")

# DAG A: marks dataset as updated
with DAG("producer_dag", schedule="@daily") as dag:
    task = PythonOperator(
        task_id="update_data",
        python_callable=process_sales,
        outlets=[my_dataset],   # signals: this task updates the dataset
    )

# DAG B: runs when the dataset is updated
with DAG("consumer_dag", schedule=[my_dataset]) as dag:
    task = PythonOperator(task_id="use_data", python_callable=train_model)
```

---

### XCom (Cross-Communication Between Tasks)

**Interview Q:** *"How do tasks share data in Airflow?"*

XCom (Cross-Communication) lets tasks push and pull small values (metadata, file paths, counts).

```python
def extract(**context):
    file_path = "s3://bucket/data/2024-01-01.parquet"
    # Push value to XCom
    context["ti"].xcom_push(key="file_path", value=file_path)
    return file_path   # returning also pushes to XCom with key="return_value"

def transform(**context):
    # Pull value from upstream task
    file_path = context["ti"].xcom_pull(task_ids="extract", key="file_path")
    print(f"Transforming {file_path}")

extract_task = PythonOperator(task_id="extract", python_callable=extract)
transform_task = PythonOperator(task_id="transform", python_callable=transform)
extract_task >> transform_task
```

**⚠️ INTERVIEW TRAP:** XCom is stored in the Airflow metadata DB. It's for small data only
(row counts, file paths, status flags). NEVER pass large DataFrames through XCom.
For large data, write to S3/ADLS and pass the path.

---

### Sensors

**Interview Q:** *"What is a Sensor in Airflow? When would you use one?"*

A Sensor is a special operator that **waits** for a condition to be true before proceeding.

```python
from airflow.sensors.filesystem import FileSensor
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.sensors.external_task import ExternalTaskSensor

# Wait for a file to appear in S3
wait_for_data = S3KeySensor(
    task_id="wait_for_s3_file",
    bucket_name="my-bucket",
    bucket_key="data/{{ ds }}/sales.csv",  # {{ ds }} = execution date
    poke_interval=60,    # check every 60 seconds
    timeout=3600,        # fail if not found within 1 hour
    mode="reschedule",   # release the worker slot while waiting (preferred)
)

# Wait for another DAG to complete
wait_for_upstream = ExternalTaskSensor(
    task_id="wait_for_ingestion",
    external_dag_id="raw_ingestion_dag",
    external_task_id="final_task",
    execution_delta=timedelta(hours=1),
)
```

**Sensor mode:**
- `poke` → worker holds the slot the entire time (wastes resources for long waits)
- `reschedule` → worker releases slot between checks (preferred for long waits)

---

### TaskGroup (Organising Tasks)

**Interview Q:** *"How do you organise a large DAG with many tasks?"*

```python
from airflow.utils.task_group import TaskGroup

with DAG("large_pipeline") as dag:
    with TaskGroup("ingest") as ingest_group:
        t1 = PythonOperator(task_id="extract_orders",   ...)
        t2 = PythonOperator(task_id="extract_products", ...)

    with TaskGroup("transform") as transform_group:
        t3 = PythonOperator(task_id="clean_orders",     ...)
        t4 = PythonOperator(task_id="join_products",    ...)

    with TaskGroup("load") as load_group:
        t5 = PythonOperator(task_id="write_warehouse",  ...)

    ingest_group >> transform_group >> load_group
```

---

### Backfill & Catchup

**Interview Q:** *"What is backfilling in Airflow? When is catchup=True dangerous?"*

- **Catchup = True** (default): If you create a DAG with `start_date` in the past,
  Airflow will run a DAG run for every missed schedule interval since `start_date`.
  For a daily DAG with `start_date` 1 year ago → 365 DAG runs fire at once!

- **Best practice:** Set `catchup=False` in production unless you explicitly need historical runs.
  Use `airflow dags backfill` CLI command to manually trigger specific date ranges.

```bash
# Manually backfill a range
airflow dags backfill sales_pipeline --start-date 2024-01-01 --end-date 2024-01-31
```

---

### Variables & Connections

**Interview Q:** *"How do you manage configuration and secrets in Airflow?"*

```python
from airflow.models import Variable
from airflow.hooks.base import BaseHook

# Variables (stored in metadata DB, encrypted optionally)
bucket_name = Variable.get("s3_bucket_name")
config = Variable.get("pipeline_config", deserialize_json=True)

# Connections (stored in metadata DB, encrypted credentials)
conn = BaseHook.get_connection("my_postgres_db")
# conn.host, conn.login, conn.password, conn.schema

# Best practice: use Airflow Connections for credentials, not hard-coded strings.
# For production secrets: integrate with AWS Secrets Manager / HashiCorp Vault.
```

---

### Dynamic DAGs & Dynamic Task Mapping (Airflow 2.3+)

**Interview Q:** *"How do you create tasks dynamically in Airflow?"*

```python
# Dynamic task mapping (Airflow 2.3+) — creates one task per element
from airflow.decorators import task

@task
def process_file(file_path: str):
    print(f"Processing {file_path}")

@task
def get_files():
    return ["s3://bucket/file1.csv", "s3://bucket/file2.csv", "s3://bucket/file3.csv"]

with DAG("dynamic_tasks") as dag:
    files = get_files()
    process_file.expand(file_path=files)   # creates 3 parallel tasks at runtime
```

---

## ❓ Top 15 Airflow Interview Questions

**Q1: What is the Airflow scheduler doing at all times?**
Parsing DAG files, creating DagRun objects for scheduled intervals, queuing TaskInstances whose dependencies are met, and updating task states.

**Q2: What is the difference between execution_date and run_id?**
`execution_date` (now called `data_interval_start`) is the START of the data interval the DAG is processing, not the time it actually ran. A DAG scheduled `@daily` with `start_date=2024-01-01` runs on 2024-01-02 but processes data for 2024-01-01.

**Q3: What are the task states in Airflow?**
`scheduled → queued → running → success / failed / skipped / up_for_retry / upstream_failed`

**Q4: How do you trigger a DAG from another DAG?**
Use `TriggerDagRunOperator`. For simple dependencies, prefer `ExternalTaskSensor` (waits for completion) or Dataset scheduling (event-driven).

**Q5: What is a Hook in Airflow?**
A Hook is a low-level interface to an external system (S3Hook, PostgresHook, HttpHook). Operators use Hooks internally. You use Hooks when writing custom operators.

**Q6: How do you handle secrets in production Airflow?**
Use Airflow's Secrets Backend: integrate with AWS Secrets Manager, HashiCorp Vault, or GCP Secret Manager. Never store real credentials in Variables directly.

**Q7: LocalExecutor vs CeleryExecutor vs KubernetesExecutor?**
- LocalExecutor: runs tasks as subprocesses on the scheduler machine. Good for small setups.
- CeleryExecutor: tasks run on worker machines (Redis/RabbitMQ as message broker). Scales horizontally.
- KubernetesExecutor: each task runs in its own ephemeral K8s pod. Best isolation and auto-scaling.

**Q8: What is a Pool in Airflow?**
A named resource limit on parallel task execution. E.g., a database connection Pool with 10 slots ensures no more than 10 tasks hit the DB simultaneously. Assign tasks to a pool: `PythonOperator(pool="db_pool", pool_slots=1)`.

**Q9: What is SLA in Airflow?**
Service Level Agreement — expected maximum duration for a task/DAG. If a task exceeds its SLA, Airflow sends an alert. Defined as: `sla=timedelta(hours=2)` on a task.

**Q10: How do you handle a failed task with retries?**
Set `retries=3` and `retry_delay=timedelta(minutes=5)` in default_args or on the task directly. Airflow will automatically retry the task up to 3 times before marking it failed.

**Q11: What is a SubDAG? Why is it now discouraged?**
SubDAGs allowed nesting a DAG inside a task. Discouraged because they cause deadlocks (SubDAG task holds a slot while its children need slots). Use `TaskGroup` instead — same visual grouping, no slot issues.

**Q12: How do you debug a failing Airflow task in production?**
1. Check task log in UI (Task Instance → Log)
2. Click "Clear" to rerun just that task
3. Use `airflow tasks test dag_id task_id execution_date` locally to run without the scheduler
4. Check XCom values if data-dependent
5. Use `airflow tasks render` to see rendered template values

**Q13: What are Jinja templates in Airflow?**
Airflow renders `{{ }}` expressions in string parameters using Jinja templating.
```python
bash_command="echo {{ ds }} {{ execution_date }}"
# ds = execution date as YYYY-MM-DD string
# execution_date = full datetime object
# macros.ds_add(ds, 7) = ds + 7 days
```

**Q14: How do you pass parameters to a DAG run?**
Trigger via UI/API with a JSON `conf` dict:
```python
def my_task(**context):
    run_config = context["dag_run"].conf
    table = run_config.get("table", "default_table")
```

**Q15: What is Airflow 2.0's TaskFlow API?**
The `@task` decorator wraps a Python function as a task. Return value is automatically XCom-pushed. Arguments from upstream `@task` are automatically XCom-pulled.
```python
@task
def extract() -> dict:
    return {"rows": 1000, "path": "s3://..."}

@task
def transform(data: dict):
    print(data["rows"])   # no explicit xcom_pull needed

with DAG("taskflow") as dag:
    transform(extract())  # Python-native dependency expression
```
