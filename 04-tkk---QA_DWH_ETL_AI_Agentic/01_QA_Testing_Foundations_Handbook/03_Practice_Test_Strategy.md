# Practice — Risk-Based Test Strategy

## SUT

A payment analytics platform ingests card events hourly, produces a warehouse dashboard and exposes a RAG assistant that answers policy questions. The assistant may read masked customer information but cannot make account changes.

## Your deliverables

1. Draw a SUT/dependency diagram.
2. Rank at least ten risks using impact, likelihood and detectability.
3. Write test coverage for data, API, LLM/RAG, security, performance and recovery.
4. Define five release-blocking gates and a waiver process.
5. Write a production monitoring and incident handoff plan.

## Self-review

Your strategy is incomplete if it has no test data plan, no oracle for AI outputs, no recovery testing, or no evidence-based release decision.
