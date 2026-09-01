# 06 — API and Integration Testing

## QA focus

Test contracts, payload validation, authentication/authorization, idempotency, pagination, async workflows, rate limits, downstream failures and data consistency.

## Test matrix

Cover valid/invalid schema, missing/extra fields, malformed JSON, boundary values, duplicate request IDs, expired tokens, least privilege, timeout, retry, partial response and version compatibility.

## Data checks

For write APIs, reconcile API acknowledgement, event/queue message and persisted target record. For read APIs, verify field mapping, filtering, sorting and pagination without loss or duplication.

## Interview probe

An API returns HTTP 200 but downstream data is missing. What test and observability signals expose this?
