# Security Test Catalog

1. Anonymous/expired/wrong-tenant access is denied.
2. Least-privilege role can perform only approved action.
3. Row/column masking cannot be bypassed by export/filter/API.
4. Logs/errors/traces contain no raw sensitive values or secrets.
5. Malformed and injection payloads are rejected/safely handled.
6. Agent tool calls require authority and record auditable rationale.
7. Retention/delete request propagates to all governed stores.
