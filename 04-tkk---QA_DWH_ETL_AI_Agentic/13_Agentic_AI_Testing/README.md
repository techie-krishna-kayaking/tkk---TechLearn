# 13 — Agentic AI Testing

## QA focus

Test task completion, planning, tool choice, argument correctness, authorization, state/memory, retries, loops, timeouts, recovery, auditability and multi-agent interaction.

## Critical negative tests

Unauthorized tool requests, malicious tool output, invalid arguments, unavailable tool, slow tool, repeated failure, stale memory, conflicting multi-agent recommendations, unbounded loop and unsafe external side effect.

## Quality gates

Set limits for task-success rate, policy-violation rate, unauthorized-tool attempts, max steps, timeout/retry behavior, trace completeness, cost and human-escalation correctness.

## Interview probe

What makes agent testing materially different from ordinary API testing, and what remains the same?
