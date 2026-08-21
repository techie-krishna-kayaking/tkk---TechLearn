# ============================================================
# CHAPTER 4: LLMs & GenAI
# Practice in: VS Code / Google Colab
# Topics: RAG pipeline, LoRA concepts, prompt engineering,
#         LLM agents, evaluation, production patterns
# ============================================================

# ============================================================
# SECTION 1: RAG Pipeline — Production Implementation
# ============================================================

"""
RAG Architecture:
  Documents → Chunking → Embedding → Vector Store
  Query     → Embedding → ANN Search → Top-K Chunks → LLM → Answer

This is the most asked system in AI Engineer interviews.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional

# --- Chunking Strategy ---

def chunk_document(text: str, chunk_size: int = 512, overlap: int = 64) -> List[str]:
    """
    Sliding window chunking with overlap.
    Overlap ensures context isn't lost at chunk boundaries.
    """
    words  = text.split()
    chunks = []
    step   = chunk_size - overlap
    for i in range(0, len(words), step):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

sample_doc = " ".join([f"word{i}" for i in range(2000)])  # simulate long doc
chunks = chunk_document(sample_doc, chunk_size=512, overlap=64)
print(f"Document: {len(sample_doc.split())} words → {len(chunks)} chunks")


# --- Simple Vector Store (FAISS-like) ---

class SimpleVectorStore:
    """
    In production: use FAISS, Pinecone, Chroma, Weaviate.
    This shows the core mechanics interviewers want to see.
    """
    def __init__(self, dim: int = 1536):
        self.dim      = dim
        self.vectors  = []
        self.texts    = []
        self.metadata = []

    def add(self, text: str, vector: np.ndarray, meta: dict = None):
        self.vectors.append(vector / (np.linalg.norm(vector) + 1e-8))  # normalize
        self.texts.append(text)
        self.metadata.append(meta or {})

    def search(self, query_vec: np.ndarray, top_k: int = 5) -> List[Tuple]:
        if not self.vectors:
            return []
        q_norm = query_vec / (np.linalg.norm(query_vec) + 1e-8)
        matrix = np.array(self.vectors)                     # (n, dim)
        scores = matrix @ q_norm                            # cosine similarity
        top_idx = np.argsort(scores)[::-1][:top_k]
        return [(self.texts[i], float(scores[i]), self.metadata[i]) for i in top_idx]

    def __len__(self):
        return len(self.vectors)


# --- Simulated Embedding Function ---

def embed(text: str, dim: int = 1536) -> np.ndarray:
    """
    In production: use OpenAI text-embedding-3-small, all-MiniLM-L6-v2,
    or E5-large-v2 (best open-source for RAG).
    """
    np.random.seed(hash(text) % 2**32)
    return np.random.randn(dim).astype(np.float32)


# --- Build RAG Index ---

documents = [
    "Python is a high-level programming language known for its simplicity.",
    "Machine learning is a subset of AI that enables computers to learn from data.",
    "Transformers revolutionized NLP by using self-attention mechanisms.",
    "RAG combines retrieval from a knowledge base with LLM generation.",
    "Fine-tuning adapts a pre-trained model to a specific task or domain.",
    "LoRA reduces fine-tuning cost by adding low-rank weight matrices.",
    "Vector databases store embeddings and support approximate nearest neighbor search.",
    "RLHF trains a reward model on human preferences, then optimizes the LLM with PPO.",
]

store = SimpleVectorStore(dim=1536)
for doc in documents:
    for chunk in chunk_document(doc, chunk_size=20, overlap=5):
        store.add(chunk, embed(chunk), meta={"source": doc[:30]})

print(f"\nIndexed {len(store)} chunks into vector store")


# --- RAG Query Pipeline ---

def rag_query(query: str, store: SimpleVectorStore, top_k: int = 3) -> dict:
    """Full RAG pipeline"""
    # Step 1: Embed query
    query_embedding = embed(query)

    # Step 2: Retrieve relevant chunks
    results = store.search(query_embedding, top_k=top_k)

    # Step 3: Build augmented prompt
    context = "\n\n".join([f"[Chunk {i+1}] {text}" for i, (text, score, _) in enumerate(results)])

    prompt = f"""You are a helpful AI assistant. Answer the question based ONLY on the context provided.
If the context doesn't contain the answer, say "I don't know."

Context:
{context}

Question: {query}

Answer:"""

    # Step 4: (In production) call LLM API
    # response = openai.chat.completions.create(
    #     model="gpt-4o", messages=[{"role": "user", "content": prompt}]
    # )
    # answer = response.choices[0].message.content

    return {
        "query":     query,
        "chunks":    [(text, f"{score:.4f}") for text, score, _ in results],
        "prompt_len": len(prompt.split()),
        "prompt":    prompt[:200] + "..."
    }

result = rag_query("What is LoRA fine-tuning?", store, top_k=3)
print(f"\nRAG Query: '{result['query']}'")
print(f"Retrieved {len(result['chunks'])} chunks, prompt length: {result['prompt_len']} words")

# ============================================================
# SECTION 2: LoRA — Intuition + Math
# ============================================================

print("\n=== LoRA: LOW-RANK ADAPTATION ===")

class LoRALayer:
    """
    LoRA adds two small matrices A and B to a frozen weight W.
    Forward: output = x @ W  +  x @ B @ A  * (alpha/r)
    Only A and B are trained. W is frozen.
    Memory saving: instead of fine-tuning W (d x k), only train A (r x k) + B (d x r)
    """
    def __init__(self, d_in: int, d_out: int, rank: int = 4, alpha: float = 16):
        self.W     = np.random.randn(d_in, d_out) * 0.01  # frozen base model
        self.A     = np.random.randn(rank, d_out) * 0.01  # trainable
        self.B     = np.zeros((d_in, rank))                # trainable, init=0
        self.scale = alpha / rank

    def forward(self, x: np.ndarray) -> np.ndarray:
        base     = x @ self.W                  # frozen forward pass
        lora     = x @ self.B @ self.A         # low-rank adaptation
        return base + self.scale * lora

    @property
    def trainable_params(self) -> int:
        return self.A.size + self.B.size

    @property
    def total_params(self) -> int:
        return self.W.size + self.trainable_params


d_in, d_out, rank = 4096, 4096, 8
layer = LoRALayer(d_in, d_out, rank=rank, alpha=16)
x_test = np.random.randn(32, d_in)  # batch of 32
output = layer.forward(x_test)
print(f"Full weight matrix:  {d_in:,} × {d_out:,} = {d_in*d_out:,} params")
print(f"LoRA trainable:      {layer.trainable_params:,} params ({layer.trainable_params/layer.total_params*100:.2f}%)")
print(f"Memory saved:        ~{(1 - layer.trainable_params/layer.total_params)*100:.1f}%")
print(f"Output shape:        {output.shape}")

# ============================================================
# SECTION 3: Prompt Engineering Patterns
# ============================================================

print("\n=== PROMPT ENGINEERING PATTERNS ===")

prompts = {
    "Zero-Shot": """
Classify the sentiment of this review as POSITIVE, NEGATIVE, or NEUTRAL.
Review: "The product works okay but shipping was terrible."
Sentiment:""",

    "Few-Shot": """
Classify sentiment. Examples:
"Amazing quality!" → POSITIVE
"Total waste of money." → NEGATIVE
"It does what it says." → NEUTRAL

Review: "The product works okay but shipping was terrible."
Sentiment:""",

    "Chain-of-Thought": """
A customer spent $150 on 3 items. Item A costs $40, item B costs $65.
Let's think step by step:
1. Cost of A and B: $40 + $65 = $105
2. Remaining for C: $150 - $105 = $45
Therefore, item C costs: $45""",

    "ReAct (Reason + Act)": """
Question: What is the population of India divided by the population of Australia?
Thought: I need to find populations of both countries.
Action: search("population of India 2024")
Observation: India population: 1.44 billion
Action: search("population of Australia 2024")
Observation: Australia population: 26 million
Thought: Now I can calculate.
Action: calculate(1440 / 26)
Observation: 55.38
Answer: India's population is approximately 55× that of Australia.""",

    "System + User separation": """
SYSTEM: You are a senior data scientist. Be precise, concise, cite formulas.
USER: Explain regularization in ML.""",
}

for name, prompt in prompts.items():
    print(f"\n  [{name}]")
    print(f"  {prompt[:120].strip()}...")

# ============================================================
# SECTION 4: LLM Evaluation Metrics
# ============================================================

print("\n=== LLM EVALUATION METRICS ===")

evaluation_metrics = {
    "BLEU": "n-gram precision vs reference. Good for translation. Bad for open-ended.",
    "ROUGE-L": "Longest common subsequence recall. Good for summarization.",
    "BERTScore": "Semantic similarity using BERT embeddings. Better than n-gram metrics.",
    "Perplexity": "2^(avg cross-entropy). Lower = model more confident. Intrinsic metric.",
    "G-Eval": "LLM-as-judge: GPT-4 rates output on coherence, fluency, relevance (1-5).",
    "RAGAS": "RAG-specific: context_precision, context_recall, faithfulness, answer_relevancy.",
    "Human Eval": "Gold standard. Expensive. Measure: preference rate, helpfulness, safety.",
}

for metric, description in evaluation_metrics.items():
    print(f"  {metric:15s}: {description}")

# ============================================================
# SECTION 5: Hallucination Mitigation Patterns
# ============================================================

print("\n=== HALLUCINATION MITIGATION ===")

class HallucinationMitigator:
    """Production patterns to reduce LLM hallucination"""

    @staticmethod
    def self_consistency(query: str, n_samples: int = 5) -> str:
        """
        Sample n responses, take majority vote.
        Best for reasoning/math tasks.
        Increases cost n×, reduces error rate ~40%.
        """
        # In production: call LLM n times with temperature > 0
        responses = [f"Answer_variant_{i}" for i in range(n_samples)]
        # Take most common answer
        return max(set(responses), key=responses.count)

    @staticmethod
    def grounded_generation(query: str, retrieved_chunks: List[str]) -> str:
        """Force model to cite sources — enables fact-checking"""
        prompt = f"""Answer based ONLY on the sources below. 
For each claim, cite the source number in [brackets].
If unsure, say "Based on available context, I cannot confirm..."

Sources:
{''.join(f'[{i+1}] {c}' for i, c in enumerate(retrieved_chunks))}

Question: {query}"""
        return prompt  # pass to LLM

    @staticmethod
    def constitutional_ai_check(response: str) -> str:
        """
        Have LLM critique its own response for:
        1. Factual accuracy
        2. Potential harms
        3. Completeness
        Then revise.
        """
        critique_prompt = f"""Review this response for factual errors, missing caveats, or harmful content:

Response: {response}

Critique:
1. What might be incorrect?
2. What important caveats are missing?
3. What should be changed?

Revised response:"""
        return critique_prompt


mitigator = HallucinationMitigator()
print("\nHallucination mitigation strategies:")
print("  1. RAG with grounded generation + citations")
print("  2. Self-consistency (majority vote across N samples)")
print("  3. Constitutional AI (self-critique + revise)")
print("  4. Temperature = 0 for factual tasks")
print("  5. JSON-mode + schema validation")
print("  6. LlamaGuard / NeMo Guardrails for safety filtering")

print("\n✅ Chapter 4: LLMs & GenAI complete!")
