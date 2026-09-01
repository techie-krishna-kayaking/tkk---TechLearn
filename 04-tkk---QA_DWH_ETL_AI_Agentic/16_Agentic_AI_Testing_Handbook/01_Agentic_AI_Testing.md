# 16 — Agentic AI Testing Handbook

## QA focus

Test task success, planning, tool selection, argument correctness, authorization, state/memory, retry, loop/timeout, recovery, audit trace and side-effect safety.

## Test model

```text
Goal → plan → tool choice → arguments → tool result → state update → final response / escalation
```

Each transition has a quality oracle. A final response can appear good while the agent used an unauthorized tool, stale memory or incorrect argument.

## Critical negatives

Unavailable/slow tool; invalid argument; malicious tool output; unauthorized action; stale/conflicting memory; repeated failure; infinite loop; budget breach; conflicting multi-agent advice; human approval required but bypassed.

## Quality gates

Task-success rate, policy-violation rate, unauthorized tool attempts, max steps, timeout/retry behavior, trace completeness, human-escalation correctness, latency and cost.
