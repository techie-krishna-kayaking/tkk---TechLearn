# ============================================================
# CHAPTER 15: DISTRIBUTED TRAINING AT SCALE
# Practice in: VS Code (runnable numpy math — no GPU/cluster)
# For ML-infra / applied-research-engineer roles (the top of the
# 100-150 LPA band), "how do you train a model that doesn't fit
# on one GPU?" is a must-answer. This chapter gives you the
# parallelism strategies, memory math, and trade-offs.
# ============================================================

import numpy as np

# ============================================================
# SECTION 1: THE MEMORY WALL (why we need this at all)
# ------------------------------------------------------------
# Training memory per parameter (mixed precision + Adam):
#   fp16 weights(2) + fp16 grads(2) + fp32 master weights(4)
#   + Adam m(4) + Adam v(4)  ~= 16 bytes/param
# Plus ACTIVATIONS (scale with batch x seq x layers).
# ============================================================

def training_memory_gb(params_b, bytes_per_param=16):
    return params_b * 1e9 * bytes_per_param / 1e9

print("=== The memory wall (model states only, ~16 B/param) ===")
for p in (7, 13, 70, 175):
    print(f"  {p:3d}B params -> {training_memory_gb(p):7.0f} GB just for states")
print("  (an 80GB H100 holds model states for only a ~5B model at fp16+Adam)\n")
assert training_memory_gb(70) > 1000


# ============================================================
# SECTION 2: DATA PARALLELISM (DP / DDP) — throughput
# ------------------------------------------------------------
# Replicate the FULL model on each GPU; each processes a
# different micro-batch; gradients are AVERAGED via ALL-REDUCE
# every step, so all replicas stay in sync.
#   + Simple, near-linear throughput scaling.
#   - Model must FIT on one GPU (every GPU holds a full copy).
#   - Communication = all-reduce of the full gradient each step.
# PyTorch: DistributedDataParallel (DDP). Ring all-reduce makes
# comms volume independent of the number of GPUs.
# ============================================================

def ddp_effective_batch(per_gpu_batch, n_gpus, grad_accum=1):
    return per_gpu_batch * n_gpus * grad_accum

print("=== Data parallelism (DDP) ===")
eff = ddp_effective_batch(per_gpu_batch=8, n_gpus=64, grad_accum=4)
print(f"  8/GPU x 64 GPUs x 4 accum = effective batch {eff:,}")
print("  Gradient accumulation simulates a big batch without the memory.\n")
assert eff == 2048


# ============================================================
# SECTION 3: ZeRO / FSDP — shard the states (fit bigger models)
# ------------------------------------------------------------
# DDP wastes memory by REPLICATING optimizer states, gradients,
# and weights on every GPU. ZeRO (DeepSpeed) / FSDP (PyTorch)
# SHARD them across N GPUs and gather just-in-time:
#   Stage 1: shard optimizer states           (~4x saving)
#   Stage 2: + shard gradients                 (~8x saving)
#   Stage 3: + shard parameters (FSDP)         (~Nx saving)
# Trade-off: more communication (gather/scatter shards) for less
# memory. ZeRO-Offload/Infinity can push state to CPU/NVMe.
# ============================================================

def zero_memory_per_gpu_gb(params_b, n_gpus, stage):
    total = training_memory_gb(params_b)      # all model states
    if stage == 0:   # DDP: full replica per GPU
        return total
    if stage == 1:   # shard optimizer states (12 of 16 bytes)
        return training_memory_gb(params_b, 4) + (training_memory_gb(params_b, 12) / n_gpus)
    if stage == 2:   # + shard gradients (2 of remaining)
        return training_memory_gb(params_b, 2) + (training_memory_gb(params_b, 14) / n_gpus)
    if stage == 3:   # shard everything
        return total / n_gpus

print("=== ZeRO / FSDP memory per GPU (13B model, 64 GPUs) ===")
for stage in (0, 1, 2, 3):
    print(f"  stage {stage}: {zero_memory_per_gpu_gb(13, 64, stage):7.1f} GB/GPU")
assert zero_memory_per_gpu_gb(13, 64, 3) < zero_memory_per_gpu_gb(13, 64, 0)
print("[PASS] ZeRO-3/FSDP shards states -> per-GPU memory drops ~N x\n")


# ============================================================
# SECTION 4: TENSOR & PIPELINE PARALLELISM (model too big period)
# ------------------------------------------------------------
# TENSOR (intra-layer): split a single matmul across GPUs; each
#   holds a slice of the weight matrix. Needs an all-reduce PER
#   layer -> very chatty -> keep WITHIN a node (fast NVLink).
# PIPELINE (inter-layer): put different LAYERS on different GPUs;
#   micro-batches flow through the pipeline. Watch the "bubble"
#   (idle time at fill/drain) -> use more micro-batches (GPipe/1F1B).
# ============================================================

def pipeline_bubble_fraction(n_stages, n_microbatches):
    # bubble ~ (p - 1) / (m + p - 1)
    p, m = n_stages, n_microbatches
    return (p - 1) / (m + p - 1)

print("=== Pipeline parallelism bubble ===")
for m in (1, 4, 16, 64):
    print(f"  4 stages, {m:2d} micro-batches -> bubble {pipeline_bubble_fraction(4, m)*100:4.1f}% idle")
assert pipeline_bubble_fraction(4, 64) < pipeline_bubble_fraction(4, 1)
print("[PASS] more micro-batches shrink the pipeline bubble\n")


# ============================================================
# SECTION 5: 3D PARALLELISM (how frontier models are trained)
# ------------------------------------------------------------
# Combine all three (Megatron-LM / DeepSpeed):
#   TENSOR-parallel WITHIN a node (NVLink),
#   PIPELINE-parallel ACROSS nodes,
#   DATA-parallel (+ ZeRO) across the remaining dimension.
# Total GPUs = TP x PP x DP. Plus EXPERT parallelism for MoE.
# Interview line: "tensor-parallel within the node, pipeline
# across nodes, data-parallel on top — that's 3D parallelism."
# ============================================================

def total_gpus(tp, pp, dp):
    return tp * pp * dp

print("=== 3D parallelism GPU budget ===")
tp, pp, dp = 8, 4, 16
print(f"  TP={tp} x PP={pp} x DP={dp} = {total_gpus(tp, pp, dp)} GPUs")
assert total_gpus(8, 4, 16) == 512
print()


# ============================================================
# SECTION 6: MEMORY-SAVING TECHNIQUES (name these)
# ------------------------------------------------------------
# - MIXED PRECISION (bf16/fp16 + fp32 master): ~2x memory + speed;
#   bf16 preferred (no loss-scaling headaches).
# - GRADIENT (ACTIVATION) CHECKPOINTING: recompute activations in
#   backward instead of storing them -> big activation-memory cut
#   for ~30% extra compute.
# - GRADIENT ACCUMULATION: big effective batch without the memory.
# - FLASH ATTENTION: IO-aware attention -> less memory + faster
#   (no full N x N attention matrix materialized).
# - CPU/NVMe OFFLOAD (ZeRO-Infinity): trade bandwidth for capacity.
# ============================================================

def checkpointing_activation_saving(layers, stored_with_ckpt):
    # store ~sqrt(L) activations instead of L
    return layers / stored_with_ckpt

print("=== Gradient checkpointing ===")
saving = checkpointing_activation_saving(layers=64, stored_with_ckpt=8)
print(f"  store ~8 checkpoints instead of 64 activations -> ~{saving:.0f}x activation memory saved")
print("  cost: recompute activations in backward (~30% extra compute)\n")


# ============================================================
# SECTION 7: COMMUNICATION & FScaling REALITY
# ------------------------------------------------------------
# - Interconnect matters: NVLink/NVSwitch within node, InfiniBand
#   across nodes. Comms often the bottleneck at scale.
# - Overlap compute + comms (async all-reduce) to hide latency.
# - Scaling is SUBLINEAR: watch "scaling efficiency" (throughput
#   vs #GPUs). Stragglers + comms erode it.
# - Checkpoint frequently: at 1000s of GPUs, failures are routine;
#   you must resume, not restart.
# ============================================================

def scaling_efficiency(throughput_1gpu, throughput_n, n):
    return throughput_n / (throughput_1gpu * n)

print("=== Scaling efficiency (sublinear reality) ===")
eff = scaling_efficiency(throughput_1gpu=100, throughput_n=100*64*0.82, n=64)
print(f"  64 GPUs at 82% efficiency -> {eff*100:.0f}% of ideal linear speedup")
assert eff < 1.0
print("[PASS] real clusters scale sublinearly; comms + stragglers cost you\n")

# ============================================================
# 30-SECOND ANSWER TO 'TRAIN A 70B MODEL':
# ------------------------------------------------------------
# "Mixed precision (bf16) + Flash Attention + gradient checkpointing
#  to cut memory; ZeRO-3/FSDP to shard optimizer/grad/params; 3D
#  parallelism (tensor within node, pipeline across nodes, data-
#  parallel on top); gradient accumulation for a large effective
#  batch; frequent checkpointing for fault tolerance; and I'd track
#  scaling efficiency + MFU to know it's actually using the cluster."
# ============================================================

if __name__ == "__main__":
    print("Chapter 15 complete: DP/ZeRO/FSDP + tensor/pipeline + memory. ✅")
