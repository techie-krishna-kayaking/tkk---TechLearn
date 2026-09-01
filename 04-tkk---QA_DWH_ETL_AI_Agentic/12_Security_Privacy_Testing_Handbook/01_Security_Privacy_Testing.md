# 12 — Security & Privacy Testing Handbook

## QA focus

Validate identity, authorization, least privilege, sensitive-data handling, auditability, injection resistance, secret management and safe failure behavior.

## Data/AI threat cases

Unauthorized table/API/tool access; cross-tenant data exposure; PII in logs/errors; prompt injection; malicious document instruction; secret leakage; unsafe agent action; role escalation; expired credential; export bypass.

## Evidence standard

Prove both allow and deny paths. For every sensitive operation retain actor/role, resource, decision, request/trace ID, data classification and audit event. Never use real secrets or production PII for a training test.

## Interview line

“I test authorization as a matrix of actor × resource × action × context, and I include denial, logging and safe error behavior—not just successful login.”
