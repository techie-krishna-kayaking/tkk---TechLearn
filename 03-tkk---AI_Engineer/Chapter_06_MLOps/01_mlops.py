# ============================================================
# CHAPTER 6: MLOps
# Practice in: VS Code / Terminal
# Topics: MLflow tracking, model registry, CI/CD for ML,
#         Docker patterns, drift detection, retraining
# ============================================================

"""
MLOps Maturity Levels (know this framework):

Level 0 — Manual: notebooks, manual training, no versioning
Level 1 — ML Pipeline: automated training, model registry, basic monitoring
Level 2 — CI/CD Pipeline: automated trigger, validation gate, canary deployment
Level 3 — Full Automation: data drift triggers retraining, shadow mode, self-healing

Most companies are Level 1-2. Targeting Level 3 shows senior thinking.
"""

# ============================================================
# SECTION 1: MLflow Experiment Tracking
# ============================================================

"""
# PRODUCTION CODE — run this with: pip install mlflow scikit-learn

import mlflow
import mlflow.sklearn
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, f1_score
import numpy as np

# Set tracking URI (local or remote MLflow server)
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("fraud-detection-v2")

X, y = make_classification(n_samples=5000, n_features=20, weights=[0.95, 0.05], random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# Hyperparameter grid search with MLflow tracking
for n_est in [50, 100, 200]:
    for lr in [0.05, 0.1]:
        with mlflow.start_run(run_name=f"gbm_n{n_est}_lr{lr}"):

            # Log parameters
            mlflow.log_params({
                "n_estimators":  n_est,
                "learning_rate": lr,
                "max_depth":     5,
                "dataset_version": "v1.2.0",
            })

            # Train
            model = GradientBoostingClassifier(
                n_estimators=n_est, learning_rate=lr, max_depth=5, random_state=42
            )
            model.fit(X_train, y_train)
            y_prob = model.predict_proba(X_test)[:, 1]
            y_pred = (y_prob > 0.5).astype(int)

            # Log metrics
            auc = roc_auc_score(y_test, y_prob)
            f1  = f1_score(y_test, y_pred)
            mlflow.log_metrics({"auc_roc": auc, "f1": f1})

            # Log model artifact (auto-logs signature + input example)
            mlflow.sklearn.log_model(
                model, "model",
                input_example=X_train[:5],
                registered_model_name="fraud-detector"
            )

            print(f"  n_est={n_est}, lr={lr}: AUC={auc:.4f}, F1={f1:.4f}")
"""

# ============================================================
# SECTION 2: Model Registry — Lifecycle Management
# ============================================================

"""
# MLflow Model Registry stages:
# None → Staging → Production → Archived

import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()
model_name = "fraud-detector"

# Promote best model to Staging
best_run = client.search_runs(
    experiment_ids=["1"],
    filter_string="",
    order_by=["metrics.auc_roc DESC"],
    max_results=1
)[0]
best_run_id = best_run.info.run_id

# Register and transition
model_version = client.create_model_version(
    name=model_name,
    source=f"runs:/{best_run_id}/model",
    run_id=best_run_id
)
client.transition_model_version_stage(
    name=model_name,
    version=model_version.version,
    stage="Staging",
    archive_existing_versions=False
)
print(f"Model v{model_version.version} promoted to Staging")

# After validation → Production
client.transition_model_version_stage(
    name=model_name, version=model_version.version,
    stage="Production", archive_existing_versions=True  # archives old production
)
"""

# ============================================================
# SECTION 3: Automated Retraining Pipeline
# ============================================================

import numpy as np
from dataclasses import dataclass
from typing import Callable, Optional
import time

@dataclass
class RetrainingConfig:
    """Configuration for automated retraining triggers"""
    psi_threshold:         float = 0.20   # trigger on high drift
    performance_threshold: float = 0.02   # trigger if AUC drops > 2%
    max_model_age_days:    int   = 30     # always retrain after 30 days
    min_new_samples:       int   = 10000  # need enough new data


class AutoRetrainingPipeline:
    """
    Automated ML retraining with drift-based triggers.
    In production: orchestrated by Airflow/Kubeflow/Vertex AI Pipelines.
    """

    def __init__(self, config: RetrainingConfig):
        self.config     = config
        self.base_auc   = 0.92
        self.model_date = time.time() - 15 * 86400  # 15 days old

    def _compute_psi(self, baseline: np.ndarray, current: np.ndarray) -> float:
        bins   = np.percentile(baseline, np.linspace(0, 100, 11))
        bins[0] -= 1e-8; bins[-1] += 1e-8
        b = np.histogram(baseline, bins=bins)[0] / len(baseline) + 1e-8
        c = np.histogram(current,  bins=bins)[0] / len(current)  + 1e-8
        return float(np.sum((b - c) * np.log(b / c)))

    def check_triggers(self, baseline_feats: np.ndarray,
                        current_feats: np.ndarray,
                        current_auc: float,
                        n_new_samples: int) -> dict:
        psi        = self._compute_psi(baseline_feats, current_feats)
        age_days   = (time.time() - self.model_date) / 86400
        perf_drop  = self.base_auc - current_auc

        triggers = {
            'data_drift':   psi        > self.config.psi_threshold,
            'perf_degraded': perf_drop > self.config.performance_threshold,
            'model_stale':  age_days   > self.config.max_model_age_days,
            'enough_data':  n_new_samples >= self.config.min_new_samples,
        }
        trigger_reasons = [k for k, v in triggers.items() if v]
        should_retrain  = any([triggers['data_drift'], triggers['perf_degraded'],
                                triggers['model_stale']]) and triggers['enough_data']

        return {
            'should_retrain': should_retrain,
            'reasons':        trigger_reasons,
            'psi':            round(psi, 4),
            'perf_drop':      round(perf_drop, 4),
            'model_age_days': round(age_days, 1),
            'n_new_samples':  n_new_samples,
        }

    def retrain(self, new_data: dict) -> str:
        """Simulate retraining + validation gate + promotion"""
        print("  [1] Loading training data...")
        print("  [2] Training new model...")
        new_auc = self.base_auc + np.random.uniform(-0.01, 0.03)
        print(f"  [3] Validating: new_auc={new_auc:.4f}, baseline_auc={self.base_auc:.4f}")
        if new_auc >= self.base_auc - 0.005:  # allow 0.5% tolerance
            self.base_auc   = new_auc
            self.model_date = time.time()
            return f"✅ New model deployed (AUC: {new_auc:.4f})"
        else:
            return f"❌ Validation failed — keeping current model"


# Demo
np.random.seed(42)
config   = RetrainingConfig()
pipeline = AutoRetrainingPipeline(config)

baseline = np.random.normal(50, 10, 10000)
drifted  = np.random.normal(68, 15, 15000)  # significant drift

status = pipeline.check_triggers(
    baseline_feats=baseline,
    current_feats=drifted,
    current_auc=0.89,       # dropped from 0.92
    n_new_samples=15000
)
print("=== AUTO-RETRAINING STATUS ===")
for k, v in status.items():
    print(f"  {k}: {v}")

if status['should_retrain']:
    result = pipeline.retrain({})
    print(f"\nRetraining result: {result}")

# ============================================================
# SECTION 4: CI/CD for ML — GitHub Actions Workflow (YAML)
# ============================================================

CICD_YAML = """
# .github/workflows/ml_pipeline.yml
name: ML Pipeline CI/CD

on:
  push:
    paths: ['src/**', 'configs/**']
  schedule:
    - cron: '0 2 * * 1'  # every Monday at 2am — weekly retraining

jobs:
  data_validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate data schema
        run: python src/validate_data.py --config configs/data_schema.yaml
      - name: Check data drift
        run: python src/drift_check.py --psi-threshold 0.20

  train_and_validate:
    needs: data_validation
    runs-on: [self-hosted, gpu]  # use GPU runner for training
    steps:
      - name: Train model
        run: python src/train.py --config configs/model_config.yaml
      - name: Run offline evaluation
        run: python src/evaluate.py --min-auc 0.90 --min-f1 0.75
      - name: Log to MLflow
        run: python src/log_experiment.py

  promote_to_staging:
    needs: train_and_validate
    runs-on: ubuntu-latest
    steps:
      - name: Register model
        run: python src/register_model.py --stage Staging
      - name: Run integration tests
        run: pytest tests/integration/ -v

  deploy_canary:
    needs: promote_to_staging
    environment: production  # requires manual approval
    steps:
      - name: Canary deploy (5% traffic)
        run: kubectl apply -f k8s/canary.yaml
      - name: Monitor canary (30 min)
        run: python src/monitor_canary.py --duration 1800 --max-error-rate 0.01
      - name: Promote to production
        run: kubectl apply -f k8s/production.yaml
"""

print("\n=== CI/CD PIPELINE (GitHub Actions) ===")
print(CICD_YAML)

# ============================================================
# SECTION 5: Docker Pattern for ML Serving
# ============================================================

DOCKERFILE = """
# Dockerfile for ML model serving
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies (layer cached separately for faster rebuilds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY models/ ./models/

# Non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \\
    CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080
CMD ["uvicorn", "src.serve:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
"""

print("=== DOCKERFILE FOR ML SERVING ===")
print(DOCKERFILE)

print("\n✅ Chapter 6: MLOps complete!")
