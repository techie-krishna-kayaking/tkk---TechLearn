# Security & Privacy Testing — Interview Q&A

**Authentication versus authorization?** Authentication verifies identity; authorization verifies permitted action/resource/context after identity is known.

**How do you test PII leakage?** Exercise APIs, exports, prompts, logs/errors/traces and retrieval; assert masking/redaction/refusal and verify audit evidence.

**How do you test AI tool authorization?** Matrix of actor/agent role × tool × argument × target resource; assert no execution without policy/approval and retain complete trace.

**Why test denial paths?** Incorrect denial creates availability issues, while missing denial causes breaches; both reveal policy implementation gaps.

**What is secure failure?** Failing closed where appropriate, not exposing internals/secrets, creating an auditable alert and supporting controlled recovery.
