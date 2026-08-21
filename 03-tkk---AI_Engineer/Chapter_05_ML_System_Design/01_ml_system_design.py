# ============================================================
# CHAPTER 5: ML SYSTEM DESIGN
# Practice in: VS Code (architecture + code patterns)
# Topics: Feature stores, model serving, A/B testing,
#         monitoring, recommendation system design
# The #1 differentiator at senior AI engineer interviews
# ============================================================

"""
ML System Design Interview Framework (always follow this):

1. REQUIREMENTS (2-3 min)
   - Functional: what the system does
   - Non-functional: latency, throughput, accuracy, freshness

2. DATA (5 min)
   - What data do we have?
   - Volume, velocity, schema
   - Labels: available, delayed, proxy?

3. FEATURE ENGINEERING (5 min)
   - User features, item features, context features
   - Training vs serving consistency (training-serving skew!)

4. MODEL CHOICE (5 min)
   - Simplest model first, justify complexity
   - Offline vs online learning

5. TRAINING PIPELINE (5 min)
   - Data pipeline, training triggers, validation gate

6. SERVING ARCHITECTURE (10 min)
   - Latency budget, caching, batching, hardware

7. MONITORING (5 min)
   - Data drift, prediction drift, business metrics

8. FAILURE MODES (3 min)
   - Cold start, data outages, model degradation
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import time
import hashlib

# ============================================================
# SECTION 1: Feature Store — Core ML Infrastructure
# ============================================================

@dataclass
class Feature:
    name: str
    value: Any
    timestamp: float
    ttl_seconds: int = 3600  # 1 hour default


class OnlineFeatureStore:
    """
    Simulates Redis-backed online feature store.
    Production: Feast + Redis, Tecton, Databricks Feature Store
    """
    def __init__(self):
        self._store: Dict[str, Dict[str, Feature]] = {}

    def write(self, entity_id: str, feature_name: str, value: Any, ttl: int = 3600):
        if entity_id not in self._store:
            self._store[entity_id] = {}
        self._store[entity_id][feature_name] = Feature(
            name=feature_name, value=value,
            timestamp=time.time(), ttl_seconds=ttl
        )

    def read(self, entity_id: str, feature_names: List[str]) -> Dict[str, Any]:
        result = {}
        entity_feats = self._store.get(entity_id, {})
        for name in feature_names:
            feat = entity_feats.get(name)
            if feat and (time.time() - feat.timestamp) < feat.ttl_seconds:
                result[name] = feat.value
            else:
                result[name] = None  # stale or missing — handle with defaults
        return result

    def batch_read(self, entity_ids: List[str], feature_names: List[str]) -> Dict[str, Dict]:
        return {eid: self.read(eid, feature_names) for eid in entity_ids}


# Demo: Write and read user features
online_store = OnlineFeatureStore()
online_store.write("user_123", "age_bucket", "25-34", ttl=86400)
online_store.write("user_123", "avg_order_value_30d", 245.50, ttl=3600)
online_store.write("user_123", "days_since_last_order", 3, ttl=1800)
online_store.write("user_123", "preferred_category", "Electronics", ttl=86400)

features = online_store.read("user_123", [
    "age_bucket", "avg_order_value_30d", "days_since_last_order", "preferred_category"
])
print("=== FEATURE STORE READ ===")
for k, v in features.items():
    print(f"  {k}: {v}")

# ============================================================
# SECTION 2: Model Serving — Patterns
# ============================================================

class ModelServer:
    """
    Simulates a production model server.
    Production: Triton Inference Server, TorchServe, Seldon, BentoML
    """
    def __init__(self, model_fn, feature_store: OnlineFeatureStore):
        self.model_fn      = model_fn
        self.feature_store = feature_store
        self._cache        = {}          # prediction cache (Redis in prod)
        self._request_log  = []          # for monitoring

    def _make_cache_key(self, entity_id: str, context: dict) -> str:
        payload = f"{entity_id}:{sorted(context.items())}"
        return hashlib.md5(payload.encode()).hexdigest()

    def predict(self, entity_id: str, feature_names: List[str],
                context: dict = None, cache_ttl: int = 60) -> dict:
        start = time.time()

        # 1. Check prediction cache
        cache_key = self._make_cache_key(entity_id, context or {})
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if time.time() - cached['ts'] < cache_ttl:
                return {**cached['result'], 'cached': True, 'latency_ms': 0}

        # 2. Fetch features (online store)
        features = self.feature_store.read(entity_id, feature_names)

        # 3. Merge with request context
        if context:
            features.update(context)

        # 4. Handle missing features
        features = {k: v if v is not None else 0.0 for k, v in features.items()}

        # 5. Model inference
        prediction = self.model_fn(features)

        # 6. Cache result
        result = {'entity_id': entity_id, 'prediction': prediction,
                  'features_used': list(features.keys())}
        self._cache[cache_key] = {'result': result, 'ts': time.time()}

        # 7. Log for monitoring
        latency = (time.time() - start) * 1000
        self._request_log.append({'entity_id': entity_id, 'latency_ms': latency,
                                   'prediction': prediction})

        return {**result, 'cached': False, 'latency_ms': round(latency, 2)}

    def get_metrics(self) -> dict:
        if not self._request_log:
            return {}
        latencies = [r['latency_ms'] for r in self._request_log]
        preds = [r['prediction'] for r in self._request_log]
        return {
            'total_requests': len(self._request_log),
            'p50_latency_ms': np.percentile(latencies, 50),
            'p95_latency_ms': np.percentile(latencies, 95),
            'p99_latency_ms': np.percentile(latencies, 99),
            'avg_prediction':  np.mean(preds),
            'pred_std':        np.std(preds),
        }


# Simple demo model
def churn_model(features: dict) -> float:
    """Simulated churn probability model"""
    score = 0.5
    score += (features.get('days_since_last_order', 0) / 365) * 0.3
    score -= (features.get('avg_order_value_30d', 100) / 500) * 0.2
    return float(np.clip(score, 0, 1))

server = ModelServer(
    model_fn=churn_model,
    feature_store=online_store
)
feat_names = ["days_since_last_order", "avg_order_value_30d", "preferred_category"]
result = server.predict("user_123", feat_names, context={"current_page": "cart"})
print(f"\n=== MODEL SERVER PREDICTION ===")
print(f"  Entity: {result['entity_id']}")
print(f"  Churn probability: {result['prediction']:.4f}")
print(f"  Cached: {result['cached']}")
print(f"  Latency: {result['latency_ms']}ms")

# Second call — should be cached
result2 = server.predict("user_123", feat_names, context={"current_page": "cart"})
print(f"  Second call cached: {result2['cached']}")

# ============================================================
# SECTION 3: A/B Testing Framework for ML Models
# ============================================================

class ABTestFramework:
    """
    Traffic splitting for ML model experiments.
    Production: Statsig, LaunchDarkly, custom with Redis
    """
    def __init__(self, experiment_name: str, control_pct: float = 0.90):
        self.experiment_name = experiment_name
        self.control_pct     = control_pct
        self.results         = {'control': [], 'treatment': []}

    def assign(self, user_id: str) -> str:
        """Deterministic assignment — same user always gets same group"""
        hash_val = int(hashlib.md5(
            f"{self.experiment_name}:{user_id}".encode()
        ).hexdigest(), 16)
        return 'control' if (hash_val % 100) < (self.control_pct * 100) else 'treatment'

    def log_outcome(self, user_id: str, outcome: float):
        group = self.assign(user_id)
        self.results[group].append(outcome)

    def analyze(self) -> dict:
        from scipy import stats
        ctrl  = np.array(self.results['control'])
        treat = np.array(self.results['treatment'])
        if len(ctrl) < 30 or len(treat) < 30:
            return {'status': 'insufficient_data', 'n_ctrl': len(ctrl), 'n_treat': len(treat)}
        t_stat, p_value = stats.ttest_ind(ctrl, treat)
        lift = (treat.mean() - ctrl.mean()) / ctrl.mean() * 100
        return {
            'n_control':    len(ctrl),
            'n_treatment':  len(treat),
            'ctrl_mean':    round(ctrl.mean(), 4),
            'treat_mean':   round(treat.mean(), 4),
            'lift_pct':     round(lift, 2),
            't_stat':       round(t_stat, 4),
            'p_value':      round(p_value, 4),
            'significant':  p_value < 0.05,
            'conclusion':   'SHIP IT ✅' if (p_value < 0.05 and lift > 0) else 'DO NOT SHIP ❌'
        }


# Simulate A/B test
np.random.seed(42)
ab_test = ABTestFramework("new_rec_model_v2", control_pct=0.9)
user_ids = [f"user_{i}" for i in range(5000)]
for uid in user_ids:
    group   = ab_test.assign(uid)
    outcome = np.random.normal(50, 20) + (8 if group == 'treatment' else 0)
    ab_test.log_outcome(uid, outcome)

print("\n=== A/B TEST RESULTS ===")
analysis = ab_test.analyze()
for k, v in analysis.items():
    print(f"  {k}: {v}")

# ============================================================
# SECTION 4: Model Drift Detection
# ============================================================

class DriftDetector:
    """
    Population Stability Index (PSI) for feature drift detection.
    PSI < 0.10: No drift | 0.10-0.20: Moderate | > 0.20: Significant drift
    """
    def psi(self, baseline: np.ndarray, current: np.ndarray, n_bins: int = 10) -> float:
        bins = np.percentile(baseline, np.linspace(0, 100, n_bins + 1))
        bins[0]  -= 1e-8
        bins[-1] += 1e-8
        b_counts = np.histogram(baseline, bins=bins)[0]
        c_counts = np.histogram(current,  bins=bins)[0]
        # Add small epsilon to avoid log(0)
        b_pct = (b_counts / len(baseline)) + 1e-8
        c_pct = (c_counts / len(current))  + 1e-8
        return float(np.sum((b_pct - c_pct) * np.log(b_pct / c_pct)))

    def ks_test(self, baseline: np.ndarray, current: np.ndarray) -> dict:
        from scipy import stats
        stat, p_value = stats.ks_2samp(baseline, current)
        return {'statistic': round(stat, 4), 'p_value': round(p_value, 4),
                'drift_detected': p_value < 0.05}

    def monitor(self, feature_name: str, baseline: np.ndarray, current: np.ndarray) -> dict:
        psi_val = self.psi(baseline, current)
        ks      = self.ks_test(baseline, current)
        severity = 'none' if psi_val < 0.1 else ('moderate' if psi_val < 0.2 else 'high')
        return {
            'feature': feature_name,
            'psi': round(psi_val, 4), 'severity': severity,
            'ks_drift': ks['drift_detected'],
            'action': 'RETRAIN 🚨' if severity == 'high' else ('MONITOR ⚠️' if severity == 'moderate' else 'OK ✅')
        }


detector = DriftDetector()
np.random.seed(42)
baseline_data = np.random.normal(50, 10, 10000)
drifted_data  = np.random.normal(65, 15, 5000)  # distribution shifted

print("\n=== DRIFT DETECTION ===")
report = detector.monitor("avg_order_value", baseline_data, drifted_data)
for k, v in report.items():
    print(f"  {k}: {v}")

print("\n✅ Chapter 5: ML System Design complete!")
