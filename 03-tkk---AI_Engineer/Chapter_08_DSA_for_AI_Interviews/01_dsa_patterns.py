# ============================================================
# CHAPTER 8: DSA FOR AI ENGINEER INTERVIEWS
# Practice in: VS Code
# Topics: 15 core patterns, 60+ problems
# Calibrated for: Google, Meta, Amazon, Microsoft, Databricks
#
# REALITY CHECK: AI Engineer DSA bar = Software Engineer bar.
# No concessions. Master these 15 patterns.
# ============================================================

from typing import List, Optional, Dict, Tuple
from collections import defaultdict, deque, Counter
import heapq

# ============================================================
# PATTERN 1: Two Pointers
# ============================================================

def two_sum_sorted(nums: List[int], target: int) -> List[int]:
    """Two pointers on sorted array. O(n) time, O(1) space."""
    l, r = 0, len(nums) - 1
    while l < r:
        s = nums[l] + nums[r]
        if s == target:   return [l, r]
        elif s < target:  l += 1
        else:             r -= 1
    return []

def container_with_most_water(heights: List[int]) -> int:
    """LC 11 — two pointers, always move the shorter side."""
    l, r = 0, len(heights) - 1
    max_water = 0
    while l < r:
        max_water = max(max_water, min(heights[l], heights[r]) * (r - l))
        if heights[l] < heights[r]: l += 1
        else:                       r -= 1
    return max_water

print("=== PATTERN 1: Two Pointers ===")
print(two_sum_sorted([1, 2, 4, 6, 8], 10))        # [1, 4]
print(container_with_most_water([1,8,6,2,5,4,8,3,7]))  # 49

# ============================================================
# PATTERN 2: Sliding Window
# ============================================================

def max_subarray_sum_k(nums: List[int], k: int) -> int:
    """Fixed-size window. O(n)."""
    window_sum = sum(nums[:k])
    max_sum = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]
        max_sum = max(max_sum, window_sum)
    return max_sum

def longest_substring_no_repeat(s: str) -> int:
    """Variable window — expand right, shrink left when invalid. O(n)."""
    char_idx = {}
    l, max_len = 0, 0
    for r, c in enumerate(s):
        if c in char_idx and char_idx[c] >= l:
            l = char_idx[c] + 1
        char_idx[c] = r
        max_len = max(max_len, r - l + 1)
    return max_len

print("\n=== PATTERN 2: Sliding Window ===")
print(max_subarray_sum_k([2, 1, 5, 1, 3, 2], 3))   # 9
print(longest_substring_no_repeat("abcabcbb"))        # 3

# ============================================================
# PATTERN 3: HashMap / HashSet
# ============================================================

def two_sum(nums: List[int], target: int) -> List[int]:
    """Classic — O(n) with HashMap."""
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i
    return []

def group_anagrams(strs: List[str]) -> List[List[str]]:
    """Sort each string as key → group. O(n·k·log k)."""
    groups = defaultdict(list)
    for s in strs:
        groups[tuple(sorted(s))].append(s)
    return list(groups.values())

def top_k_frequent(nums: List[int], k: int) -> List[int]:
    """Count + min-heap. O(n log k)."""
    count = Counter(nums)
    return [x for x, _ in count.most_common(k)]

print("\n=== PATTERN 3: HashMap ===")
print(two_sum([2, 7, 11, 15], 9))          # [0, 1]
print(group_anagrams(["eat","tea","tan","ate","nat","bat"]))
print(top_k_frequent([1,1,1,2,2,3], 2))    # [1, 2]

# ============================================================
# PATTERN 4: Binary Search
# ============================================================

def binary_search(nums: List[int], target: int) -> int:
    """Standard binary search. O(log n)."""
    l, r = 0, len(nums) - 1
    while l <= r:
        mid = l + (r - l) // 2     # prevents overflow
        if nums[mid] == target:     return mid
        elif nums[mid] < target:    l = mid + 1
        else:                       r = mid - 1
    return -1

def search_rotated(nums: List[int], target: int) -> int:
    """Binary search on rotated sorted array. O(log n)."""
    l, r = 0, len(nums) - 1
    while l <= r:
        mid = (l + r) // 2
        if nums[mid] == target: return mid
        if nums[l] <= nums[mid]:  # left half sorted
            if nums[l] <= target < nums[mid]: r = mid - 1
            else:                              l = mid + 1
        else:                     # right half sorted
            if nums[mid] < target <= nums[r]: l = mid + 1
            else:                              r = mid - 1
    return -1

print("\n=== PATTERN 4: Binary Search ===")
print(binary_search([1, 3, 5, 7, 9, 11], 7))   # 3
print(search_rotated([4,5,6,7,0,1,2], 0))       # 4

# ============================================================
# PATTERN 5: BFS (Graph / Tree)
# ============================================================

def level_order_traversal(root) -> List[List[int]]:
    """BFS level by level. O(n)."""
    if not root: return []
    result, queue = [], deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:  queue.append(node.left)
            if node.right: queue.append(node.right)
        result.append(level)
    return result

def word_ladder(begin: str, end: str, word_list: List[str]) -> int:
    """BFS on implicit graph — each step changes 1 char. O(n·L²)."""
    word_set = set(word_list)
    if end not in word_set: return 0
    queue = deque([(begin, 1)])
    visited = {begin}
    while queue:
        word, steps = queue.popleft()
        for i in range(len(word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                next_word = word[:i] + c + word[i+1:]
                if next_word == end: return steps + 1
                if next_word in word_set and next_word not in visited:
                    visited.add(next_word)
                    queue.append((next_word, steps + 1))
    return 0

print("\n=== PATTERN 5: BFS ===")
print(word_ladder("hit", "cog", ["hot","dot","dog","lot","log","cog"]))  # 5

# ============================================================
# PATTERN 6: DFS (Graph / Tree)
# ============================================================

def num_islands(grid: List[List[str]]) -> int:
    """DFS flood fill. O(m·n)."""
    if not grid: return 0
    rows, cols = len(grid), len(grid[0])

    def dfs(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != '1':
            return
        grid[r][c] = '#'  # mark visited
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            dfs(r + dr, c + dc)

    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                dfs(r, c)
                count += 1
    return count

print("\n=== PATTERN 6: DFS ===")
grid = [["1","1","0","0"],["1","0","0","1"],["0","0","1","1"],["0","0","1","1"]]
print(num_islands(grid))  # 3

# ============================================================
# PATTERN 7: Heap / Priority Queue
# ============================================================

def kth_largest(nums: List[int], k: int) -> int:
    """Min-heap of size k. O(n log k)."""
    heap = []
    for n in nums:
        heapq.heappush(heap, n)
        if len(heap) > k:
            heapq.heappop(heap)
    return heap[0]

def merge_k_sorted_lists(lists):
    """Merge k sorted linked lists. O(n log k)."""
    heap = []
    dummy = curr = type('Node', (), {'val': 0, 'next': None})()
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))
    while heap:
        val, i, node = heapq.heappop(heap)
        curr.next = node
        curr = curr.next
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next

print("\n=== PATTERN 7: Heap ===")
print(kth_largest([3,2,1,5,6,4], 2))  # 5

# ============================================================
# PATTERN 8: Dynamic Programming
# ============================================================

def climbing_stairs(n: int) -> int:
    """Fibonacci DP. O(n) time, O(1) space."""
    if n <= 2: return n
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b

def longest_common_subsequence(s1: str, s2: str) -> int:
    """2D DP. O(m·n) time and space."""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]

def coin_change(coins: List[int], amount: int) -> int:
    """Classic unbounded knapsack DP. O(amount × coins)."""
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for a in range(coin, amount + 1):
            dp[a] = min(dp[a], dp[a - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1

def word_break(s: str, word_dict: List[str]) -> bool:
    """DP: can we partition s into words from dict? O(n²)."""
    word_set = set(word_dict)
    dp = [False] * (len(s) + 1)
    dp[0] = True
    for i in range(1, len(s) + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break
    return dp[len(s)]

print("\n=== PATTERN 8: Dynamic Programming ===")
print(climbing_stairs(10))                           # 89
print(longest_common_subsequence("abcde", "ace"))    # 3
print(coin_change([1, 5, 11], 15))                  # 3
print(word_break("leetcode", ["leet","code"]))       # True

# ============================================================
# PATTERN 9: Backtracking
# ============================================================

def subsets(nums: List[int]) -> List[List[int]]:
    """All subsets. 2^n subsets. O(n·2^n)."""
    result = []
    def backtrack(start, current):
        result.append(current[:])
        for i in range(start, len(nums)):
            current.append(nums[i])
            backtrack(i + 1, current)
            current.pop()
    backtrack(0, [])
    return result

def permutations(nums: List[int]) -> List[List[int]]:
    """All permutations. O(n!)."""
    result = []
    def backtrack(current, remaining):
        if not remaining:
            result.append(current[:])
        for i, n in enumerate(remaining):
            current.append(n)
            backtrack(current, remaining[:i] + remaining[i+1:])
            current.pop()
    backtrack([], nums)
    return result

print("\n=== PATTERN 9: Backtracking ===")
print(subsets([1, 2, 3]))          # 8 subsets
print(len(permutations([1,2,3])))  # 6

# ============================================================
# PATTERN 10: Monotonic Stack
# ============================================================

def daily_temperatures(temps: List[int]) -> List[int]:
    """
    Next greater element with monotonic stack. O(n).
    Classic interview problem — also asked as stock span.
    """
    n = len(temps)
    result = [0] * n
    stack = []  # indices, decreasing temperatures
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            idx = stack.pop()
            result[idx] = i - idx
        stack.append(i)
    return result

print("\n=== PATTERN 10: Monotonic Stack ===")
print(daily_temperatures([73,74,75,71,69,72,76,73]))  # [1,1,4,2,1,1,0,0]

# ============================================================
# AI-SPECIFIC CODING PATTERNS
# ============================================================

print("\n=== AI-SPECIFIC PATTERNS ===")

# 1. Implement softmax (asked at AI labs)
import math
def softmax(logits: List[float]) -> List[float]:
    """Numerically stable softmax"""
    max_val = max(logits)
    exp_vals = [math.exp(x - max_val) for x in logits]
    total = sum(exp_vals)
    return [e / total for e in exp_vals]

print("Softmax([2,1,0.1]):", [round(p, 4) for p in softmax([2, 1, 0.1])])

# 2. K-nearest neighbors (asked at Google)
def knn_predict(X_train, y_train, x_query, k=3):
    """Brute force KNN. O(n·d + n·log·n)."""
    dists = sorted(
        enumerate(sum((xi - qi)**2 for xi, qi in zip(x, x_query))**0.5
                  for x in X_train),
        key=lambda t: t[1]
    )
    k_labels = [y_train[i] for i, _ in dists[:k]]
    return max(set(k_labels), key=k_labels.count)

X = [[1,2],[2,3],[3,4],[10,11],[11,12]]
y = [0,0,0,1,1]
print(f"KNN prediction: {knn_predict(X, y, [2.5, 3.5], k=3)}")  # 0

# 3. Find top-K similar embeddings (mini vector search)
def top_k_similar(query_vec: List[float], corpus: List[List[float]], k: int) -> List[int]:
    """Cosine similarity + heap. O(n·d + n·log·k)."""
    def cosine_sim(a, b):
        dot = sum(ai*bi for ai, bi in zip(a, b))
        norm_a = sum(ai**2 for ai in a)**0.5
        norm_b = sum(bi**2 for bi in b)**0.5
        return dot / (norm_a * norm_b + 1e-8)

    heap = []
    for i, vec in enumerate(corpus):
        sim = cosine_sim(query_vec, vec)
        heapq.heappush(heap, (sim, i))
        if len(heap) > k:
            heapq.heappop(heap)
    return [i for _, i in sorted(heap, reverse=True)]

query = [1, 0, 0, 1]
corpus = [[1,0,0,1], [0,1,1,0], [0.9,0.1,0,0.9], [0,0,1,1]]
print(f"Top-2 similar docs: {top_k_similar(query, corpus, k=2)}")  # [0, 2]

print("\n✅ Chapter 8: DSA for AI Interviews complete!")
print("Practice: solve each problem without looking, then time yourself. Target: < 15 min per medium.")
