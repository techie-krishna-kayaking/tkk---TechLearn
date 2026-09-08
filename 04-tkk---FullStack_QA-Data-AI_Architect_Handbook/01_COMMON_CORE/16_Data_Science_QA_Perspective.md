# Data Science - QA Perspective

## Executive Summary

Data Science combines statistics, machine learning, and domain expertise to extract insights and build predictive models from data. From a **QA perspective**, testing data science workflows requires validating data quality, feature engineering, model accuracy, reproducibility, performance, and ethical considerations (bias, fairness).

**Target Audience**: Senior QA engineers (7+ years) testing data science pipelines, ML models, and analytics applications.

---

## Why This Matters in Enterprise

### Business Impact
- **Data science market**: $230B in 2025, projected $1.1T by 2030 (IDC)
- **AI adoption**: 77% of enterprises using or exploring data science/ML (Gartner 2024)
- **ROI**: $13.01 return for every $1 invested in data science initiatives (Forrester)
- **Decision automation**: 60% of business decisions augmented by ML by 2026

### Technical Imperative
- **Model drift**: Production models degrade 15-20% within 6 months without retraining
- **Data quality**: 80% of data science time spent on data cleaning (CrowdFlower)
- **Reproducibility crisis**: 70% of ML models not reproducible (Nature 2023)
- **Ethical risks**: Biased models lead to discrimination, regulatory fines, reputational damage

### Career Value
- **Data Science QA demand**: 94% growth in ML testing roles (LinkedIn 2025)
- **Salary premium**: 40-65% higher for Data Science + QA expertise
- **Cross-domain skills**: Bridges engineering, statistics, business analytics

---

## Scope and Boundaries

### In Scope
- Data science lifecycle (CRISP-DM, TDSP)
- Exploratory data analysis (EDA) validation
- Feature engineering testing
- Model evaluation metrics (accuracy, precision, recall, F1, AUC)
- Model validation (train/test split, cross-validation, holdout)
- Bias and fairness testing
- Model deployment and monitoring
- A/B testing for models

### Out of Scope
- Deep learning specifics (covered in [07_ML_Concepts_QA_Perspective.md](./07_ML_Concepts_QA_Perspective.md))
- MLOps platforms (covered in stack files)
- Statistical theory (consult data scientists)

---

## Data Science Lifecycle

### CRISP-DM (Cross-Industry Standard Process for Data Mining)

    ```mermaid
    graph TD
        A[Business Understanding] --> B[Data Understanding]
        B --> C[Data Preparation]
        C --> D[Modeling]
        D --> E[Evaluation]
        E --> F[Deployment]
        F --> G[Monitoring]
        
        E -->|Iterate| B
        G -->|Retrain| C
        
        style A fill:#e1f5ff
        style D fill:#ffe1f5
        style E fill:#fff4e1
        style G fill:#e7ffe1
    ```

**QA Focus by Phase**:
1. **Business Understanding**: Validate success metrics defined (accuracy target, business KPI)
2. **Data Understanding**: Test data quality, completeness, distribution
3. **Data Preparation**: Validate feature engineering, transformations
4. **Modeling**: Test model training, hyperparameter tuning
5. **Evaluation**: Validate metrics, compare to baseline
6. **Deployment**: Test inference API, latency, throughput
7. **Monitoring**: Validate drift detection, retraining triggers

---

## Exploratory Data Analysis (EDA) Validation

### Data Quality Checks

    ```python
    import pandas as pd
    import numpy as np
    
    def test_data_quality():
        """Validate data quality before modeling"""
        
        df = pd.read_csv("training_data.csv")
        
        # 1. Completeness: Check missing values
        missing_pct = df.isnull().sum() / len(df) * 100
        
        critical_features = ['customer_id', 'transaction_date', 'amount']
        for feature in critical_features:
            assert missing_pct[feature] < 1.0, \
                f"{feature}: {missing_pct[feature]:.2f}% missing (threshold: 1%)"
        
        # 2. Uniqueness: Check for duplicates
        duplicates = df.duplicated(subset=['customer_id', 'transaction_date'])
        dup_count = duplicates.sum()
        dup_pct = dup_count / len(df) * 100
        
        assert dup_pct < 0.1, \
            f"{dup_pct:.4f}% duplicates (threshold: 0.1%)"
        
        # 3. Validity: Check data types
        assert df['customer_id'].dtype == 'object' or df['customer_id'].dtype == 'int64'
        assert pd.api.types.is_datetime64_any_dtype(df['transaction_date'])
        assert pd.api.types.is_numeric_dtype(df['amount'])
        
        # 4. Range validation
        assert df['amount'].min() >= 0, \
            f"Negative amounts found: min={df['amount'].min()}"
        
        # 5. Distribution checks (detect anomalies)
        q1 = df['amount'].quantile(0.25)
        q3 = df['amount'].quantile(0.75)
        iqr = q3 - q1
        
        outliers = df[(df['amount'] < q1 - 3*iqr) | (df['amount'] > q3 + 3*iqr)]
        outlier_pct = len(outliers) / len(df) * 100
        
        assert outlier_pct < 5.0, \
            f"{outlier_pct:.2f}% outliers (threshold: 5%)"
    ```

### Statistical Distribution Testing

    ```python
    from scipy import stats
    
    def test_data_distribution():
        """Validate training and test data have similar distributions"""
        
        train_df = pd.read_csv("train.csv")
        test_df = pd.read_csv("test.csv")
        
        numeric_features = ['age', 'income', 'credit_score']
        
        for feature in numeric_features:
            # Kolmogorov-Smirnov test (distribution similarity)
            statistic, p_value = stats.ks_2samp(
                train_df[feature].dropna(),
                test_df[feature].dropna()
            )
            
            # p-value > 0.05 → distributions not significantly different
            assert p_value > 0.05, \
                f"{feature} distribution differs between train/test " \
                f"(p-value={p_value:.4f})"
    ```

---

## Feature Engineering Validation

### Feature Transformation Testing

    ```python
    def test_feature_scaling():
        """Validate feature scaling (normalization/standardization)"""
        
        from sklearn.preprocessing import StandardScaler
        
        # Original data
        X_train = pd.DataFrame({
            'age': [25, 35, 45, 55],
            'income': [30000, 50000, 70000, 90000]
        })
        
        # Apply scaling
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_train)
        X_scaled_df = pd.DataFrame(X_scaled, columns=X_train.columns)
        
        # Validate mean ≈ 0, std ≈ 1 (standardization)
        for col in X_scaled_df.columns:
            mean = X_scaled_df[col].mean()
            std = X_scaled_df[col].std()
            
            assert abs(mean) < 1e-10, \
                f"{col} mean={mean:.6f} (expected ≈ 0)"
            assert abs(std - 1.0) < 0.01, \
                f"{col} std={std:.6f} (expected ≈ 1)"
    ```

### Feature Encoding Testing

    ```python
    def test_one_hot_encoding():
        """Validate categorical encoding"""
        
        from sklearn.preprocessing import OneHotEncoder
        
        df = pd.DataFrame({
            'category': ['A', 'B', 'C', 'A', 'B']
        })
        
        encoder = OneHotEncoder(sparse_output=False)
        encoded = encoder.fit_transform(df[['category']])
        
        # Validate shape (5 rows, 3 categories)
        assert encoded.shape == (5, 3), \
            f"Wrong shape: {encoded.shape} (expected: (5, 3))"
        
        # Validate each row sums to 1 (one-hot property)
        row_sums = encoded.sum(axis=1)
        assert all(row_sums == 1), \
            f"Rows don't sum to 1: {row_sums}"
        
        # Validate categories preserved
        categories = encoder.categories_[0]
        assert list(categories) == ['A', 'B', 'C'], \
            f"Categories mismatch: {categories}"
    ```

### Feature Importance Validation

    ```python
    def test_feature_importance():
        """Validate feature importance scores make business sense"""
        
        from sklearn.ensemble import RandomForestClassifier
        
        # Train model
        model = RandomForestClassifier(random_state=42)
        model.fit(X_train, y_train)
        
        # Get feature importances
        importances = pd.DataFrame({
            'feature': X_train.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Validate top features align with domain knowledge
        top_features = importances.head(5)['feature'].tolist()
        
        expected_important_features = ['credit_score', 'income', 'debt_ratio']
        
        # At least 2 of expected features in top 5
        overlap = set(top_features) & set(expected_important_features)
        
        assert len(overlap) >= 2, \
            f"Top features {top_features} don't align with expected {expected_important_features}"
        
        # Validate importances sum to 1
        total_importance = importances['importance'].sum()
        assert abs(total_importance - 1.0) < 0.01, \
            f"Importances sum to {total_importance:.4f} (expected: 1.0)"
    ```

---

## Model Training and Validation

### Train/Test Split Validation

    ```python
    from sklearn.model_selection import train_test_split
    
    def test_train_test_split():
        """Validate train/test split performed correctly"""
        
        X = pd.DataFrame(np.random.rand(1000, 5))
        y = pd.Series(np.random.randint(0, 2, 1000))
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Validate split ratio (80/20)
        assert len(X_train) == 800, f"Train size: {len(X_train)} (expected: 800)"
        assert len(X_test) == 200, f"Test size: {len(X_test)} (expected: 200)"
        
        # Validate stratification (class balance preserved)
        train_class_ratio = y_train.value_counts(normalize=True)
        test_class_ratio = y_test.value_counts(normalize=True)
        
        for cls in [0, 1]:
            diff = abs(train_class_ratio[cls] - test_class_ratio[cls])
            assert diff < 0.05, \
                f"Class {cls} ratio differs: train={train_class_ratio[cls]:.3f}, " \
                f"test={test_class_ratio[cls]:.3f}"
        
        # Validate no data leakage (no overlap)
        train_indices = set(X_train.index)
        test_indices = set(X_test.index)
        
        assert len(train_indices & test_indices) == 0, \
            "Data leakage: train and test sets overlap"
    ```

### Cross-Validation Testing

    ```python
    from sklearn.model_selection import cross_val_score
    from sklearn.ensemble import RandomForestClassifier
    
    def test_cross_validation():
        """Validate k-fold cross-validation"""
        
        model = RandomForestClassifier(random_state=42)
        
        # 5-fold cross-validation
        cv_scores = cross_val_score(
            model, X_train, y_train, cv=5, scoring='accuracy'
        )
        
        # Validate 5 scores returned
        assert len(cv_scores) == 5, \
            f"Expected 5 CV scores, got {len(cv_scores)}"
        
        # Validate scores in reasonable range (0-1)
        assert all(0 <= score <= 1 for score in cv_scores), \
            f"CV scores out of range: {cv_scores}"
        
        # Validate low variance (consistent performance)
        cv_std = cv_scores.std()
        assert cv_std < 0.1, \
            f"High CV variance: std={cv_std:.4f} (threshold: 0.1)"
        
        # Validate mean accuracy above baseline
        cv_mean = cv_scores.mean()
        baseline_accuracy = max(y_train.value_counts(normalize=True))
        
        assert cv_mean > baseline_accuracy, \
            f"CV accuracy {cv_mean:.3f} not better than baseline {baseline_accuracy:.3f}"
    ```

---

## Model Evaluation Metrics

### Classification Metrics

    ```python
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
    
    def test_classification_metrics():
        """Validate classification model performance"""
        
        # Train model
        model = RandomForestClassifier(random_state=42)
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_pred_proba)
        
        # Validate against requirements
        assert accuracy >= 0.85, \
            f"Accuracy {accuracy:.3f} below requirement 0.85"
        assert precision >= 0.80, \
            f"Precision {precision:.3f} below requirement 0.80"
        assert recall >= 0.75, \
            f"Recall {recall:.3f} below requirement 0.75"
        assert f1 >= 0.77, \
            f"F1 score {f1:.3f} below requirement 0.77"
        assert auc >= 0.90, \
            f"AUC {auc:.3f} below requirement 0.90"
    ```

### Regression Metrics

    ```python
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    
    def test_regression_metrics():
        """Validate regression model performance"""
        
        from sklearn.ensemble import RandomForestRegressor
        
        # Train model
        model = RandomForestRegressor(random_state=42)
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Validate against requirements
        assert rmse < 1000, \
            f"RMSE {rmse:.2f} above threshold 1000"
        assert mae < 500, \
            f"MAE {mae:.2f} above threshold 500"
        assert r2 >= 0.80, \
            f"R² {r2:.3f} below requirement 0.80"
        
        # Validate residuals (errors) normally distributed
        residuals = y_test - y_pred
        _, p_value = stats.normaltest(residuals)
        
        assert p_value > 0.05, \
            f"Residuals not normally distributed (p={p_value:.4f})"
    ```

### Confusion Matrix Analysis

    ```python
    from sklearn.metrics import confusion_matrix
    
    def test_confusion_matrix():
        """Validate confusion matrix for classification"""
        
        model = RandomForestClassifier(random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        cm = confusion_matrix(y_test, y_pred)
        
        # Extract values
        tn, fp, fn, tp = cm.ravel()
        
        # Validate shape (2x2 for binary classification)
        assert cm.shape == (2, 2), \
            f"Confusion matrix wrong shape: {cm.shape}"
        
        # Calculate rates
        fpr = fp / (fp + tn)  # False Positive Rate
        fnr = fn / (fn + tp)  # False Negative Rate
        
        # Business requirement: FPR < 10% (not too many false alarms)
        assert fpr < 0.10, \
            f"False Positive Rate {fpr:.3f} above 10% threshold"
        
        # Business requirement: FNR < 15% (not missing too many positives)
        assert fnr < 0.15, \
            f"False Negative Rate {fnr:.3f} above 15% threshold"
    ```

---

## Model Reproducibility

### Random Seed Testing

    ```python
    def test_model_reproducibility():
        """Validate model training is reproducible"""
        
        # Train model 1
        model1 = RandomForestClassifier(random_state=42, n_estimators=100)
        model1.fit(X_train, y_train)
        pred1 = model1.predict(X_test)
        
        # Train model 2 (same random seed)
        model2 = RandomForestClassifier(random_state=42, n_estimators=100)
        model2.fit(X_train, y_train)
        pred2 = model2.predict(X_test)
        
        # Validate predictions identical
        assert np.array_equal(pred1, pred2), \
            "Models with same random seed produced different predictions"
        
        # Validate feature importances identical
        assert np.allclose(model1.feature_importances_, model2.feature_importances_), \
            "Feature importances differ despite same random seed"
    ```

### Version Control Testing

    ```python
    def test_model_versioning():
        """Validate model artifacts versioned correctly"""
        
        import joblib
        import hashlib
        
        # Train and save model
        model = RandomForestClassifier(random_state=42)
        model.fit(X_train, y_train)
        
        model_path = "models/model_v1.pkl"
        joblib.dump(model, model_path)
        
        # Calculate checksum
        with open(model_path, 'rb') as f:
            checksum = hashlib.md5(f.read()).hexdigest()
        
        # Save metadata
        metadata = {
            "version": "1.0",
            "date": "2024-01-15",
            "checksum": checksum,
            "accuracy": accuracy_score(y_test, model.predict(X_test))
        }
        
        # Load model and validate
        loaded_model = joblib.load(model_path)
        loaded_pred = loaded_model.predict(X_test)
        original_pred = model.predict(X_test)
        
        assert np.array_equal(loaded_pred, original_pred), \
            "Loaded model produces different predictions"
        
        # Validate checksum matches
        with open(model_path, 'rb') as f:
            new_checksum = hashlib.md5(f.read()).hexdigest()
        
        assert new_checksum == checksum, \
            "Model file checksum mismatch (file corrupted or modified)"
    ```

---

## Bias and Fairness Testing

### Demographic Parity Testing

    ```python
    def test_demographic_parity():
        """Validate model predictions fair across demographic groups"""
        
        model = RandomForestClassifier(random_state=42)
        model.fit(X_train, y_train)
        
        # Predictions
        test_df = X_test.copy()
        test_df['prediction'] = model.predict(X_test)
        test_df['gender'] = y_test  # Assume gender is protected attribute
        
        # Calculate positive prediction rate by group
        male_positive_rate = test_df[test_df['gender'] == 0]['prediction'].mean()
        female_positive_rate = test_df[test_df['gender'] == 1]['prediction'].mean()
        
        # Demographic parity: difference should be small
        disparity = abs(male_positive_rate - female_positive_rate)
        
        assert disparity < 0.10, \
            f"Demographic disparity {disparity:.3f} exceeds 10% threshold " \
            f"(Male: {male_positive_rate:.3f}, Female: {female_positive_rate:.3f})"
    ```

### Equal Opportunity Testing

    ```python
    def test_equal_opportunity():
        """Validate equal true positive rate across groups"""
        
        model = RandomForestClassifier(random_state=42)
        model.fit(X_train, y_train)
        
        test_df = X_test.copy()
        test_df['prediction'] = model.predict(X_test)
        test_df['actual'] = y_test
        test_df['protected_attr'] = ...  # e.g., race, gender
        
        # Calculate TPR (True Positive Rate) for each group
        def tpr(df):
            tp = ((df['actual'] == 1) & (df['prediction'] == 1)).sum()
            actual_positive = (df['actual'] == 1).sum()
            return tp / actual_positive if actual_positive > 0 else 0
        
        group_tprs = test_df.groupby('protected_attr').apply(tpr)
        
        # Validate TPR similar across groups
        tpr_diff = group_tprs.max() - group_tprs.min()
        
        assert tpr_diff < 0.10, \
            f"TPR difference {tpr_diff:.3f} across groups exceeds 10%: {group_tprs}"
    ```

---

## Model Deployment Testing

### Inference API Testing

    ```python
    def test_inference_api():
        """Validate model inference API"""
        
        import requests
        
        # Sample input
        payload = {
            "features": {
                "age": 35,
                "income": 50000,
                "credit_score": 720
            }
        }
        
        # Call API
        response = requests.post(
            "https://api.example.com/predict",
            json=payload,
            headers={"Authorization": f"Bearer {api_token}"}
        )
        
        # Validate response
        assert response.status_code == 200, \
            f"API error: {response.status_code} - {response.text}"
        
        result = response.json()
        
        # Validate response structure
        assert "prediction" in result, "Missing 'prediction' in response"
        assert "probability" in result, "Missing 'probability' in response"
        
        # Validate data types
        assert isinstance(result["prediction"], int), \
            f"Prediction wrong type: {type(result['prediction'])}"
        assert 0 <= result["probability"] <= 1, \
            f"Probability out of range: {result['probability']}"
    ```

### Latency Testing

    ```python
    import time
    
    def test_inference_latency():
        """Validate inference latency meets SLA"""
        
        # Load model
        model = joblib.load("models/production_model.pkl")
        
        # Sample inputs
        test_samples = X_test.sample(100, random_state=42)
        
        # Measure latency
        latencies = []
        for _, row in test_samples.iterrows():
            start = time.time()
            prediction = model.predict([row.values])
            latency = time.time() - start
            latencies.append(latency)
        
        # Calculate percentiles
        p50 = np.percentile(latencies, 50)
        p95 = np.percentile(latencies, 95)
        p99 = np.percentile(latencies, 99)
        
        # Validate SLAs
        assert p50 < 0.010, \
            f"p50 latency {p50:.4f}s exceeds 10ms SLA"
        assert p95 < 0.050, \
            f"p95 latency {p95:.4f}s exceeds 50ms SLA"
        assert p99 < 0.100, \
            f"p99 latency {p99:.4f}s exceeds 100ms SLA"
    ```

### Batch Prediction Testing

    ```python
    def test_batch_prediction():
        """Validate batch prediction performance"""
        
        model = joblib.load("models/production_model.pkl")
        
        # Large batch (10,000 samples)
        batch_data = X_test.sample(10000, replace=True, random_state=42)
        
        # Measure throughput
        start = time.time()
        predictions = model.predict(batch_data)
        duration = time.time() - start
        
        throughput = len(batch_data) / duration  # predictions/sec
        
        # Validate throughput
        assert throughput > 1000, \
            f"Throughput {throughput:.0f} pred/sec below 1000 threshold"
        
        # Validate all predictions returned
        assert len(predictions) == len(batch_data), \
            f"Prediction count mismatch: {len(predictions)} vs {len(batch_data)}"
    ```

---

## Model Monitoring

### Data Drift Detection

    ```python
    from scipy.stats import ks_2samp
    
    def test_data_drift():
        """Detect drift in production data vs training data"""
        
        # Training data distribution
        train_feature = X_train['age']
        
        # Production data (simulated)
        production_data = pd.read_csv("production_logs.csv")
        prod_feature = production_data['age']
        
        # Kolmogorov-Smirnov test
        statistic, p_value = ks_2samp(train_feature, prod_feature)
        
        # p-value < 0.05 → distributions differ (drift detected)
        if p_value < 0.05:
            # Alert for retraining
            alert_message = f"Data drift detected in 'age': p-value={p_value:.4f}"
            send_alert(alert_message)
            
            # Fail test if drift significant
            assert False, alert_message
    ```

### Model Performance Monitoring

    ```python
    def test_production_model_performance():
        """Monitor production model accuracy"""
        
        # Fetch production predictions + ground truth (labels available later)
        prod_data = pd.read_sql("""
            SELECT prediction, actual_label
            FROM predictions
            WHERE prediction_date >= CURRENT_DATE - INTERVAL 7 DAY
            AND actual_label IS NOT NULL
        """, conn)
        
        # Calculate production accuracy
        prod_accuracy = (prod_data['prediction'] == prod_data['actual_label']).mean()
        
        # Baseline accuracy (from test set)
        baseline_accuracy = 0.85
        
        # Alert if accuracy drops >5%
        accuracy_drop = baseline_accuracy - prod_accuracy
        
        if accuracy_drop > 0.05:
            alert_message = f"Model accuracy dropped {accuracy_drop:.2%}: " \
                           f"baseline={baseline_accuracy:.3f}, prod={prod_accuracy:.3f}"
            send_alert(alert_message)
        
        # Fail test if accuracy drops >10% (critical)
        assert accuracy_drop < 0.10, \
            f"Critical accuracy drop: {alert_message}"
    ```

---

## A/B Testing for Models

### A/B Test Validation

    ```python
    def test_ab_test_for_model():
        """Validate A/B test comparing model A vs model B"""
        
        # Simulate A/B test results
        # Model A (control): 1000 users, 100 conversions
        # Model B (treatment): 1000 users, 120 conversions
        
        conversion_a = 100 / 1000  # 10%
        conversion_b = 120 / 1000  # 12%
        
        # Chi-square test for statistical significance
        from scipy.stats import chi2_contingency
        
        observed = np.array([
            [100, 900],  # Model A: conversions, non-conversions
            [120, 880]   # Model B: conversions, non-conversions
        ])
        
        chi2, p_value, dof, expected = chi2_contingency(observed)
        
        # Validate statistical significance (p < 0.05)
        assert p_value < 0.05, \
            f"Model B not significantly better than A (p={p_value:.4f})"
        
        # Validate improvement magnitude (>10% lift)
        lift = (conversion_b - conversion_a) / conversion_a * 100
        
        assert lift > 10, \
            f"Conversion lift {lift:.1f}% below 10% threshold"
    ```

---

## Interview Questions

### Basic (0-3 years)
**Q1**: What is the difference between supervised and unsupervised learning?  
**A1**: **Supervised**: Learn from labeled data (input → output, e.g., predict house price from features). **Unsupervised**: Find patterns in unlabeled data (clustering customers, anomaly detection). Supervised for prediction, unsupervised for exploration.

**Q2**: What is overfitting?  
**A2**: Model memorizes training data (high train accuracy, low test accuracy). **Causes**: Too complex model, too little data. **Solutions**: Regularization (L1/L2), cross-validation, more training data, simpler model.

### Advanced (4-8 years)
**Q3**: How do you validate a machine learning model?  
**A3**: (1) **Train/test split**: Hold out 20-30% for testing, (2) **Cross-validation**: k-fold (5 or 10 folds), (3) **Metrics**: Classification (accuracy, precision, recall, F1, AUC), regression (RMSE, MAE, R²), (4) **Baseline comparison**: Validate better than naive baseline, (5) **Business validation**: Test on real-world data, measure business impact.

**Q4**: What is the bias-variance tradeoff?  
**A4**: **Bias**: Model assumptions (high bias = underfitting, e.g., linear model for non-linear data). **Variance**: Model sensitivity to training data (high variance = overfitting, e.g., deep tree). **Tradeoff**: Simple model (high bias, low variance), complex model (low bias, high variance). Optimal model balances both.

### Scenario (8-12 years)
**Q5**: Production model accuracy dropped from 90% to 75% in 3 months. Troubleshoot?  
**A5**: (1) **Data drift**: Check if input distribution changed (seasonality, new user behavior), (2) **Label drift**: Check if target definition changed, (3) **Feature engineering**: Check if new features needed (missing important signals), (4) **Model staleness**: Retrain with recent data, (5) **Data quality**: Check for missing/corrupt data in production, (6) **Monitoring**: Set up drift detection (KS test), retrain triggers (accuracy <80%).

### Architect (12+ years)
**Q6**: Design QA strategy for enterprise ML platform (100 models, real-time + batch)?  
**A6**: (1) **Pre-deployment**: Unit tests (feature engineering), integration tests (model training pipeline), performance tests (latency <50ms, throughput >1000/sec), (2) **Validation**: Cross-validation (k=5), holdout set (20%), A/B tests (treatment >10% lift, p<0.05), (3) **Metrics**: Classification (accuracy >85%, F1 >0.80), regression (RMSE <threshold, R²>0.80), (4) **Bias/fairness**: Demographic parity (<10% disparity), equal opportunity (TPR diff <10%), (5) **Monitoring**: Data drift (KS test weekly), performance drift (accuracy drop >5% triggers alert), (6) **Retraining**: Automated retraining (monthly or drift-triggered), champion/challenger (A/B test new model), (7) **Governance**: Model registry (version, metadata, lineage), explainability (SHAP values), audit logs (predictions, decisions), (8) **Reproducibility**: Random seeds, versioned data/code/models, CI/CD pipelines, (9) **Compliance**: GDPR (right to explanation), fairness regulations, (10) **Disaster recovery**: Model rollback (<5 min), fallback to baseline model.

---

## Frequently Asked Questions

**Q1**: What is feature engineering?  
**A1**: Creating new features from raw data to improve model performance. **Examples**: (1) Interaction features (age × income), (2) Polynomial features (age²), (3) Binning (age → age_group: young/middle/senior), (4) Date features (extract day_of_week from timestamp), (5) Aggregations (customer_avg_purchase). **Testing**: Validate transformations correct, features improve model accuracy.

**Q2**: How to handle imbalanced datasets?  
**A2**: When one class rare (e.g., 1% fraud, 99% legitimate). **Solutions**: (1) **Oversampling minority** (SMOTE), (2) **Undersampling majority**, (3) **Class weights** (penalize misclassifying minority more), (4) **Different metrics** (use F1, AUC instead of accuracy), (5) **Ensemble methods** (boosting). **Test**: Validate minority class recall >70%.

**Q3**: What is cross-validation and why use it?  
**A3**: Split data into k folds (typically 5), train on k-1 folds, validate on 1 fold, repeat k times. **Benefits**: (1) Use all data for training/validation, (2) Reduce overfitting (more reliable than single train/test), (3) Estimate generalization error. **Test**: Validate low CV variance (<0.1 std).

**Q4**: How to test model explainability?  
**A4**: (1) **Feature importance**: Validate top features make business sense, (2) **SHAP values**: Explain individual predictions (why customer denied loan?), (3) **Partial dependence plots**: Show feature effect on prediction, (4) **LIME**: Local explanations (approximate model locally). **Test**: Generate explanation for sample prediction, validate with domain expert.

**Q5**: What is data leakage?  
**A5**: Training data contains info about target not available at prediction time. **Examples**: (1) Using future data (predicting churn using "account_closed_date"), (2) Target leakage (feature highly correlated with target, e.g., "refund_issued" predicting fraud). **Prevention**: Temporal validation (train on past, test on future), careful feature selection. **Test**: Validate features only use data available before prediction.

**Q6**: How to test ensemble models?  
**A6**: **Ensemble** = combine multiple models (Random Forest, Gradient Boosting, Voting Classifier). **Test**: (1) **Individual models**: Validate each base model, (2) **Diversity**: Models make different errors (low correlation), (3) **Ensemble improvement**: Ensemble accuracy > best individual model, (4) **Weights**: If weighted voting, validate weights sum to 1.

**Q7**: What is hyperparameter tuning?  
**A7**: Optimizing model parameters (not learned, set before training). Examples: learning rate, tree depth, regularization strength. **Methods**: Grid search (all combinations), random search (sample), Bayesian optimization. **Test**: Validate tuning improves performance, no overfitting (test score also improves).

**Q8**: How to test model versioning?  
**A8**: (1) **Unique version**: Each model has version ID (v1.0.0), (2) **Metadata**: Track training date, data version, hyperparameters, metrics, (3) **Reproducibility**: Same version produces same predictions (checksums), (4) **Rollback**: Can revert to previous version (<5 min), (5) **Lineage**: Track which data/code produced model.

**Q9**: What is the curse of dimensionality?  
**A9**: As feature count increases, data becomes sparse (observations far apart). **Effects**: Model requires exponentially more data, overfitting risk. **Solutions**: Feature selection (remove irrelevant), dimensionality reduction (PCA), regularization. **Test**: Validate performance improves with fewer features (remove low-importance).

**Q10**: How to test real-time vs batch models differently?  
**A10**: **Real-time** (single prediction <100ms): Test latency (p95 <50ms), concurrent requests (100+ users), availability (99.9%), input validation (reject malformed). **Batch** (thousands predictions): Test throughput (>1000/sec), memory usage (no OOM), data volume (handle 1M records), failure recovery (restart from checkpoint).

**Q11**: What is model drift?  
**A11**: Production model performance degrades over time. **Types**: (1) **Data drift**: Input distribution changes (concept same), (2) **Concept drift**: Relationship between input-output changes. **Detection**: KS test (data drift), monitor accuracy (concept drift). **Mitigation**: Retrain monthly or when drift detected.

**Q12**: How to test feature selection?  
**A12**: **Methods**: Filter (correlation), wrapper (recursive feature elimination), embedded (L1 regularization). **Test**: (1) **Performance**: Model with selected features ≈ all features, (2) **Feature count**: Reduced by >50%, (3) **Business value**: Selected features interpretable, (4) **Stability**: Same features selected with different train sets.

**Q13**: What is stratified sampling?  
**A13**: Sampling that preserves class distribution. Example: If 70% class 0, 30% class 1 in full data, train/test have same ratio. **Why**: Prevent imbalance in small datasets. **Test**: Validate train/test class ratios within 5% of original.

**Q14**: How to test model calibration?  
**A14**: **Calibration**: Predicted probability matches actual probability (if model says 70% probability, event happens 70% of time). **Test**: Calibration plot (predicted vs actual), Brier score (<0.1). **Recalibration**: Platt scaling, isotonic regression.

**Q15**: What is the no free lunch theorem?  
**A15**: No single ML algorithm best for all problems. Must try multiple algorithms (linear, tree, neural net), select best for your data. **Testing**: Benchmark 3-5 algorithms, select based on metrics + business constraints (interpretability, latency).

**Q16**: How to test multi-class classification?  
**A16**: More than 2 classes (e.g., classify product into electronics/clothing/food). **Metrics**: Accuracy, macro/micro-averaged precision/recall/F1, confusion matrix (NxN). **Test**: Validate each class recall >70%, no class completely missed (all rows/cols in confusion matrix non-zero).

**Q17**: What is bootstrapping in ML?  
**A17**: Random sampling with replacement to estimate uncertainty. **Uses**: Confidence intervals for metrics, feature importance stability. **Example**: Train model on 100 bootstrap samples, calculate accuracy 100 times, report mean ± std. **Test**: Validate 95% CI width reasonable.

**Q18**: How to test model on edge cases?  
**A18**: **Edge cases**: Unusual inputs (very high/low values, missing features, new categories). **Test**: (1) **Boundary values**: Min/max feature values, (2) **Missing data**: All features missing (model should reject or impute), (3) **New categories**: Category not in training data (should use "unknown" encoding), (4) **Adversarial**: Inputs designed to fool model.

**Q19**: What is the Gini coefficient in ML?  
**A19**: Measure of inequality in feature importance (tree models). High Gini (0.8-1.0) = few features dominate, low Gini (0.0-0.2) = features equally important. **Test**: Validate Gini aligns with business (if 1 feature should dominate, high Gini OK; if multiple equally important, low Gini expected).

**Q20**: How to test automated feature engineering (AutoML)?  
**A20**: **AutoML tools**: Auto-sklearn, H2O AutoML, TPOT. **Test**: (1) **Feature quality**: Inspect generated features (make sense?), (2) **Performance**: AutoML model competitive with manual features, (3) **Reproducibility**: Same features generated with same seed, (4) **Runtime**: Completes within budget (e.g., 1 hour), (5) **Explainability**: Can explain generated features to stakeholders.

---

## Actionable Checklists

### Data Preparation Testing Checklist
- [ ] Data quality validated (completeness, uniqueness, validity, range)
- [ ] Missing values handled (imputation or removal documented)
- [ ] Outliers detected and treated (cap, remove, or keep with justification)
- [ ] Train/test split validated (ratio, stratification, no leakage)
- [ ] Feature scaling tested (mean ≈ 0, std ≈ 1)
- [ ] Categorical encoding validated (one-hot, label encoding)
- [ ] Feature engineering tested (transformations correct)
- [ ] Data distribution checked (train/test similar, KS test p>0.05)

### Model Training Testing Checklist
- [ ] Baseline model tested (naive predictor for comparison)
- [ ] Multiple algorithms benchmarked (3-5 models)
- [ ] Hyperparameter tuning validated (grid/random search)
- [ ] Cross-validation performed (k=5 or 10, low variance)
- [ ] Model reproducibility tested (random seed, same results)
- [ ] Training time measured (within budget)
- [ ] Model artifacts saved (versioned, checksummed)

### Model Evaluation Testing Checklist
- [ ] Metrics calculated (accuracy, precision, recall, F1, AUC for classification; RMSE, MAE, R² for regression)
- [ ] Metrics meet requirements (accuracy >85%, R² >0.80)
- [ ] Confusion matrix analyzed (FPR, FNR within limits)
- [ ] Feature importance validated (top features make business sense)
- [ ] Model explainability tested (SHAP, LIME)
- [ ] Bias/fairness validated (demographic parity <10% disparity)
- [ ] Edge cases tested (boundary values, missing data)

### Model Deployment Testing Checklist
- [ ] Inference API tested (correct predictions, error handling)
- [ ] Latency validated (p95 <50ms for real-time)
- [ ] Throughput tested (>1000 predictions/sec for batch)
- [ ] Concurrent users tested (100+ users, success rate >95%)
- [ ] Model versioning implemented (unique ID, metadata)
- [ ] Monitoring configured (data drift, performance drift)
- [ ] Rollback tested (revert to previous version <5 min)
- [ ] A/B test planned (treatment lift >10%, p<0.05)

---

## References

### Books
- **Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow** (Aurélien Géron): Practical ML
- **The Elements of Statistical Learning** (Hastie, Tibshirani, Friedman): ML theory
- **Introduction to Statistical Learning** (James, Witten, Hastie, Tibshirani): Beginner-friendly ML

### Courses
- **Andrew Ng's Machine Learning** (Coursera): Foundational ML course
- **Fast.ai**: Practical deep learning
- **Google Machine Learning Crash Course**: Quick ML intro

### Libraries
- **Scikit-learn**: Python ML library (classification, regression, clustering)
- **XGBoost**: Gradient boosting (high performance)
- **LightGBM**: Fast gradient boosting
- **CatBoost**: Gradient boosting for categorical features

### Metrics & Evaluation
- **Scikit-learn Metrics**: Classification, regression, clustering metrics
- **MLflow**: Model tracking, versioning, deployment
- **Weights & Biases**: Experiment tracking, hyperparameter tuning

---

**Core References**: Platform-agnostic data science concepts  
**Stack Deltas**: Platform-specific ML tools (AWS SageMaker, Azure ML, GCP Vertex AI) in stack files

**Previous**: [15_Data_Security_QA_Perspective.md](./15_Data_Security_QA_Perspective.md)  
**Next**: [17_GenAI_Concepts_QA_Perspective.md](./17_GenAI_Concepts_QA_Perspective.md)  
**Up**: [Master Index](../00_MASTER_INDEX.md)