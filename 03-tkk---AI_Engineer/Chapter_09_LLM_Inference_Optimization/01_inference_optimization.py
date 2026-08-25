# ============================================================
# CHAPTER 9: LLM INFERENCE OPTIMIZATION & SERVING
# Practice in: VS Code (runnable numpy sims — no GPU needed)
# The #1 differentiator for AI-INFRA / applied roles at
# OpenAI, Anthropic, Meta, NVIDIA, Databricks. This is what
# separates a 100 LPA offer from a 150 LPA offer.
# ============================================================
#
# WHY THIS CHAPTER: "How would you serve a 70B model at low
# latency and high throughput, cheaply?" is THE senior AI
# infra question. You must speak KV cache, batching, quant,
# and parallelism fluently — with the numbers.
# ============================================================

import numpy as np

# ============================================================
# SECTION 1: THE TWO PHASES — PREFILL vs DECODE (say this first)
# ------------------------------------------------------------
# Autoregressive generation has two very different phases:
#   PREFILL : process the whole prompt in ONE parallel pass ->
#             compute-bound (big matmuls), fills the KV cache.
#   DECODE  : generate 1 token at a time, reusing the cache ->
#             MEMORY-BANDWIDTH-bound (tiny matmuls, load weights
#             + KV each step). This is where latency lives.
# Interview line: "Prefill is compute-bound; decode is memory-
# bandwidth-bound. Most serving optimizations target decode."
# ============================================================


# ============================================================
# SECTION 2: KV CACHE — why it exists and what it costs
# ------------------------------------------------------------
# Without a cache, generating token t re-attends over tokens
# 0..t-1 from scratch -> O(n^2) recompute. The KV cache stores
# the K and V projections of past tokens so each new token is
# O(n) attention against cached keys/values.
# ============================================================

def kv_cache_bytes(n_layers, n_kv_heads, head_dim, seq_len,
                   batch, dtype_bytes=2):
    """Memory for the KV cache. 2 = one K + one V tensor."""
    return 2 * n_layers * n_kv_heads * head_dim * seq_len * batch * dtype_bytes


# Example: a Llama-3-8B-ish config (GQA: 8 KV heads), fp16
cfg = dict(n_layers=32, n_kv_heads=8, head_dim=128)
for seq in (2048, 8192, 32768):
    gb = kv_cache_bytes(**cfg, seq_len=seq, batch=1) / 1e9
    print(f"KV cache @ seq={seq:6d}, batch=1 : {gb:5.2f} GB")

# Compare naive recompute vs cached FLOPs growth for decode
def attention_flops(seq_len, cached):
    # per new token: cached -> O(seq), naive -> O(seq^2) recompute
    return seq_len if cached else seq_len * seq_len

n = 4096
speedup = attention_flops(n, cached=False) / attention_flops(n, cached=True)
print(f"\nKV cache cuts per-token attention work ~{speedup:.0f}x at seq={n}")
assert speedup == n
print("[TEACHING] KV cache trades MEMORY for COMPUTE — but memory becomes the bottleneck.\n")


# ============================================================
# SECTION 3: PagedAttention / vLLM — fixing KV memory waste
# ------------------------------------------------------------
# Problem: pre-allocating max_seq_len per request wastes huge
# memory (internal fragmentation) since most requests are short.
# PagedAttention (vLLM) stores the KV cache in fixed-size BLOCKS
# (like OS virtual memory pages), allocated on demand, enabling:
#   - near-zero fragmentation (>90% memory utilization)
#   - copy-on-write sharing of a shared prompt prefix across
#     parallel samples / beams (prefix caching)
# Result: 2-4x higher throughput than naive HF generate().
# ============================================================

def memory_utilization(requests_len, max_len, block_size=16):
    """Compare naive pre-allocation vs paged (block) allocation."""
    naive = sum(max_len for _ in requests_len)               # every req reserves max
    paged = sum(int(np.ceil(l / block_size)) * block_size    # only blocks needed
                for l in requests_len)
    used = sum(requests_len)
    return used / naive, used / paged

reqs = [37, 120, 8, 512, 64, 15]      # varied real request lengths
u_naive, u_paged = memory_utilization(reqs, max_len=2048)
print("=== PagedAttention memory utilization ===")
print(f"Naive pre-allocation (max_len=2048): {u_naive*100:5.1f}% useful")
print(f"Paged block allocation (block=16)  : {u_paged*100:5.1f}% useful")
assert u_paged > u_naive * 5
print("[PASS] paging removes fragmentation -> far higher effective capacity\n")


# ============================================================
# SECTION 4: CONTINUOUS (IN-FLIGHT) BATCHING — throughput king
# ------------------------------------------------------------
# Static batching waits for the SLOWEST sequence in a batch to
# finish before starting new work -> GPU idles. Continuous
# batching evicts finished sequences and injects new ones EVERY
# step, keeping the GPU saturated. This is vLLM/TGI's core win.
# ============================================================

def simulate_batching(seq_lengths, max_batch=4, continuous=True):
    """Return total GPU 'steps' to finish all requests."""
    remaining = list(seq_lengths)
    active, steps, i = [], 0, 0
    while i < len(remaining) or active:
        # fill free slots
        while len(active) < max_batch and i < len(remaining):
            active.append(remaining[i]); i += 1
        steps += 1
        active = [x - 1 for x in active]
        if continuous:
            active = [x for x in active if x > 0]          # evict finished immediately
        else:
            if all(x <= 0 for x in active):                # static: wait for whole batch
                active = []
    return steps

lengths = [50, 6, 6, 6, 48, 5, 5, 5]
static = simulate_batching(lengths, continuous=False)
cont = simulate_batching(lengths, continuous=True)
print("=== Continuous vs static batching (GPU steps to clear queue) ===")
print(f"Static batching     : {static} steps")
print(f"Continuous batching : {cont} steps  ({static/cont:.2f}x faster)")
assert cont < static
print("[PASS] continuous batching keeps the GPU busy -> higher throughput\n")


# ============================================================
# SECTION 5: QUANTIZATION — fit bigger models, go faster
# ------------------------------------------------------------
# Store weights in fewer bits. Decode is memory-bandwidth-bound,
# so smaller weights => less to load => faster + cheaper.
#   FP16/BF16 (16-bit) : training/default
#   INT8               : ~2x smaller, minimal quality loss
#   INT4 (GPTQ/AWQ/GGUF): ~4x smaller, small quality loss
# GPTQ = post-training, layer-wise error minimization.
# AWQ  = activation-aware (protect salient weights).
# GGUF = llama.cpp format for CPU/edge.
# ============================================================

def model_mem_gb(params_billion, bits):
    return params_billion * 1e9 * (bits / 8) / 1e9

print("=== Quantization: weight memory for a 70B model ===")
for bits, name in [(16, "FP16"), (8, "INT8"), (4, "INT4")]:
    print(f"{name:5} ({bits:2d}-bit): {model_mem_gb(70, bits):6.1f} GB")
fp16 = model_mem_gb(70, 16); int4 = model_mem_gb(70, 4)
print(f"INT4 vs FP16 memory reduction: {fp16/int4:.0f}x "
      f"(70B fits on a single 40GB GPU at INT4)")
assert abs(fp16 / int4 - 4) < 1e-6
print()


# ============================================================
# SECTION 6: SPECULATIVE DECODING — latency without quality loss
# ------------------------------------------------------------
# A small cheap DRAFT model proposes k tokens; the big TARGET
# model VERIFIES them in one parallel pass. Accepted tokens are
# free; on reject you fall back. Output distribution is provably
# identical to the target model (lossless). 2-3x fewer big-model
# steps when acceptance is high.
# ============================================================

rng = np.random.default_rng(0)
def speculative_decode(n_tokens, k=4, accept_rate=0.7):
    produced, big_model_calls = 0, 0
    while produced < n_tokens:
        big_model_calls += 1                 # one verification pass covers up to k drafts
        accepted = 0
        for _ in range(k):
            if rng.random() < accept_rate:
                accepted += 1
            else:
                break
        produced += accepted + 1             # +1 correction/bonus token from target
    return big_model_calls

N = 200
baseline_calls = N                            # 1 big-model call per token normally
spec_calls = speculative_decode(N, k=4, accept_rate=0.75)
print("=== Speculative decoding (draft + verify) ===")
print(f"Baseline big-model calls : {baseline_calls}")
print(f"Speculative big-model calls: {spec_calls}  ({baseline_calls/spec_calls:.2f}x fewer)")
assert spec_calls < baseline_calls
print("[PASS] verify-in-parallel cuts expensive big-model steps, lossless\n")


# ============================================================
# SECTION 7: PARALLELISM (fit models too big for one GPU)
# ------------------------------------------------------------
# TENSOR parallelism : split each layer's matmul across GPUs
#                      (all-reduce per layer; needs fast NVLink).
# PIPELINE parallelism: split LAYERS across GPUs (micro-batches
#                      to fill the pipeline; watch the bubble).
# EXPERT parallelism : route tokens to experts (MoE) across GPUs.
# Data parallelism   : replicas for THROUGHPUT (see Ch15 training).
# Rule: tensor-parallel within a node (NVLink), pipeline across nodes.
# ============================================================


# ============================================================
# SECTION 8: THE METRICS + STACK YOU MUST NAME
# ------------------------------------------------------------
# Latency metrics:
#   TTFT  (time to first token)  -> prefill speed / prompt length
#   TPOT / ITL (time per output token) -> decode speed
#   e2e latency = TTFT + TPOT * output_tokens
# Throughput: tokens/sec across all concurrent requests.
# Serving stacks: vLLM, TGI (HF), TensorRT-LLM (NVIDIA),
#   SGLang, llama.cpp (CPU/edge), Ray Serve for orchestration.
# ============================================================

def e2e_latency_ms(ttft_ms, tpot_ms, out_tokens):
    return ttft_ms + tpot_ms * out_tokens

print("=== Latency budgeting ===")
lat = e2e_latency_ms(ttft_ms=180, tpot_ms=18, out_tokens=200)
print(f"TTFT=180ms, TPOT=18ms, 200 out tokens -> e2e = {lat/1000:.2f}s")
print("Lever: cut TPOT (quant/batching/spec-decode) to hit a p95 SLA.\n")

# ============================================================
# 30-SECOND ANSWER TO 'SERVE A 70B MODEL CHEAPLY & FAST':
# ------------------------------------------------------------
# "INT4/AWQ quantize to fit + cut bandwidth; vLLM with Paged-
#  Attention + continuous batching for throughput; tensor-
#  parallel within the node; speculative decoding to drop TPOT;
#  prefix-cache shared system prompts. Budget to a TTFT/TPOT SLA
#  and measure tokens/sec/$ ."
# ============================================================

if __name__ == "__main__":
    print("Chapter 9 complete: you can now design LLM serving to an SLA. ✅")
