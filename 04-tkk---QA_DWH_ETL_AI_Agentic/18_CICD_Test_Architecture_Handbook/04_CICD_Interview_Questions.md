# CI/CD Test Architecture — Interview Q&A

**How do you order test stages?** Fast deterministic checks first, then contracts/data validators, integration/evaluation, NFR in suitable environment and post-deploy monitors.

**What is a quality gate?** A documented release decision with threshold, evidence, owner, failure action and waiver/expiry—not merely a dashboard number.

**How do you handle flaky critical tests?** Investigate/root-cause urgently; do not ignore. If temporary workaround is needed, block or add compensating control with owner and expiry.

**How do you version test data?** Store synthetic/masked fixtures and gold sets with code, label provenance, expected oracle and controlled change review.

**What artifacts matter?** Test report, mismatch extract, traces/logs, data/model/prompt/index versions, environment and release decision.
