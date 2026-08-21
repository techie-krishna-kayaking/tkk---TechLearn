# ============================================================
# CHAPTER 3: DEEP LEARNING & NEURAL NETWORKS
# Practice in: VS Code / Google Colab
# Topics: MLP from scratch, backprop, Transformer attention,
#         training tricks, CNN/RNN intuition
# ============================================================

import numpy as np

# ============================================================
# SECTION 1: Neural Network from Scratch (NumPy only)
# This is the single most important exercise — know it cold
# ============================================================

class Sigmoid:
    def forward(self, x):
        self.out = 1 / (1 + np.exp(-np.clip(x, -500, 500)))
        return self.out
    def backward(self, grad):
        return grad * self.out * (1 - self.out)

class ReLU:
    def forward(self, x):
        self.mask = x > 0
        return x * self.mask
    def backward(self, grad):
        return grad * self.mask

class Linear:
    def __init__(self, in_dim, out_dim):
        # He initialization — critical for ReLU networks
        self.W = np.random.randn(in_dim, out_dim) * np.sqrt(2.0 / in_dim)
        self.b = np.zeros(out_dim)
        self.dW = None
        self.db = None

    def forward(self, x):
        self.x = x
        return x @ self.W + self.b

    def backward(self, grad):
        self.dW = self.x.T @ grad           # (in_dim, out_dim)
        self.db = grad.sum(axis=0)           # (out_dim,)
        return grad @ self.W.T              # pass gradient upstream


class MLP:
    """2-layer MLP: Linear → ReLU → Linear → Sigmoid"""
    def __init__(self, in_dim, hidden_dim, out_dim, lr=0.01):
        self.l1  = Linear(in_dim, hidden_dim)
        self.a1  = ReLU()
        self.l2  = Linear(hidden_dim, out_dim)
        self.a2  = Sigmoid()
        self.lr  = lr

    def forward(self, x):
        return self.a2.forward(self.l2.forward(self.a1.forward(self.l1.forward(x))))

    def loss(self, y_pred, y_true):
        """Binary cross-entropy"""
        eps = 1e-8
        return -np.mean(y_true * np.log(y_pred + eps) + (1 - y_true) * np.log(1 - y_pred + eps))

    def backward(self, y_pred, y_true):
        """Backprop: compute all gradients via chain rule"""
        n = len(y_true)
        # dL/d(y_pred) for BCE
        grad = (y_pred - y_true) / (y_pred * (1 - y_pred) + 1e-8) / n
        # Through sigmoid
        grad = self.a2.backward(grad)
        # Through l2
        grad = self.l2.backward(grad)
        # Through relu
        grad = self.a1.backward(grad)
        # Through l1
        self.l1.backward(grad)

    def step(self):
        """SGD update"""
        for layer in [self.l1, self.l2]:
            layer.W -= self.lr * layer.dW
            layer.b -= self.lr * layer.db

    def train(self, X, y, epochs=200):
        losses = []
        for epoch in range(epochs):
            y_pred = self.forward(X)
            loss   = self.loss(y_pred, y)
            self.backward(y_pred, y)
            self.step()
            losses.append(loss)
            if epoch % 50 == 0:
                acc = ((y_pred > 0.5).astype(int).flatten() == y.flatten()).mean()
                print(f"  Epoch {epoch:3d}: loss={loss:.4f}, acc={acc:.4f}")
        return losses


# Demo
np.random.seed(42)
X = np.random.randn(500, 2)
y = ((X[:, 0] ** 2 + X[:, 1] ** 2) < 1.2).astype(float).reshape(-1, 1)

print("=== MLP FROM SCRATCH (NumPy Only) ===")
mlp = MLP(in_dim=2, hidden_dim=16, out_dim=1, lr=0.05)
mlp.train(X, y, epochs=200)

# ============================================================
# SECTION 2: Scaled Dot-Product Attention — From Scratch
# "Implement attention" is the #1 DL interview question at AI labs
# ============================================================

def scaled_dot_product_attention(Q, K, V, mask=None):
    """
    Q: (batch, heads, seq_len, d_k)
    K: (batch, heads, seq_len, d_k)
    V: (batch, heads, seq_len, d_v)
    Returns: (batch, heads, seq_len, d_v), attention_weights
    """
    d_k = Q.shape[-1]

    # Step 1: Compute attention scores
    scores = Q @ K.transpose(0, 1, 3, 2) / np.sqrt(d_k)   # (batch, heads, seq, seq)

    # Step 2: Apply causal mask (for autoregressive generation, GPT-style)
    if mask is not None:
        scores = np.where(mask == 0, -1e9, scores)  # mask future tokens

    # Step 3: Softmax
    exp_scores = np.exp(scores - scores.max(axis=-1, keepdims=True))
    attn_weights = exp_scores / (exp_scores.sum(axis=-1, keepdims=True) + 1e-8)

    # Step 4: Weighted sum of values
    output = attn_weights @ V                                # (batch, heads, seq, d_v)

    return output, attn_weights


# Multi-head attention
def multi_head_attention(Q_in, K_in, V_in, num_heads=4, d_model=64):
    """Split into heads, attend, concatenate"""
    assert d_model % num_heads == 0
    d_k = d_model // num_heads
    batch, seq_len, _ = Q_in.shape

    # Project input (in practice: learned weight matrices W_Q, W_K, W_V)
    W_Q = np.random.randn(d_model, d_model) * 0.01
    W_K = np.random.randn(d_model, d_model) * 0.01
    W_V = np.random.randn(d_model, d_model) * 0.01
    W_O = np.random.randn(d_model, d_model) * 0.01

    Q = Q_in @ W_Q  # (batch, seq, d_model)
    K = K_in @ W_K
    V = V_in @ W_V

    # Reshape to (batch, heads, seq, d_k)
    def split_heads(x):
        return x.reshape(batch, seq_len, num_heads, d_k).transpose(0, 2, 1, 3)

    Q, K, V = split_heads(Q), split_heads(K), split_heads(V)

    # Build causal mask (lower triangular — can't see future)
    causal_mask = np.tril(np.ones((seq_len, seq_len)))[np.newaxis, np.newaxis, :, :]

    # Attend
    attn_out, weights = scaled_dot_product_attention(Q, K, V, mask=causal_mask)

    # Concatenate heads
    attn_out = attn_out.transpose(0, 2, 1, 3).reshape(batch, seq_len, d_model)

    # Output projection
    return attn_out @ W_O, weights  # (batch, seq, d_model)


print("\n=== MULTI-HEAD ATTENTION FROM SCRATCH ===")
batch, seq_len, d_model, n_heads = 2, 10, 64, 4
X_attn = np.random.randn(batch, seq_len, d_model)
output, weights = multi_head_attention(X_attn, X_attn, X_attn, num_heads=n_heads, d_model=d_model)
print(f"Input:  {X_attn.shape}")
print(f"Output: {output.shape}   (same shape — attention is sequence-to-sequence)")
print(f"Attention weights: {weights.shape}  (batch, heads, seq, seq)")

# ============================================================
# SECTION 3: Key Training Tricks — With Code
# ============================================================

print("\n=== TRAINING TRICKS ===")

# 1. Batch Normalization — what it does numerically
def batch_norm(x, gamma=1.0, beta=0.0, eps=1e-8):
    """Normalize across batch dimension"""
    mu    = x.mean(axis=0)
    sigma = x.std(axis=0)
    x_hat = (x - mu) / (sigma + eps)
    return gamma * x_hat + beta, mu, sigma

x_layer = np.random.randn(32, 64) * 10 + 5  # unnormalized activations
x_bn, mu, sigma = batch_norm(x_layer)
print(f"Before BN: mean={x_layer.mean():.2f}, std={x_layer.std():.2f}")
print(f"After  BN: mean={x_bn.mean():.4f},  std={x_bn.std():.4f}")

# 2. Cosine Learning Rate Schedule
def cosine_lr(epoch, max_epochs, lr_max=0.001, lr_min=1e-6):
    """Warmup + cosine decay"""
    warmup_epochs = max_epochs // 10
    if epoch < warmup_epochs:
        return lr_max * epoch / warmup_epochs
    progress = (epoch - warmup_epochs) / (max_epochs - warmup_epochs)
    return lr_min + 0.5 * (lr_max - lr_min) * (1 + np.cos(np.pi * progress))

lrs = [cosine_lr(e, 100) for e in range(100)]
print(f"\nLR schedule: start={lrs[0]:.6f}, peak={max(lrs):.6f}, end={lrs[-1]:.8f}")

# 3. Gradient Clipping
def clip_gradients(params_grads, max_norm=1.0):
    """Prevent exploding gradients in RNNs/Transformers"""
    total_norm = np.sqrt(sum(np.sum(g**2) for _, g in params_grads))
    clip_coef  = max_norm / (total_norm + 1e-8)
    if clip_coef < 1.0:
        params_grads = [(p, g * clip_coef) for p, g in params_grads]
    return params_grads, total_norm

# 4. Label Smoothing — prevents overconfident predictions
def label_smoothing_loss(y_pred, y_true, n_classes, smoothing=0.1):
    """
    Instead of one-hot [0,0,1,0], use [ε/K, ε/K, 1-ε+ε/K, ε/K]
    Forces model to maintain uncertainty → better calibration + regularization
    """
    confidence = 1 - smoothing
    smooth_val = smoothing / n_classes
    y_smooth = y_true * confidence + smooth_val
    eps = 1e-8
    return -np.mean(np.sum(y_smooth * np.log(y_pred + eps), axis=-1))

# ============================================================
# SECTION 4: Key Interview Derivations
# ============================================================

print("\n=== KEY DERIVATIONS TO KNOW ===")

# Softmax + Cross-Entropy gradient (used in every classifier)
def softmax(x):
    """Numerically stable softmax"""
    e = np.exp(x - x.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)

def cross_entropy(probs, labels):
    """labels = integers (class indices)"""
    n = len(labels)
    return -np.mean(np.log(probs[np.arange(n), labels] + 1e-8))

# KEY INSIGHT: Gradient of softmax+CE w.r.t. logits = (probs - one_hot_labels) / n
# This is WHY backprop is clean for classification — gradient is just the error!

logits = np.array([[2.0, 1.0, 0.1], [0.5, 2.5, 0.1]])
labels = np.array([0, 1])
probs  = softmax(logits)
loss   = cross_entropy(probs, labels)
grad   = probs.copy()
grad[np.arange(len(labels)), labels] -= 1
grad  /= len(labels)

print(f"Logits: {logits}")
print(f"Probs:  {probs.round(4)}")
print(f"Loss:   {loss:.4f}")
print(f"Grad:   {grad.round(4)}  ← (probs - one_hot) / n  — clean and elegant")

print("\n✅ Chapter 3: Deep Learning & Neural Networks complete!")
