# ============================================================
# CHAPTER 10: ADVANCED RAG (Retrieval-Augmented Generation)
# Practice in: VS Code (runnable numpy — no API keys needed)
# Basic RAG (embed -> ANN -> stuff context) is table stakes.
# THIS chapter is what product companies actually grill:
# hybrid search, reranking, query rewriting, and RAG EVALUATION.
# ============================================================

import numpy as np
import re
import hashlib
from collections import Counter, defaultdict

rng = np.random.default_rng(7)

# ============================================================
# SECTION 1: WHY BASIC RAG FAILS (name these in interviews)
# ------------------------------------------------------------
# 1. Dense-only retrieval misses EXACT terms (IDs, codes, rare
#    keywords) -> add lexical (BM25) = HYBRID search.
# 2. Top-k by similarity != most RELEVANT -> add a RERANKER.
# 3. Bad user queries -> QUERY REWRITING / HyDE.
# 4. Wrong chunking destroys context -> chunking strategy.
# 5. "It works on my 5 examples" -> you need RAG EVALUATION.
# ============================================================

CORPUS = [
    "The Model Context Protocol (MCP) standardizes tool access for LLM agents.",
    "PagedAttention in vLLM stores the KV cache in fixed-size blocks.",
    "LoRA freezes base weights and trains low-rank adapter matrices A and B.",
    "Error code E-4092 indicates a payment gateway timeout in checkout.",
    "RAG combines a retriever with a generator to ground answers in documents.",
    "Speculative decoding uses a small draft model verified by the target model.",
    "The refund policy allows returns within 30 days for error code E-4092 orders.",
    "BM25 is a bag-of-words ranking function based on term frequency and IDF.",
]


# ============================================================
# SECTION 2: BM25 (lexical) — exact-term retrieval
# ------------------------------------------------------------
def tokenize(t):
    return re.findall(r"[a-z0-9\-]+", t.lower())

class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.docs = [tokenize(d) for d in docs]
        self.k1, self.b = k1, b
        self.N = len(docs)
        self.avgdl = np.mean([len(d) for d in self.docs])
        self.df = Counter()
        for d in self.docs:
            for term in set(d):
                self.df[term] += 1

    def idf(self, term):
        n = self.df.get(term, 0)
        return np.log((self.N - n + 0.5) / (n + 0.5) + 1)

    def score(self, query, i):
        d = self.docs[i]; freqs = Counter(d); dl = len(d)
        s = 0.0
        for term in tokenize(query):
            if term not in freqs:
                continue
            tf = freqs[term]
            s += self.idf(term) * tf * (self.k1 + 1) / (
                tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
        return s

    def search(self, query, top_k=5):
        scores = [(i, self.score(query, i)) for i in range(self.N)]
        return sorted(scores, key=lambda x: -x[1])[:top_k]


bm25 = BM25(CORPUS)
q = "what does error code E-4092 mean"
print("=== BM25 lexical search (nails the exact code) ===")
for i, s in bm25.search(q, 3):
    print(f"  {s:5.2f}  {CORPUS[i][:60]}")
top_bm25 = bm25.search(q, 1)[0][0]
assert "E-4092" in CORPUS[top_bm25]
print("[PASS] lexical retrieval finds the exact-term doc dense search often misses\n")


# ============================================================
# SECTION 3: DENSE search (semantic) — fake but deterministic
# ------------------------------------------------------------
# We simulate embeddings with a hashed bag-of-words vector so it
# runs offline. In production use a real embedding model.
# ============================================================
DIM = 64
def _tok_hash(tok):
    # deterministic across processes (unlike Python's randomized hash())
    return int(hashlib.md5(tok.encode()).hexdigest(), 16) % DIM

def embed(text):
    v = np.zeros(DIM)
    for tok in tokenize(text):
        v[_tok_hash(tok)] += 1.0
    n = np.linalg.norm(v)
    return v / n if n else v

DOC_EMB = np.array([embed(d) for d in CORPUS])

def dense_search(query, top_k=5):
    qe = embed(query)
    sims = DOC_EMB @ qe
    idx = np.argsort(-sims)[:top_k]
    return [(int(i), float(sims[i])) for i in idx]


# ============================================================
# SECTION 4: HYBRID SEARCH — fuse lexical + dense (RRF)
# ------------------------------------------------------------
# Reciprocal Rank Fusion: score = sum 1/(k + rank) across
# retrievers. Robust, no score normalization needed.
# ============================================================
def reciprocal_rank_fusion(rankings, k=60):
    fused = defaultdict(float)
    for ranking in rankings:
        for rank, (doc_id, _) in enumerate(ranking):
            fused[doc_id] += 1.0 / (k + rank)
    return sorted(fused.items(), key=lambda x: -x[1])

q2 = "how to fix payment timeout E-4092 and get a refund"
bm = bm25.search(q2, 5)
dn = dense_search(q2, 5)
hybrid = reciprocal_rank_fusion([bm, dn])
print("=== Hybrid search (RRF of BM25 + dense) ===")
for doc_id, s in hybrid[:4]:
    print(f"  {s:.4f}  {CORPUS[doc_id][:60]}")
hybrid_ids = {d for d, _ in hybrid[:4]}
# hybrid should surface BOTH the error-code doc AND the refund-policy doc
assert any("E-4092" in CORPUS[d] for d in hybrid_ids)
assert any("refund" in CORPUS[d] for d in hybrid_ids)
print("[PASS] hybrid recalls exact-term AND semantically related docs\n")


# ============================================================
# SECTION 5: RERANKING — cross-encoder precision
# ------------------------------------------------------------
# Retrieval (bi-encoder/BM25) is cheap but coarse: get top-50.
# A cross-encoder RERANKER jointly encodes (query, doc) and
# scores relevance precisely -> keep top-5. Big precision win.
# We simulate a cross-encoder with token-overlap + a relevance
# prior; in prod use bge-reranker / Cohere Rerank.
# ============================================================
def cross_encoder_score(query, doc):
    qs, ds = set(tokenize(query)), set(tokenize(doc))
    overlap = len(qs & ds) / (len(qs) + 1e-9)
    # cross-encoders also reward phrase/entity matches:
    entity_bonus = 0.5 if any(t.upper() in doc for t in tokenize(query) if "-" in t) else 0
    return overlap + entity_bonus

def rerank(query, candidate_ids, top_k=3):
    scored = [(i, cross_encoder_score(query, CORPUS[i])) for i in candidate_ids]
    return sorted(scored, key=lambda x: -x[1])[:top_k]

candidates = [d for d, _ in hybrid[:6]]
reranked = rerank(q2, candidates, top_k=3)
print("=== Cross-encoder reranking (retrieve wide, rerank tight) ===")
for i, s in reranked:
    print(f"  {s:.3f}  {CORPUS[i][:60]}")
print("[PATTERN] retrieve top-50 (cheap) -> rerank to top-5 (precise) -> generate\n")


# ============================================================
# SECTION 6: QUERY TRANSFORMATION (rewriting + HyDE)
# ------------------------------------------------------------
# - Query rewriting: expand vague queries, add synonyms, resolve
#   pronouns from chat history before retrieval.
# - HyDE (Hypothetical Document Embeddings): ask the LLM to draft
#   a hypothetical ANSWER, embed THAT, and retrieve with it —
#   answers look more like documents than questions do.
# - Multi-query: generate N paraphrases, retrieve each, fuse.
# - Decomposition: split multi-hop questions into sub-queries.
# ============================================================
def multi_query_expand(query):
    # In prod an LLM generates these; here a rule-based stub.
    base = [query]
    if "fix" in query or "how" in query:
        base.append(query.replace("how to fix", "solution for"))
    base.append(" ".join(tokenize(query)))
    return base

expansions = multi_query_expand(q2)
fused_multi = reciprocal_rank_fusion([bm25.search(e, 5) for e in expansions])
print("=== Multi-query expansion + fusion ===")
print(f"Expanded '{q2[:40]}...' into {len(expansions)} queries")
print(f"Top doc after fusion: {CORPUS[fused_multi[0][0]][:60]}\n")


# ============================================================
# SECTION 7: CHUNKING STRATEGIES (retrieval quality starts here)
# ------------------------------------------------------------
# - Fixed-size + overlap: simple baseline.
# - Semantic/recursive: split on structure (headings, sentences)
#   so a chunk is a coherent idea.
# - Small-to-big: retrieve small precise chunks, then expand to
#   the parent section for the LLM (best of both).
# - Add METADATA (source, title, section) for filtering + citations.
# Trade-off: small chunks = precise retrieval, less context;
#            large chunks = more context, noisier retrieval.
# ============================================================


# ============================================================
# SECTION 8: RAG EVALUATION (RAGAS-style) — the senior signal
# ------------------------------------------------------------
# You CANNOT ship RAG without metrics. Evaluate two halves:
#   RETRIEVAL:  context_precision (are retrieved chunks relevant?)
#               context_recall    (did we get all needed chunks?)
#   GENERATION: faithfulness      (is the answer grounded, no
#                                  hallucination?)
#               answer_relevancy  (does it address the question?)
# In prod: RAGAS / an LLM-as-judge computes these. Here we do it
# with set overlap so it's runnable and transparent.
# ============================================================
def context_precision(retrieved_ids, relevant_ids):
    if not retrieved_ids:
        return 0.0
    hits = sum(1 for i in retrieved_ids if i in relevant_ids)
    return hits / len(retrieved_ids)

def context_recall(retrieved_ids, relevant_ids):
    if not relevant_ids:
        return 1.0
    hits = sum(1 for i in relevant_ids if i in retrieved_ids)
    return hits / len(relevant_ids)

STOPWORDS = {"a", "an", "the", "you", "also", "is", "are", "and", "or", "to",
             "of", "in", "for", "on", "within", "can", "get", "receive", "it"}

def _content(text):
    return {t for t in tokenize(text) if t not in STOPWORDS}

def faithfulness(answer_claims, context_text):
    ctx = _content(context_text)
    grounded = sum(1 for c in answer_claims if _content(c) & ctx)
    return grounded / max(len(answer_claims), 1)

# gold: docs 3 (E-4092) and 6 (refund policy) are the relevant ones
relevant = {3, 6}
retrieved = [i for i, _ in reranked]
answer_claims = [
    "Error E-4092 is a payment gateway timeout",   # grounded
    "You can get a refund within 30 days",         # grounded
    "You also receive a free coupon",              # NOT grounded -> hallucination
]
context = " ".join(CORPUS[i] for i in retrieved)

cp = context_precision(retrieved, relevant)
cr = context_recall(retrieved, relevant)
fa = faithfulness(answer_claims, context)
print("=== RAG evaluation scorecard ===")
print(f"context_precision : {cp:.2f}")
print(f"context_recall    : {cr:.2f}")
print(f"faithfulness      : {fa:.2f}   (<1.0 flags a hallucinated claim)")
assert cr == 1.0, "reranked set should contain both gold docs"
assert fa < 1.0, "the ungrounded claim must lower faithfulness"
print("[PASS] eval catches perfect recall but a hallucinated 3rd claim\n")

# ============================================================
# 30-SECOND ANSWER TO 'DESIGN A PRODUCTION RAG SYSTEM':
# ------------------------------------------------------------
# "Semantic chunking + metadata; HYBRID retrieval (BM25 + dense)
#  fused with RRF; retrieve wide then CROSS-ENCODER rerank to
#  top-k; query rewriting/HyDE for weak queries; grounded
#  generation with citations; and continuous RAGAS eval
#  (context precision/recall + faithfulness) in CI + online."
# ============================================================

if __name__ == "__main__":
    print("Chapter 10 complete: production-grade RAG + evaluation. ✅")
