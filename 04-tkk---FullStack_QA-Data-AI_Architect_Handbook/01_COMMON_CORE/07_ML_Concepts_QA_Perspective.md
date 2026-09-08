# ML Concepts - Machine Learning from QA Perspective

## Executive Summary

Machine Learning (ML) enables systems to learn patterns from data and make predictions without explicit programming. From a **QA perspective**, testing ML systems requires understanding training pipelines, hyperparameter tuning, feature engineering, model validation techniques, and MLOps practices.

**Target Audience**: Senior QA engineers (8+ years) specializing in ML model testing, data science QA, and MLOps validation.

---

## Why This Matters in Enterprise

### Business Impact
- **ML ROI**: 76% of organizations report positive ROI from ML initiatives (Algorithmia 2025)
- **Revenue impact**: Recommendation engines drive 35% of Amazon revenue, 75% of Netflix views
- **Cost savings**: Predictive maintenance reduces downtime by 30-50%, saves $millions annually

### Technical Imperative
- **ML failures are invisible**: Models can degrade silently (no error logs, just bad predictions)
- **Data dependency**: 80% of ML project time spent on data preparation and quality
- **Model complexity**: Deep learning models have millions of parameters—debugging requires specialized techniques

### Career Value
- **High demand**: ML QA roles increased 143% year-over-year (Dice 2025)
- **Salary premium**: ML QA engineers earn 40-55% more than traditional QA
- **Interdisciplinary**: Bridges data engineering, data science, software engineering, and QA

---

## Scope and Boundaries

### In Scope
- ML algorithms (linear regression, decision trees, neural networks, ensemble methods)
- Feature engineering and selection
- Hyperparameter tuning and optimization
- Model validation techniques (cross-validation, holdout, time-series split)
- MLOps pipeline testing (training, deployment, monitoring)
- Model performance metrics (regression, classification, ranking)

### Out of Scope
- LLM-specific testing (covered in [08_LLM_Concepts_QA_Perspective.md](./08_LLM_Concepts_QA_Perspective.md))
- Deep learning architectures (CNNs, RNNs covered in separate advanced docs)
- Platform-specific implementations (SageMaker, Azure ML covered in stack files)

---

## ML Algorithm Categories

### 1. Linear Models

**Linear Regression** (Regression):
    ```python
    # Predict house price = β0 + β1*sqft + β2*bedrooms + ε
    from sklearn.linear_model import LinearRegression
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    
    # QA Test: Coefficients make business sense
    assert model.coef_[0] > 0, "Square footage coefficient should be positive"
    assert model.coef_[1] > 0, "More bedrooms should increase price"
    ```

**Logistic Regression** (Classification):
    ```python
    # Predict probability: P(spam) = 1 / (1 + e^-(β0 + β1*x1 + β2*x2))
    from sklearn.linear_model import LogisticRegression
    
    model = LogisticRegression()
    model.fit(X_train, y_train)
    
    # QA Test: Probability output in [0, 1]
    probs = model.predict_proba(X_test)[:, 1]
    assert all(0 <= p <= 1 for p in probs), "Probabilities out of range"
    ```

### 2. Tree-Based Models

**Decision Tree**:
    ```mermaid
    graph TD
        A[Credit Score > 650?] -->|Yes| B[Income > 50K?]
        A -->|No| C[Deny Loan]
        B -->|Yes| D[Approve Loan]
        B -->|No| E[Debt Ratio < 0.4?]
        E -->|Yes| F[Approve Loan]
        E -->|No| G[Deny Loan]
        
        style D fill:#e7ffe1
        style F fill:#e7ffe1
        style C fill:#ffe1e1
        style G fill:#ffe1e1
    ```

**QA Tests**:
    ```python
    from sklearn.tree import DecisionTreeClassifier
    
    def test_decision_tree():
        model = DecisionTreeClassifier(max_depth=5, random_state=42)
        model.fit(X_train, y_train)
        
        # Test: Max depth enforced
        assert model.get_depth() <= 5, f"Tree depth {model.get_depth()} exceeds max"
        
        # Test: Feature importance makes sense
        feature_importance = dict(zip(feature_names, model.feature_importances_))
        top_feature = max(feature_importance, key=feature_importance.get)
        assert top_feature == 'credit_score', f"Expected credit_score, got {top_feature}"
    ```

**Random Forest** (Ensemble of Trees):
    ```python
    from sklearn.ensemble import RandomForestClassifier
    
    def test_random_forest():
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Test: All trees trained
        assert len(model.estimators_) == 100
        
        # Test: Out-of-bag score reasonable (internal validation)
        assert model.oob_score_ > 0.80, f"OOB score {model.oob_score_:.2f} too low"
    ```

**Gradient Boosting** (XGBoost, LightGBM):
    ```python
    import xgboost as xgb
    
    def test_xgboost():
        model = xgb.XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.1)
        model.fit(X_train, y_train)
        
        # Test: Learning converged (training loss decreasing)
        evals_result = model.evals_result()
        train_loss = evals_result['validation_0']['logloss']
        assert train_loss[-1] < train_loss[0], "Loss not decreasing (convergence issue)"
    ```

### 3. Support Vector Machines (SVM)

**Concept**: Find hyperplane that maximally separates classes.

    ```python
    from sklearn.svm import SVC
    
    def test_svm():
        model = SVC(kernel='rbf', C=1.0, gamma='scale')
        model.fit(X_train, y_train)
        
        # Test: Support vector count reasonable (not overfitting)
        n_support = model.n_support_.sum()
        assert n_support < len(X_train) * 0.5, f"{n_support} support vectors (potential overfit)"
    ```

### 4. Neural Networks

**Multi-Layer Perceptron (MLP)**:
    ```python
    from sklearn.neural_network import MLPClassifier
    
    def test_neural_network():
        model = MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
        model.fit(X_train, y_train)
        
        # Test: Converged within max iterations
        assert model.n_iter_ < 500, f"Did not converge ({model.n_iter_} iterations)"
        
        # Test: Loss decreasing
        assert model.loss_curve_[-1] < model.loss_curve_[0], "Loss not decreasing"
    ```

---

## Feature Engineering

### Feature Creation

**Polynomial Features**:
    ```python
    # Original: sqft
    # New: sqft, sqft^2, sqft^3 (capture non-linear relationships)
    from sklearn.preprocessing import PolynomialFeatures
    
    poly = PolynomialFeatures(degree=2, include_bias=False)
    X_poly = poly.fit_transform(X)
    
    # QA Test: Correct number of features
    # Original features: n, Polynomial: n + n*(n-1)/2 (for degree=2)
    expected_features = X.shape[1] + X.shape[1] * (X.shape[1] - 1) // 2
    assert X_poly.shape[1] == expected_features
    ```

**Interaction Features**:
    ```python
    # Create sqft * bedrooms (interaction effect)
    X['sqft_bedrooms'] = X['sqft'] * X['bedrooms']
    
    # QA Test: Interaction feature has expected correlation
    correlation = X['sqft_bedrooms'].corr(X['price'])
    assert correlation > 0.5, f"Interaction feature correlation {correlation:.2f} too low"
    ```

**Binning**:
    ```python
    # Convert continuous age to categorical bins
    X['age_group'] = pd.cut(X['age'], bins=[0, 18, 35, 50, 65, 100], 
                            labels=['0-18', '19-35', '36-50', '51-65', '65+'])
    
    # QA Test: All ages assigned to bin
    assert X['age_group'].isnull().sum() == 0, "Some ages not binned"
    ```

### Feature Scaling

**Standardization (Z-score)**:
    ```python
    # Transform to mean=0, std=1: (x - μ) / σ
    from sklearn.preprocessing import StandardScaler
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    
    # QA Test: Mean ≈ 0, Std ≈ 1
    assert abs(X_scaled.mean()) < 0.01, f"Mean {X_scaled.mean():.4f} not zero"
    assert abs(X_scaled.std() - 1) < 0.01, f"Std {X_scaled.std():.4f} not one"
    ```

**Normalization (Min-Max)**:
    ```python
    # Transform to [0, 1]: (x - min) / (max - min)
    from sklearn.preprocessing import MinMaxScaler
    
    scaler = MinMaxScaler()
    X_normalized = scaler.fit_transform(X_train)
    
    # QA Test: Values in [0, 1]
    assert X_normalized.min() >= 0, f"Min {X_normalized.min():.4f} < 0"
    assert X_normalized.max() <= 1, f"Max {X_normalized.max():.4f} > 1"
    ```

### Feature Selection

**Remove Low Variance**:
    ```python
    from sklearn.feature_selection import VarianceThreshold
    
    selector = VarianceThreshold(threshold=0.01)  # Remove features with <1% variance
    X_selected = selector.fit_transform(X)
    
    # QA Test: Low-variance features removed
    removed_features = [f for f, v in zip(feature_names, selector.variances_) if v < 0.01]
    print(f"Removed {len(removed_features)} low-variance features: {removed_features}")
    ```

**Univariate Selection**:
    ```python
    from sklearn.feature_selection import SelectKBest, f_classif
    
    selector = SelectKBest(score_func=f_classif, k=10)  # Keep top 10 features
    X_selected = selector.fit_transform(X, y)
    
    # QA Test: Correct number of features selected
    assert X_selected.shape[1] == 10
    ```

**Recursive Feature Elimination (RFE)**:
    ```python
    from sklearn.feature_selection import RFE
    from sklearn.ensemble import RandomForestClassifier
    
    estimator = RandomForestClassifier(n_estimators=50)
    selector = RFE(estimator, n_features_to_select=10)
    X_selected = selector.fit_transform(X, y)
    
    # QA Test: Validate selected features make business sense
    selected_features = [f for f, s in zip(feature_names, selector.support_) if s]
    assert 'credit_score' in selected_features, "Expected credit_score in top features"
    ```

---

## Hyperparameter Tuning

### Grid Search

    ```python
    from sklearn.model_selection import GridSearchCV
    from sklearn.ensemble import RandomForestClassifier
    
    # Define hyperparameter grid
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [5, 10, 15],
        'min_samples_split': [2, 5, 10]
    }
    
    # Exhaustive search (3 * 3 * 3 = 27 combinations)
    grid_search = GridSearchCV(
        RandomForestClassifier(random_state=42),
        param_grid,
        cv=5,
        scoring='f1',
        n_jobs=-1
    )
    grid_search.fit(X_train, y_train)
    
    # QA Test: Best parameters found
    best_params = grid_search.best_params_
    print(f"Best parameters: {best_params}")
    assert grid_search.best_score_ > 0.80, f"Best F1 score {grid_search.best_score_:.2f} too low"
    ```

### Random Search

    ```python
    from sklearn.model_selection import RandomizedSearchCV
    from scipy.stats import randint
    
    # Define distributions
    param_distributions = {
        'n_estimators': randint(50, 500),
        'max_depth': randint(3, 20),
        'min_samples_split': randint(2, 20)
    }
    
    # Random sampling (100 combinations)
    random_search = RandomizedSearchCV(
        RandomForestClassifier(random_state=42),
        param_distributions,
        n_iter=100,
        cv=5,
        scoring='f1',
        random_state=42
    )
    random_search.fit(X_train, y_train)
    
    # QA Test: Compare to grid search (should be similar)
    assert random_search.best_score_ >= grid_search.best_score_ * 0.95, \
        "Random search significantly worse than grid search"
    ```

### Bayesian Optimization

    ```python
    from skopt import BayesSearchCV
    
    # Define search space
    search_space = {
        'n_estimators': (50, 500),
        'max_depth': (3, 20),
        'learning_rate': (0.01, 0.3, 'log-uniform')
    }
    
    bayes_search = BayesSearchCV(
        xgb.XGBClassifier(),
        search_space,
        n_iter=50,
        cv=5,
        scoring='f1'
    )
    bayes_search.fit(X_train, y_train)
    
    # QA Test: Converged to good parameters
    assert bayes_search.best_score_ > 0.85
    ```

---

## Model Validation Techniques

### Holdout Validation

    ```python
    from sklearn.model_selection import train_test_split
    
    # 80/20 split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    model.fit(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    # QA Test: No data leakage (test set not seen during training)
    assert len(set(X_train.index) & set(X_test.index)) == 0, "Train/test overlap"
    ```

### K-Fold Cross-Validation

    ```python
    from sklearn.model_selection import cross_val_score
    
    # 5-fold CV (train on 4 folds, test on 1, rotate)
    scores = cross_val_score(model, X, y, cv=5, scoring='f1')
    
    # QA Test: Consistent performance across folds
    assert scores.std() < 0.05, f"High variance across folds: {scores}"
    assert scores.mean() > 0.80, f"Mean F1 {scores.mean():.2f} below threshold"
    ```

### Stratified K-Fold (Imbalanced Classes)

    ```python
    from sklearn.model_selection import StratifiedKFold
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        # QA Test: Class distribution maintained
        train_dist = y_train.value_counts(normalize=True)
        test_dist = y_test.value_counts(normalize=True)
        assert abs(train_dist[1] - test_dist[1]) < 0.05, "Class imbalance in split"
    ```

### Time-Series Split

    ```python
    from sklearn.model_selection import TimeSeriesSplit
    
    tscv = TimeSeriesSplit(n_splits=5)
    
    for train_idx, test_idx in tscv.split(X):
        # QA Test: Test data comes after train data (no future leakage)
        assert train_idx.max() < test_idx.min(), "Future data in training set"
    ```

---

## Model Performance Metrics

### Regression Metrics

**Mean Absolute Error (MAE)**:
    ```python
    from sklearn.metrics import mean_absolute_error
    
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    
    # Interpretation: Average prediction error
    print(f"MAE: ${mae:,.2f}")  # e.g., "MAE: $15,000" (avg house price error)
    ```

**Mean Squared Error (MSE) / Root MSE (RMSE)**:
    ```python
    from sklearn.metrics import mean_squared_error
    
    mse = mean_squared_error(y_test, y_pred)
    rmse = mse ** 0.5
    
    # Interpretation: Penalizes large errors more (squared)
    print(f"RMSE: ${rmse:,.2f}")
    ```

**R² Score (Coefficient of Determination)**:
    ```python
    from sklearn.metrics import r2_score
    
    r2 = r2_score(y_test, y_pred)
    
    # Interpretation: % variance explained (1.0 = perfect, 0 = baseline, <0 = worse than baseline)
    assert r2 > 0.70, f"R² {r2:.2f} too low (model explains <70% variance)"
    ```

### Classification Metrics

**Precision, Recall, F1 (Binary Classification)**:
    ```python
    from sklearn.metrics import precision_score, recall_score, f1_score
    
    precision = precision_score(y_test, y_pred)  # TP / (TP + FP)
    recall = recall_score(y_test, y_pred)        # TP / (TP + FN)
    f1 = f1_score(y_test, y_pred)                # 2 * (P * R) / (P + R)
    
    # QA Test: Balance precision/recall
    assert abs(precision - recall) < 0.10, "Precision/Recall imbalance"
    ```

**ROC-AUC (Receiver Operating Characteristic)**:
    ```python
    from sklearn.metrics import roc_auc_score, roc_curve
    
    y_proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_proba)
    
    # Interpretation: 0.5 = random, 1.0 = perfect
    assert auc > 0.85, f"AUC {auc:.2f} below threshold"
    
    # Plot ROC curve
    fpr, tpr, thresholds = roc_curve(y_test, y_proba)
    ```

**Multi-Class Metrics**:
    ```python
    from sklearn.metrics import classification_report
    
    # Macro avg: unweighted mean (treat all classes equal)
    # Weighted avg: weighted by support (class frequency)
    print(classification_report(y_test, y_pred, target_names=['Class A', 'Class B', 'Class C']))
    ```

### Ranking Metrics

**Mean Average Precision (MAP)**:
    ```python
    # For recommendation systems, search engines
    from sklearn.metrics import average_precision_score
    
    # Binary relevance (1 = relevant, 0 = not relevant)
    y_true = [1, 1, 0, 1, 0, 0, 1, 0, 0, 1]
    y_scores = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05]
    
    ap = average_precision_score(y_true, y_scores)
    print(f"Average Precision: {ap:.2f}")
    ```

---

## MLOps Pipeline Testing

### Training Pipeline Validation

    ```python
    # Automated training pipeline test
    def test_training_pipeline():
        # Step 1: Data loading
        data = load_data('s3://bucket/training_data.parquet')
        assert len(data) > 10000, "Insufficient training data"
        
        # Step 2: Data preprocessing
        X, y = preprocess(data)
        assert X.isnull().sum().sum() == 0, "Null values in features"
        
        # Step 3: Train/test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        # Step 4: Model training
        model = RandomForestClassifier(n_estimators=100)
        model.fit(X_train, y_train)
        
        # Step 5: Validation
        test_score = model.score(X_test, y_test)
        assert test_score > 0.80, f"Test accuracy {test_score:.2f} below threshold"
        
        # Step 6: Model serialization
        import joblib
        joblib.dump(model, 'model.pkl')
        
        # QA: Model file created
        assert os.path.exists('model.pkl')
    ```

### Model Deployment Testing

    ```python
    # Test model API endpoint
    import requests
    
    def test_model_api():
        # Deploy model as REST API
        url = "http://model-api.example.com/predict"
        
        # Test payload
        payload = {
            "features": {
                "credit_score": 700,
                "income": 60000,
                "debt": 20000
            }
        }
        
        response = requests.post(url, json=payload)
        
        # QA Tests
        assert response.status_code == 200, f"API error: {response.status_code}"
        
        result = response.json()
        assert 'prediction' in result
        assert 'probability' in result
        assert 0 <= result['probability'] <= 1
        
        # Latency test (p95 < 100ms)
        latencies = [requests.post(url, json=payload).elapsed.total_seconds() * 1000 
                     for _ in range(100)]
        p95_latency = sorted(latencies)[94]
        assert p95_latency < 100, f"p95 latency {p95_latency:.2f}ms exceeds SLA"
    ```

### Model Monitoring

    ```python
    # Monitor prediction distribution (detect drift)
    import numpy as np
    from scipy.stats import ks_2samp
    
    def test_prediction_drift():
        # Training set predictions (baseline)
        train_preds = model.predict_proba(X_train)[:, 1]
        
        # Production predictions (last 7 days)
        prod_preds = load_production_predictions(days=7)
        
        # KS test (p-value < 0.05 indicates distribution shift)
        statistic, p_value = ks_2samp(train_preds, prod_preds)
        
        assert p_value > 0.05, f"Prediction drift detected: p={p_value:.4f}"
    ```

---

## Interview Questions

### Basic (0-3 years)
**Q1**: What's the difference between classification and regression?  
**A1**: Classification predicts discrete labels (spam/not spam, cat/dog). Regression predicts continuous values (house price, temperature). Classification = categories, Regression = numbers.

**Q2**: Explain overfitting.  
**A2**: Model memorizes training data instead of learning patterns. High train accuracy, low test accuracy. Causes: too complex model, too little data. Prevention: regularization, cross-validation, more data.

### Advanced (4-8 years)
**Q3**: How do you handle imbalanced classes (99% negative, 1% positive)?  
**A3**: (1) Resampling: Oversample minority (SMOTE), undersample majority, (2) Class weights: Penalize minority misclassification more, (3) Metrics: Use precision/recall/F1 instead of accuracy, (4) Ensemble: Combine multiple models, (5) Anomaly detection: Treat minority as anomalies.

**Q4**: What is regularization and why use it?  
**A4**: Penalty for model complexity (L1/Lasso, L2/Ridge). Prevents overfitting by shrinking coefficients. L1 produces sparse models (feature selection), L2 reduces magnitude. Test by comparing regularized vs. unregularized performance.

### Scenario (8-12 years)
**Q5**: Fraud detection model has 95% accuracy but misses high-value fraud. Troubleshoot?  
**A5**: (1) **Class imbalance**: Fraud is rare (1%), model predicts "not fraud" for 99% accuracy, (2) **Wrong metric**: Use precision/recall, not accuracy, (3) **Cost-sensitive**: Weight fraud errors higher (false negatives costly), (4) **Threshold tuning**: Lower threshold to catch more fraud (trade precision for recall), (5) **Feature engineering**: Add transaction amount as feature to prioritize high-value fraud.

### Architect (12+ years)
**Q6**: Design ML testing strategy for credit scoring model (regulatory compliance required)?  
**A6**: (1) **Data quality**: Validate no bias in training data (demographic parity), (2) **Model validation**: Cross-validation, holdout test set (time-based split), (3) **Fairness testing**: Equal opportunity across protected groups (race, gender, age), (4) **Explainability**: SHAP values for every decision (regulatory requirement), (5) **Performance**: Precision/recall >90%, AUC >0.85, (6) **Stress testing**: Adversarial examples, edge cases (credit score=0, income=$0), (7) **Model monitoring**: Weekly drift detection, monthly retraining, (8) **Compliance**: Model documentation (model card), audit trail (decisions logged), (9) **A/B testing**: Shadow mode for 30 days before production, (10) **Rollback plan**: Maintain previous model version for 90 days.

---

## Frequently Asked Questions

**Q1**: What is feature engineering and why does it matter?  
**A1**: Creating new features from raw data to improve model performance. Matters because: (1) Better features > better algorithms, (2) Domain knowledge encoded as features, (3) Can reduce need for complex models. Example: Create "debt_to_income_ratio" from debt and income features.

**Q2**: How to detect data leakage?  
**A2**: (1) **Time leakage**: Future data in training (use time-based split), (2) **Target leakage**: Feature derived from target (e.g., "fraud_flag" in fraud detection), (3) **Train/test leakage**: Same data in both sets, (4) **Feature leakage**: Feature not available at prediction time. Test: Remove feature, if performance drops significantly, investigate leakage.

**Q3**: What is ensemble learning and when to use?  
**A3**: Combine multiple models to improve performance. Types: (1) Bagging (Random Forest), (2) Boosting (XGBoost), (3) Stacking (meta-model). Use when: (1) Need accuracy boost, (2) Have diverse models (different algorithms), (3) Production latency acceptable (ensemble slower). Test by comparing to single best model.

**Q4**: How to validate model reproducibility?  
**A4**: (1) Fix random seed (`random_state=42`), (2) Version data (DVC, MLflow), (3) Version code (Git), (4) Document environment (`requirements.txt`), (5) Test: Re-train model, validate same metrics (within tolerance, e.g., ±0.01 accuracy).

**Q5**: Difference between grid search and random search?  
**A5**: **Grid**: Exhaustive search over all combinations (slow, thorough). **Random**: Sample random combinations (fast, may miss optimum). Use grid for small search space (<100 combinations), random for large (>1000). Test by comparing best scores.

**Q6**: What is cross-validation and when not to use?  
**A6**: Train/test on multiple folds to reduce variance in performance estimate. **Don't use**: (1) Time-series data (use time-based split), (2) Large datasets (expensive, holdout sufficient), (3) Severe class imbalance (stratified CV required).

**Q7**: How to test feature importance?  
**A7**: (1) **Model-based**: Use `feature_importances_` (tree models) or coefficients (linear models), (2) **Permutation**: Shuffle feature, measure performance drop, (3) **SHAP**: Shapley values (global + local importance), (4) **Test**: Remove top feature, validate performance degrades significantly.

**Q8**: What is the bias-variance tradeoff?  
**A8**: **Bias** = error from wrong assumptions (underfitting). **Variance** = error from sensitivity to training data (overfitting). **Tradeoff**: Complex models (low bias, high variance), simple models (high bias, low variance). Optimal: Balance both (minimize total error).

**Q9**: How to handle missing values during training?  
**A9**: (1) **Remove**: Drop rows (<5% missing), (2) **Impute**: Mean/median (numeric), mode (categorical), model-based (predict missing), (3) **Indicator**: Add "is_missing" binary feature, (4) **Algorithm**: Use tree-based models (handle missing natively). Test impact on performance.

**Q10**: What is learning curve and how to use?  
**A10**: Plot training/validation error vs. training set size. **Diagnose**: (1) High bias: Both errors high (need complex model), (2) High variance: Large gap (need more data or regularization), (3) Good fit: Both errors low and converged. Test by generating learning curve, validate convergence.

**Q11**: How to test model on new data distribution?  
**A11**: (1) **Collect**: Sample new data (different region, time period), (2) **Validate**: Check feature distributions vs. training (KS test), (3) **Test**: Measure performance on new data, (4) **Adapt**: Retrain if performance degrades >10%, (5) **Monitor**: Track drift over time.

**Q12**: What is calibration and why does it matter?  
**A12**: Predicted probabilities match actual frequencies. Example: Of all predictions with 70% confidence, 70% should be correct. Matters for: (1) Decision-making (business uses probabilities), (2) Ranking (recommendation systems), (3) Compliance (explain confidence). Test with calibration plot, fix with Platt scaling.

**Q13**: How to optimize hyperparameters efficiently?  
**A13**: (1) **Start simple**: Grid search on small range, (2) **Narrow down**: Zoom into promising regions, (3) **Use Bayesian**: For expensive models (deep learning), (4) **Early stopping**: Halt unpromising combinations early, (5) **Parallelize**: Use all CPU cores (`n_jobs=-1`). Validate best params on holdout set.

**Q14**: What is feature scaling and when is it required?  
**A14**: Transform features to similar scale. **Required**: (1) Distance-based (KNN, SVM, neural networks), (2) Gradient descent (faster convergence), (3) Regularization (fair penalty). **Not required**: Tree-based (invariant to scaling). Test by comparing scaled vs. unscaled performance.

**Q15**: How to test model latency in production?  
**A15**: (1) **Unit test**: Single prediction (<50ms), (2) **Batch test**: 1000 predictions (<1 sec), (3) **Load test**: 1000 concurrent requests, measure p95 latency, (4) **Optimization**: Model compression (quantization), batching, caching. Monitor p95/p99 latency in production.

**Q16**: What is data augmentation and when to use?  
**A16**: Generate synthetic training data (image rotation, text paraphrasing). Use when: (1) Limited data, (2) Imbalanced classes, (3) Expensive labeling. Test by comparing with/without augmentation. Common in computer vision, NLP.

**Q17**: How to handle outliers in training data?  
**A17**: (1) **Detect**: Statistical methods (IQR, Z-score), visual (box plots), (2) **Action**: Remove (if errors), cap (winsorize), transform (log), keep (if real), (3) **Robust models**: Use tree-based (less sensitive) or robust regression. Test impact on performance.

**Q18**: What is the curse of dimensionality in ML?  
**A18**: High feature count causes data sparsity (points far apart), requires exponentially more data. **Solutions**: (1) Feature selection, (2) Dimensionality reduction (PCA), (3) Regularization. Test by reducing features, validating performance maintained.

**Q19**: How to test model fairness across demographics?  
**A19**: (1) **Identify**: Protected attributes (race, gender, age), (2) **Test**: Compare performance across groups (precision, recall, FPR), (3) **Metrics**: Demographic parity, equal opportunity, equalized odds, (4) **Fix**: Resampling, reweighting, post-processing. Validate fairness metrics meet thresholds.

**Q20**: What is transfer learning and how to validate?  
**A20**: Use pre-trained model (ImageNet, BERT) as starting point, fine-tune on your data. **Validate**: (1) Compare to training from scratch (transfer should be faster/better), (2) Test feature extraction (frozen base) vs. fine-tuning (update base), (3) Validate performance on target domain. Common in vision, NLP.

---

## Actionable Checklists

### ML Model Training Checklist
- [ ] Training data quality validated (completeness, balance, no leakage)
- [ ] Train/test split appropriate (stratified, time-based if applicable)
- [ ] Features scaled/normalized (if required by algorithm)
- [ ] Hyperparameters tuned (grid/random/Bayesian search)
- [ ] Model convergence verified (loss decreasing, no early stopping)
- [ ] Cross-validation performed (reduce variance)
- [ ] Overfitting checked (train vs. validation gap <10%)
- [ ] Feature importance reviewed (makes business sense)

### ML Model Evaluation Checklist
- [ ] Performance metrics meet thresholds (accuracy, precision, recall, F1)
- [ ] Confusion matrix reviewed (understand error types)
- [ ] ROC-AUC curve analyzed (optimal threshold selected)
- [ ] Calibration validated (predicted probabilities accurate)
- [ ] Bias/fairness tested (across demographic groups)
- [ ] Edge cases tested (boundary values, outliers)
- [ ] Adversarial robustness tested (perturbed inputs)
- [ ] Reproducibility confirmed (same results on re-train)

### MLOps Deployment Checklist
- [ ] Model serialized and versioned (MLflow, model registry)
- [ ] API endpoint tested (input/output contracts)
- [ ] Inference latency validated (p95 < SLA)
- [ ] Load testing performed (1000+ concurrent requests)
- [ ] A/B testing plan defined (gradual rollout)
- [ ] Monitoring dashboards created (drift, latency, errors)
- [ ] Alerting configured (performance degradation, anomalies)
- [ ] Rollback plan documented (revert to previous version)

---

## References

### Books
- **Hands-On Machine Learning** (Aurélien Géron): Comprehensive ML guide
- **Feature Engineering for Machine Learning** (Zheng, Casari): Feature engineering techniques
- **Designing Machine Learning Systems** (Chip Huyen): Production ML systems
- **Machine Learning Engineering** (Andriy Burkov): MLOps best practices

### Standards
- **ISO/IEC TR 29119-11**: ML Testing Standard (draft)
- **IEEE P2801**: AI Quality Standard

### Tools
- **scikit-learn**: https://scikit-learn.org (ML algorithms, preprocessing)
- **XGBoost**: https://xgboost.readthedocs.io (Gradient boosting)
- **MLflow**: https://mlflow.org (Model tracking, registry)
- **SHAP**: https://shap.readthedocs.io (Model explainability)

---

**Core References**: Platform-agnostic ML concepts  
**Stack Deltas**: See SageMaker/Azure ML/Vertex AI stack files for platform-specific implementations

**Previous**: [06_AI_Concepts.md](./06_AI_Concepts.md)  
**Next**: [08_LLM_Concepts_QA_Perspective.md](./08_LLM_Concepts_QA_Perspective.md)  
**Up**: [Master Index](../00_MASTER_INDEX.md)