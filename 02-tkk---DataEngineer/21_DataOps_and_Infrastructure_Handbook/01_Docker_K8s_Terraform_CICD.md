# 21 — DataOps & Infrastructure (Docker · Kubernetes · Terraform · CI/CD)

> The gap between a "data engineer" and a **staff/principal** DE is often *operational
> maturity*: containerize, deploy, automate, and make infra reproducible. Product companies
> at 80–120 LPA expect you to ship pipelines like software. This is effectively absent from
> most DE prep — master it and you stand out.

---

## 🎯 SECTION 1: What DataOps Means

DataOps = DevOps applied to data: **version control + CI/CD + testing + IaC + monitoring**
for data pipelines. Principles: everything in git, automated tests, reproducible
environments, fast/safe deploys, observability (Handbook 20).

**Interview line:** *"I treat pipelines as software: code-reviewed, tested in CI,
containerized, deployed via IaC, and monitored. A pipeline change should be as safe and
auditable as an app deploy."*

---

## 🐳 SECTION 2: Docker (containers)

**Why:** "works on my machine" → reproducible everywhere. Package Spark/Airflow/dbt jobs
with exact dependencies.

```dockerfile
# Multi-stage build for a lean, cache-friendly Python job image
FROM python:3.11-slim AS base
WORKDIR /app
# 1) deps layer (changes rarely → cached)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# 2) code layer (changes often)
COPY src/ ./src/
ENV PYTHONUNBUFFERED=1
USER 1000                        # don't run as root (security)
ENTRYPOINT ["python", "-m", "src.pipeline"]
```

**Key concepts to speak to:**
- **Image vs container**: image = template; container = running instance.
- **Layer caching**: order Dockerfile from least→most frequently changing (deps before code).
- **Multi-stage builds**: compile/build in one stage, copy only artifacts → small image.
- **Slim/distroless base**, non-root user, pinned versions, `.dockerignore`.
- **Volumes** for data, **env vars/secrets** for config (never bake secrets into images).

---

## ☸️ SECTION 3: Kubernetes (orchestrating containers)

**Why DE cares:** Spark-on-K8s, Airflow **KubernetesPodOperator**, Flink-on-K8s, and
autoscaling batch jobs. K8s gives isolation, elastic scaling, and self-healing.

**Core objects:**
| Object | Purpose |
|---|---|
| **Pod** | Smallest unit; one or more containers |
| **Deployment** | Declarative replicas for stateless services |
| **StatefulSet** | Stable identity/storage (Kafka, databases) |
| **Job / CronJob** | Run-to-completion batch / scheduled batch |
| **Service** | Stable network endpoint / load balancing |
| **ConfigMap / Secret** | Config and credentials injection |
| **PVC** | Persistent storage claim |
| **HPA** | Horizontal Pod Autoscaler (scale on CPU/custom metrics) |

```yaml
# A daily Spark-submit style batch job as a CronJob
apiVersion: batch/v1
kind: CronJob
metadata: { name: daily-etl }
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: Never
          containers:
            - name: etl
              image: registry/etl:1.4.2
              resources:
                requests: { cpu: "1", memory: "2Gi" }
                limits:   { cpu: "2", memory: "4Gi" }
              envFrom:
                - secretRef: { name: warehouse-creds }
```

**Talking points:** requests vs limits (scheduling vs OOM-kill), liveness/readiness
probes, namespaces for env isolation, node selectors/taints for GPU/spot nodes,
**Spark on K8s** (driver pod + executor pods) vs YARN, and **KEDA** for event-driven
autoscaling (e.g. scale consumers on Kafka lag).

---

## 🏗️ SECTION 4: Terraform (Infrastructure as Code)

**Why:** click-ops in a cloud console is not reproducible or reviewable. Terraform
declares infra (S3, Glue, EMR, MSK, IAM, Redshift) in versioned code.

```hcl
resource "aws_s3_bucket" "lake" {
  bucket = "acme-datalake-prod"
}

resource "aws_s3_bucket_lifecycle_configuration" "lake" {
  bucket = aws_s3_bucket.lake.id
  rule {
    id     = "archive-old"
    status = "Enabled"
    transition { days = 90  storage_class = "GLACIER" }   # cost optimization
    expiration { days = 2555 }                             # 7-yr retention
  }
}

resource "aws_glue_catalog_database" "analytics" {
  name = "analytics"
}
```

**Core concepts:**
- **Declarative + idempotent**: `plan` (preview diff) → `apply` (converge to desired state).
- **State file** (`terraform.tfstate`): source of truth of what exists; store **remote**
  (S3 + DynamoDB lock) so teams don't clobber each other. **Never commit state/secrets.**
- **Modules** for reuse (a reusable "data-lake" or "airflow" module across envs).
- **Workspaces / var files** for dev/stage/prod parity.
- **Drift**: when someone changes infra manually; `plan` detects it.

**Interview line:** *"Infra is code: peer-reviewed, versioned, and reproducible. Spinning
up an identical staging environment is a `terraform apply`, not a two-day ticket."*

---

## 🔄 SECTION 5: CI/CD for Data Pipelines

**CI (on every PR):**
```yaml
# .github/workflows/ci.yml (sketch)
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: ruff check . && black --check .        # lint/format
      - run: pytest tests/ --cov=src                 # unit tests
      - run: dbt build --select state:modified+ --target ci  # only changed models + downstream
      - run: great_expectations checkpoint run nightly       # data tests on sample
```

**CD (on merge to main):**
- Build & scan the Docker image → push to registry (ECR/GCR).
- `terraform apply` gated infra changes.
- Deploy DAGs/jobs (Airflow, Databricks, K8s) with **blue-green / canary** where possible.
- **Environments:** dev → staging → prod parity; **secrets** from a vault (AWS Secrets
  Manager / Vault), never in git.

**Testing pyramid for pipelines:**
1. **Unit** — transformation logic on tiny fixtures (fast, many).
2. **Data/contract tests** — dbt/GE assertions on schema & values.
3. **Integration** — run the DAG end-to-end against a staging warehouse on sample data.
4. **Regression** — snapshot expected outputs; diff on change.

**Deployment safety for data:** backfill strategy, **idempotent + rerunnable** jobs,
**blue-green tables** (write to `table_new`, atomically swap), feature-flag risky logic,
and easy rollback (time travel — Handbook 19).

---

## 🔀 SECTION 6: Environments, Secrets & Config

- **Env parity**: same code, different config/secrets per env (12-factor).
- **Secrets**: AWS Secrets Manager, HashiCorp Vault, K8s Secrets (sealed), or SSM — never
  hardcoded, never in images, never in git. Rotate regularly.
- **Config**: env vars / config files per env; keep infra + app config in code.

---

## ❓ SECTION 7: Rapid-Fire Q&A

**Q: Image vs container?** Image = immutable template; container = a running instance of it.

**Q: Why multi-stage Docker builds?** Build/compile in one stage, ship only artifacts →
smaller, more secure images, faster pulls.

**Q: requests vs limits in K8s?** requests = guaranteed/scheduled amount; limits = hard cap
(exceed memory → OOM-killed). Set both to protect the node.

**Q: What's in the Terraform state and why remote?** The mapping of config → real
resources; remote + locking prevents concurrent corruption and enables team collaboration.

**Q: How do you deploy a pipeline change safely?** CI tests (unit + data + integration) →
build/scan image → gated `terraform apply` → blue-green/canary deploy → monitor → rollback
via time travel or previous image if metrics degrade.

**Q: How do you make a job idempotent?** Deterministic outputs, MERGE/upsert on keys,
overwrite partition by run date, and dedupe — so a rerun/backfill can't double-write.

**Q: Spark on K8s vs YARN?** K8s gives container isolation, cloud-native autoscaling, and a
single orchestrator for all workloads; YARN is Hadoop-native. Most greenfield stacks pick
K8s or serverless (EMR Serverless/Databricks).

**Q: How do you autoscale consumers on load?** HPA on CPU/custom metrics, or **KEDA** on
Kafka consumer lag, so throughput scales with the backlog.

---

## ✅ Mastery Checklist
- [ ] Write a lean multi-stage Dockerfile from memory
- [ ] Explain core K8s objects + requests/limits/probes; Spark-on-K8s
- [ ] Explain Terraform plan/apply, remote state + locking, modules, drift
- [ ] Design a CI/CD pipeline with unit + data + integration tests
- [ ] Describe blue-green/canary + idempotent backfills + rollback
- [ ] Handle secrets/config with env parity and a vault

---

## 🧪 Hands-On Practice (runnable)

A complete tiny DataOps project lives in [`sample_pipeline_project/`](./sample_pipeline_project)
(walkthrough in `02_Hands_On_Sample_Project.md`): pure-function transform, unit +
data-quality tests, multi-stage Dockerfile, docker-compose, Terraform (S3 lifecycle +
Glue), a GitHub Actions CI pipeline, and a Makefile.

```bash
cd sample_pipeline_project
pip install -r requirements.txt
python -m pipeline.transform     # run the transform on sample data
pytest -q                        # 11 unit + data-quality tests (all green)
# make build && make docker-run  # containerized run (needs Docker)
# cd terraform && terraform init && terraform plan   # preview infra (needs Terraform)
```
