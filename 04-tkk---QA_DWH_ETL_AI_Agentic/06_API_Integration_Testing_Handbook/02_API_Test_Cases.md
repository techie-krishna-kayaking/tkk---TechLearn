# API Test Cases

`POST /orders`: valid payload; missing ID; invalid amount; duplicate idempotency key; expired token; caller from wrong tenant; downstream database timeout; retry after timeout; response contract change; event delivered once; persisted order matches acknowledgement.

For every case capture request ID, actor/role, payload version, response, trace ID, event ID and final database/query evidence.
