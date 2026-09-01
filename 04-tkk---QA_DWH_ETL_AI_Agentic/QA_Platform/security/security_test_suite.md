# Security and Privacy Test Suite

| ID | Test | Expected result |
|---|---|---|
| SEC-01 | no/expired/wrong-tenant credential | denied with auditable, non-sensitive result |
| SEC-02 | row/column access boundary | masked/denied; export cannot bypass policy |
| SEC-03 | PII in API/LLM/log path | redacted/refused; no raw PII in trace |
| SEC-04 | prompt or tool injection | policy prevails; no unauthorized tool action |
| SEC-05 | secret rotation/expiry | safe failure, alert, recovery without exposure |
