# ============================================================
# CHAPTER 13: FINE-TUNING & ALIGNMENT
# Practice in: VS Code (runnable numpy math — no GPU/network)
# "When do you fine-tune vs RAG vs prompt? Explain LoRA/QLoRA
# and DPO vs RLHF." These are staple senior questions. This
# chapter gives you the DECISION FRAMEWORK + the math, runnable.
# ============================================================

import numpy as np

rng = np.random.default_rng(0)

# ============================================================
# SECTION 1: THE DECISION FRAMEWORK (lead with this)
# ------------------------------------------------------------
# Ordered by cost/effort — try cheaper first:
#   1. PROMPTING (few-shot, better instructions)  -> fastest, free
#   2. RAG (inject knowledge at inference)         -> for FACTS that
#      change / are proprietary. Fixes "doesn't KNOW".
#   3. FINE-TUNING                                 -> for BEHAVIOR/
#      FORMAT/STYLE/skill the model can't be prompted into. Fixes
#      "doesn't know HOW". Does NOT reliably add fresh facts.
#   4. Continued PRE-TRAINING                      -> new domain/
#      language at scale; expensive, rare.
# Interview line: "RAG for knowledge, fine-tuning for behavior.
# If the model doesn't KNOW -> RAG. If it can't DO the task in the
# right way -> fine-tune. They compose: fine-tune the style, RAG
# the facts."
# ============================================================


# ============================================================
# SECTION 2: PEFT & LoRA — the math that makes it cheap
# ------------------------------------------------------------
# Full fine-tuning updates ALL weights (billions) -> huge memory.
# LoRA freezes W and learns a LOW-RANK update: W' = W + (alpha/r)*B@A
# where A is (r x d_in), B is (d_out x r), r << d.
# You train only A and B -> ~0.1-1% of parameters.
# ============================================================

def lora_param_stats(d_in, d_out, r):
    full = d_in * d_out                 # a full weight matrix
    lora = r * d_in + d_out * r         # A + B
    return full, lora, full / lora

print("=== LoRA parameter efficiency (per weight matrix) ===")
for (d_in, d_out, r) in [(4096, 4096, 8), (4096, 4096, 16), (4096, 11008, 8)]:
    full, lora, ratio = lora_param_stats(d_in, d_out, r)
    print(f"  d=({d_in}x{d_out}) r={r:2d}: full={full:>11,}  lora={lora:>8,}  "
          f"{ratio:>6.0f}x fewer")
full, lora, ratio = lora_param_stats(4096, 4096, 8)
assert ratio > 100
print("[PASS] LoRA trains ~hundreds of times fewer params per matrix\n")

# A runnable LoRA-adapted linear layer to show it actually works
class LoRALinear:
    def __init__(self, d_in, d_out, r=8, alpha=16):
        self.W = rng.normal(0, 0.02, (d_out, d_in))   # frozen base
        self.A = rng.normal(0, 0.02, (r, d_in))       # trainable
        self.B = np.zeros((d_out, r))                 # init 0 -> starts as base
        self.scale = alpha / r
    def forward(self, x):
        return self.W @ x + self.scale * (self.B @ (self.A @ x))
    def trainable_fraction(self):
        base = self.W.size
        adapt = self.A.size + self.B.size
        return adapt / (base + adapt)

layer = LoRALinear(512, 512, r=8)
x = rng.normal(size=512)
# At init (B=0) the adapter is a no-op -> output equals the frozen base
assert np.allclose(layer.forward(x), layer.W @ x)
print(f"LoRA layer trainable fraction: {layer.trainable_fraction()*100:.2f}% "
      f"(B init=0 so training starts from the base model)\n")


# ============================================================
# SECTION 3: QLoRA — fine-tune a huge model on ONE GPU
# ------------------------------------------------------------
# QLoRA = quantize the FROZEN base to 4-bit (NF4) + train LoRA
# adapters in 16-bit on top. Key tricks:
#   - NF4 (4-bit NormalFloat) quantization of base weights
#   - Double quantization (quantize the quant constants too)
#   - Paged optimizers (page optimizer state to CPU on spikes)
# Result: fine-tune a 65B model on a single 48GB GPU. Adapters
# stay 16-bit so quality ~matches full-precision LoRA.
# ============================================================

def finetune_memory_gb(params_b, mode):
    """Rough training memory: weights + grads + Adam optimizer state."""
    if mode == "full_fp16":
        # weights(2) + grads(2) + Adam m,v(8) ~= 16 bytes/param
        return params_b * 1e9 * 16 / 1e9
    if mode == "lora_fp16":
        # frozen weights in 16-bit + tiny adapter state
        return params_b * 1e9 * 2 / 1e9 + 1
    if mode == "qlora_4bit":
        # frozen weights in 4-bit + tiny adapter state
        return params_b * 1e9 * 0.5 / 1e9 + 1

print("=== Fine-tuning memory for a 13B model ===")
for mode in ("full_fp16", "lora_fp16", "qlora_4bit"):
    print(f"  {mode:12}: {finetune_memory_gb(13, mode):6.1f} GB")
assert finetune_memory_gb(13, "qlora_4bit") < finetune_memory_gb(13, "full_fp16") / 10
print("[PASS] QLoRA fits where full fine-tuning would OOM\n")


# ============================================================
# SECTION 4: ALIGNMENT — SFT -> preference optimization
# ------------------------------------------------------------
# The post-training pipeline:
#   1. SFT (Supervised Fine-Tuning): imitate high-quality
#      instruction/response pairs. Teaches format + task.
#   2. PREFERENCE OPTIMIZATION: make the model prefer BETTER
#      responses using pairs (chosen > rejected). Two ways:
#        a. RLHF (PPO): train a REWARD MODEL on preferences, then
#           RL-optimize the policy against it (+ KL penalty to a
#           reference so it doesn't drift/reward-hack). Powerful,
#           complex, unstable, needs 4 models in memory.
#        b. DPO (Direct Preference Optimization): skip the reward
#           model + RL. Optimize a simple classification-style loss
#           directly on (chosen, rejected) pairs. Simpler, stable,
#           now the default for most teams.
#        c. ORPO / KTO / IPO: newer variants (ORPO folds preference
#           into SFT in one stage; KTO needs only good/bad labels).
# ============================================================


# ============================================================
# SECTION 5: DPO LOSS — runnable
# ------------------------------------------------------------
# DPO increases the policy's log-prob of CHOSEN over REJECTED
# relative to a frozen REFERENCE model, scaled by beta:
#   loss = -log( sigmoid( beta * ( (logp_chosen - logp_ref_chosen)
#                                 -(logp_reject - logp_ref_reject) ) ) )
# Minimizing it pushes chosen up and rejected down (with a KL
# leash to the reference). We verify the gradient direction.
# ============================================================

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

def dpo_loss(logp_chosen, logp_reject, ref_chosen, ref_reject, beta=0.1):
    margin = (logp_chosen - ref_chosen) - (logp_reject - ref_reject)
    return -np.log(sigmoid(beta * margin) + 1e-12)

print("=== DPO loss behavior ===")
ref_c, ref_r = -2.0, -2.0                 # reference log-probs
# Case A: policy prefers chosen more than reject -> LOW loss
loss_good = dpo_loss(logp_chosen=-1.0, logp_reject=-3.0,
                     ref_chosen=ref_c, ref_reject=ref_r)
# Case B: policy prefers the REJECTED one -> HIGH loss
loss_bad = dpo_loss(logp_chosen=-3.0, logp_reject=-1.0,
                    ref_chosen=ref_c, ref_reject=ref_r)
print(f"  loss when policy prefers CHOSEN : {loss_good:.3f}  (low, good)")
print(f"  loss when policy prefers REJECT : {loss_bad:.3f}  (high, penalized)")
assert loss_good < loss_bad
print("[PASS] DPO rewards preferring the chosen response over the rejected\n")


# ============================================================
# SECTION 6: DATA — the real bottleneck (senior insight)
# ------------------------------------------------------------
# Model quality is usually DATA-limited, not method-limited:
#   - SFT: a few thousand HIGH-QUALITY, diverse examples beat
#     millions of noisy ones ("quality > quantity", LIMA).
#   - Format consistency, deduplication, decontamination (remove
#     eval-set leakage), and coverage of edge cases matter most.
#   - Preference data: clear, consistent labeling of chosen/rejected.
#   - Synthetic data + distillation from a stronger model is common
#     (watch licensing + error amplification).
# Interview line: "I'd spend 80% of effort on data quality and
# eval, not on the training method."
# ============================================================


# ============================================================
# SECTION 7: EVALUATION & PITFALLS
# ------------------------------------------------------------
# - CATASTROPHIC FORGETTING: fine-tuning narrows the model; mix in
#   general data / keep LoRA rank modest / evaluate broad benchmarks.
# - OVERFITTING to the fine-tune set: hold out; watch val loss.
# - Eval on the RIGHT thing: task metrics + safety, not just loss.
# - Adapter management: LoRA adapters are small + swappable -> serve
#   many tasks from ONE base model (multi-LoRA serving).
# - Reproducibility: version data, config, base model, seed.
# ============================================================

# ============================================================
# 30-SECOND ANSWER TO 'FINE-TUNE OR NOT?':
# ------------------------------------------------------------
# "First prompt, then RAG for knowledge. Fine-tune only for
#  behavior/format/skill the model can't be prompted into. I'd use
#  QLoRA to keep it cheap, DPO over PPO for stable alignment, and
#  spend most effort on high-quality data + eval to avoid forgetting.
#  Serve many LoRA adapters off one base model."
# ============================================================

if __name__ == "__main__":
    print("Chapter 13 complete: PEFT/QLoRA + DPO/RLHF + data. ✅")
