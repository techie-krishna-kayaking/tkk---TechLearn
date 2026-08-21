"""
10_Concurrency_and_Parallelism.py
================================================================================
Python Interview Handbook
Chapter 10: CONCURRENCY & PARALLELISM

Covered in this file
--------------------
* The GIL (Global Interpreter Lock) — the #1 concurrency interview topic
* threading            : good for I/O-bound work
* Locks / race conditions
* queue.Queue          : thread-safe producer/consumer
* multiprocessing      : true parallelism for CPU-bound work
* concurrent.futures    : ThreadPoolExecutor / ProcessPoolExecutor (high level)
* asyncio              : single-threaded cooperative concurrency (async/await)

IMPORTANT (macOS/Windows): multiprocessing uses 'spawn', which re-imports this
module in child processes. Therefore any function run in a subprocess MUST be
defined at MODULE level (top-level, picklable) — not nested inside main().

Run:
    python3 10_Concurrency_and_Parallelism.py
================================================================================
"""

import asyncio
import concurrent.futures
import multiprocessing
import queue
import threading
import time


# -----------------------------------------------------------------------------
# MODULE-LEVEL worker functions (must be top-level so multiprocessing can pickle
# and re-import them in spawned child processes).
# -----------------------------------------------------------------------------
def cpu_task(n: int) -> int:
    """CPU-bound: sum of squares up to n. Real parallelism needs processes."""
    return sum(i * i for i in range(n))


def square(x: int) -> int:
    return x * x


def io_task(seconds: float) -> str:
    """Simulate an I/O-bound wait (e.g. a network/disk call)."""
    time.sleep(seconds)
    return f"slept {seconds}s"


# =============================================================================
# THREADING (I/O-bound) — concurrency, NOT parallelism (bounded by the GIL)
# =============================================================================
def threading_demo() -> None:
    print("\n--- threading (I/O-bound) ---")
    results = []

    def worker(name, delay):
        time.sleep(delay)            # releases the GIL while sleeping -> overlap
        results.append(name)

    threads = [
        threading.Thread(target=worker, args=(f"t{i}", 0.05))
        for i in range(4)
    ]
    start = time.perf_counter()
    for t in threads:
        t.start()                    # start running
    for t in threads:
        t.join()                     # wait for completion
    elapsed = time.perf_counter() - start
    # 4 threads * 0.05s run concurrently -> ~0.05s total (not 0.20s).
    assert len(results) == 4
    assert elapsed < 0.15
    print(f"4 x 0.05s I/O tasks finished in ~{elapsed:.2f}s (overlapped)")


# =============================================================================
# LOCKS & RACE CONDITIONS
# =============================================================================
def locking_demo() -> None:
    print("\n--- locks / race conditions ---")
    lock = threading.Lock()
    counter = {"value": 0}

    def increment_unsafe():
        for _ in range(10000):
            counter["value"] += 1    # read-modify-write is NOT atomic

    def increment_safe():
        for _ in range(10000):
            with lock:               # critical section — one thread at a time
                counter["value"] += 1

    # Safe version yields a deterministic, correct result.
    counter["value"] = 0
    threads = [threading.Thread(target=increment_safe) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert counter["value"] == 40000
    print("safe increment with Lock ->", counter["value"])
    # KEY POINT: without the lock, concurrent += can lose updates (race condition).


# =============================================================================
# QUEUE — thread-safe producer/consumer
# =============================================================================
def queue_demo() -> None:
    print("\n--- queue.Queue producer/consumer ---")
    q: "queue.Queue[int]" = queue.Queue()
    produced = list(range(10))
    consumed = []

    def producer():
        for item in produced:
            q.put(item)
        q.put(None)                  # sentinel to signal "done"

    def consumer():
        while True:
            item = q.get()
            if item is None:
                q.task_done()
                break
            consumed.append(item)
            q.task_done()

    pt = threading.Thread(target=producer)
    ct = threading.Thread(target=consumer)
    pt.start()
    ct.start()
    pt.join()
    ct.join()
    assert consumed == produced
    print("consumed:", consumed)


# =============================================================================
# concurrent.futures — high-level pools (preferred modern API)
# =============================================================================
def futures_demo() -> None:
    print("\n--- concurrent.futures ---")
    # ThreadPoolExecutor -> best for I/O-bound tasks.
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(io_task, 0.05) for _ in range(4)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    assert len(results) == 4

    # executor.map preserves input order.
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        mapped = list(pool.map(square, [1, 2, 3, 4]))
    assert mapped == [1, 4, 9, 16]
    print("thread pool map:", mapped)


# =============================================================================
# multiprocessing — true parallelism (bypasses the GIL)
# =============================================================================
def multiprocessing_demo() -> None:
    print("\n--- multiprocessing (CPU-bound) ---")
    # Each process has its own interpreter & memory -> real parallel CPU work.
    with multiprocessing.Pool(processes=2) as pool:
        results = pool.map(square, [1, 2, 3, 4, 5])
    assert results == [1, 4, 9, 16, 25]
    print("process pool squares:", results)

    # ProcessPoolExecutor is the futures-based equivalent.
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
        cpu_results = list(pool.map(cpu_task, [10000, 20000]))
    assert len(cpu_results) == 2
    print("process pool cpu_task done")


# =============================================================================
# asyncio — cooperative, single-threaded concurrency (async/await)
# =============================================================================
async def async_fetch(name: str, delay: float) -> str:
    """Simulate an async I/O call. 'await' yields control while waiting."""
    await asyncio.sleep(delay)       # non-blocking sleep
    return f"{name} done"


async def async_main() -> list:
    # gather runs coroutines CONCURRENTLY on ONE thread (event loop).
    start = time.perf_counter()
    results = await asyncio.gather(
        async_fetch("a", 0.05),
        async_fetch("b", 0.05),
        async_fetch("c", 0.05),
    )
    elapsed = time.perf_counter() - start
    # 3 concurrent 0.05s awaits -> ~0.05s total, not 0.15s.
    assert elapsed < 0.13
    return results


def asyncio_demo() -> None:
    print("\n--- asyncio (async/await) ---")
    results = asyncio.run(async_main())   # create loop, run, close
    assert results == ["a done", "b done", "c done"]
    print("asyncio gather:", results)


def main() -> None:
    ###########################################################
    # THE GIL — say this in interviews
    ###########################################################
    # The Global Interpreter Lock lets only ONE thread execute Python bytecode at
    # a time in CPython. Consequences:
    #   * Threads DO help I/O-bound work (the GIL is released during I/O/sleep).
    #   * Threads do NOT speed up CPU-bound work -> use multiprocessing instead.
    # Rule of thumb:
    #   I/O-bound  -> threading or asyncio
    #   CPU-bound  -> multiprocessing (or C extensions / numpy that release the GIL)
    print("=== 10_Concurrency_and_Parallelism demo ===")

    threading_demo()
    locking_demo()
    queue_demo()
    futures_demo()
    multiprocessing_demo()
    asyncio_demo()

    print("\nAll 10_Concurrency_and_Parallelism demos passed ✅")


if __name__ == "__main__":
    # The __main__ guard is REQUIRED for multiprocessing with 'spawn'
    # (macOS/Windows) to avoid infinite process re-spawning.
    main()
