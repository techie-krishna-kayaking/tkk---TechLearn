# Agentic AI Testing — Interview Q&A

**What is an agent test oracle?** Task outcome plus acceptable process: approved plan/tool/argument/authority/state, bounded cost/time and audit trace.

**How do you test a loop?** Force repeating failure or misleading tool result; assert max-step/time/cost guard, safe stop/escalation and trace evidence.

**How do you test memory?** Seed correct/stale/conflicting state; validate retrieval/update/expiry/privacy policy and that current authoritative evidence wins.

**How do you test tool arguments?** Valid, missing, malformed, boundary, wrong-tenant and dangerous target values; independently validate before invocation.

**Multi-agent test risk?** Conflicting plans, unsafe delegation, shared-state race, authority confusion and unbounded interaction; test governance and escalation.
