# Defect Library

## DEF-001 — Join multiplication doubles paid revenue

**Evidence:** source/target row count may appear plausible; monetary reconciliation by date/status shows variance.  
**Root cause:** dimension join was not unique at effective business grain.  
**Containment:** block dashboard publish; correct/backfill.  
**Prevention:** input uniqueness + join-cardinality + aggregate reconciliation gate.

## DEF-002 — RAG cites stale policy

**Evidence:** index version/traces retrieve superseded document.  
**Prevention:** freshness/index-version gate, citation gold tests and production alert.

## DEF-003 — Agent retries an unavailable tool indefinitely

**Evidence:** trace exceeds step/cost budget without escalation.  
**Prevention:** timeout, bounded retry, loop detection and human-handoff test.
