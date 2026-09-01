# RAG Golden Set Template

| Case | Query | Authorized source/passages | Expected facts/citation | Unacceptable result | Retrieval expectation |
|---|---|---|---|---|---|
| RAG-01 | policy question | policy-v3 §4 | accurate answer citing §4 | invented rule | source returned in top-k |

Include permission context, index version, chunk IDs, metadata filters, retrieved context and generation configuration in each execution record.
