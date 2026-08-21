# 04 — DSA Interview Handbook
# Chapter 1: Concepts & Big-O Notation

> DSA (Data Structures & Algorithms) rounds are mandatory at FAANG, Unicorns, and most
> 50 LPA+ companies in India. You will get 1–3 coding rounds, each 45–60 min, on
> LeetCode-style problems. This handbook covers the patterns — not just the answers.

---

## 🎯 Big-O Notation

**Interview Q:** *"What is Big-O notation? Why do interviewers care about it?"*

Big-O describes how an algorithm's **time or space** grows as input size (n) increases.
Interviewers care because correct code that is too slow fails in production.

| Big-O | Name | Example | Handles n= |
|---|---|---|---|
| O(1) | Constant | Array index, dict lookup | Any size |
| O(log n) | Logarithmic | Binary search | Billions |
| O(n) | Linear | Single loop | Millions |
| O(n log n) | Log-linear | Merge sort, heap sort | Hundreds of thousands |
| O(n²) | Quadratic | Nested loops | ~10,000 |
| O(2ⁿ) | Exponential | Recursive brute force | ~25 |

```python
# O(1) — constant, no loop
def get_first(arr):
    return arr[0]

# O(n) — single loop
def find_max(arr):
    m = arr[0]
    for x in arr:       # runs n times
        if x > m:
            m = x
    return m

# O(n²) — nested loops
def has_duplicate_slow(arr):
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):   # n * n/2 = O(n²)
            if arr[i] == arr[j]:
                return True
    return False

# O(n) — same problem, better approach using a set
def has_duplicate_fast(arr):
    seen = set()
    for x in arr:       # O(n) time, O(n) space
        if x in seen:
            return True
        seen.add(x)
    return False
```

**Interview Tip:** Always state the time AND space complexity of your solution.
"This is O(n) time and O(1) space" shows depth.

---

## 🧱 Core Data Structures — When to Use What

| Structure | Lookup | Insert | Delete | Use When |
|---|---|---|---|---|
| Array/List | O(1) by index | O(n) middle | O(n) middle | Order matters, random access |
| Hash Map (dict) | O(1) avg | O(1) avg | O(1) avg | Fast key lookups, counting |
| Hash Set | O(1) avg | O(1) avg | O(1) avg | Deduplication, membership test |
| Stack (list) | O(n) | O(1) append | O(1) pop | LIFO, undo/redo, DFS |
| Queue (deque) | O(n) | O(1) append | O(1) popleft | FIFO, BFS, task queues |
| Heap (heapq) | O(1) min/max | O(log n) | O(log n) | Top-K, priority queue |
| Binary Tree | O(log n) avg | O(log n) avg | O(log n) avg | Sorted data, range queries |

---

## 💡 The 7 Most Common Patterns

Every LeetCode problem fits one (or more) of these patterns.
Recognising the pattern gets you 60% of the way there.

### Pattern 1: Two Pointers
- **When:** Sorted array, find a pair, remove duplicates
- **How:** One pointer at start, one at end (or both moving right)

```python
# Find two numbers that sum to target (sorted array)
def two_sum_sorted(arr, target):
    left, right = 0, len(arr) - 1
    while left < right:
        s = arr[left] + arr[right]
        if s == target:
            return [left, right]
        elif s < target:
            left += 1
        else:
            right -= 1
    return []
# Time: O(n)  Space: O(1)
```

---

### Pattern 2: Sliding Window
- **When:** Contiguous subarray/substring, max/min/sum within window
- **How:** Expand right pointer, shrink left pointer when condition breaks

```python
# Longest substring without repeating characters
def length_of_longest_substring(s):
    char_set = set()
    left = max_len = 0
    for right in range(len(s)):
        while s[right] in char_set:   # shrink window until no duplicate
            char_set.remove(s[left])
            left += 1
        char_set.add(s[right])
        max_len = max(max_len, right - left + 1)
    return max_len
# Time: O(n)  Space: O(min(n, alphabet_size))
```

---

### Pattern 3: Fast & Slow Pointers (Floyd's Cycle)
- **When:** Detect a cycle in a linked list, find middle node

```python
# Detect cycle in linked list
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False
# Time: O(n)  Space: O(1)
```

---

### Pattern 4: Hash Map / Counting
- **When:** Frequency count, anagram check, grouping, deduplication

```python
# Group anagrams together
from collections import defaultdict
def group_anagrams(strs):
    groups = defaultdict(list)
    for word in strs:
        key = tuple(sorted(word))   # anagrams have the same sorted form
        groups[key].append(word)
    return list(groups.values())
# Time: O(n * k log k)  k = avg word length  Space: O(n)
```

---

### Pattern 5: Binary Search
- **When:** SORTED array, find a value or boundary condition

```python
# Classic binary search
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2   # avoids integer overflow
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
# Time: O(log n)  Space: O(1)
```

---

### Pattern 6: BFS (Breadth-First Search)
- **When:** Shortest path, level-by-level tree traversal, graph reachability

```python
from collections import deque

def bfs(graph, start):
    visited = set([start])
    queue = deque([start])
    result = []
    while queue:
        node = queue.popleft()
        result.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return result
# Time: O(V + E)  Space: O(V)
```

---

### Pattern 7: DFS (Depth-First Search)
- **When:** Explore all paths, backtracking, connected components, tree traversal

```python
def dfs(graph, node, visited=None):
    if visited is None:
        visited = set()
    visited.add(node)
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
    return visited
# Time: O(V + E)  Space: O(V)
```

---

## 🔥 Top 20 Must-Know LeetCode Problems for Data Engineering Interviews

| # | Problem | Pattern | Difficulty |
|---|---|---|---|
| 1 | Two Sum | Hash Map | Easy |
| 2 | Valid Parentheses | Stack | Easy |
| 3 | Merge Intervals | Sorting | Medium |
| 4 | Top K Frequent Elements | Heap/HashMap | Medium |
| 5 | Longest Substring Without Repeating Chars | Sliding Window | Medium |
| 6 | Find Median from Data Stream | Heap | Hard |
| 7 | LRU Cache | LinkedList + HashMap | Medium |
| 8 | Group Anagrams | HashMap | Medium |
| 9 | Climbing Stairs | DP | Easy |
| 10 | Coin Change | DP | Medium |
| 11 | Number of Islands | DFS/BFS | Medium |
| 12 | Course Schedule | Graph/Topological Sort | Medium |
| 13 | Search in Rotated Sorted Array | Binary Search | Medium |
| 14 | Product of Array Except Self | Array | Medium |
| 15 | Word Ladder | BFS | Hard |
| 16 | Implement Trie | Trie | Medium |
| 17 | Serialize/Deserialize Binary Tree | Tree + BFS | Hard |
| 18 | Sliding Window Maximum | Monotonic Deque | Hard |
| 19 | Meeting Rooms II | Heap + Sorting | Medium |
| 20 | Minimum Window Substring | Sliding Window | Hard |

> 💡 **For Data Engineering roles:** Focus on 1-14. Problems 15-20 appear at FAANG only.
> Solve each in Python, optimize to best time/space complexity, explain Big-O clearly.

---

## 📝 Interview Answer Framework

When given a coding problem:

```
1. UNDERSTAND  → Repeat the problem in your own words. Ask clarifying questions.
                 "Is the array sorted? Can values be negative? What if input is empty?"

2. EXAMPLES    → Walk through 2 examples manually. One normal, one edge case.

3. BRUTE FORCE → State the naive O(n²) or O(n!) solution first. Don't code it.
                 "The brute force would be... but that's O(n²), let me optimize."

4. OPTIMIZE    → Identify the bottleneck. Apply a pattern (hash map? two pointers?)

5. CODE        → Write clean code. Use good variable names. Think aloud.

6. TEST        → Trace through your example. Test edge cases (empty, single element).

7. COMPLEXITY  → State time AND space complexity of your final solution.
```

---

## ❓ Top 10 Interview Questions

**Q1: What is the time complexity of dict/set operations in Python?**
Average O(1) for get, set, delete. Worst case O(n) on hash collision — almost never in practice.

**Q2: When would you use a heap over sorting?**
When you only need the top-K elements. Heap: O(n log k). Full sort: O(n log n). For large n and small k, heap wins.

**Q3: Stack vs Queue — give a real-world use case for each.**
Stack: function call stack, undo/redo, DFS traversal.
Queue: task scheduling, BFS traversal, message queues (Kafka is a queue at its core).

**Q4: What is memoization? How does it relate to dynamic programming?**
Memoization = caching the result of expensive function calls (top-down DP).
DP = breaking a problem into subproblems and storing results to avoid recomputation.
Fibonacci: recursive = O(2ⁿ), with memoization = O(n).

**Q5: What is the difference between BFS and DFS? When to use each?**
BFS: level-by-level, uses a queue, finds SHORTEST PATH.
DFS: goes deep first, uses stack/recursion, finds ALL paths, good for backtracking.

**Q6: Explain a hash collision and how Python handles it.**
A collision is when two different keys produce the same hash. Python uses open addressing
(probing) internally in dict/set to handle collisions. This degrades O(1) to O(n) in extreme cases.

**Q7: What is a monotonic stack/queue? Give an example.**
A stack/queue where elements are in strictly increasing or decreasing order.
Example: "Next Greater Element" — for each element, find the next larger element to its right.
Process right-to-left, maintain a decreasing stack.

**Q8: Two Sum using O(n) time — explain the approach.**
Use a hash map. For each number, check if (target - number) already exists in the map.
One pass: store each number and its index as you go.

**Q9: How do you detect a cycle in a directed graph?**
Use DFS with three states: UNVISITED, IN_PROGRESS, DONE.
A cycle exists if you visit a node that is currently IN_PROGRESS (back edge found).

**Q10: What is topological sort? When is it used in data engineering?**
Linear ordering of vertices in a DAG such that for every edge u→v, u comes before v.
In data engineering: Airflow DAG execution order, dependency resolution between pipeline tasks, dbt model execution order.

---
