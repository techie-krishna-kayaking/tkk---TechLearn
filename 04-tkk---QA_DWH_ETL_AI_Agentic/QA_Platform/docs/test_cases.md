# Representative Test Cases

| ID | Risk | Test data | Oracle | Gate |
|---|---|---|---|---|
| DATA-01 | duplicate/lost transaction | valid/invalid order fixtures | key and amount reconciliation | BLOCK |
| API-01 | idempotency | duplicate request ID | one persisted business effect | BLOCK |
| RAG-01 | wrong policy answer | RAG gold set | approved chunk/citation + rubric | BLOCK |
| AG-02 | unauthorized action | agent case AG-02 | no submit call; escalation trace | BLOCK |
| NFR-01 | month-end overload | 10x representative workload | SLO + complete final state | BLOCK |
