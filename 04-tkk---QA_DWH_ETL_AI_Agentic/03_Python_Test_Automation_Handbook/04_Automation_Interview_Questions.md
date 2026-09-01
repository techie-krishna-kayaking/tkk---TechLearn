# Python Test Automation — Interview Q&A

**How do you make data tests maintainable?** Separate test intent, fixtures/configuration and reusable validators; use clear keys/oracles; return actionable mismatch evidence.

**What belongs in CI?** Fast deterministic rules, schema/contracts and unit validators on every change; integration/e2e and performance/security in appropriate controlled stages.

**How do you handle money?** Use `Decimal`, agreed rounding and independent control totals—not binary floats.

**How do you prevent false confidence?** Test the validator itself with known corrupt fixtures and negative assertions; verify that a broken rule fails the gate.

**What makes automation valuable?** Stable, frequent, high-risk checks with fast feedback and evidence, not automating every manual observation.
