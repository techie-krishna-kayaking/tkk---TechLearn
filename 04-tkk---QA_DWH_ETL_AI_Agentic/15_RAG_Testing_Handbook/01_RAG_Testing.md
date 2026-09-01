# 15 — RAG Testing Handbook

## QA focus

Test the chain separately and end to end: source ingestion → chunking → index → retrieval → context assembly → generation → citation/access-control behavior.

## Quality signals

Retrieval Recall@k/ranking, context relevance, citation coverage, groundedness, answer correctness, freshness and authorization compliance. A good final answer can hide poor retrieval; a wrong final answer can occur despite correct retrieval—keep diagnostics separate.

## Risks

Stale index, chunk boundary loss, duplicate chunks, wrong metadata filter, unauthorized document retrieval, malicious embedded instructions, retrieval miss, fabricated citation and context-window truncation.

## Interview line

“I create a gold set that names approved source passages and expected citations, then I distinguish ingestion/retrieval/context/generation defects with stage-level evidence.”
