# 06 — API & Integration Testing Handbook

## QA focus

Validate contracts, authentication and authorization, request/response mapping, idempotency, pagination, asynchronous work, error behavior and downstream data consistency.

## Test matrix

| Area | Test examples |
|---|---|
| Contract | required/extra fields, types, enums, backward compatibility |
| Auth | no token, expired token, wrong tenant, least-privilege role |
| Behavior | valid request, malformed JSON, boundary values, duplicate ID |
| Resilience | timeout, retry, rate limit, partial downstream failure |
| Data | acknowledgement → queue/event → target record reconciliation |

## Senior answer

HTTP 200 is transport success, not business success. Test the asynchronous final state, correlation ID, downstream effect, idempotent retry and error visibility.

## Checklist

- [ ] Contract version and schema validation.
- [ ] Negative, boundary and authorization cases.
- [ ] API response reconciled to persistence/event state.
- [ ] Timeout/retry behavior avoids duplicate side effects.
- [ ] Sensitive fields absent from logs and errors.
