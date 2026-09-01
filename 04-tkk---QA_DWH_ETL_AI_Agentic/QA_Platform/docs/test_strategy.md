# Master QA Strategy

**SUT:** transaction ingestion, warehouse/BI, policy RAG assistant and constrained agent.  
**Critical risks:** financial misstatement; missing/duplicate transactions; stale dashboard; cross-tenant/PII exposure; hallucinated policy; unauthorized agent side effect; SLA/recovery failure.

Coverage layers: contracts/schema → data rules/reconciliation → API/integration → ML/LLM/RAG/agent evaluations → performance/security/resilience → production observability. Critical tests use synthetic/masked data, explicit oracles, traceable evidence and a BLOCK gate.
