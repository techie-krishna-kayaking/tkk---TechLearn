# Databricks notebook source
# ================================================================================
# DSA Interview Handbook — Chapter 2: Practice Problems (Python)
# ================================================================================
# 25 most common interview problems with:
#   - Problem statement
#   - Approach explanation (plain English)
#   - Clean Python solution
#   - Time & Space complexity
#   - Interview notes
#
# Run each problem in any Python 3 environment (local, Databricks, Colab).
# ================================================================================

from collections import defaultdict, Counter, deque
import heapq

# ==============================================================================
# ARRAYS & STRINGS
# ==============================================================================

# Problem 1: Two Sum
# ------------------
# Given an array of integers and a target, return indices of two numbers that sum to target.
# Approach: Use a hash map. For each number, check if (target - num) was seen before.
def two_sum(nums, target):
    seen = {}                         # value → index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
# Time: O(n)  Space: O(n)
# INTERVIEW: Brute force is O(n²). Hash map reduces to O(n) — classic trade-off.
print(two_sum([2, 7, 11, 15], 9))    # [0, 1]
print(two_sum([3, 2, 4], 6))         # [1, 2]


# Problem 2: Best Time to Buy and Sell Stock
# ------------------------------------------
# Find max profit from one buy and one sell (buy before sell).
# Approach: Track minimum price seen so far. Max profit = current - min_so_far.
def max_profit(prices):
    min_price = float('inf')
    max_profit_val = 0
    for price in prices:
        min_price = min(min_price, price)
        max_profit_val = max(max_profit_val, price - min_price)
    return max_profit_val
# Time: O(n)  Space: O(1)
# INTERVIEW: One-pass greedy. Never actually need to "look back" further than min.
print(max_profit([7, 1, 5, 3, 6, 4]))   # 5


# Problem 3: Product of Array Except Self
# ----------------------------------------
# Return array where output[i] = product of all elements except nums[i]. No division.
# Approach: Two passes — prefix products left-to-right, suffix right-to-left.
def product_except_self(nums):
    n = len(nums)
    result = [1] * n
    prefix = 1
    for i in range(n):                 # left pass: result[i] = product of all left
        result[i] = prefix
        prefix *= nums[i]
    suffix = 1
    for i in range(n - 1, -1, -1):    # right pass: multiply product of all right
        result[i] *= suffix
        suffix *= nums[i]
    return result
# Time: O(n)  Space: O(1) extra (output array doesn't count)
print(product_except_self([1, 2, 3, 4]))   # [24, 12, 8, 6]


# Problem 4: Merge Intervals
# --------------------------
# Given list of intervals, merge all overlapping ones.
# Approach: Sort by start. Compare each interval's start to last merged end.
def merge_intervals(intervals):
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:             # overlaps: extend end
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])        # no overlap: new interval
    return merged
# Time: O(n log n) — dominated by sort  Space: O(n)
print(merge_intervals([[1,3],[2,6],[8,10],[15,18]]))   # [[1,6],[8,10],[15,18]]


# Problem 5: Valid Parentheses
# ----------------------------
# Determine if the string of brackets is valid (every open has matching close).
# Approach: Stack. Push opens, pop and match on closes.
def is_valid_parens(s):
    stack = []
    pairs = {')': '(', '}': '{', ']': '['}
    for ch in s:
        if ch in '([{':
            stack.append(ch)
        elif ch in ')]}':
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
    return len(stack) == 0
# Time: O(n)  Space: O(n)
print(is_valid_parens("()[]{}"))   # True
print(is_valid_parens("(]"))       # False


# ==============================================================================
# HASH MAPS & STRINGS
# ==============================================================================

# Problem 6: Group Anagrams
# -------------------------
# Group strings that are anagrams of each other.
# Approach: Sorted version of each word is the group key.
def group_anagrams(strs):
    groups = defaultdict(list)
    for word in strs:
        groups[tuple(sorted(word))].append(word)
    return list(groups.values())
# Time: O(n * k log k)  Space: O(n)
print(group_anagrams(["eat","tea","tan","ate","nat","bat"]))


# Problem 7: Top K Frequent Elements
# -----------------------------------
# Return the K most frequent elements in an array.
# Approach: Count frequencies, use a min-heap of size K.
def top_k_frequent(nums, k):
    count = Counter(nums)
    return [x for x, _ in count.most_common(k)]
# Time: O(n log k)  Space: O(n)
# INTERVIEW: heapq.nlargest(k, count, key=count.get) is another clean approach.
print(top_k_frequent([1,1,1,2,2,3], 2))   # [1, 2]


# Problem 8: Longest Substring Without Repeating Characters
# ----------------------------------------------------------
# Find the length of the longest substring with all unique characters.
# Approach: Sliding window — use a set, expand right, shrink left on duplicate.
def length_of_longest_substring(s):
    char_set = set()
    left = max_len = 0
    for right in range(len(s)):
        while s[right] in char_set:
            char_set.remove(s[left])
            left += 1
        char_set.add(s[right])
        max_len = max(max_len, right - left + 1)
    return max_len
# Time: O(n)  Space: O(min(n, charset))
print(length_of_longest_substring("abcabcbb"))   # 3


# ==============================================================================
# BINARY SEARCH
# ==============================================================================

# Problem 9: Search in Rotated Sorted Array
# ------------------------------------------
# Array was sorted then rotated. Find target index or -1.
# Approach: Modified binary search — one half is always sorted.
def search_rotated(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[left] <= nums[mid]:         # left half is sorted
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:                               # right half is sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
# Time: O(log n)  Space: O(1)
print(search_rotated([4,5,6,7,0,1,2], 0))   # 4


# Problem 10: Find Minimum in Rotated Sorted Array
# -------------------------------------------------
# Approach: Binary search — minimum is where the "drop" happens.
def find_min_rotated(nums):
    left, right = 0, len(nums) - 1
    while left < right:
        mid = (left + right) // 2
        if nums[mid] > nums[right]:
            left = mid + 1    # min is in right half
        else:
            right = mid       # min is in left half (inclusive of mid)
    return nums[left]
# Time: O(log n)  Space: O(1)
print(find_min_rotated([3,4,5,1,2]))   # 1


# ==============================================================================
# TREES & GRAPHS
# ==============================================================================

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


# Problem 11: Maximum Depth of Binary Tree
# -----------------------------------------
# Approach: DFS — max depth = 1 + max(left depth, right depth)
def max_depth(root):
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))
# Time: O(n)  Space: O(h) where h = tree height


# Problem 12: Level Order Traversal (BFS)
# ----------------------------------------
# Return nodes level by level.
# Approach: BFS with deque. Track level boundaries by processing queue size per level.
def level_order(root):
    if not root:
        return []
    result, queue = [], deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):      # process exactly one level
            node = queue.popleft()
            level.append(node.val)
            if node.left:  queue.append(node.left)
            if node.right: queue.append(node.right)
        result.append(level)
    return result
# Time: O(n)  Space: O(w) where w = max width


# Problem 13: Number of Islands (DFS on Grid)
# --------------------------------------------
# Count connected groups of '1's in a 2D grid.
# Approach: DFS from each unvisited '1', mark all connected '1's as visited.
def num_islands(grid):
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    count = 0

    def dfs(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != '1':
            return
        grid[r][c] = '#'   # mark visited by overwriting
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            dfs(r + dr, c + dc)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                dfs(r, c)
                count += 1
    return count
# Time: O(m*n)  Space: O(m*n) recursion stack
grid = [["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]]
print(num_islands([row[:] for row in grid]))   # 3


# Problem 14: Clone Graph
# -----------------------
# Approach: BFS + hash map from original node → cloned node.
class GraphNode:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors or []

def clone_graph(node):
    if not node:
        return None
    clones = {node: GraphNode(node.val)}
    queue = deque([node])
    while queue:
        cur = queue.popleft()
        for neighbor in cur.neighbors:
            if neighbor not in clones:
                clones[neighbor] = GraphNode(neighbor.val)
                queue.append(neighbor)
            clones[cur].neighbors.append(clones[neighbor])
    return clones[node]
# Time: O(V+E)  Space: O(V)


# Problem 15: Course Schedule (Cycle Detection in DAG)
# ------------------------------------------------------
# Can you finish all courses given prerequisites? = Detect cycle in directed graph.
# Approach: DFS with 3 states: 0=unvisited, 1=in-progress, 2=done
def can_finish(num_courses, prerequisites):
    graph = defaultdict(list)
    for a, b in prerequisites:
        graph[b].append(a)
    state = [0] * num_courses  # 0=unvisited, 1=in-progress, 2=done

    def has_cycle(node):
        if state[node] == 1: return True   # back edge → cycle
        if state[node] == 2: return False  # already fully explored
        state[node] = 1
        for neighbor in graph[node]:
            if has_cycle(neighbor):
                return True
        state[node] = 2
        return False

    return not any(has_cycle(i) for i in range(num_courses) if state[i] == 0)
# Time: O(V+E)  Space: O(V+E)
# INTERVIEW: Topological sort = no cycle exists. Airflow DAG validation uses this logic!
print(can_finish(2, [[1,0]]))        # True
print(can_finish(2, [[1,0],[0,1]]))  # False (cycle)


# ==============================================================================
# HEAPS
# ==============================================================================

# Problem 16: Kth Largest Element in an Array
# --------------------------------------------
# Approach: Min-heap of size K. Smallest element in heap = Kth largest overall.
def find_kth_largest(nums, k):
    heap = nums[:k]
    heapq.heapify(heap)
    for num in nums[k:]:
        if num > heap[0]:
            heapq.heapreplace(heap, num)
    return heap[0]
# Time: O(n log k)  Space: O(k)
# INTERVIEW: Python heapq is a MIN heap. Negate values to simulate MAX heap.
print(find_kth_largest([3,2,1,5,6,4], 2))   # 5


# Problem 17: Merge K Sorted Lists
# ----------------------------------
# Merge K sorted linked lists into one sorted list.
# Approach: Use a min-heap. Push (value, list_index, node) for each list head.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def merge_k_lists(lists):
    heap = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))
    dummy = cur = ListNode(0)
    while heap:
        val, i, node = heapq.heappop(heap)
        cur.next = node
        cur = cur.next
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next
# Time: O(n log k)  Space: O(k)
# INTERVIEW: Classic n = total nodes, k = number of lists. Heap avoids O(n*k).


# ==============================================================================
# DYNAMIC PROGRAMMING
# ==============================================================================

# Problem 18: Climbing Stairs
# ----------------------------
# N stairs, can climb 1 or 2 steps. How many distinct ways?
# Approach: DP. ways[i] = ways[i-1] + ways[i-2] (Fibonacci pattern).
def climb_stairs(n):
    if n <= 2:
        return n
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b
# Time: O(n)  Space: O(1)
print(climb_stairs(5))   # 8


# Problem 19: Coin Change (Minimum Coins)
# ----------------------------------------
# Given coin denominations and a target amount, find minimum coins needed.
# Approach: Bottom-up DP. dp[amount] = min coins to make that amount.
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for amt in range(1, amount + 1):
        for coin in coins:
            if coin <= amt:
                dp[amt] = min(dp[amt], dp[amt - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
# Time: O(amount * len(coins))  Space: O(amount)
print(coin_change([1, 5, 6, 9], 11))   # 2 (5+6)


# Problem 20: Longest Common Subsequence
# ----------------------------------------
# Find the length of the longest subsequence present in both strings.
# Approach: 2D DP grid.  dp[i][j] = LCS of s1[:i] and s2[:j].
def longest_common_subsequence(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]
# Time: O(m*n)  Space: O(m*n)
print(longest_common_subsequence("abcde", "ace"))   # 3


# ==============================================================================
# DESIGN PROBLEMS
# ==============================================================================

# Problem 21: LRU Cache
# ----------------------
# Design a cache with O(1) get and put. Evict least recently used item when full.
# Approach: OrderedDict — maintains insertion order + O(1) operations.
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)   # mark as recently used
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # evict oldest (LRU)

# Time: O(1) for both get and put  Space: O(capacity)
# INTERVIEW: Real LRU uses a doubly linked list + hash map for O(1). OrderedDict is the Pythonic shortcut.
lru = LRUCache(2)
lru.put(1, 1)
lru.put(2, 2)
print(lru.get(1))      # 1
lru.put(3, 3)          # evicts key 2
print(lru.get(2))      # -1


# Problem 22: Moving Average from Data Stream
# --------------------------------------------
# Given a stream of integers, compute the moving average of the last K elements.
# Approach: Deque of max size K.
class MovingAverage:
    def __init__(self, size):
        self.size = size
        self.window = deque()
        self.total = 0

    def next(self, val):
        if len(self.window) == self.size:
            self.total -= self.window.popleft()
        self.window.append(val)
        self.total += val
        return self.total / len(self.window)

# Time: O(1) per call  Space: O(K)
ma = MovingAverage(3)
print(ma.next(1))    # 1.0
print(ma.next(10))   # 5.5
print(ma.next(3))    # 4.67
print(ma.next(5))    # 6.0 (window = [10,3,5])


# ==============================================================================
# BONUS: String Problems
# ==============================================================================

# Problem 23: Valid Anagram
def is_anagram(s, t):
    return Counter(s) == Counter(t)
print(is_anagram("anagram", "nagaram"))   # True

# Problem 24: Palindrome Check
def is_palindrome(s):
    s = ''.join(c.lower() for c in s if c.isalnum())
    return s == s[::-1]
print(is_palindrome("A man a plan a canal Panama"))   # True

# Problem 25: Find All Duplicates in Array
# Numbers are in range [1, n]. Find all that appear twice.
# Approach: Use the array itself as a "visited" marker by negating.
def find_duplicates(nums):
    result = []
    for num in nums:
        idx = abs(num) - 1
        if nums[idx] < 0:
            result.append(abs(num))   # already negated = seen before
        else:
            nums[idx] = -nums[idx]    # negate to mark as seen
    return result
# Time: O(n)  Space: O(1)
print(find_duplicates([4,3,2,7,8,2,3,1]))   # [2, 3]

print("\n✅ All 25 problems completed!")
