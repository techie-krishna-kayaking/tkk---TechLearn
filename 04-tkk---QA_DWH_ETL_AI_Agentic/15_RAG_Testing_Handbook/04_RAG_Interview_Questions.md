# RAG Testing — Interview Q&A

**How do you isolate a wrong RAG answer?** Check authoritative source, ingestion/index version, retrieval top-k/filters, assembled context and generation/citation separately; preserve each stage in trace.

**What is retrieval recall@k?** Whether the required approved passage appears among top k retrieved results; it is necessary but not sufficient for a correct answer.

**How do you test access control?** Use persona/tenant contexts and assert unauthorized chunks never enter retrieval/context/output, including via metadata/filter bypass attempts.

**How do you test stale knowledge?** Version source/index, use known superseded documents and assert current source retrieval/citation; monitor ingestion-to-index freshness.

**Why test malicious documents?** Indirect prompt injection can be embedded in retrieved content; assert it is treated as untrusted data, not system instruction.
