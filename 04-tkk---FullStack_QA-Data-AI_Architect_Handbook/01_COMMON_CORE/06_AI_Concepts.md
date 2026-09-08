# AI Concepts - Artificial Intelligence Fundamentals

## Executive Summary

Artificial Intelligence (AI) encompasses systems that perform tasks requiring human-like intelligence—learning, reasoning, perception, and decision-making. From a **QA perspective**, testing AI systems requires understanding model types, training/inference workflows, bias detection, explainability requirements, and ethical considerations.

**Target Audience**: Senior QA engineers (7+ years) transitioning to AI/ML testing or seeking architect-level mastery.

---

## Why This Matters in Enterprise

### Business Impact
- **AI market size**: $196B in 2025, projected $1.8T by 2030 (Fortune Business Insights)
- **ROI**: Companies using AI see 20-30% cost reduction in operations (McKinsey 2025)
- **Competitive necessity**: 91% of leading businesses invest in AI continuously (NewVantage Partners)

### Technical Imperative
- **AI failures are costly**: Biased hiring algorithms, misdiagnosed medical images, autonomous vehicle accidents
- **Regulatory scrutiny**: EU AI Act, US Executive Order on AI require testing, validation, explainability
- **Data dependency**: AI quality directly tied to training data quality (garbage in → garbage out)

### Career Value
- **Emerging field**: AI QA roles grew 127% in 2024 (LinkedIn)
- **Premium salaries**: AI/ML QA engineers earn 35-50% more than traditional QA
- **Future-proof**: AI testing skills applicable across all industries (healthcare, finance, automotive, retail)

---

## Scope and Boundaries

### In Scope
- AI vs. ML vs. Deep Learning distinctions
- AI model types (supervised, unsupervised, reinforcement learning)
- AI lifecycle (data collection, training, deployment, monitoring)
- AI testing strategies (model validation, bias testing, adversarial testing)
- Explainability and interpretability
- AI ethics and responsible AI principles

### Out of Scope
- Deep ML/DL algorithms (covered in [07_ML_Concepts_QA_Perspective.md](./07_ML_Concepts_QA_Perspective.md))
- LLM-specific testing (covered in [08_LLM_Concepts_QA_Perspective.md](./08_LLM_Concepts_QA_Perspective.md))
- AI platform implementations (covered in stack files: Azure ML, SageMaker, Vertex AI)

---

## AI Taxonomy

### AI vs. ML vs. Deep Learning

    ```mermaid
    graph TD
        A[Artificial Intelligence] --> B[Machine Learning]
        B --> C[Deep Learning]
        
        A1[Broader: Any intelligent system] -.-> A
        B1[Subset: Learn from data] -.-> B
        C1[Subset: Neural networks] -.-> C
        
        style A fill:#e1f5ff
        style B fill:#fff4e1
        style C fill:#ffe1f5
    ```

**Artificial Intelligence (Broad)**:
- Systems that mimic human intelligence
- Examples: Expert systems, rule-based chatbots, chess engines (minimax algorithm), symbolic reasoning

**Machine Learning (Subset)**:
- Systems that learn patterns from data without explicit programming
- Examples: Spam filters, recommendation engines, fraud detection

**Deep Learning (Subset of ML)**:
- Neural networks with multiple layers (deep architectures)
- Examples: Image recognition (CNNs), language models (Transformers), speech recognition (RNNs)

**QA Distinction**:
- **AI (rule-based)**: Test rules exhaustively (decision tables, state machines)
- **ML**: Test data quality, model performance (accuracy, precision, recall)
- **DL**: Test at scale (millions of parameters), interpretability challenges

---

## AI Model Types

### 1. Supervised Learning

**Definition**: Learn from labeled examples (input-output pairs).

**Use Cases**:
- **Classification**: Spam detection (email → spam/not spam), image recognition (photo → cat/dog/bird)
- **Regression**: House price prediction (features → price), sales forecasting (historical data → future sales)

**QA Focus**:
    ```python
    # Test classification model
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    
    def test_spam_classifier():
        # Test data (emails with known labels)
        test_emails = [
            ("Win free iPhone now!", 1),  # Spam
            ("Meeting at 3pm today", 0),  # Not spam
            ("Congratulations! You won $1M", 1),  # Spam
            ("Project deadline tomorrow", 0)  # Not spam
        ]
        
        X_test = [email for email, label in test_emails]
        y_true = [label for email, label in test_emails]
        y_pred = model.predict(X_test)
        
        # Validate performance metrics
        assert accuracy_score(y_true, y_pred) > 0.90, "Accuracy below 90%"
        assert precision_score(y_true, y_pred) > 0.85, "Precision below 85%"
        assert recall_score(y_true, y_pred) > 0.85, "Recall below 85%"
    ```

### 2. Unsupervised Learning

**Definition**: Find patterns in unlabeled data (no ground truth).

**Use Cases**:
- **Clustering**: Customer segmentation (group similar customers), anomaly detection (identify outliers)
- **Dimensionality Reduction**: Feature extraction (reduce 1000 features to 50), data visualization (3D → 2D)

**QA Focus**:
    ```python
    # Test clustering model (K-Means example)
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    
    def test_customer_segmentation():
        # Customer features (spending, frequency, recency)
        X = [[100, 5, 30], [150, 8, 10], [50, 2, 90], [120, 6, 20], ...]
        
        # Train K-Means (3 segments: low/medium/high value)
        kmeans = KMeans(n_clusters=3, random_state=42)
        clusters = kmeans.fit_predict(X)
        
        # Validate cluster quality (Silhouette score: -1 to 1, higher better)
        score = silhouette_score(X, clusters)
        assert score > 0.5, f"Poor cluster separation: {score}"
        
        # Validate cluster sizes (no cluster too small/large)
        cluster_sizes = [sum(clusters == i) for i in range(3)]
        assert min(cluster_sizes) > len(X) * 0.1, "Cluster too small (<10%)"
        assert max(cluster_sizes) < len(X) * 0.7, "Cluster too large (>70%)"
    ```

### 3. Reinforcement Learning

**Definition**: Learn by trial-and-error through rewards/penalties.

**Use Cases**:
- Game AI (AlphaGo, chess bots), robotics (autonomous navigation), recommendation systems (personalized content)

**QA Focus**:
    ```python
    # Test RL agent (simulated environment)
    import gym
    
    def test_cartpole_agent():
        env = gym.make('CartPole-v1')
        agent = load_trained_agent()
        
        rewards = []
        for episode in range(100):
            state = env.reset()
            total_reward = 0
            
            for step in range(500):
                action = agent.select_action(state)
                state, reward, done, _ = env.step(action)
                total_reward += reward
                
                if done:
                    break
            
            rewards.append(total_reward)
        
        # Validate agent performance (avg reward > threshold)
        avg_reward = sum(rewards) / len(rewards)
        assert avg_reward > 450, f"Agent performance below target: {avg_reward}"
    ```

---

## AI Lifecycle and Testing Touchpoints

### AI Development Lifecycle

    ```mermaid
    graph LR
        A[Data Collection] --> B[Data Preparation]
        B --> C[Model Training]
        C --> D[Model Evaluation]
        D --> E{Meets Criteria?}
        E -->|No| C
        E -->|Yes| F[Model Deployment]
        F --> G[Monitoring]
        G -->|Drift Detected| C
        
        style A fill:#e1f5ff
        style B fill:#e1f5ff
        style C fill:#fff4e1
        style D fill:#ffe1f5
        style F fill:#e7ffe1
        style G fill:#ffe1e1
    ```

### Testing Touchpoints

| Phase | QA Activities |
|-------|---------------|
| **Data Collection** | Validate data sources, check data licenses, verify consent (GDPR) |
| **Data Preparation** | Test data quality (completeness, accuracy), validate train/test split, check for data leakage |
| **Model Training** | Monitor training metrics (loss, accuracy), validate hyperparameters, test reproducibility |
| **Model Evaluation** | Test on holdout set, validate metrics (accuracy, precision, recall, F1), test edge cases |
| **Model Deployment** | Test inference latency, validate API contracts, load testing |
| **Monitoring** | Track model drift, monitor prediction distribution, alert on anomalies |

---

## AI Testing Strategies

### 1. Data Quality Testing

**Critical Principle**: Model quality ≤ Data quality (garbage in → garbage out)

**Tests**:
    ```python
    # Test training data quality
    def test_training_data_quality():
        train_df = pd.read_csv('training_data.csv')
        
        # Completeness: No excessive nulls
        null_pct = train_df.isnull().sum() / len(train_df) * 100
        assert null_pct.max() < 5, f"Column with {null_pct.max():.1f}% nulls"
        
        # Balance: Classes not too imbalanced (for classification)
        class_distribution = train_df['label'].value_counts(normalize=True)
        assert class_distribution.min() > 0.1, "Class imbalance >90/10"
        
        # Duplicates: No duplicate rows
        duplicates = train_df.duplicated().sum()
        assert duplicates == 0, f"{duplicates} duplicate rows found"
        
        # Outliers: No extreme outliers (statistical check)
        numeric_cols = train_df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_cols:
            q1, q3 = train_df[col].quantile([0.25, 0.75])
            iqr = q3 - q1
            outliers = train_df[(train_df[col] < q1 - 3*iqr) | (train_df[col] > q3 + 3*iqr)]
            assert len(outliers) < len(train_df) * 0.01, f"{col}: {len(outliers)} outliers"
    ```

### 2. Model Performance Testing

**Key Metrics**:

| Metric | Formula | When to Use |
|--------|---------|-------------|
| **Accuracy** | (TP+TN) / Total | Balanced classes |
| **Precision** | TP / (TP+FP) | Cost of false positives high (spam filter) |
| **Recall** | TP / (TP+FN) | Cost of false negatives high (cancer detection) |
| **F1 Score** | 2 × (Precision × Recall) / (Precision + Recall) | Balance precision/recall |
| **AUC-ROC** | Area under ROC curve | Overall discriminative ability |

**Confusion Matrix**:
Code





            Predicted
          Spam | Not Spam
Actual Spam TP | FN Not Spam FP | TN

TP = True Positive (correctly predicted spam) TN = True Negative (correctly predicted not spam) FP = False Positive (incorrectly predicted spam) FN = False Negative (incorrectly predicted not spam)

Code






**Test Example**:
```python
from sklearn.metrics import confusion_matrix, classification_report

def test_model_performance():
    y_true = [0, 1, 0, 1, 1, 0, 1, 0]  # Ground truth
    y_pred = model.predict(X_test)
    
    # Generate confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    print(cm)
    
    # Classification report
    report = classification_report(y_true, y_pred, target_names=['Not Spam', 'Spam'])
    print(report)
    
    # Validate minimum thresholds
    from sklearn.metrics import precision_score, recall_score
    assert precision_score(y_true, y_pred) > 0.85
    assert recall_score(y_true, y_pred) > 0.80
3. Bias and Fairness Testing
Definition: Ensure AI doesn't discriminate based on protected attributes (race, gender, age).

Test Example:

python





# Test for gender bias in hiring model
def test_gender_bias():
    # Test data with same qualifications, different genders
    male_candidate = {"experience": 5, "education": "Master", "gender": "M"}
    female_candidate = {"experience": 5, "education": "Master", "gender": "F"}
    
    male_score = hiring_model.predict_proba([male_candidate])[0][1]  # Prob of hire
    female_score = hiring_model.predict_proba([female_candidate])[0][1]
    
    # Validate no significant bias (within 5% tolerance)
    assert abs(male_score - female_score) < 0.05, \
        f"Gender bias detected: M={male_score:.2f}, F={female_score:.2f}"
Fairness Metrics:

Demographic Parity: P(positive | Group A) ≈ P(positive | Group B)
Equal Opportunity: P(positive | actual positive, Group A) ≈ P(positive | actual positive, Group B)
Equalized Odds: Both true positive rate and false positive rate equal across groups
4. Adversarial Testing
Definition: Test model robustness against malicious inputs.

Test Example:

python





# Adversarial attack on image classifier
def test_adversarial_robustness():
    # Original image correctly classified as "cat"
    original_image = load_image('cat.jpg')
    assert model.predict(original_image) == 'cat'
    
    # Add small perturbation (invisible to human eye)
    epsilon = 0.01
    perturbation = epsilon * np.sign(np.random.randn(*original_image.shape))
    adversarial_image = original_image + perturbation
    
    # Model should still predict "cat" (robust to small noise)
    prediction = model.predict(adversarial_image)
    assert prediction == 'cat', f"Adversarial attack succeeded: predicted {prediction}"
5. Model Drift Testing
Definition: Monitor if model performance degrades over time (data distribution changes).

Test Example:

python





# Detect data drift (production vs. training distribution)
from scipy.stats import ks_2samp

def test_data_drift():
    # Training data distribution
    train_feature = train_df['age'].values
    
    # Production data distribution (last 7 days)
    prod_feature = prod_df['age'].values
    
    # Kolmogorov-Smirnov test (p-value < 0.05 indicates drift)
    statistic, p_value = ks_2samp(train_feature, prod_feature)
    
    assert p_value > 0.05, f"Data drift detected: p={p_value:.4f}"
Explainability and Interpretability
Why Explainability Matters
Trust: Users need to understand AI decisions (especially high-stakes: healthcare, finance)
Debugging: Identify why model makes errors
Compliance: EU GDPR Article 22 (right to explanation), US Equal Credit Opportunity Act
Techniques
1. Feature Importance (Global Explainability):

python





# Which features most influence predictions?
import shap

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Plot feature importance
shap.summary_plot(shap_values, X_test)

# Test: Most important feature is expected
feature_importance = abs(shap_values).mean(axis=0)
most_important = X_test.columns[feature_importance.argmax()]
assert most_important == 'credit_score', f"Unexpected top feature: {most_important}"
2. LIME (Local Explainability - single prediction):

python





from lime.lime_tabular import LimeTabularExplainer

def test_loan_rejection_explanation():
    # Applicant denied loan
    applicant = {"income": 30000, "credit_score": 550, "debt": 50000}
    prediction = loan_model.predict([applicant])[0]
    assert prediction == 'denied'
    
    # Generate explanation
    explainer = LimeTabularExplainer(X_train, mode='classification')
    explanation = explainer.explain_instance(applicant, loan_model.predict_proba)
    
    # Validate top reason is low credit score
    top_reason = explanation.as_list()[0][0]
    assert 'credit_score' in top_reason, f"Expected credit_score, got {top_reason}"
AI Ethics and Responsible AI
Core Principles
Fairness: No discrimination based on protected attributes
Transparency: Explain how AI makes decisions
Privacy: Protect user data (differential privacy, federated learning)
Accountability: Clear ownership of AI outcomes
Safety: Robust to adversarial attacks, fail-safe mechanisms
Sustainability: Environmental impact of training (carbon footprint)
QA Checklist for Responsible AI
 Bias testing: Validated across demographic groups
 Explainability: Model decisions interpretable by stakeholders
 Privacy: PII anonymized, consent obtained, GDPR compliant
 Transparency: Model card published (performance, limitations, intended use)
 Safety: Adversarial robustness tested, fallback mechanisms
 Human oversight: Human-in-the-loop for high-stakes decisions
 Auditability: Logging enabled (inputs, outputs, model versions)
Interview Questions
Basic (0-3 years)
Q1: What's the difference between AI and ML?
A1: AI is broader (any intelligent system, including rule-based). ML is subset that learns from data without explicit programming. All ML is AI, but not all AI is ML.

Q2: Explain supervised vs. unsupervised learning.
A2: Supervised = learn from labeled data (input-output pairs), e.g., spam classification. Unsupervised = find patterns in unlabeled data, e.g., customer clustering. Supervised needs ground truth, unsupervised doesn't.

Advanced (4-8 years)
Q3: How do you test for bias in AI models?
A3: (1) Identify protected attributes (gender, race, age), (2) Create test sets with same qualifications, different attributes, (3) Validate predictions similar across groups (within tolerance), (4) Use fairness metrics (demographic parity, equal opportunity), (5) Test intersectionality (Black female vs. white male).

Q4: What is overfitting and how to detect it?
A4: Model memorizes training data instead of learning patterns. Detection: High accuracy on train set, low on test set (generalization gap). Prevention: Cross-validation, regularization, more training data, simpler model.

Scenario (8-12 years)
Q5: Production AI model's accuracy dropped from 95% to 75%. Troubleshoot?
A5: (1) Data drift: Compare prod data distribution to training (KS test), (2) Concept drift: Business logic changed (e.g., fraud patterns evolved), (3) Data quality: Check for missing values, outliers in prod data, (4) Model degradation: Retrain with recent data, (5) Bug: Validate inference pipeline (preprocessing, feature engineering), (6) Adversarial attack: Check for malicious inputs.

Architect (12+ years)
Q6: Design AI testing strategy for autonomous vehicle perception system (safety-critical)?
A6: (1) Data: Diverse scenarios (weather, lighting, road types), 10M+ labeled images, (2) Model validation: 99.99% accuracy on test set, adversarial robustness tested, (3) Edge cases: Rare events (animals, debris, construction), (4) Simulation: Test in virtual environment (Unity, Carla) before road, (5) Shadow mode: Run in prod without control, compare to human, (6) Fail-safe: Fallback to safe stop if confidence <threshold, (7) Continuous monitoring: Track prediction distribution, alert on drift, (8) Compliance: ISO 26262 (automotive safety), regulatory approvals.

Frequently Asked Questions
Q1: How much training data is enough?
A1: Rule of thumb: 10x examples per feature for traditional ML, 1000x for deep learning. Depends on complexity: Simple (linear regression) needs less, complex (image classification) needs millions. Use learning curves to assess.

Q2: Train/test split best practices?
A2: Standard: 70/30 or 80/20. Use stratified split (maintain class distribution). Critical: No data leakage (test data in training), temporal split for time-series (train on past, test on future).

Q3: What is cross-validation and when to use?
A3: Split data into K folds, train on K-1, test on 1, rotate. Reduces variance in performance estimate. Use when data limited, not for large datasets (expensive). Common: 5-fold or 10-fold CV.

Q4: How to handle imbalanced classes (99% negative, 1% positive)?
A4: (1) Resampling: Oversample minority (SMOTE), undersample majority, (2) Class weights: Penalize misclassifying minority more, (3) Metrics: Use precision/recall/F1 instead of accuracy, (4) Ensemble: Combine multiple models.

Q5: Difference between model accuracy and business value?
A5: High accuracy ≠ business value. Example: 99% accuracy detecting fraud, but misses high-value fraud. Focus on business metric ($ saved, customer retention) not just accuracy. Align model optimization to business KPI.

Q6: How to test AI model reproducibility?
A6: (1) Seed: Fix random seed, (2) Environment: Document library versions (requirements.txt), (3) Data: Version training data (DVC, MLflow), (4) Code: Version control model code (Git), (5) Test: Re-train model, validate same metrics (within tolerance).

Q7: What is transfer learning and when to use?
A7: Use pre-trained model (trained on large dataset) as starting point, fine-tune on your data. Use when: (1) Limited data, (2) Similar problem (image classification → medical image classification), (3) Speed (weeks → days). Test by comparing to training from scratch.

Q8: How to validate AI model in production?
A8: (1) A/B testing: Deploy to 5% traffic, compare to baseline, (2) Shadow mode: Run new model alongside old, log predictions without using, (3) Canary release: Gradual rollout (5% → 25% → 100%), (4) Monitoring: Track latency, error rate, prediction distribution.

Q9: What is the curse of dimensionality?
A9: As feature count increases, data becomes sparse (distance between points increases). Requires exponentially more data. Solution: Feature selection, dimensionality reduction (PCA), regularization.

Q10: How to test AI explainability?
A10: (1) Feature importance: Validate expected features top-ranked (SHAP, LIME), (2) Sanity check: Change important feature, prediction should change significantly, (3) Stakeholder review: Domain expert validates explanations make sense, (4) Compliance: Confirm explanations meet regulatory requirements.

Q11: Difference between online and offline evaluation?
A11: Offline: Test on historical data (fast, cheap, reproducible). Online: Test in production with real users (A/B testing, more accurate but slow/expensive). Use offline for development, online for final validation.

Q12: How to handle missing values in AI training data?
A12: (1) Remove: Drop rows with nulls (if <5%), (2) Impute: Fill with mean/median/mode (numeric), most frequent (categorical), (3) Model: Predict missing values, (4) Indicator: Add binary column (is_missing) as feature. Test impact on model performance.

Q13: What is ensemble learning?
A13: Combine multiple models to improve performance. Types: (1) Bagging: Train on random subsets (Random Forest), (2) Boosting: Train sequentially, focus on errors (XGBoost, AdaBoost), (3) Stacking: Use model outputs as features for meta-model. Test by comparing to single model.

Q14: How to test AI model latency?
A14: (1) Unit test: Measure inference time (single prediction <100ms target), (2) Load test: 1000 concurrent requests, validate p95 latency <SLA, (3) Optimization: Model compression (quantization, pruning), batching, caching.

Q15: What is federated learning?
A15: Train model across decentralized devices (phones, hospitals) without sharing raw data (privacy). Each device trains locally, shares model updates. Test by validating: (1) Model converges, (2) No data leakage, (3) Performance comparable to centralized training.

Q16: How to validate AI model version control?
A16: (1) Model registry: Track models (MLflow, SageMaker Model Registry), (2) Metadata: Store metrics, hyperparameters, training data version, (3) Rollback: Ability to revert to previous version, (4) Test: Deploy old version, validate predictions match historical.

Q17: What is AutoML and should QA use it?
A17: Automated machine learning (auto feature engineering, model selection, hyperparameter tuning). QA use: Yes for baseline (fast prototyping), but validate: (1) Model choice makes sense, (2) No data leakage, (3) Explainability maintained, (4) Not black-box (understand what AutoML did).

Q18: How to test AI for edge cases?
A18: (1) Boundary analysis: Test min/max values, (2) Adversarial: Craft inputs designed to fool model, (3) Rare events: Collect long-tail examples (uncommon scenarios), (4) Synthetic: Generate edge cases (data augmentation), (5) Production logs: Mine production for unusual inputs.

Q19: What is model calibration?
A19: Ensure predicted probabilities match actual frequencies. Example: Of all predictions with 70% confidence, 70% should be correct. Test with calibration plots (predicted vs. actual). Fix with Platt scaling or isotonic regression.

Q20: How to test AI model security?
A20: (1) Model stealing: Validate API doesn't leak model (rate limiting, query monitoring), (2) Data poisoning: Test on corrupted training data, validate detection, (3) Adversarial robustness: Test with perturbed inputs, (4) Backdoor: Scan for triggers that change predictions, (5) Access control: Validate only authorized users can access model.

Actionable Checklists
Pre-Training QA Checklist
 Training data quality validated (completeness, accuracy, balance)
 Data lineage documented (sources, transformations)
 Bias assessment (demographic representation)
 Privacy compliance (consent, anonymization, GDPR)
 Train/test split validated (no leakage, stratified)
 Feature engineering reviewed (domain expert sign-off)
Model Evaluation QA Checklist
 Performance metrics meet thresholds (accuracy, precision, recall)
 Confusion matrix reviewed (understand error types)
 Cross-validation performed (reduce variance)
 Overfitting checked (train vs. test performance gap)
 Bias/fairness tested (across demographic groups)
 Explainability validated (SHAP, LIME)
 Edge cases tested (boundary values, adversarial)
 Reproducibility confirmed (same results on re-train)
Production Deployment QA Checklist
 Inference latency tested (p95 < SLA)
 Load testing performed (1000+ concurrent requests)
 API contract validated (input/output schemas)
 Model versioning enabled (rollback capability)
 Monitoring dashboards created (drift, latency, errors)
 Alerting configured (performance degradation, anomalies)
 A/B testing plan defined (gradual rollout)
 Incident response runbook documented
References
Books
Hands-On Machine Learning (Aurélien Géron): Practical ML guide
Interpretable Machine Learning (Christoph Molnar): Explainability techniques
Fairness and Machine Learning (Barocas, Hardt, Narayanan): Bias and fairness
The Hundred-Page Machine Learning Book (Andriy Burkov): Concise ML overview
Standards
ISO/IEC 23894: AI Risk Management
IEEE 7000: AI Ethics Standard
EU AI Act: Regulatory framework for AI systems
Tools
SHAP: https://github.com/slundberg/shap (Explainability)
LIME: https://github.com/marcotcr/lime (Local explanations)
Fairlearn: https://fairlearn.org (Bias mitigation)
MLflow: https://mlflow.org (Model tracking)
Core References: Platform-agnostic AI concepts
Stack Deltas: See Azure ML/SageMaker/Vertex AI stack files for platform-specific implementations

Previous: 05_Big_Data_Concepts.md
Next: 07_ML_Concepts_QA_Perspective.md
Up: Master Index

Code






---

**✅ FILE 6 COMPLETE** (20 FAQs included)

Ready for **FILE 7/20**? Type "next" for `07_ML_Concepts_QA_Perspective.md`.