# QA Concepts - Foundational Quality Engineering Principles

## Executive Summary

Quality Assurance in data and AI systems requires a paradigm shift from traditional software testing. This document establishes **foundational QA principles** applicable across data warehousing, ETL pipelines, big data platforms, and AI/ML systems.

**Target Audience**: QA professionals (5+ years) transitioning to data/AI domains or seeking architect-level mastery.

---

## Why This Matters in Enterprise

### Business Impact
- **Quality costs**: 15-40% of total IT budget spent on rework due to poor quality (NIST)
- **Production incidents**: 60% trace back to insufficient testing in data pipelines (DataKitchen 2025)
- **Revenue loss**: $1.7M average cost per hour of data downtime (Gartner)

### Technical Imperative
- **Shift-left strategy**: Defects found in production cost 100x more than those caught in design
- **Continuous testing**: Modern data systems require testing in CI/CD pipelines
- **Data-specific risks**: Schema drift, data quality degradation, model drift in ML systems

### Career Value
- **Market demand**: 73% of organizations report QA skill gaps in data/AI testing (LinkedIn 2025)
- **Salary premium**: Data QA engineers earn 20-30% more than general QA roles
- **Future-proof skills**: AI/ML testing expertise positions you for emerging fields

---

## Scope and Boundaries

### In Scope
- QA fundamentals (test design techniques, test levels, test types)
- SDLC integration (Agile, DevOps, DataOps, MLOps)
- Test strategy and planning
- Defect management and root cause analysis
- Quality metrics and KPIs
- Test automation frameworks
- Risk-based testing approaches

### Out of Scope
- Domain-specific testing (covered in specialized files: DWH, ETL, ML, etc.)
- Platform-specific tools (covered in stack files)
- Programming language tutorials (see practice files for code examples)

---

## QA Fundamentals

### Test Levels

    ```mermaid
    graph TD
        A[Unit Testing] --> B[Integration Testing]
        B --> C[System Testing]
        C --> D[Acceptance Testing]
        
        A1[Component level] -.-> A
        B1[Interface level] -.-> B
        C1[End-to-end] -.-> C
        D1[Business validation] -.-> D
        
        style A fill:#e1f5ff
        style B fill:#fff4e1
        style C fill:#ffe1f5
        style D fill:#e7ffe1
    ```

**Unit Testing (Data Context)**:
- Test individual SQL queries, Python functions, Spark transformations
- Mock external dependencies (databases, APIs)
- Example: Test a date parsing function with valid/invalid inputs

**Integration Testing (Data Context)**:
- Test interactions between pipeline stages (extract → transform → load)
- Validate schema compatibility between systems
- Example: Verify source system → staging → DWH data flow

**System Testing (Data Context)**:
- End-to-end pipeline validation
- Performance testing at scale (million+ rows)
- Example: Full ETL run from source refresh to BI dashboard update

**Acceptance Testing (Data Context)**:
- Business user validation (data quality, report accuracy)
- Regulatory compliance checks (GDPR, HIPAA)
- Example: CFO validates month-end financial reports against GL system

---

## Test Design Techniques

### Equivalence Partitioning

**Definition**: Divide input domain into classes where all values should behave similarly.

**Example (Age Field Validation)**:
- **Valid partition**: 0-120 (pick test value: 25)
- **Invalid low**: <0 (pick test value: -5)
- **Invalid high**: >120 (pick test value: 150)

**Data Context Example (Transaction Amount)**:
    ```python
    # Partitions for transaction_amount validation
    # Valid: 0.01 to 999,999.99
    # Invalid: <=0, >=1,000,000, null, non-numeric
    
    test_cases = [
        (100.50, "valid"),      # Valid partition
        (0.00, "invalid"),      # Boundary: zero
        (-50, "invalid"),       # Invalid: negative
        (1_000_000, "invalid"), # Invalid: exceeds max
        (None, "invalid"),      # Invalid: null
        ("abc", "invalid")      # Invalid: non-numeric
    ]
    ```

### Boundary Value Analysis (BVA)

**Definition**: Test values at boundaries of partitions (edges where behavior changes).

**Example (Date Range: 2024-01-01 to 2024-12-31)**:
- Test: 2023-12-31 (before range)
- Test: 2024-01-01 (start boundary) ✅
- Test: 2024-06-15 (mid-range)
- Test: 2024-12-31 (end boundary) ✅
- Test: 2025-01-01 (after range)

### Decision Table Testing

**Example (Discount Calculation)**:

| Customer Type | Order Amount | Loyalty Member? | Discount |
|--------------|--------------|-----------------|----------|
| Retail       | <$100        | No              | 0%       |
| Retail       | <$100        | Yes             | 5%       |
| Retail       | >=$100       | No              | 10%      |
| Retail       | >=$100       | Yes             | 15%      |
| Wholesale    | Any          | Any             | 20%      |

**Test Cases**: One per row = 5 test cases

### Pairwise Testing

**Use Case**: Reduce combinatorial explosion when testing multiple parameters.

**Example (ETL Configuration)**:
- Source: [MySQL, PostgreSQL, Oracle] (3 options)
- Destination: [Snowflake, Redshift, BigQuery] (3 options)
- Load Type: [Full, Incremental] (2 options)
- **Full factorial**: 3 × 3 × 2 = 18 test cases
- **Pairwise**: ~9 test cases (covers all pairs of parameter interactions)

---

## Test Types

### Functional Testing
**Purpose**: Verify system behavior matches requirements  
**Data Context**: Validate data transformations, business rule implementation  
**Example**: Ensure sales tax calculation = sales_amount × tax_rate for all states

### Non-Functional Testing

**Performance Testing**:
- **Load testing**: System behavior under expected load (10K concurrent users)
- **Stress testing**: System behavior under peak load (100K concurrent users)
- **Soak testing**: System stability over extended period (72-hour ETL run)
- **Data Context**: Query response time <5sec for 1B row fact table

**Security Testing**:
- **Authentication**: Verify identity (SSO, MFA)
- **Authorization**: Verify access controls (RBAC, ABAC)
- **Encryption**: Data at rest (AES-256), data in transit (TLS 1.3)
- **Data Context**: PII/PHI access logging, data masking for non-prod environments

**Usability Testing**:
- **BI Dashboard**: Can business user find sales by region without training?
- **Data Catalog**: Can data engineer discover customer dimension in <2 minutes?

---

## SDLC Integration

### Agile/Scrum Context

**Sprint Planning**:
- QA reviews user stories for testability
- Acceptance criteria = test conditions
- Estimate testing effort (story points)

**During Sprint**:
- QA writes test cases as developers write code (parallel activity)
- Daily standup: Blockers, testing progress
- Continuous exploratory testing

**Sprint Review**:
- Demo tested features to stakeholders
- QA sign-off required for "Definition of Done"

**Retrospective**:
- What QA practices worked/didn't work?
- Escaped defects root cause analysis

### DevOps/DataOps Integration

    ```mermaid
    graph LR
        A[Code Commit] --> B[CI Pipeline]
        B --> C[Automated Tests]
        C --> D{Pass?}
        D -->|Yes| E[Deploy to Test]
        D -->|No| F[Notify Developer]
        E --> G[Manual QA]
        G --> H{Approve?}
        H -->|Yes| I[Deploy to Prod]
        H -->|No| F
        
        style C fill:#e1f5ff
        style G fill:#ffe1f5
    ```

**CI Pipeline QA Gates**:
1. **Unit tests** (Python/SQL): Must pass 100%
2. **Data quality checks**: Completeness, validity, consistency
3. **Schema validation**: DDL diff against baseline
4. **Performance tests**: Query execution <SLA threshold
5. **Security scan**: No PII in logs, credentials encrypted

**Shift-Left Testing**:
- Test data generation in dev environments
- Schema review before code commit
- Static code analysis (linting, SQL anti-patterns)

---

## Test Strategy and Planning

### Test Strategy Document Components

1. **Scope**: Systems under test, integrations, data sources
2. **Approach**: Manual vs. automated ratio (target: 80% automated)
3. **Entry/Exit Criteria**: When to start/stop testing
4. **Resources**: Team size, skills, tools
5. **Schedule**: Test phases aligned to release calendar
6. **Risks**: Data availability, environment stability
7. **Deliverables**: Test plan, test cases, defect reports

### Risk-Based Testing

**Risk Matrix**:

| Impact | Probability | Priority | Example |
|--------|------------|----------|---------|
| High   | High       | Critical | Financial reconciliation failure |
| High   | Low        | High     | Data breach due to encryption bug |
| Low    | High       | Medium   | Dashboard refresh delay |
| Low    | Low        | Low      | Cosmetic UI issue in internal tool |

**Test Prioritization**:
- **Critical risk**: 100% test coverage, automate, run every build
- **High risk**: 90% coverage, automate key paths, run daily
- **Medium risk**: 70% coverage, mix of manual/automated, run weekly
- **Low risk**: Exploratory testing, manual, run before release

---

## Defect Management

### Defect Lifecycle

    ```mermaid
    stateDiagram-v2
        [*] --> New
        New --> Open: Triage
        Open --> InProgress: Assigned
        InProgress --> Fixed: Developer completes
        Fixed --> Verified: QA confirms fix
        Fixed --> Reopened: QA finds issue
        Reopened --> InProgress
        Verified --> Closed
        Open --> Deferred: Low priority
        Open --> Rejected: Not a defect
    ```

### Defect Report Template

**ID**: DEF-2024-001  
**Title**: Sales fact table missing 10% of transactions on 2024-09-07  
**Severity**: Critical (data loss)  
**Priority**: P1 (immediate fix required)  
**Environment**: Production DWH  
**Steps to Reproduce**:
1. Run: `SELECT COUNT(*) FROM fact_sales WHERE date_key=20240907;`
2. Expected: 1,000,000 rows (per source system count)
3. Actual: 900,000 rows (10% missing)

**Root Cause**: ETL timeout after 90 minutes; source extract incomplete  
**Fix**: Increase timeout to 120 minutes, add checkpoint/restart logic  
**Verification**: Re-run ETL for 2024-09-07, confirm 1M rows loaded

---

## Quality Metrics and KPIs

### Test Effectiveness Metrics

**Defect Detection Rate (DDR)**: