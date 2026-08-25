# 21 — Hands-On: Sample DataOps Project

A tiny but **real** end-to-end DataOps project you can run and read. It shows how a
data pipeline is shipped like software: transformation code, **unit + data-quality
tests**, containerization, IaC, and CI.

```
sample_pipeline_project/
├── pipeline/
│   ├── __init__.py
│   └── transform.py          # the ETL transform logic (pure, testable)
├── tests/
│   ├── test_transform.py     # unit tests
│   └── test_data_quality.py  # data-quality / contract tests
├── Dockerfile                # multi-stage, non-root image
├── docker-compose.yml        # local run + Postgres dependency
├── Makefile                  # one-word commands (lint/test/build/run)
├── requirements.txt
├── terraform/
│   └── main.tf               # S3 lake bucket + lifecycle + Glue DB (IaC)
└── .github/workflows/
    └── ci.yml                # lint -> unit tests -> data tests -> build
```

## Run it locally (no Docker needed for the tests)
```bash
cd sample_pipeline_project
pip install -r requirements.txt
make test          # runs unit + data-quality tests with pytest
python -m pipeline.transform    # runs the transform on sample data
```

## Run it containerized
```bash
make build         # docker build
make run           # docker run the pipeline
docker compose up  # pipeline + Postgres together
```

## Provision infra (dry run — no cloud account needed to read the plan)
```bash
cd terraform
terraform init
terraform plan     # preview the S3 bucket + lifecycle + Glue DB it would create
```

## What each piece teaches (interview talking points)
- **`transform.py`** — pure functions → trivially unit-testable; no hidden I/O in logic.
- **`test_data_quality.py`** — schema/null/range/uniqueness assertions that would gate a
  publish in CI (shift-left, Handbook 20).
- **Dockerfile** — multi-stage build, pinned deps, **non-root user**, slim base.
- **Terraform** — S3 lifecycle (hot→Glacier) = cost optimization as code (Handbook 14).
- **ci.yml** — lint → unit → data tests → build image; nothing merges unless green.
- **Makefile** — the "paved road": one command per task so the whole team is consistent.
