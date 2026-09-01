# 12 — RAG Testing

## QA focus

Separately validate ingestion/chunking, indexing, retrieval, context assembly and generation; then test the end-to-end answer.

## Metrics and risks

Recall@k and ranking quality for retrieval; context relevance and citation coverage; groundedness and answer correctness; stale/unauthorized source content, chunk-boundary loss, duplicate chunks and prompt injection embedded in documents.

## Practice

Create a golden set with questions, approved source passages, expected citations, unacceptable claims and access-control expectations. Include tests where retrieval is correct but generation invents an answer.

## Interview probe

How would you isolate whether a wrong RAG answer is a retrieval defect, generation defect, source-data defect or test-oracle defect?
