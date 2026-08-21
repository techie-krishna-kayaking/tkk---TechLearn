# ============================================================
# CHAPTER 1: PYTHON FOR AI ENGINEERING
# Practice in: VS Code
# Topics: OOP, decorators, generators, async, NumPy,
#         memory profiling, efficient data handling
# ============================================================

import time
import asyncio
import functools
import tracemalloc
from typing import Generator, Iterator, Callable, Any
import numpy as np

# ============================================================
# SECTION 1: Generators — Lazy Data Loading (Critical for ML)
# ============================================================

# Simulate streaming a large dataset without loading into RAM
def data_stream(filepath: str, batch_size: int = 32) -> Generator:
    """Lazy batch generator — O(batch_size) memory, not O(dataset_size)"""
    batch = []
    # Simulating file reading
    for i in range(1000):  # pretend 1000 rows
        batch.append({"id": i, "feature": np.random.randn(128)})
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:  # yield remaining
        yield batch

# Usage
for batch in data_stream("data.csv", batch_size=32):
    # Process batch — only 32 items in memory at a time
    features = np.array([item["feature"] for item in batch])
    break  # just show first batch
print(f"Batch shape: {features.shape}")  # (32, 128)

# Generator expression vs list comprehension
squares_list = [x**2 for x in range(10_000_000)]   # allocates ~80 MB
squares_gen  = (x**2 for x in range(10_000_000))   # allocates ~120 bytes
# sum(squares_gen) computes lazily — same result, 1000× less memory

# ============================================================
# SECTION 2: Decorators — Logging, Timing, Caching
# ============================================================

# 1. Timer decorator — wrap training steps
def timer(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[TIMER] {func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

# 2. Retry decorator — for flaky API calls (LLM APIs, embeddings)
def retry(max_attempts: int = 3, delay: float = 1.0):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    print(f"[RETRY] Attempt {attempt} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

# 3. Cache decorator — for expensive embeddings
def lru_cache_embeddings(maxsize: int = 1000):
    """Cache embeddings to avoid recomputing for same input"""
    def decorator(func: Callable) -> Callable:
        cache = {}
        @functools.wraps(func)
        def wrapper(text: str):
            if text not in cache:
                if len(cache) >= maxsize:
                    cache.pop(next(iter(cache)))  # evict oldest (FIFO approx)
                cache[text] = func(text)
            return cache[text]
        wrapper.cache_info = lambda: {"size": len(cache), "maxsize": maxsize}
        return wrapper
    return decorator

@timer
def train_one_epoch(X, y, model_weights):
    """Simulated training step"""
    # Simulate computation
    time.sleep(0.01)
    loss = np.mean((X @ model_weights - y) ** 2)
    return loss

@retry(max_attempts=3, delay=0.5)
def call_embedding_api(text: str) -> np.ndarray:
    """Simulate an API call that might fail"""
    if np.random.random() < 0.3:  # 30% chance of failure
        raise ConnectionError("API timeout")
    return np.random.randn(1536)  # OpenAI ada-002 dimension

# Demo
X = np.random.randn(100, 10)
y = np.random.randn(100)
w = np.random.randn(10)
loss = train_one_epoch(X, y, w)
print(f"Loss: {loss:.4f}")

# ============================================================
# SECTION 3: OOP for ML — Dataset and Model Classes
# ============================================================

class Dataset:
    """Efficient dataset class with __slots__ for memory saving"""
    __slots__ = ['_data', '_labels', '_transform']

    def __init__(self, data: np.ndarray, labels: np.ndarray, transform=None):
        self._data      = data
        self._labels    = labels
        self._transform = transform

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, idx: int):
        x = self._data[idx]
        y = self._labels[idx]
        if self._transform:
            x = self._transform(x)
        return x, y

    def __iter__(self) -> Iterator:
        for i in range(len(self)):
            yield self[i]

    def batch(self, batch_size: int) -> Generator:
        for i in range(0, len(self), batch_size):
            indices = range(i, min(i + batch_size, len(self)))
            X = np.array([self._data[j] for j in indices])
            y = np.array([self._labels[j] for j in indices])
            yield X, y


class LinearModel:
    """Clean OOP model with fit/predict/score interface"""

    def __init__(self, learning_rate: float = 0.01, epochs: int = 100):
        self.lr      = learning_rate
        self.epochs  = epochs
        self.weights = None
        self.bias    = None
        self.history = []

    def _initialize(self, n_features: int) -> None:
        self.weights = np.zeros(n_features)
        self.bias    = 0.0

    def fit(self, X: np.ndarray, y: np.ndarray) -> 'LinearModel':
        self._initialize(X.shape[1])
        for epoch in range(self.epochs):
            y_pred = self._forward(X)
            loss   = np.mean((y_pred - y) ** 2)
            # Gradients
            dw = (2 / len(X)) * X.T @ (y_pred - y)
            db = (2 / len(X)) * np.sum(y_pred - y)
            # Update
            self.weights -= self.lr * dw
            self.bias    -= self.lr * db
            self.history.append(loss)
        return self  # enables chaining: model.fit(X, y).score(X, y)

    def _forward(self, X: np.ndarray) -> np.ndarray:
        return X @ self.weights + self.bias

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self._forward(X)

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """R² score"""
        y_pred = self.predict(X)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        return 1 - ss_res / ss_tot


# Demo
X_train = np.random.randn(500, 10)
y_train = X_train @ np.array([1,2,3,4,5,6,7,8,9,10]) + np.random.randn(500)*0.1

model = LinearModel(learning_rate=0.01, epochs=200)
model.fit(X_train, y_train)
print(f"R² score: {model.score(X_train, y_train):.4f}")
print(f"Final loss: {model.history[-1]:.6f}")

# ============================================================
# SECTION 4: NumPy Vectorization — Speed Tricks
# ============================================================

# Broadcasting — apply operation across arrays of different shapes
X = np.random.randn(1000, 128)  # 1000 samples, 128 features
mean = X.mean(axis=0)           # shape (128,) — computed per feature
std  = X.std(axis=0)
X_normalized = (X - mean) / (std + 1e-8)  # broadcasts: (1000,128) - (128,) = (1000,128)

# Vectorized cosine similarity (vs nested loops)
def cosine_similarity_vectorized(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between all pairs in A and B"""
    A_norm = A / (np.linalg.norm(A, axis=1, keepdims=True) + 1e-8)
    B_norm = B / (np.linalg.norm(B, axis=1, keepdims=True) + 1e-8)
    return A_norm @ B_norm.T  # (n, m) similarity matrix

queries    = np.random.randn(10, 128)    # 10 query embeddings
documents  = np.random.randn(100, 128)  # 100 document embeddings
sim_matrix = cosine_similarity_vectorized(queries, documents)  # (10, 100)
top_docs   = np.argsort(sim_matrix, axis=1)[:, -5:][:, ::-1]  # top 5 per query
print(f"Similarity matrix shape: {sim_matrix.shape}")
print(f"Top doc indices per query: {top_docs[0]}")

# ============================================================
# SECTION 5: Async — Concurrent API Calls
# ============================================================

async def embed_text_async(text: str, semaphore: asyncio.Semaphore) -> dict:
    """Async embedding call with rate limiting"""
    async with semaphore:
        await asyncio.sleep(0.05)  # simulate API latency
        return {
            "text": text[:20],
            "embedding": np.random.randn(1536).tolist()
        }

async def batch_embed(texts: list, max_concurrent: int = 10) -> list:
    """Embed many texts concurrently, respecting rate limits"""
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = [embed_text_async(t, semaphore) for t in texts]
    results = await asyncio.gather(*tasks)
    return results

async def main():
    texts = [f"Document number {i}" for i in range(50)]
    start = time.time()
    results = await batch_embed(texts, max_concurrent=10)
    elapsed = time.time() - start
    print(f"Embedded {len(results)} texts in {elapsed:.2f}s (async concurrent)")
    print(f"Sequential would take: {0.05 * 50:.2f}s — {0.05*50/elapsed:.1f}× faster")

asyncio.run(main())

# ============================================================
# SECTION 6: Memory Profiling — Critical for Large Models
# ============================================================

def profile_memory(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        result = func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f"[MEMORY] {func.__name__}: current={current/1e6:.2f}MB, peak={peak/1e6:.2f}MB")
        return result
    return wrapper

@profile_memory
def load_embeddings_list(n: int) -> list:
    """Inefficient: Python list of arrays"""
    return [np.random.randn(1536) for _ in range(n)]

@profile_memory
def load_embeddings_matrix(n: int) -> np.ndarray:
    """Efficient: single contiguous NumPy array"""
    return np.random.randn(n, 1536)

load_embeddings_list(1000)
load_embeddings_matrix(1000)
# Matrix uses ~50% less memory + is cache-friendly → faster operations

print("\n✅ Chapter 1: Python for AI Engineering complete!")
