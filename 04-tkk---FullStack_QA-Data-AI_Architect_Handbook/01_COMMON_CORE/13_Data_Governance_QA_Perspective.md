# Data Governance - QA Perspective

## Executive Summary

Data Governance establishes policies, processes, and controls to ensure data is trustworthy, secure, and compliant. From a **QA perspective**, testing governance implementations requires validating data lineage, access controls, data quality rules, retention policies, and regulatory compliance (GDPR, HIPAA, SOC 2).

**Target Audience**: Principal QA engineers (10+ years) testing enterprise data platforms, compliance systems, and governance frameworks.

---

## Why This Matters in Enterprise

### Business Impact
- **Compliance fines**: GDPR violations average €20M or 4% of revenue (€1.2B total fines 2019-2024)
- **Data breaches**: Average cost $4.45M per breach (IBM 2024)
- **Trust**: 81% of consumers won't do business with companies they don't trust with data (Cisco)

### Technical Imperative
- **Regulatory requirements**: GDPR, CCPA, HIPAA, SOC 2, ISO 27001 mandate governance controls
- **Data quality**: Poor governance → poor data quality → bad business decisions
- **Risk management**: Ungoverned data = security vulnerabilities, legal liability

### Career Value
- **High demand**: Data governance expertise in 72% of senior data roles (LinkedIn 2025)
- **Salary premium**: 35-50% higher for governance + QA skills
- **Future-proof**: Regulations increasing globally, governance skills always needed

---

## Scope and Boundaries

### In Scope
- Data governance frameworks (policies, processes, roles)
- Data quality management (profiling, rules, monitoring)
- Data lineage and cataloging
- Access control and security (RBAC, ABAC, data masking)
- Compliance testing (GDPR, HIPAA, SOC 2, CCPA)
- Data retention and archival
- Privacy and PII protection

### Out of Scope
- Platform-specific tools (Collibra, Informatica covered in stack files)
- Data security infrastructure (firewalls, encryption algorithms)
- Legal interpretation of regulations (consult legal team)

---

## Data Governance Framework

### DAMA-DMBOK Framework

    ```mermaid
    graph TD
        A[Data Governance] --> B[Data Quality]
        A --> C[Metadata Management]
        A --> D[Data Security]
        A --> E[Master Data Management]
        A --> F[Data Architecture]
        A --> G[Data Warehousing]
        A --> H[Data Integration]
        
        style A fill:#e1f5ff
        style B fill:#ffe1f5
        style C fill:#ffe1f5
        style D fill:#ffe1f5
    ```

### Governance Operating Model (RACI)

| Activity | Data Owner | Data Steward | QA | IT Security | Legal |
|----------|------------|--------------|-----|-------------|-------|
| Define Data Policies | A | C | I | C | C |
| Data Quality Rules | A | R | C | I | I |
| Access Control Policies | C | C | R | A | C |
| Compliance Audits | I | C | R | C | A |
| Data Classification | A | R | C | I | C |

**Legend**: R=Responsible, A=Accountable, C=Consulted, I=Informed

---

## Data Quality Management

### Data Quality Dimensions

    ```python
    # Test data quality dimensions
    def test_data_quality_dimensions():
        df = pd.read_sql("SELECT * FROM customers", conn)
        
        # 1. Completeness (no nulls in mandatory fields)
        mandatory_fields = ['customer_id', 'email', 'created_date']
        for field in mandatory_fields:
            null_count = df[field].isnull().sum()
            null_pct = null_count / len(df) * 100
            assert null_pct < 1.0, f"{field}: {null_pct:.2f}% null (threshold: 1%)"
        
        # 2. Validity (format checks)
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        invalid_emails = df[~df['email'].str.match(email_pattern, na=False)]
        assert len(invalid_emails) == 0, f"{len(invalid_emails)} invalid emails"
        
        # 3. Uniqueness (no duplicates)
        duplicates = df[df.duplicated(subset=['customer_id'], keep=False)]
        assert len(duplicates) == 0, f"{len(duplicates)} duplicate customer_ids"
        
        # 4. Consistency (cross-field validation)
        invalid_dates = df[df['updated_date'] < df['created_date']]
        assert len(invalid_dates) == 0, \
            f"{len(invalid_dates)} records with updated_date < created_date"
        
        # 5. Accuracy (sample verification against source)
        sample = df.sample(n=100, random_state=42)
        mismatches = verify_against_source(sample)
        accuracy = (100 - len(mismatches)) / 100 * 100
        assert accuracy >= 99.0, f"Accuracy {accuracy:.1f}% below 99% threshold"
        
        # 6. Timeliness (data freshness)
        max_age_hours = (datetime.now() - df['created_date'].max()).total_seconds() / 3600
        assert max_age_hours < 24, f"Data stale: {max_age_hours:.1f} hours old"
    ```

### Data Quality Rules

    ```python
    def test_data_quality_rules():
        # Define quality rules
        rules = [
            {
                "name": "email_format",
                "description": "Email must be valid format",
                "query": "SELECT COUNT(*) FROM customers WHERE email NOT LIKE '%@%.%'",
                "threshold": 0
            },
            {
                "name": "age_range",
                "description": "Customer age must be 18-120",
                "query": "SELECT COUNT(*) FROM customers WHERE age < 18 OR age > 120",
                "threshold": 0
            },
            {
                "name": "revenue_positive",
                "description": "Revenue must be >= 0",
                "query": "SELECT COUNT(*) FROM orders WHERE total_amount < 0",
                "threshold": 0
            }
        ]
        
        # Execute and validate rules
        for rule in rules:
            result = execute_query(rule["query"])
            violation_count = result[0][0]
            
            assert violation_count <= rule["threshold"], \
                f"Rule '{rule['name']}' failed: {violation_count} violations " \
                f"(threshold: {rule['threshold']})"
    ```

---

## Data Lineage and Cataloging

### Lineage Testing

    ```python
    def test_data_lineage():
        """Validate data lineage from source to consumption"""
        
        # Define expected lineage path
        expected_path = [
            "source_db.customers",
            "staging.customers",
            "dwh.dim_customer",
            "bi.customer_report"
        ]
        
        # Query lineage metadata (from data catalog)
        lineage = get_lineage("bi.customer_report")
        
        # Validate complete path
        actual_path = [node["table"] for node in lineage]
        assert actual_path == expected_path, \
            f"Lineage mismatch:\nExpected: {expected_path}\nActual: {actual_path}"
        
        # Validate transformations documented
        for node in lineage:
            if "transformation" in node:
                assert len(node["transformation"]) > 0, \
                    f"Missing transformation documentation for {node['table']}"
    ```

### Data Catalog Validation

    ```python
    def test_data_catalog():
        """Validate data catalog metadata accuracy"""
        
        # Get catalog entry
        catalog_entry = catalog.get_table("dwh.dim_customer")
        
        # Validate metadata completeness
        required_fields = [
            "description", "owner", "schema", "columns",
            "update_frequency", "last_updated", "lineage"
        ]
        
        for field in required_fields:
            assert field in catalog_entry, f"Missing required field: {field}"
            assert catalog_entry[field] is not None, f"Field '{field}' is null"
        
        # Validate column metadata
        for column in catalog_entry["columns"]:
            assert "name" in column, "Column missing name"
            assert "data_type" in column, f"Column {column['name']} missing data_type"
            assert "description" in column, f"Column {column['name']} missing description"
        
        # Validate schema matches actual table
        actual_schema = get_table_schema("dwh.dim_customer")
        catalog_schema = {c["name"]: c["data_type"] for c in catalog_entry["columns"]}
        
        for col_name, col_type in actual_schema.items():
            assert col_name in catalog_schema, f"Column {col_name} not in catalog"
            assert catalog_schema[col_name] == col_type, \
                f"Type mismatch for {col_name}: {catalog_schema[col_name]} vs {col_type}"
    ```

---

## Access Control and Security

### Role-Based Access Control (RBAC)

    ```python
    def test_rbac():
        """Validate role-based access control"""
        
        # Define test users with different roles
        test_users = [
            {"user": "analyst@example.com", "role": "analyst", "allowed": ["read"], "denied": ["write", "delete"]},
            {"user": "admin@example.com", "role": "admin", "allowed": ["read", "write", "delete"], "denied": []},
            {"user": "viewer@example.com", "role": "viewer", "allowed": ["read"], "denied": ["write", "delete"]}
        ]
        
        for user_config in test_users:
            # Test allowed operations
            for operation in user_config["allowed"]:
                result = execute_operation(
                    user=user_config["user"],
                    operation=operation,
                    table="dwh.dim_customer"
                )
                assert result["success"], \
                    f"User {user_config['user']} denied {operation} (should be allowed)"
            
            # Test denied operations
            for operation in user_config["denied"]:
                result = execute_operation(
                    user=user_config["user"],
                    operation=operation,
                    table="dwh.dim_customer"
                )
                assert not result["success"], \
                    f"User {user_config['user']} allowed {operation} (should be denied)"
                assert "permission denied" in result["error"].lower(), \
                    f"Wrong error message: {result['error']}"
    ```

### Attribute-Based Access Control (ABAC)

    ```python
    def test_abac():
        """Validate attribute-based access control (e.g., region-based)"""
        
        # User in US region
        us_user = "analyst_us@example.com"
        
        # Should access US customer data
        us_query = "SELECT * FROM customers WHERE region = 'US'"
        result = execute_query_as_user(us_user, us_query)
        assert result["success"], "US user denied access to US data"
        
        # Should NOT access EU customer data (GDPR)
        eu_query = "SELECT * FROM customers WHERE region = 'EU'"
        result = execute_query_as_user(us_user, eu_query)
        assert not result["success"], "US user allowed access to EU data"
        assert "region restriction" in result["error"].lower()
    ```

### Data Masking

    ```python
    def test_data_masking():
        """Validate PII masking for non-privileged users"""
        
        # Privileged user sees real data
        admin_query = "SELECT customer_id, email, ssn FROM customers LIMIT 1"
        admin_result = execute_query_as_user("admin@example.com", admin_query)
        
        assert "@" in admin_result[0]["email"], "Admin email not real"
        assert len(admin_result[0]["ssn"]) == 11, "Admin SSN not real (XXX-XX-XXXX)"
        
        # Analyst sees masked data
        analyst_result = execute_query_as_user("analyst@example.com", admin_query)
        
        assert analyst_result[0]["email"].endswith("@masked.com"), \
            f"Analyst email not masked: {analyst_result[0]['email']}"
        assert analyst_result[0]["ssn"] == "XXX-XX-XXXX", \
            f"Analyst SSN not masked: {analyst_result[0]['ssn']}"
    ```

---

## Compliance Testing

### GDPR Compliance

**Right to Access**:
    ```python
    def test_gdpr_right_to_access():
        """User can request all their personal data"""
        
        user_email = "testuser@example.com"
        
        # Submit access request
        request_id = submit_access_request(user_email)
        
        # Wait for processing (max 30 days per GDPR, test uses 1 hour)
        wait_for_completion(request_id, timeout=3600)
        
        # Retrieve data package
        data_package = get_access_request_result(request_id)
        
        # Validate completeness (all tables with user data)
        expected_tables = ["customers", "orders", "support_tickets", "preferences"]
        actual_tables = list(data_package.keys())
        
        assert set(expected_tables) == set(actual_tables), \
            f"Missing tables: {set(expected_tables) - set(actual_tables)}"
        
        # Validate data accuracy (spot check)
        assert data_package["customers"]["email"] == user_email
    ```

**Right to Erasure**:
    ```python
    def test_gdpr_right_to_erasure():
        """User can request deletion of their data"""
        
        user_id = "test_user_123"
        
        # Verify user exists
        assert user_exists(user_id), "Test user not found"
        
        # Submit deletion request
        request_id = submit_deletion_request(user_id)
        wait_for_completion(request_id, timeout=3600)
        
        # Validate user deleted from all systems
        tables = ["customers", "orders", "support_tickets", "preferences"]
        
        for table in tables:
            count = execute_query(
                f"SELECT COUNT(*) FROM {table} WHERE user_id = '{user_id}'"
            )[0][0]
            assert count == 0, f"User data still exists in {table}"
        
        # Validate audit log
        audit = get_audit_log(request_id)
        assert audit["action"] == "deletion"
        assert audit["status"] == "completed"
        assert audit["tables_affected"] == tables
    ```

**Data Minimization**:
    ```python
    def test_gdpr_data_minimization():
        """Only collect necessary data"""
        
        # Define necessary fields for customer table
        necessary_fields = ["customer_id", "email", "created_date"]
        
        # Get actual schema
        actual_schema = get_table_schema("customers")
        
        # Identify potentially unnecessary fields
        pii_fields = ["ssn", "passport_number", "drivers_license"]
        
        for field in pii_fields:
            if field in actual_schema:
                # Validate business justification documented
                justification = get_field_justification("customers", field)
                assert justification is not None, \
                    f"No justification for collecting {field}"
                assert len(justification) > 50, \
                    f"Insufficient justification for {field}: {justification}"
    ```

### HIPAA Compliance (Healthcare)

    ```python
    def test_hipaa_compliance():
        """Validate HIPAA Protected Health Information (PHI) controls"""
        
        # PHI fields must be encrypted at rest
        phi_tables = ["patients", "diagnoses", "prescriptions"]
        
        for table in phi_tables:
            encryption_status = get_table_encryption(table)
            assert encryption_status["enabled"], f"Table {table} not encrypted"
            assert encryption_status["algorithm"] in ["AES-256", "AES-128"], \
                f"Weak encryption for {table}: {encryption_status['algorithm']}"
        
        # Access to PHI must be logged
        audit_log = get_access_audit_log(table="patients", hours=24)
        
        for entry in audit_log:
            assert "user" in entry, "Missing user in audit log"
            assert "timestamp" in entry, "Missing timestamp in audit log"
            assert "action" in entry, "Missing action in audit log"
            assert "record_id" in entry, "Missing record_id in audit log"
        
        # Minimum necessary rule (users only see data needed for job)
        doctor_query = "SELECT * FROM patients"
        result = execute_query_as_user("doctor@hospital.com", doctor_query)
        
        # Doctor should only see their own patients
        for record in result:
            assert record["attending_physician"] == "doctor@hospital.com", \
                "Doctor accessed patient not under their care"
    ```

### SOC 2 Compliance

    ```python
    def test_soc2_controls():
        """Validate SOC 2 Type II controls"""
        
        # Control: Logical access controls
        # Test: Passwords must meet complexity requirements
        weak_password = "password123"
        result = create_user("test@example.com", weak_password)
        assert not result["success"], "Weak password accepted"
        assert "complexity" in result["error"].lower()
        
        # Control: Change management
        # Test: All schema changes require approval
        change_request = submit_schema_change("ALTER TABLE customers ADD COLUMN test VARCHAR(10)")
        assert change_request["status"] == "pending_approval", \
            "Schema change not requiring approval"
        
        # Control: Monitoring and incident response
        # Test: Suspicious activity triggers alert
        simulate_brute_force_attack("admin@example.com")
        
        alerts = get_security_alerts(minutes=5)
        assert any(a["type"] == "brute_force" for a in alerts), \
            "Brute force attack not detected"
    ```

---

## Data Retention and Archival

### Retention Policy Testing

    ```python
    def test_retention_policy():
        """Validate data retention policies enforced"""
        
        # Define retention policies
        policies = [
            {"table": "orders", "retention_days": 2555},  # 7 years (financial)
            {"table": "sessions", "retention_days": 90},   # 90 days (analytics)
            {"table": "audit_logs", "retention_days": 365} # 1 year (compliance)
        ]
        
        for policy in policies:
            # Check oldest record
            oldest_record = execute_query(
                f"SELECT MIN(created_date) as oldest FROM {policy['table']}"
            )[0]["oldest"]
            
            age_days = (datetime.now() - oldest_record).days
            
            # Allow 10% buffer (e.g., 7 years → 7.7 years max)
            max_age = policy["retention_days"] * 1.1
            
            assert age_days <= max_age, \
                f"Table {policy['table']} has data older than retention policy: " \
                f"{age_days} days (max: {max_age})"
    ```

### Archival Testing

    ```python
    def test_archival_process():
        """Validate archival process (move old data to cold storage)"""
        
        # Create old records (simulate)
        old_date = datetime.now() - timedelta(days=400)
        insert_test_records("sessions", created_date=old_date, count=100)
        
        # Trigger archival job
        archive_job_id = run_archival_job("sessions")
        wait_for_job_completion(archive_job_id)
        
        # Validate old records moved to archive
        active_count = execute_query(
            "SELECT COUNT(*) FROM sessions WHERE created_date < NOW() - INTERVAL 90 DAY"
        )[0][0]
        
        assert active_count == 0, \
            f"{active_count} old records still in active table"
        
        # Validate records exist in archive
        archive_count = execute_query(
            "SELECT COUNT(*) FROM sessions_archive WHERE created_date < NOW() - INTERVAL 90 DAY"
        )[0][0]
        
        assert archive_count >= 100, \
            f"Only {archive_count} records in archive (expected >= 100)"
        
        # Validate archived data is readable
        archived_records = execute_query(
            "SELECT * FROM sessions_archive LIMIT 10"
        )
        assert len(archived_records) > 0, "Cannot read archived data"
    ```

---

## Privacy and PII Protection

### PII Classification

    ```python
    def test_pii_classification():
        """Validate all PII fields are classified and tagged"""
        
        pii_patterns = {
            "email": r"email|mail",
            "phone": r"phone|mobile|tel",
            "ssn": r"ssn|social.*security",
            "address": r"address|street|city|zip",
            "dob": r"birth|dob",
            "credit_card": r"card|cc_number"
        }
        
        # Scan all tables
        tables = get_all_tables()
        
        for table in tables:
            columns = get_table_columns(table)
            
            for column in columns:
                # Check if column name matches PII pattern
                for pii_type, pattern in pii_patterns.items():
                    if re.search(pattern, column["name"], re.IGNORECASE):
                        # Validate PII tag exists
                        tags = get_column_tags(table, column["name"])
                        assert "PII" in tags or f"PII:{pii_type}" in tags, \
                            f"Column {table}.{column['name']} appears to be PII but not tagged"
    ```

### PII Encryption

    ```python
    def test_pii_encryption():
        """Validate PII encrypted at rest"""
        
        # Get all PII columns
        pii_columns = get_columns_with_tag("PII")
        
        for pii_col in pii_columns:
            table = pii_col["table"]
            column = pii_col["column"]
            
            # Check encryption status
            encryption = get_column_encryption(table, column)
            
            assert encryption["enabled"], \
                f"{table}.{column} (PII) not encrypted"
            assert encryption["algorithm"] in ["AES-256", "AES-128"], \
                f"Weak encryption for {table}.{column}: {encryption['algorithm']}"
    ```

---

## Interview Questions

### Basic (0-3 years)
**Q1**: What is data governance?  
**A1**: Policies, processes, and controls to ensure data is accurate, secure, and compliant. Includes: data quality, security, privacy, lineage, retention. Goal: Trustworthy data for business decisions.

**Q2**: Difference between data governance and data management?  
**A2**: **Governance**: Policies and oversight (what/why). **Management**: Technical execution (how). Example: Governance sets policy "PII must be encrypted", Management implements encryption.

### Advanced (4-8 years)
**Q3**: How do you test GDPR compliance?  
**A3**: (1) **Right to access**: User can download all their data, (2) **Right to erasure**: User data deleted from all systems, (3) **Consent**: Track opt-in/opt-out, (4) **Data minimization**: Only collect necessary fields, (5) **Breach notification**: Alert within 72 hours, (6) **Audit**: All tests logged for compliance proof.

**Q4**: What is data lineage and why test it?  
**A4**: Data lineage = tracing data flow from source to consumption. **Why test**: (1) Impact analysis (if source changes, what breaks?), (2) Compliance (prove data origin), (3) Debugging (find where data quality issue introduced), (4) Trust (users know data provenance).

### Scenario (8-12 years)
**Q5**: Data quality check fails (10% of emails invalid). Troubleshoot?  
**A5**: (1) **Root cause**: Check when invalids introduced (recent ETL change? source system issue?), (2) **Quarantine**: Move invalid records to separate table (don't delete, may need recovery), (3) **Fix source**: If source issue, work with source team, (4) **Backfill**: Re-process correct data, (5) **Prevent**: Add validation at ingestion (reject invalid emails), (6) **Monitor**: Alert if invalid% > 1% in future.

### Architect (12+ years)
**Q6**: Design data governance framework for global enterprise (50 countries, 100 data sources)?  
**A6**: (1) **Organization**: Central governance council (policies), regional stewards (local compliance), (2) **Policies**: Data classification (public/internal/confidential/restricted), retention (by region/regulation), access (RBAC + ABAC), (3) **Data catalog**: Centralized metadata (Collibra/Alation), auto-discovery of data sources, (4) **Quality**: Automated profiling daily, quality score per dataset (0-100), SLAs (critical data >95% quality), (5) **Lineage**: End-to-end traceability, impact analysis tools, (6) **Compliance**: Multi-regulation support (GDPR, CCPA, LGPD), region-specific data residency, (7) **Security**: Encryption at rest/transit, data masking for non-prod, audit logging, (8) **Testing**: Golden dataset (500 test cases), compliance suite (GDPR, HIPAA), quarterly audits, (9) **Monitoring**: Quality dashboards, compliance metrics, incident tracking, (10) **Training**: Mandatory governance training for all data users.

---

## Frequently Asked Questions

**Q1**: Who is responsible for data governance?  
**A1**: **Shared responsibility**: (1) **Data Owner** (business): Accountable for data quality, access policies, (2) **Data Steward** (business/IT): Implements policies, monitors quality, (3) **QA**: Tests governance controls, (4) **IT Security**: Enforces access controls, encryption, (5) **Legal**: Defines compliance requirements.

**Q2**: How to measure data governance maturity?  
**A2**: Maturity levels: (1) **Initial**: No formal governance, ad-hoc processes, (2) **Managed**: Basic policies, manual enforcement, (3) **Defined**: Documented processes, some automation, (4) **Quantitatively managed**: Metrics tracked, continuous improvement, (5) **Optimizing**: Fully automated, predictive quality, proactive governance. Assess using frameworks (DAMA, DCAM).

**Q3**: What is a data catalog and why is it important?  
**A3**: **Data catalog** = searchable inventory of all data assets (metadata, lineage, owners, quality). **Importance**: (1) **Discovery**: Users find data easily, (2) **Understanding**: Metadata explains what data means, (3) **Trust**: Quality scores show data reliability, (4) **Compliance**: Track sensitive data (PII, PHI). Tools: Collibra, Alation, Informatica, AWS Glue Data Catalog.

**Q4**: How to handle conflicting data regulations (GDPR vs. CCPA)?  
**A4**: (1) **Strictest standard**: Implement most restrictive requirement (if GDPR stricter, use GDPR), (2) **Region-specific**: Different policies per region (EU: GDPR, California: CCPA), (3) **Unified approach**: Design system to meet all regulations (right to access, erasure, portability), (4) **Legal review**: Consult legal team for conflicts.

**Q5**: What is data lineage vs. data provenance?  
**A5**: **Lineage** = flow of data (source → transformations → destination). **Provenance** = origin and history (who created, when, why, how changed). Lineage = technical path, Provenance = detailed audit trail.

**Q6**: How to test data quality in production?  
**A6**: (1) **Automated monitoring**: Run quality checks hourly/daily, (2) **Anomaly detection**: Alert on volume spikes, null% increases, (3) **SLA tracking**: Monitor against quality SLAs (>95% completeness), (4) **Sampling**: Profile 1% of data daily (cost-effective), (5) **User feedback**: Capture data quality issues from users.

**Q7**: What is master data management (MDM)?  
**A7**: **MDM** = single source of truth for critical entities (customers, products, suppliers). Consolidates data from multiple sources, resolves duplicates, maintains golden record. **QA focus**: Test de-duplication logic, match rules, data quality of golden records.

**Q8**: How to implement data masking?  
**A8**: (1) **Static masking**: Mask data in non-prod (dev, test) databases, (2) **Dynamic masking**: Real-time masking based on user role (analysts see masked SSN), (3) **Techniques**: Substitution (real SSN → fake SSN), shuffling (swap values), nulling (replace with NULL), (4) **Testing**: Verify privileged users see real data, others see masked.

**Q9**: What is data sovereignty?  
**A9**: Legal requirement that data must be stored/processed in specific geographic region. Example: EU data must stay in EU (GDPR), China data must stay in China. **Testing**: Validate data residency (EU customer data in EU datacenter), cross-region transfers comply with regulations.

**Q10**: How to test data retention policies?  
**A10**: (1) **Scheduled jobs**: Verify deletion jobs run on schedule (nightly), (2) **Data age**: Check oldest record <= retention period, (3) **Deletion accuracy**: Validate only old data deleted (not recent), (4) **Audit trail**: Deletion logged with user, timestamp, record count, (5) **Restore**: Test ability to restore archived data if needed.

**Q11**: What is data classification?  
**A11**: Categorizing data by sensitivity: **Public** (can be shared), **Internal** (employees only), **Confidential** (restricted access), **Restricted** (highly sensitive, PII/PHI). **Testing**: Validate classification tags applied, access controls match classification.

**Q12**: How to handle data breaches?  
**A12**: (1) **Detection**: Monitoring alerts on unusual access patterns, (2) **Containment**: Disable compromised accounts, revoke access, (3) **Investigation**: Forensics to determine scope (what data accessed), (4) **Notification**: Inform users within regulation timeframe (GDPR: 72 hours), (5) **Remediation**: Fix vulnerability, reset credentials, (6) **Testing**: Quarterly breach simulation drills.

**Q13**: What is data anonymization vs. pseudonymization?  
**A13**: **Anonymization**: Remove PII irreversibly (cannot re-identify). **Pseudonymization**: Replace PII with pseudonym (reversible with key). GDPR allows pseudonymized data for analytics, anonymized data not subject to GDPR. **Testing**: Verify anonymized data cannot be re-identified, pseudonymized data requires key to reverse.

**Q14**: How to test data access controls at scale?  
**A14**: (1) **RBAC matrix**: Test all role-permission combinations (admin, analyst, viewer), (2) **Automated tests**: Script access tests (thousands of combinations), (3) **Regression**: Re-test after every permission change, (4) **Audit**: Review access logs weekly for violations, (5) **Penetration**: Security team attempts unauthorized access.

**Q15**: What is data quality score?  
**A15**: Composite metric (0-100) measuring overall data quality. Example: `Quality Score = (40% completeness + 30% accuracy + 20% timeliness + 10% consistency)`. **Usage**: Prioritize cleanup (low-score datasets), SLAs (critical data >95% score), dashboards (track trends).

**Q16**: How to validate data lineage accuracy?  
**A16**: (1) **Manual trace**: Follow data flow manually (source → staging → DWH → BI), compare to documented lineage, (2) **Automated discovery**: Tools scan code (SQL, Python) to build lineage, validate against catalog, (3) **Impact testing**: Change source field, confirm downstream updates match lineage.

**Q17**: What is a data steward?  
**A17**: **Role**: Business or technical person responsible for data quality, metadata, policies for specific domain (customer data steward, product data steward). **Responsibilities**: Define quality rules, resolve data issues, approve data access, maintain catalog. **QA interaction**: Partner on testing, provide business validation.

**Q18**: How to test CCPA compliance (California Consumer Privacy Act)?  
**A18**: Similar to GDPR but California-specific: (1) **Right to know**: User can request data collected, (2) **Right to delete**: User can request deletion, (3) **Right to opt-out**: User can opt-out of data sale, (4) **Non-discrimination**: Cannot penalize users who opt-out. Test same as GDPR but add opt-out testing.

**Q19**: What is a data quality SLA?  
**A19**: **Service Level Agreement** for data quality. Example: "Customer data will be 99% complete, 99.5% accurate, refreshed within 2 hours." **Components**: Metrics (completeness, accuracy), targets (99%), measurement frequency (daily), consequences (penalty if breached). **QA role**: Monitor SLAs, report violations.

**Q20**: How to test data governance in multi-cloud environments?  
**A20**: (1) **Unified catalog**: Single catalog across AWS, Azure, GCP, (2) **Cross-cloud lineage**: Trace data moving between clouds, (3) **Access federation**: SSO works across all clouds, (4) **Compliance**: Each cloud meets same standards (encryption, retention), (5) **Testing**: Validate governance controls in each cloud, cross-cloud data flows.

---

## Actionable Checklists

### Data Quality Testing Checklist
- [ ] Completeness validated (null checks on mandatory fields)
- [ ] Validity tested (format, range, business rules)
- [ ] Uniqueness verified (no duplicates on PKs)
- [ ] Consistency checked (cross-field validation)
- [ ] Accuracy measured (sample vs. source)
- [ ] Timeliness confirmed (data freshness within SLA)
- [ ] Quality rules automated (run daily)
- [ ] Quality metrics tracked (dashboards, trends)

### Data Governance Compliance Checklist
- [ ] Data catalog complete (all datasets documented)
- [ ] Data lineage mapped (source to consumption)
- [ ] Data classification applied (public/internal/confidential/restricted)
- [ ] Access controls tested (RBAC/ABAC)
- [ ] PII identified and tagged
- [ ] PII encrypted at rest
- [ ] Data masking validated (non-prod environments)
- [ ] Retention policies enforced (archival tested)
- [ ] Compliance validated (GDPR, HIPAA, SOC 2 as applicable)
- [ ] Audit logging enabled (all access tracked)

### GDPR Compliance Testing Checklist
- [ ] Right to access tested (user can download data)
- [ ] Right to erasure tested (user data deleted)
- [ ] Right to portability tested (data export in standard format)
- [ ] Consent management tested (opt-in/opt-out)
- [ ] Data minimization validated (only necessary fields)
- [ ] Breach notification tested (alert within 72 hours)
- [ ] DPO contact available (Data Protection Officer)
- [ ] Privacy policy published (accessible to users)
- [ ] Data processing agreements (with vendors)
- [ ] Audit trail maintained (compliance evidence)

---

## References

### Frameworks
- **DAMA-DMBOK**: Data Management Body of Knowledge (governance framework)
- **DCAM**: Data Management Capability Assessment Model (maturity model)
- **ISO 8000**: Data quality standard

### Regulations
- **GDPR**: EU General Data Protection Regulation
- **CCPA**: California Consumer Privacy Act
- **HIPAA**: Health Insurance Portability and Accountability Act
- **SOC 2**: Service Organization Control 2 (security controls)

### Tools
- **Collibra**: Data governance platform (catalog, lineage, quality)
- **Alation**: Data catalog and governance
- **Informatica**: Data quality and governance suite
- **Talend**: Data integration and governance

### Books
- **Data Governance: How to Design, Deploy and Sustain an Effective Data Governance Program** (John Ladley)
- **Non-Invasive Data Governance** (Robert Seiner): Practical governance approach

---

**Core References**: Platform-agnostic governance concepts  
**Stack Deltas**: Platform-specific governance tools (AWS Lake Formation, Azure Purview) in stack files

**Previous**: [12_AI_Agentic_Concepts_QA_Perspective.md](./12_AI_Agentic_Concepts_QA_Perspective.md)  
**Next**: [14_AI_BI_Concepts_QA_Perspective.md](./14_AI_BI_Concepts_QA_Perspective.md)  
**Up**: [Master Index](../00_MASTER_INDEX.md)