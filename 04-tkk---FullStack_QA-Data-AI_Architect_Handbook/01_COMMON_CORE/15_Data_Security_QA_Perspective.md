# Data Security - QA Perspective

## Executive Summary

Data Security protects data from unauthorized access, breaches, corruption, and theft throughout its lifecycle. From a **QA perspective**, testing security requires validating authentication, authorization, encryption, network security, audit logging, vulnerability management, and compliance with security standards.

**Target Audience**: Principal QA engineers (10+ years) testing enterprise data platforms, security controls, and compliance frameworks.

---

## Why This Matters in Enterprise

### Business Impact
- **Data breach cost**: $4.45M average per breach (IBM 2024)
- **Compliance fines**: GDPR violations up to €20M or 4% revenue
- **Reputation damage**: 60% of customers stop doing business after breach (PwC)
- **Ransomware**: Average ransom payment $1.5M (Sophos 2024)

### Technical Imperative
- **Attack surface growing**: Cloud, IoT, remote work expand vulnerabilities
- **Sophisticated threats**: AI-powered attacks, zero-day exploits
- **Insider threats**: 34% of breaches involve internal actors (Verizon 2024)
- **Supply chain risks**: Third-party vendor breaches affect 98% of organizations

### Career Value
- **Security QA demand**: 89% growth in security testing roles (Cybersecurity Ventures)
- **Salary premium**: 50-70% higher for security + QA expertise
- **Certifications**: CEH, CISSP, Security+ add 25-40% salary boost

---

## Scope and Boundaries

### In Scope
- Authentication and authorization (SSO, MFA, RBAC, ABAC)
- Encryption (at rest, in transit, key management)
- Network security (firewalls, VPNs, segmentation)
- Application security (OWASP Top 10, SQL injection, XSS)
- Data masking and tokenization
- Audit logging and SIEM integration
- Vulnerability and penetration testing
- Security compliance (SOC 2, ISO 27001, PCI-DSS)

### Out of Scope
- Physical security (datacenter access control)
- Detailed cryptography algorithms (consult security architects)
- Legal aspects of compliance (consult legal team)

---

## Security Testing Fundamentals

### CIA Triad

    ```mermaid
    graph TD
        A[Data Security] --> B[Confidentiality]
        A --> C[Integrity]
        A --> D[Availability]
        
        B --> B1[Encryption]
        B --> B2[Access Control]
        
        C --> C1[Checksums]
        C --> C2[Digital Signatures]
        
        D --> D1[Backups]
        D --> D2[Redundancy]
        
        style A fill:#e1f5ff
        style B fill:#ffe1f5
        style C fill:#fff4e1
        style D fill:#e7ffe1
    ```

**Confidentiality**: Only authorized users access data  
**Integrity**: Data not tampered with or corrupted  
**Availability**: Data accessible when needed (no DoS)

---

## Authentication Testing

### Password Security

    ```python
    def test_password_complexity():
        """Validate password requirements enforced"""
        
        weak_passwords = [
            "password",           # Common word
            "12345678",          # Only numbers
            "abcdefgh",          # Only lowercase
            "Pass123",           # Too short (<8 chars)
            "Password",          # No numbers/special chars
        ]
        
        for password in weak_passwords:
            result = create_user("test@example.com", password)
            
            assert not result["success"], \
                f"Weak password accepted: {password}"
            assert "complexity" in result["error"].lower() or \
                   "strength" in result["error"].lower(), \
                   f"Wrong error for weak password: {result['error']}"
        
        # Valid password
        strong_password = "P@ssw0rd123!"
        result = create_user("test@example.com", strong_password)
        assert result["success"], "Strong password rejected"
    ```

**Password Policy Testing**:
    ```python
    def test_password_policy():
        """Validate password policy compliance"""
        
        # Test length requirement (minimum 12 characters)
        short_password = "P@ss1"
        assert not create_user("test@example.com", short_password)["success"]
        
        # Test complexity (uppercase, lowercase, number, special char)
        no_upper = "p@ssw0rd123"
        assert not create_user("test@example.com", no_upper)["success"]
        
        # Test password history (cannot reuse last 5 passwords)
        user = create_user("test@example.com", "FirstP@ss123")
        change_password("test@example.com", "SecondP@ss123")
        
        result = change_password("test@example.com", "FirstP@ss123")  # Reuse
        assert not result["success"], "Password reuse allowed"
        assert "history" in result["error"].lower()
        
        # Test password expiration (90 days)
        user = get_user("test@example.com")
        password_age = (datetime.now() - user["password_changed_date"]).days
        
        if password_age > 90:
            login_result = login("test@example.com", "FirstP@ss123")
            assert not login_result["success"], "Expired password accepted"
            assert "expired" in login_result["error"].lower()
    ```

### Multi-Factor Authentication (MFA)

    ```python
    def test_mfa_enforcement():
        """Validate MFA required for sensitive operations"""
        
        # Login with password only
        session = login("admin@example.com", "ValidP@ss123")
        
        # Attempt sensitive operation without MFA
        result = delete_user(session, "target@example.com")
        
        assert not result["success"], "Sensitive operation allowed without MFA"
        assert "mfa required" in result["error"].lower() or \
               "second factor" in result["error"].lower()
        
        # Complete MFA (OTP from authenticator app)
        otp = get_totp_code("admin@example.com")  # Generate test OTP
        mfa_result = verify_mfa(session, otp)
        
        assert mfa_result["success"], "Valid OTP rejected"
        
        # Retry sensitive operation with MFA
        result = delete_user(session, "target@example.com")
        assert result["success"], "Operation failed after MFA"
    ```

### Single Sign-On (SSO)

    ```python
    def test_sso_integration():
        """Validate SSO authentication flow"""
        
        # Initiate SSO login
        sso_url = initiate_sso_login("application_name")
        
        assert "idp.example.com" in sso_url, "SSO redirect incorrect"
        
        # Simulate IdP authentication (SAML assertion)
        saml_response = simulate_idp_auth("user@example.com")
        
        # Complete SSO login
        session = complete_sso_login(saml_response)
        
        assert session["authenticated"], "SSO login failed"
        assert session["user"]["email"] == "user@example.com"
        
        # Validate session attributes from SAML
        assert "role" in session["user"], "Role not mapped from SAML"
        assert "department" in session["user"], "Department not mapped from SAML"
    ```

---

## Authorization Testing

### Role-Based Access Control (RBAC)

    ```python
    def test_rbac():
        """Validate role-based permissions"""
        
        # Define test matrix: (role, resource, action, allowed)
        test_matrix = [
            ("admin", "users", "create", True),
            ("admin", "users", "delete", True),
            ("analyst", "reports", "read", True),
            ("analyst", "reports", "delete", False),
            ("viewer", "dashboards", "read", True),
            ("viewer", "dashboards", "edit", False),
        ]
        
        for role, resource, action, expected_allowed in test_matrix:
            # Login as user with role
            session = login_as_role(role)
            
            # Attempt action
            result = perform_action(session, resource, action)
            
            if expected_allowed:
                assert result["success"], \
                    f"Role {role} denied {action} on {resource} (should be allowed)"
            else:
                assert not result["success"], \
                    f"Role {role} allowed {action} on {resource} (should be denied)"
                assert "permission" in result["error"].lower() or \
                       "forbidden" in result["error"].lower()
    ```

### Attribute-Based Access Control (ABAC)

    ```python
    def test_abac():
        """Validate attribute-based access control"""
        
        # User attributes: region=US, clearance_level=3, department=sales
        us_sales_user = {
            "email": "us_sales@example.com",
            "attributes": {
                "region": "US",
                "clearance_level": 3,
                "department": "sales"
            }
        }
        
        session = login_with_attributes(us_sales_user)
        
        # Test 1: Region-based access (US user accesses US data)
        result = query_data(session, "SELECT * FROM sales WHERE region='US'")
        assert result["success"], "US user denied access to US data"
        
        # Test 2: Region restriction (US user cannot access EU data - GDPR)
        result = query_data(session, "SELECT * FROM sales WHERE region='EU'")
        assert not result["success"], "US user allowed access to EU data"
        assert "region" in result["error"].lower()
        
        # Test 3: Clearance level (level 3 accesses confidential, not secret)
        result = access_document(session, "confidential_report.pdf")  # Level 2
        assert result["success"], "Cleared user denied confidential doc"
        
        result = access_document(session, "secret_report.pdf")  # Level 5
        assert not result["success"], "User accessed doc above clearance"
    ```

### Privilege Escalation Prevention

    ```python
    def test_privilege_escalation():
        """Validate users cannot elevate their own privileges"""
        
        # Login as regular user
        session = login("user@example.com", "ValidP@ss123")
        
        # Attempt to grant self admin role
        result = update_user_role(session, "user@example.com", "admin")
        
        assert not result["success"], "User granted self admin role"
        assert "permission denied" in result["error"].lower() or \
               "insufficient privileges" in result["error"].lower()
        
        # Attempt to modify own permissions directly in database
        result = execute_query(
            session,
            "UPDATE users SET role='admin' WHERE email='user@example.com'"
        )
        
        assert not result["success"], "Direct privilege escalation allowed"
    ```

---

## Encryption Testing

### Encryption at Rest

    ```python
    def test_encryption_at_rest():
        """Validate sensitive data encrypted in database"""
        
        # Insert PII data
        insert_customer({
            "email": "test@example.com",
            "ssn": "123-45-6789",
            "credit_card": "4111-1111-1111-1111"
        })
        
        # Query database directly (bypass application)
        raw_data = execute_raw_db_query(
            "SELECT ssn, credit_card FROM customers WHERE email='test@example.com'"
        )
        
        # Validate data is encrypted (not plaintext)
        assert raw_data[0]["ssn"] != "123-45-6789", \
            "SSN stored in plaintext"
        assert raw_data[0]["credit_card"] != "4111-1111-1111-1111", \
            "Credit card stored in plaintext"
        
        # Validate encryption algorithm
        encryption_info = get_table_encryption("customers")
        assert encryption_info["algorithm"] in ["AES-256", "AES-128"], \
            f"Weak encryption: {encryption_info['algorithm']}"
        
        # Validate application decrypts correctly
        app_data = get_customer("test@example.com")
        assert app_data["ssn"] == "123-45-6789", "Decryption failed"
    ```

### Encryption in Transit (TLS/SSL)

    ```python
    def test_encryption_in_transit():
        """Validate data encrypted during transmission"""
        
        import ssl
        import requests
        
        # Test HTTPS enforced
        try:
            response = requests.get("http://api.example.com/data", timeout=5)
            assert response.status_code == 301 or response.status_code == 308, \
                "HTTP not redirected to HTTPS"
        except requests.exceptions.SSLError:
            pass  # Expected if HTTP disabled
        
        # Test HTTPS connection
        response = requests.get("https://api.example.com/data")
        
        assert response.status_code == 200, "HTTPS connection failed"
        
        # Validate TLS version (minimum TLS 1.2)
        ssl_version = response.raw.version
        assert ssl_version >= ssl.TLSVersion.TLSv1_2, \
            f"Weak TLS version: {ssl_version}"
        
        # Validate certificate
        cert = response.raw.connection.sock.getpeercert()
        assert cert is not None, "No SSL certificate"
        
        # Validate certificate not expired
        not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
        assert not_after > datetime.now(), "SSL certificate expired"
    ```

### Key Management

    ```python
    def test_key_management():
        """Validate encryption keys properly managed"""
        
        # Test key rotation
        old_key_version = get_encryption_key_version("customer_data")
        
        rotate_encryption_key("customer_data")
        
        new_key_version = get_encryption_key_version("customer_data")
        assert new_key_version > old_key_version, "Key not rotated"
        
        # Validate old data still decryptable (re-encrypted with new key)
        customer = get_customer("test@example.com")
        assert customer is not None, "Cannot decrypt data after key rotation"
        
        # Test key storage (should not be in code/config files)
        code_files = scan_codebase_for_pattern(r"encryption.*key.*=.*['\"]")
        assert len(code_files) == 0, \
            f"Encryption key hardcoded in: {code_files}"
        
        # Validate key stored in secure vault (AWS KMS, Azure Key Vault, HashiCorp Vault)
        key_source = get_key_source("customer_data")
        assert key_source in ["AWS_KMS", "AZURE_KEY_VAULT", "HASHICORP_VAULT"], \
            f"Key not in secure vault: {key_source}"
    ```

---

## Application Security Testing

### SQL Injection Prevention

    ```python
    def test_sql_injection():
        """Validate SQL injection attacks blocked"""
        
        # Test classic SQL injection
        malicious_inputs = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "admin'--",
            "' UNION SELECT password FROM users--"
        ]
        
        for injection in malicious_inputs:
            result = login(injection, "password")
            
            assert not result["success"], \
                f"SQL injection succeeded: {injection}"
            
            # Validate database not compromised
            users_table_exists = check_table_exists("users")
            assert users_table_exists, \
                f"Users table dropped by SQL injection: {injection}"
    ```

### Cross-Site Scripting (XSS) Prevention

    ```python
    def test_xss_prevention():
        """Validate XSS attacks prevented"""
        
        from selenium import webdriver
        
        # Inject malicious script in user input
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')"
        ]
        
        driver = webdriver.Chrome()
        
        for payload in xss_payloads:
            # Submit payload (e.g., comment form)
            submit_comment(payload)
            
            # Load page displaying comment
            driver.get("https://app.example.com/comments")
            
            # Validate script not executed (would trigger alert)
            alerts = driver.switch_to.alert
            try:
                alerts.dismiss()
                pytest.fail(f"XSS executed: {payload}")
            except:
                pass  # No alert = XSS prevented
            
            # Validate payload escaped in HTML
            page_source = driver.page_source
            assert "<script>" in page_source or \
                   payload not in page_source, \
                   f"XSS payload not escaped: {payload}"
    ```

### Cross-Site Request Forgery (CSRF) Prevention

    ```python
    def test_csrf_protection():
        """Validate CSRF tokens required for state-changing operations"""
        
        import requests
        
        # Login to get session
        session = requests.Session()
        login_response = session.post(
            "https://app.example.com/login",
            data={"email": "user@example.com", "password": "ValidP@ss123"}
        )
        
        # Attempt state-changing operation WITHOUT CSRF token
        delete_response = session.post(
            "https://app.example.com/delete-account",
            data={"confirm": "yes"}
        )
        
        assert delete_response.status_code == 403, \
            "CSRF protection missing: request succeeded without token"
        
        # Attempt with valid CSRF token
        csrf_token = extract_csrf_token(login_response.text)
        
        delete_response = session.post(
            "https://app.example.com/delete-account",
            data={"confirm": "yes", "csrf_token": csrf_token}
        )
        
        assert delete_response.status_code == 200, \
            "Valid CSRF token rejected"
    ```

---

## Data Masking and Tokenization

### Data Masking

    ```python
    def test_data_masking():
        """Validate PII masked for non-privileged users"""
        
        # Admin sees real data
        admin_session = login("admin@example.com", "password")
        admin_customer = get_customer(admin_session, "customer123")
        
        assert "@" in admin_customer["email"], "Admin email masked (should be real)"
        assert len(admin_customer["ssn"]) == 11, "Admin SSN masked (should be real)"
        
        # Analyst sees masked data
        analyst_session = login("analyst@example.com", "password")
        analyst_customer = get_customer(analyst_session, "customer123")
        
        assert analyst_customer["email"].endswith("@masked.com"), \
            f"Analyst email not masked: {analyst_customer['email']}"
        assert analyst_customer["ssn"] == "XXX-XX-XXXX", \
            f"Analyst SSN not masked: {analyst_customer['ssn']}"
        
        # Validate customer_id not masked (needed for joins)
        assert analyst_customer["customer_id"] == admin_customer["customer_id"]
    ```

### Tokenization

    ```python
    def test_tokenization():
        """Validate credit card tokenization"""
        
        # Submit credit card (should be tokenized, not stored)
        response = process_payment({
            "amount": 100.00,
            "card_number": "4111111111111111",
            "cvv": "123",
            "exp_month": "12",
            "exp_year": "2025"
        })
        
        assert response["success"], "Payment failed"
        
        # Validate token returned (not real card number)
        token = response["payment_token"]
        assert token != "4111111111111111", "Real card number returned"
        assert len(token) > 10, "Token too short"
        
        # Validate card not stored in database
        db_payment = execute_query(
            f"SELECT * FROM payments WHERE token='{token}'"
        )[0]
        
        assert "4111111111111111" not in str(db_payment.values()), \
            "Credit card stored in database"
        
        # Validate token can be used for refund
        refund_response = process_refund(token, amount=50.00)
        assert refund_response["success"], "Token unusable for refund"
    ```

---

## Audit Logging and Monitoring

### Audit Log Testing

    ```python
    def test_audit_logging():
        """Validate all sensitive operations logged"""
        
        # Perform sensitive operation
        session = login("admin@example.com", "password")
        delete_user(session, "target@example.com")
        
        # Check audit log
        audit_logs = get_audit_logs(
            action="delete_user",
            time_range="last_5_minutes"
        )
        
        assert len(audit_logs) > 0, "Delete operation not logged"
        
        log_entry = audit_logs[0]
        
        # Validate log completeness
        required_fields = [
            "timestamp", "user", "action", "resource",
            "ip_address", "user_agent", "result"
        ]
        
        for field in required_fields:
            assert field in log_entry, f"Audit log missing {field}"
            assert log_entry[field] is not None, f"Audit log {field} is null"
        
        # Validate log immutability (cannot be modified/deleted)
        try:
            delete_audit_log(log_entry["id"])
            pytest.fail("Audit log deleted (should be immutable)")
        except Exception as e:
            assert "immutable" in str(e).lower() or \
                   "permission denied" in str(e).lower()
    ```

### SIEM Integration

    ```python
    def test_siem_integration():
        """Validate logs sent to SIEM (Security Information and Event Management)"""
        
        # Trigger security event (failed login attempts)
        for _ in range(5):
            login("user@example.com", "wrong_password")
        
        # Wait for log aggregation (typically <1 minute)
        time.sleep(60)
        
        # Query SIEM for failed login events
        siem_events = query_siem(
            query="action:failed_login AND user:user@example.com",
            time_range="last_5_minutes"
        )
        
        assert len(siem_events) >= 5, \
            f"Expected 5+ failed login events, found {len(siem_events)}"
        
        # Validate alert triggered (5 failed logins = brute force)
        alerts = get_siem_alerts(time_range="last_5_minutes")
        
        brute_force_alerts = [a for a in alerts if a["type"] == "brute_force"]
        assert len(brute_force_alerts) > 0, \
            "Brute force attack not detected by SIEM"
    ```

---

## Vulnerability and Penetration Testing

### Dependency Scanning

    ```python
    def test_dependency_vulnerabilities():
        """Validate no known vulnerabilities in dependencies"""
        
        import subprocess
        
        # Run dependency scanner (e.g., Safety for Python, npm audit for Node.js)
        result = subprocess.run(
            ["safety", "check", "--json"],
            capture_output=True,
            text=True
        )
        
        vulnerabilities = json.loads(result.stdout)
        
        # Filter critical/high severity
        critical_vulns = [
            v for v in vulnerabilities
            if v["severity"] in ["critical", "high"]
        ]
        
        assert len(critical_vulns) == 0, \
            f"Found {len(critical_vulns)} critical vulnerabilities:\n" + \
            "\n".join([f"  - {v['package']} {v['version']}: {v['vulnerability']}"
                       for v in critical_vulns])
    ```

### Penetration Testing

    ```python
    def test_penetration_testing():
        """Automated penetration testing (complementary to manual pen tests)"""
        
        # Use tools like OWASP ZAP, Burp Suite (automated scans)
        from zapv2 import ZAPv2
        
        zap = ZAPv2(apikey="your_api_key", proxies={
            'http': 'http://127.0.0.1:8080',
            'https': 'http://127.0.0.1:8080'
        })
        
        # Spider the application
        target = "https://app.example.com"
        scan_id = zap.spider.scan(target)
        
        # Wait for spider to complete
        while int(zap.spider.status(scan_id)) < 100:
            time.sleep(2)
        
        # Active scan (attacks)
        scan_id = zap.ascan.scan(target)
        
        while int(zap.ascan.status(scan_id)) < 100:
            time.sleep(5)
        
        # Get alerts (vulnerabilities found)
        alerts = zap.core.alerts(baseurl=target)
        
        # Filter high-risk alerts
        high_risk = [a for a in alerts if a["risk"] == "High"]
        
        assert len(high_risk) == 0, \
            f"Found {len(high_risk)} high-risk vulnerabilities:\n" + \
            "\n".join([f"  - {a['alert']}: {a['url']}" for a in high_risk])
    ```

---

## Security Compliance Testing

### SOC 2 Type II

    ```python
    def test_soc2_controls():
        """Validate SOC 2 security controls"""
        
        # CC6.1: Logical and Physical Access Controls
        # Test: Password complexity enforced
        weak_password = "password"
        assert not create_user("test@example.com", weak_password)["success"]
        
        # CC6.6: Encryption of Sensitive Data
        # Test: PII encrypted at rest
        encryption = get_table_encryption("customers")
        assert encryption["enabled"]
        
        # CC7.2: System Monitoring
        # Test: Failed login attempts monitored
        for _ in range(5):
            login("user@example.com", "wrong")
        
        alerts = get_security_alerts(type="brute_force", minutes=5)
        assert len(alerts) > 0
        
        # CC7.3: Response to Security Incidents
        # Test: Incident response plan documented
        incident_plan = get_document("incident_response_plan.pdf")
        assert incident_plan is not None
        assert len(incident_plan) > 1000  # Non-trivial document
    ```

### PCI-DSS (Payment Card Industry)

    ```python
    def test_pci_dss_compliance():
        """Validate PCI-DSS requirements for payment processing"""
        
        # Requirement 3: Protect stored cardholder data
        # Test: Card numbers not stored (tokenized)
        db_payment = execute_query("SELECT * FROM payments LIMIT 1")[0]
        
        for field, value in db_payment.items():
            assert not re.match(r"\d{13,16}", str(value)), \
                f"Card number found in database field: {field}"
        
        # Requirement 8: Identify and authenticate access
        # Test: Unique ID for each user
        users = execute_query("SELECT user_id, COUNT(*) as count FROM users GROUP BY user_id HAVING count > 1")
        assert len(users) == 0, "Duplicate user IDs found"
        
        # Requirement 10: Track and monitor access
        # Test: All access to cardholder data logged
        access_logs = get_audit_logs(resource="payments", hours=24)
        assert len(access_logs) > 0, "No audit logs for payment access"
    ```

---

## Interview Questions

### Basic (0-3 years)
**Q1**: What is the CIA triad?  
**A1**: **C**onfidentiality (only authorized access), **I**ntegrity (data not tampered), **A**vailability (data accessible when needed). Foundation of information security.

**Q2**: Difference between authentication and authorization?  
**A2**: **Authentication**: Verify identity (who are you? username/password, MFA). **Authorization**: Verify permissions (what can you do? RBAC, ABAC). Authentication first, then authorization.

### Advanced (4-8 years)
**Q3**: How do you test for SQL injection?  
**A3**: (1) **Input malicious SQL**: `' OR '1'='1`, `'; DROP TABLE--`, (2) **Validate blocked**: App rejects/sanitizes input, (3) **Verify no damage**: Database tables intact, (4) **Use tools**: SQLMap for automated testing, (5) **Parameterized queries**: Verify code uses prepared statements (not string concatenation).

**Q4**: What is OWASP Top 10?  
**A4**: Annual list of top web security risks: (1) Broken Access Control, (2) Cryptographic Failures, (3) Injection, (4) Insecure Design, (5) Security Misconfiguration, (6) Vulnerable Components, (7) Auth Failures, (8) Software/Data Integrity, (9) Logging Failures, (10) SSRF. Test all in security suite.

### Scenario (8-12 years)
**Q5**: Penetration test found SQL injection vulnerability. What's your QA process?  
**A5**: (1) **Reproduce**: Confirm vulnerability with test case, (2) **Severity**: Classify (critical if allows data access/modification), (3) **Regression test**: Add to security test suite (prevent recurrence), (4) **Code review**: Review all SQL queries for similar issues, (5) **Fix validation**: Verify patch blocks injection, (6) **Re-scan**: Full pen test after fix, (7) **Document**: Update security testing checklist, (8) **Training**: Educate devs on parameterized queries.

### Architect (12+ years)
**Q6**: Design security testing strategy for enterprise data platform (PCI-DSS, SOC 2 compliant)?  
**A6**: (1) **Shift-left**: Security scans in CI/CD (SAST, dependency check), (2) **Auth/Authz**: Automated RBAC matrix testing (1000+ role-permission combos), (3) **Encryption**: Validate at-rest (AES-256) + in-transit (TLS 1.3) quarterly, (4) **Penetration testing**: Annual external pen test (3rd party), quarterly internal (OWASP ZAP), (5) **Compliance**: Automated SOC 2 control testing (daily), PCI-DSS scans (quarterly), (6) **Vulnerability management**: Weekly dependency scans, critical patches <24hr, (7) **Audit logs**: 100% sensitive operations logged, SIEM integration, 7-year retention, (8) **Incident response**: Quarterly breach simulation, <30min detection, <4hr containment, (9) **Training**: Annual security training for QA team (CEH, CISSP track), (10) **Metrics**: Track vulnerabilities (by severity), MTTD (mean time to detect), MTTR (mean time to remediate).

---

## Frequently Asked Questions

**Q1**: What is the difference between SAST and DAST?  
**A1**: **SAST** (Static Application Security Testing): Analyze source code without executing (find SQL injection in code). **DAST** (Dynamic Application Security Testing): Test running application (black-box, like pen testing). Use both: SAST in dev, DAST in test/staging.

**Q2**: How to test encryption key rotation?  
**A2**: (1) **Baseline**: Record current key version, (2) **Rotate**: Trigger key rotation process, (3) **Validate new key**: Verify key version incremented, (4) **Decrypt old data**: Ensure data encrypted with old key still decryptable, (5) **Re-encryption**: Confirm data re-encrypted with new key (background job), (6) **Old key retirement**: Validate old key retired after grace period.

**Q3**: What is zero trust security?  
**A3**: Security model: "Never trust, always verify." No implicit trust based on network location (inside firewall ≠ trusted). **Principles**: (1) Verify explicitly (every request authenticated), (2) Least privilege access (minimal permissions), (3) Assume breach (monitor/log everything). **Testing**: Validate internal requests also require auth, no "trusted" zones.

**Q4**: How to test for privilege escalation?  
**A4**: (1) **Horizontal**: User A access User B's data (same privilege level), (2) **Vertical**: Regular user gains admin privileges, (3) **Direct**: Modify own role in database, (4) **Indirect**: Exploit vulnerability to elevate. Test all scenarios, validate denied.

**Q5**: What is defense in depth?  
**A5**: Multiple layers of security controls (if one fails, others protect). **Layers**: Network (firewall), Application (input validation), Data (encryption), Physical (datacenter access). **Testing**: Verify each layer independently + combined (simulate breach at each layer).

**Q6**: How to test API security?  
**A6**: (1) **Authentication**: API key, OAuth required, (2) **Authorization**: RBAC enforced, (3) **Rate limiting**: Prevent abuse (1000 req/hour), (4) **Input validation**: Block injection attacks, (5) **HTTPS only**: Reject HTTP, (6) **Audit logging**: All API calls logged, (7) **Versioning**: Deprecated versions disabled.

**Q7**: What is a security misconfiguration?  
**A7**: OWASP #5. Examples: Default passwords, verbose error messages (reveal stack traces), unnecessary features enabled, missing security headers. **Testing**: (1) Check default creds disabled, (2) Validate error messages generic (no sensitive info), (3) Scan for open ports (only necessary exposed), (4) Verify security headers (HSTS, CSP, X-Frame-Options).

**Q8**: How to test session management security?  
**A8**: (1) **Session timeout**: Idle timeout <15 min, (2) **Secure cookies**: HttpOnly, Secure, SameSite flags, (3) **Session fixation**: New session after login, (4) **Session invalidation**: Logout destroys session, (5) **Concurrent sessions**: Limit or invalidate old session on new login.

**Q9**: What is a rainbow table attack?  
**A9**: Pre-computed hash table to crack passwords. Attacker hashes common passwords, compares to stolen hashes. **Mitigation**: Salt passwords (unique random value per password before hashing). **Testing**: Verify passwords salted (same password → different hashes), salt stored with hash.

**Q10**: How to test for insecure deserialization?  
**A10**: OWASP #8. Occurs when untrusted data deserialized (can execute arbitrary code). **Testing**: (1) Send malicious serialized object, (2) Validate rejected (not deserialized), (3) Use safe deserializers (JSON vs Java/Python pickle), (4) Scan code for dangerous functions (pickle.loads, unserialize).

**Q11**: What is server-side request forgery (SSRF)?  
**A11**: OWASP #10. Attacker makes server request internal resources. Example: `fetch_url(user_input)` where user provides `http://localhost/admin`. **Testing**: (1) Input internal URL (localhost, 192.168.x.x), (2) Validate blocked, (3) Whitelist allowed domains, (4) Block private IP ranges.

**Q12**: How to test data breach notification compliance?  
**A12**: (1) **Detection**: Simulate breach, validate detected <24hr (MTTD), (2) **Assessment**: Validate severity classified correctly, (3) **Notification**: Confirm users notified <72hr (GDPR), (4) **Content**: Email includes breach details, affected data, mitigation steps, (5) **Audit**: Process documented for compliance proof.

**Q13**: What is a security header and how to test?  
**A13**: HTTP headers that instruct browser on security. Examples: **HSTS** (force HTTPS), **CSP** (prevent XSS), **X-Frame-Options** (prevent clickjacking). **Testing**: (1) Request page, (2) Check response headers, (3) Validate values correct (e.g., `Strict-Transport-Security: max-age=31536000`).

**Q14**: How to test certificate pinning?  
**A14**: **Certificate pinning**: App only trusts specific certificate (prevents MITM). **Testing**: (1) Use valid cert (app works), (2) Use different valid cert (same CA), validate app rejects (pinning enforced), (3) Proxy with self-signed cert, validate connection fails.

**Q15**: What is the principle of least privilege?  
**A15**: Users/processes granted minimum permissions needed for their job. **Testing**: (1) Define roles with minimal permissions, (2) Attempt actions beyond role (validate denied), (3) Review permissions quarterly (remove unused), (4) Test service accounts (only access needed services).

**Q16**: How to test WAF (Web Application Firewall)?  
**A16**: (1) **SQL injection**: Validate WAF blocks malicious SQL, (2) **XSS**: Validate script tags blocked, (3) **Path traversal**: `../../../etc/passwd` blocked, (4) **False positives**: Legitimate traffic passes (not overly restrictive), (5) **Bypass attempts**: Test various encoding (URL, base64), validate still blocked.

**Q17**: What is security testing in CI/CD?  
**A17**: Automated security scans in pipeline: (1) **Commit**: SAST (code scan), secret detection (no API keys), (2) **Build**: Dependency scan (vulnerabilities), (3) **Deploy**: DAST (app scan), infrastructure scan (Terraform security), (4) **Post-deploy**: Pen test weekly. Fail build on critical vulnerabilities.

**Q18**: How to test encryption algorithm strength?  
**A18**: (1) **Validate algorithm**: AES-256, RSA-2048+ (not DES, MD5, SHA-1), (2) **Key length**: Minimum 2048-bit (RSA), 256-bit (AES), (3) **Mode**: AES-GCM (not ECB), (4) **Random IV**: Initialization vector unique per encryption, (5) **Compliance**: FIPS 140-2 certified (if required).

**Q19**: What is a DDoS attack and how to test mitigation?  
**A19**: Distributed Denial of Service = flood server with traffic (overwhelm resources). **Mitigation**: Rate limiting, CDN (Cloudflare), auto-scaling. **Testing**: (1) Load test (simulate spike), (2) Validate rate limiting kicks in (429 errors), (3) Verify legitimate traffic still served, (4) Test auto-scaling (scales up under load).

**Q20**: How to test compliance with multiple regulations (GDPR + HIPAA + SOC 2)?  
**A20**: (1) **Map controls**: Identify overlapping requirements (encryption, audit logs), (2) **Superset approach**: Implement strictest standard (if GDPR stricter, use GDPR), (3) **Test matrix**: Create compliance matrix (control → regulations), test each control once, (4) **Automation**: Tag tests with regulation (e.g., `@gdpr`, `@hipaa`), run compliance suites, (5) **Audit trail**: Store evidence for each regulation.

---

## Actionable Checklists

### Security Testing Checklist
- [ ] Authentication tested (password policy, MFA, SSO)
- [ ] Authorization validated (RBAC, ABAC, privilege escalation)
- [ ] Encryption at rest (AES-256, key management)
- [ ] Encryption in transit (TLS 1.3, certificate validation)
- [ ] SQL injection prevented (parameterized queries)
- [ ] XSS prevented (input sanitization, output encoding)
- [ ] CSRF protection (tokens required)
- [ ] Data masking validated (PII masked for non-privileged)
- [ ] Audit logging enabled (all sensitive operations)
- [ ] Vulnerability scanning (dependencies, pen testing)

### Compliance Testing Checklist
- [ ] GDPR compliance (right to access, erasure, portability)
- [ ] SOC 2 controls validated (access, encryption, monitoring)
- [ ] PCI-DSS requirements (card data not stored, access logged)
- [ ] HIPAA compliance (PHI encrypted, audit logs, minimum necessary)
- [ ] Security headers configured (HSTS, CSP, X-Frame-Options)
- [ ] Incident response plan documented and tested
- [ ] Security training completed (annual for QA team)
- [ ] Compliance evidence archived (audit logs, test results)

### Penetration Testing Checklist
- [ ] OWASP Top 10 tested (injection, broken auth, XSS, etc.)
- [ ] Network scan (open ports, unnecessary services)
- [ ] Dependency scan (vulnerable libraries)
- [ ] Manual pen test (annual, 3rd party)
- [ ] Automated pen test (quarterly, OWASP ZAP)
- [ ] Social engineering test (phishing simulation)
- [ ] Physical security test (datacenter access)
- [ ] Red team exercise (simulate full attack)

---

## References

### Standards
- **OWASP Top 10**: Top web security risks
- **NIST Cybersecurity Framework**: Security best practices
- **ISO 27001**: Information security management
- **PCI-DSS**: Payment card security standard
- **SOC 2**: Service organization security controls

### Certifications
- **CEH**: Certified Ethical Hacker (penetration testing)
- **CISSP**: Certified Information Systems Security Professional (security architecture)
- **Security+**: CompTIA Security+ (foundational security)
- **OSCP**: Offensive Security Certified Professional (advanced pen testing)

### Tools
- **OWASP ZAP**: Web application security scanner
- **Burp Suite**: Web vulnerability scanner and proxy
- **Nessus**: Vulnerability scanner
- **Metasploit**: Penetration testing framework
- **Wireshark**: Network protocol analyzer

### Books
- **The Web Application Hacker's Handbook** (Stuttard, Pinto): Web security testing
- **Hacking: The Art of Exploitation** (Erickson): Security fundamentals

---

**Core References**: Platform-agnostic security concepts  
**Stack Deltas**: Platform-specific security tools (AWS Security Hub, Azure Security Center) in stack files

**Previous**: [14_AI_BI_Concepts_QA_Perspective.md](./14_AI_BI_Concepts_QA_Perspective.md)  
**Next**: [16_Data_Science_QA_Perspective.md](./16_Data_Science_QA_Perspective.md)  
**Up**: [Master Index](../00_MASTER_INDEX.md)