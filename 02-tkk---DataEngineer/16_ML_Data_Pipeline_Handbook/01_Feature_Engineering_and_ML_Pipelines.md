"""
ML/AI DATA PIPELINE HANDBOOK
For Data Engineers transitioning to ML/AI roles (80 LPA - 1 Cr+)

Interview Weight: ⭐⭐⭐⭐⭐ (Critical for ML Engineer roles)
Target: Companies hiring ML-focused data engineers (Google, Meta, Databricks, unicorns)

This handbook covers:
1. Feature engineering at scale
2. ML data pipelines (training vs serving)
3. Model deployment and monitoring
4. Common ML gotchas for data engineers
5. Production ML systems
"""

# ============================================================================
# SECTION 1: FEATURE ENGINEERING AT SCALE
# ============================================================================

"""
SCENARIO: Build features for recommendation ML model (Netflix-style)

FEATURE TYPES:
1. User features (static)
   - user_id (identifier)
   - country (categorical)
   - account_age_days (numeric)
   - subscription_type (categorical)

2. User behavior features (temporal, aggregated)
   - watch_count_30d (COUNT(*) from last 30 days)
   - avg_watch_duration_30d (AVG(duration))
   - last_watch_category (MODE over watched genres)
   - days_since_last_watch (MAX(watch_date) - TODAY())

3. Content features (contextual)
   - content_id (identifier)
   - genre (categorical)
   - release_date (temporal)
   - avg_rating (numeric from reviews)
   - popularity_score (views last 30d normalized)

4. Cross features (user × content interaction)
   - user_watch_count_in_genre (user watched N in this genre)
   - content_watch_by_similar_users (how many users like this watched this)
   - days_since_user_watched_similar (temporal - did user watch similar recently)

FEATURE ENGINEERING WORKFLOW:

Step 1: Define features (YAML format)
```yaml
features:
  user_watch_count_30d:
    source: events
    type: numeric
    aggregation: COUNT(*)
    window: 30 days
    frequency: daily
    
  user_avg_watch_duration_30d:
    source: events
    type: numeric
    aggregation: AVG(duration)
    window: 30 days
    frequency: daily
```

Step 2: Offline Feature Computation (for training)
```python
# Spark batch job (daily)
from pyspark.sql import functions as F
from pyspark.sql.window import Window

events = spark.read.parquet("s3://events/")

# 30-day window
window_spec = Window.partitionBy("user_id").orderByDescending("event_date").rangeBetween(-30*86400, 0)

features = events.groupBy("user_id", "event_date").agg(
    F.count("*").over(window_spec).alias("watch_count_30d"),
    F.avg("duration").over(window_spec).alias("avg_watch_duration_30d")
).distinct()

features.write.parquet("s3://features/offline/")
```

Step 3: Point-in-time correctness (critical for ML)
```python
# Training dataset: Use features AS OF training date
# Problem: if feature computed tomorrow, training data leaks future info

# Correct approach:
# - Training date: 2024-01-01
# - Use features computed ON 2024-01-01 (not computed today)
# - This ensures NO DATA LEAKAGE

def get_training_features(training_date):
    features = spark.read.parquet(f"s3://features/offline/{training_date}/")
    return features
```

Step 4: Online Feature Serving (for inference)
```python
# Fast API to get features during prediction
from fastapi import FastAPI
import redis

app = FastAPI()
cache = redis.Redis(host='localhost', port=6379)

@app.get("/features/{user_id}")
async def get_features(user_id: int):
    # Try cache first (10ms)
    cached = cache.get(f"user_{user_id}")
    if cached:
        return json.loads(cached)
    
    # Fallback to database (100ms)
    features = db.query(f"SELECT * FROM user_features WHERE user_id = {user_id}")
    
    # Cache for 1 hour
    cache.setex(f"user_{user_id}", 3600, json.dumps(features))
    
    return features
```

COMMON FEATURE ENGINEERING MISTAKES:

Mistake 1: Training-Serving Skew
```python
# WRONG: Different computation
# Training: features computed in Python
df_train = df.groupBy("user_id").agg(avg("duration"))

# Serving: features computed in SQL
SELECT AVG(duration) FROM events GROUP BY user_id

# These might differ! (floating point rounding, NULL handling)

# RIGHT: Use same SQL for both
FEATURE_SQL = """SELECT AVG(duration) FROM events GROUP BY user_id"""
# Use in both training (via Spark SQL) and serving (via API)
```

Mistake 2: Data Leakage
```python
# WRONG: Using future data for training
features = events.groupBy("user_id").agg(
    F.count("*").over(Window.partitionBy("user_id")).alias("total_watch_count")
)
# This sums ALL events, including future events!

# RIGHT: Use only past data (as-of training date)
cutoff_date = "2024-01-01"
features = events.filter(F.col("event_date") <= cutoff_date).groupBy("user_id").agg(
    F.count("*").alias("watch_count")
)
```

Mistake 3: Not handling missing values
```python
# WRONG: Features sometimes NULL
features.groupBy("user_id").agg(F.avg("duration"))
# New users have NULL (0 events)

# RIGHT: Fill with sensible defaults
features.fillna({
    "watch_count": 0,
    "avg_duration": global_avg_duration,
    "days_since_watch": 999  # Very old
})
```

Mistake 4: Feature explosion without importance
```python
# WRONG: Create 1000 features, hope ML finds signal
features = [
    feature1, feature2, ..., feature1000
]

# RIGHT: Importance ranking, remove low-signal
feature_importance = model.feature_importances_
low_importance = [f for f, imp in zip(features, feature_importance) if imp < 0.001]
# Remove low_importance features, retrain
```

FEATURE STORE ARCHITECTURE:
┌──────────────────────────────────────┐
│ Offline Path (Training)              │
├──────────────────────────────────────┤
│ Spark Batch (daily)                  │
│ ↓                                    │
│ Delta Lake (historical data)         │
│ ↓                                    │
│ Python SDK retrieves training data   │
│ ↓                                    │
│ Training run (point-in-time correct) │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ Online Path (Inference)              │
├──────────────────────────────────────┤
│ Features computed real-time           │
│ ↓                                    │
│ Redis / DynamoDB (cache)             │
│ ↓                                    │
│ Fast API endpoint (<50ms latency)    │
│ ↓                                    │
│ Model prediction                     │
└──────────────────────────────────────┘
"""

# ============================================================================
# SECTION 2: ML DATA PIPELINE PATTERNS
# ============================================================================

"""
PATTERN 1: Batch ML Pipeline (Most common)
```
Daily Batch Job:
├─ Extract features from data warehouse
├─ Train model (on 30-day history)
├─ Evaluate metrics (accuracy, precision, recall)
├─ If better than baseline, promote to production
└─ Serve via lookup table (pre-computed predictions)
```

Latency: 1-2 hours (acceptable for non-realtime)
Cost: $2K/month compute, $500 storage
Use case: Recommender systems, churn prediction, email campaign targeting

PATTERN 2: Real-time ML Pipeline
```
Real-time Stream:
├─ Kafka (incoming features)
├─ Spark Streaming (feature engineering)
├─ MLflow Model Registry (fetch model)
├─ Predict (score each event)
├─ Write predictions (Redis/DynamoDB)
└─ Application reads predictions (<100ms latency)
```

Latency: 100-500ms
Cost: $5K/month (streaming + model serving)
Use case: Real-time personalization, fraud detection, ad bidding

PATTERN 3: Batch + Real-time (Lambda)
```
Combination:
├─ Batch: Pre-compute predictions for "typical" users (90%)
├─ Real-time: For remaining 10% (new/unusual users)
└─ Application: Check batch table first, fallback to realtime
```

Latency: <100ms for most, <500ms for all
Cost: $3K/month (balanced approach)

MODEL MONITORING:
```python
# Track model performance over time
predictions = model.predict(features)

# Log predictions
mlflow.log_metrics({
    "accuracy": accuracy_score(y_true, predictions),
    "precision": precision_score(y_true, predictions),
    "recall": recall_score(y_true, predictions),
    "f1": f1_score(y_true, predictions)
})

# Monitor for data drift
current_dist = features.describe()
baseline_dist = features_from_training.describe()

if statistical_distance(current_dist, baseline_dist) > threshold:
    alert("Data drift detected! Model may be stale")
```

RETRAINING STRATEGY:
- Automated: Retrain every 7 days (or when accuracy drops below threshold)
- Manual: On-demand when business logic changes
- A/B test: New model vs old model on 10% traffic before full rollout

MODEL SERVING:
```python
# Option 1: Batch predictions (lookup table)
# Pre-compute all predictions, save to database
# Prediction time: 1ms (just a lookup)
# Refresh frequency: daily

# Option 2: Real-time predictions (model API)
# Score on-demand via API
# Prediction time: 50ms
# Always fresh data

# Option 3: Hybrid
# Cache predictions for 1 day (lookup)
# If not in cache, score in real-time
```
"""

# ============================================================================
# SECTION 3: COMMON ML GOTCHAS (Interview Questions)
# ============================================================================

"""
GOTCHA 1: Class Imbalance
Q: You're building a fraud detection model. 99.9% of transactions are legit.
   What's wrong with a model that predicts "not fraud" for everything?
   
A: That model gets 99.9% accuracy but 0% recall (useless!).
   Solutions:
   - Oversample minority class (duplicate fraud examples)
   - Undersample majority class (sample legit examples)
   - Use weights: penalize false negatives more
   - Use different metric (F1, AUC-PR instead of accuracy)

GOTCHA 2: Concept Drift
Q: Your model trained last month works great in test, but fails in production.
   Why?
   
A: Concept drift - user behavior changed.
   Example: During COVID, user watch patterns changed (more daytime viewing)
   Solution:
   - Monitor model performance weekly
   - Retrain on recent data (last 30 days, not all history)
   - A/B test new models before full rollout
   - Alert when prediction distribution changes

GOTCHA 3: Data Leakage
Q: Your model gets 99% accuracy in training but 60% in production.
   
A: Common causes:
   - Using future data in training
   - Using target-correlated feature that won't exist at prediction time
   - Preprocessing on full dataset before train/test split
   
Solutions:
   - Split data FIRST (train 70% / test 30%)
   - Then preprocess ONLY on train set
   - Apply same preprocessing to test set

GOTCHA 4: Lookup-Train Mismatch
Q: Your feature computation for training uses SQL, but for serving uses Python.
   They give different results!
   
A: Common because of:
   - NULL handling (SQL: NULL vs Python: None)
   - Floating point precision
   - Timezone handling
   - String encoding
   
Solution: Use SAME code path for both:
   - Define features in SQL
   - Use in both training (Spark SQL) and serving (SQL query)

GOTCHA 5: Batch Size Effects
Q: Model works great in Spark (batch size 1000) but fails in production API (batch size 1).
   
A: Batch normalization / groupBy operations behave differently.
   Example: Row number across batch: RN=1 in batch size 1, vs RN=1000 in batch size 1000
   
Solution:
   - Test with batch size 1 during development
   - Don't rely on batch-specific operations
   - Use stateless features

GOTCHA 6: Feature Not Available at Prediction
Q: Training feature "upcoming_weekend" is perfect, but doesn't exist at prediction.

A: Feature selection must only use features available at prediction time.
   - Training time: You know what day you're predicting
   - Prediction time: You know what day it is
   - Both have access to same features!
   
Solution:
   - Document feature dependencies
   - Validate at prediction time that all features exist

GOTCHA 7: Model Version Management
Q: Which model version is serving? When was it last trained? Did it improve or regress?

A: Without version control, hard to track.

Solution:
   - Use MLflow Model Registry
   - Tag models: dev, staging, production
   - Track metrics for each version
   - Maintain model lineage
"""

# ============================================================================
# SECTION 4: ML INTERVIEW QUESTIONS
# ============================================================================

"""
Q1: Design a real-time recommendation system for Netflix.
ANSWER:
- Offline: Compute user embedding (Matrix factorization)
  * Historical watch data → Spark → User matrix
  * Item popularity → Spark → Item matrix
  * Save embeddings to Redis
  
- Online: Real-time prediction
  * User ID → Look up embedding from Redis
  * Get similar items (cosine similarity in embedding space)
  * Re-rank by watch trends (30-day popularity)
  * Return top 10
  
- Challenges:
  * Cold start: New user/content with no history
  * Popularity bias: Should recommend diverse, not just trending
  * Latency: <100ms required
  
- Monitoring:
  * Click-through rate (CTR) weekly
  * Recommendation diversity
  * Freshness (do we recommend recently released content?)

Q2: How would you handle model retraining at scale?
ANSWER:
- Incremental retraining (not full retrain every time)
  * Last 30 days of data for training (captures recent patterns)
  * Previous model as starting point (transfer learning)
  * Quick training (1 hour instead of 12 hours)
  
- Scheduling:
  * Cron job: Retrain every Sunday (low traffic)
  * Or: Trigger on data drift detection (some performance metric dropped)
  
- Validation:
  * A/B test: 10% traffic gets new model, 90% gets old
  * Monitor: If new model CTR > old by 1%, deploy to 100%
  * Rollback: If any regression, revert immediately

Q3: Detect data drift in production - how?
ANSWER:
- Statistical tests (Kolmogorov-Smirnov)
  * Train time: feature distribution X
  * Serving time: feature distribution Y
  * If KL-divergence(X, Y) > threshold, alert
  
- ML-based drift
  * Train classifier: "Is this from training or production?"
  * If classifier > 60% accurate, drift detected
  
- Business-based drift
  * Model accuracy prediction: compare actual vs expected
  * If accuracy drops >5%, likely drift

Q4: How would you handle 1 billion predictions per day?
ANSWER:
- Batch predictions (most efficient)
  * Daily Spark job: Score all users overnight
  * Save predictions to database
  * Application does simple lookup (1ms latency)
  * Refresh daily or when user acts
  
- Cost: $2K/month (1 Spark job)
- vs Real-time: $10K/month (model serving cluster)

Q5: Explain model serving tradeoffs:
ANSWER:
┌─────────────────┬──────────────┬──────────────┬────────────────┐
│ Approach        │ Latency      │ Freshness    │ Cost           │
├─────────────────┼──────────────┼──────────────┼────────────────┤
│ Batch lookup    │ 1ms          │ 24h old      │ $2K            │
│ Real-time API   │ 100ms        │ Fresh        │ $8K            │
│ Cache + fallback│ 10ms (hit)   │ 1h old       │ $4K            │
│ Edge inference  │ 10ms local   │ Varies       │ $5K (CDN)      │
└─────────────────┴──────────────┴──────────────┴────────────────┘
- Choose based on requirement: Does user need fresh prediction?
"""

print("✅ ML/AI Data Pipeline Handbook Loaded")
print("✅ Feature engineering at scale covered")
print("✅ ML pipeline patterns and gotchas included")
print("✅ Interview questions with answers ready")
