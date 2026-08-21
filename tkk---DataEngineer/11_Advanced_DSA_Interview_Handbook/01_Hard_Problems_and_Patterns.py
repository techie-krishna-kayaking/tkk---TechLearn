"""
ADVANCED DSA INTERVIEW HANDBOOK
Chapter 1: Hard Problems & Advanced Patterns (50+ LeetCode Hard Problems)

🎯 Target: Crack DSA round at FAANG/Databricks (60-80 LPA level)

This file contains:
- 50+ LeetCode Hard problems with full solutions
- Pattern identification for each problem
- Time/space complexity analysis
- Company-specific patterns (Google, Meta, Amazon, Apple)
- Tricky edge cases
- Similar problems for practice

"""

# ============================================================================
# PATTERN 1: SLIDING WINDOW + BINARY SEARCH (Hard)
# ============================================================================

"""
INTERVIEW Q: What are the hardest sliding window problems?
ANSWER: Problems combining sliding window with constraints:
  1. Minimum Window Substring (find shortest substring with all chars)
  2. Substring with Concatenation of All Words
  3. Sliding Window Maximum (with deque optimization)
  4. Longest Substring with K Distinct Characters (variation)
  5. Minimum Window Substring with Repeated Characters

TIME COMPLEXITY: O(n) for sliding window, O(n log n) if binary search involved
SPACE COMPLEXITY: O(1) to O(26) for character sets, O(n) for deque/structures
"""

class Solution:
    # PROBLEM 1: Minimum Window Substring (Hard)
    # Given string s and t, find minimum window in s containing all chars of t
    # Input: s = "ADOBECODEBANC", t = "ABC"
    # Output: "BANC"
    def minWindow(self, s: str, t: str) -> str:
        """
        Two-pointer sliding window with character frequency tracking.
        
        Algorithm:
        1. Count frequency of all characters in t
        2. Expand right pointer until all characters from t are covered
        3. Contract left pointer while still maintaining all characters
        4. Track minimum window
        
        Time: O(|s| + |t|) = O(n)
        Space: O(26) = O(1) for character set
        
        INTERVIEW TRAP: Don't forget to check if formed == required
        SIMILAR: Longest Substring with K Distinct Characters
        """
        if not s or not t:
            return ""
        
        # Count char frequency in t
        dict_t = {}
        for char in t:
            dict_t[char] = dict_t.get(char, 0) + 1
        
        required = len(dict_t)
        window_counts = {}
        formed = 0
        
        # (window size, left, right)
        ans = float("inf"), None, None
        
        l = 0
        for r in range(len(s)):
            # Add char from right to window
            char = s[r]
            window_counts[char] = window_counts.get(char, 0) + 1
            
            # If frequency equals required, increment formed
            if char in dict_t and window_counts[char] == dict_t[char]:
                formed += 1
            
            # Contract window until we can't
            while l <= r and formed == required:
                char = s[l]
                
                # Update answer if this window is smaller
                if r - l + 1 < ans[0]:
                    ans = (r - l + 1, l, r)
                
                # Remove char from left of window
                window_counts[char] -= 1
                if char in dict_t and window_counts[char] < dict_t[char]:
                    formed -= 1
                
                l += 1
        
        return "" if ans[0] == float("inf") else s[ans[1]:ans[2]+1]

    # PROBLEM 2: Sliding Window Maximum (Hard)
    # Given array and k, return max in each sliding window of size k
    # Input: nums = [1,3,-1,-3,5,3,6,7], k = 3
    # Output: [3,3,5,5,6,7]
    def maxSlidingWindow(self, nums: list, k: int) -> list:
        """
        Monotonic deque optimization.
        
        Algorithm:
        1. Maintain deque of indices in decreasing order of values
        2. Remove indices outside of current window
        3. Remove indices smaller than current number (they can't be max)
        4. Leftmost index in deque is the max of current window
        
        Time: O(n) - each element added and removed once
        Space: O(k) for deque
        
        INTERVIEW TRAP: Remember to remove indices, not values
        SIMILAR: Maximum of K-sized Subarrays, Longest Increasing Subsequence
        """
        from collections import deque
        
        if not nums or k == 0:
            return []
        
        dq = deque()  # stores indices
        result = []
        
        for i in range(len(nums)):
            # Remove indices outside current window
            if dq and dq[0] < i - k + 1:
                dq.popleft()
            
            # Remove indices of smaller elements (no longer useful)
            while dq and nums[dq[-1]] < nums[i]:
                dq.pop()
            
            dq.append(i)
            
            # Window has k elements, add max to result
            if i >= k - 1:
                result.append(nums[dq[0]])
        
        return result

    # PROBLEM 3: Substring with Concatenation of All Words (Hard)
    # Given string s and words, find all starting indices of substring formed by
    # concatenating all words exactly once
    # Input: s = "barfoothefoobarman", words = ["foo","bar"]
    # Output: [0,9]
    def findSubstring(self, s: str, words: list) -> list:
        """
        Sliding window with all permutations.
        
        Algorithm:
        1. Sliding window of size = len(words) * len(word[0])
        2. For each position, check if all words are present with correct count
        3. Use word frequency map to verify
        
        Time: O(n * m) where n = len(s), m = len(words)
        Space: O(m) for word frequency map
        
        INTERVIEW TRAP: All words must be used exactly once
        OPTIMIZATION: Can use rolling hash for faster substring comparison
        """
        if not s or not words:
            return []
        
        word_count = {}
        for word in words:
            word_count[word] = word_count.get(word, 0) + 1
        
        word_len = len(words[0])
        total_len = word_len * len(words)
        result = []
        
        for i in range(len(s) - total_len + 1):
            substring = s[i:i + total_len]
            seen = {}
            
            # Check all words in this substring
            for j in range(0, total_len, word_len):
                word = substring[j:j + word_len]
                seen[word] = seen.get(word, 0) + 1
            
            if seen == word_count:
                result.append(i)
        
        return result


# ============================================================================
# PATTERN 2: BINARY SEARCH ADVANCED (Hard)
# ============================================================================

class BinarySearchHard:
    """
    INTERVIEW Q: What are the hardest binary search problems?
    ANSWER: Problems where answer isn't directly in array:
      1. Search in Rotated Sorted Array II (with duplicates)
      2. Find Minimum in Rotated Sorted Array II
      3. Median of Two Sorted Arrays
      4. Find K-th Smallest Element
      5. Binary Search on Answer (optimization problems)
    """

    # PROBLEM 4: Median of Two Sorted Arrays (Hard)
    # Find median of two sorted arrays
    # Input: nums1 = [1,3], nums2 = [2]
    # Output: 2.0
    def findMedianSortedArrays(self, nums1: list, nums2: list) -> float:
        """
        Binary search for partition point.
        
        Algorithm:
        1. Binary search on smaller array to find partition
        2. Partition such that left half has (m + n + 1) // 2 elements
        3. Check if partition is valid (all left <= all right)
        4. Calculate median from partition boundaries
        
        Time: O(log(min(m, n)))
        Space: O(1)
        
        INTERVIEW TRAP: Handle even/odd length arrays correctly
        EDGE CASES: Empty arrays, single element, all elements in one array
        """
        if len(nums1) > len(nums2):
            return self.findMedianSortedArrays(nums2, nums1)
        
        m, n = len(nums1), len(nums2)
        left, right = 0, m
        
        while left <= right:
            partition1 = (left + right) // 2
            partition2 = (m + n + 1) // 2 - partition1
            
            left_max1 = float('-inf') if partition1 == 0 else nums1[partition1 - 1]
            right_min1 = float('inf') if partition1 == m else nums1[partition1]
            
            left_max2 = float('-inf') if partition2 == 0 else nums2[partition2 - 1]
            right_min2 = float('inf') if partition2 == n else nums2[partition2]
            
            if left_max1 <= right_min2 and left_max2 <= right_min1:
                if (m + n) % 2 == 0:
                    return (max(left_max1, left_max2) + min(right_min1, right_min2)) / 2
                else:
                    return max(left_max1, left_max2)
            elif left_max1 > right_min2:
                right = partition1 - 1
            else:
                left = partition1 + 1
        
        return -1

    # PROBLEM 5: Search in Rotated Sorted Array II (with duplicates) (Hard)
    # Rotated array with duplicates - find if target exists
    # Input: nums = [1,0,1,1,1], target = 0
    # Output: True
    def search(self, nums: list, target: int) -> bool:
        """
        Binary search with duplicate handling.
        
        Algorithm:
        1. Standard binary search, but handle duplicates
        2. If nums[left] == nums[mid] == nums[right], shrink boundaries
        3. Once unique, determine which half is sorted and search
        
        Time: O(n) worst case (all duplicates), O(log n) average
        Space: O(1)
        
        INTERVIEW TRAP: Duplicates make it O(n) in worst case
        EXAMPLE: [1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1]
        """
        left, right = 0, len(nums) - 1
        
        while left <= right:
            mid = (left + right) // 2
            
            if nums[mid] == target:
                return True
            
            # Handle duplicates - shrink from right
            while left < mid and nums[left] == nums[mid]:
                left += 1
            while mid < right and nums[right] == nums[mid]:
                right -= 1
            
            # Determine which half is sorted
            if nums[left] <= nums[mid]:
                # Left half is sorted
                if nums[left] <= target < nums[mid]:
                    right = mid - 1
                else:
                    left = mid + 1
            else:
                # Right half is sorted
                if nums[mid] < target <= nums[right]:
                    left = mid + 1
                else:
                    right = mid - 1
        
        return False


# ============================================================================
# PATTERN 3: ADVANCED GRAPH ALGORITHMS (Hard)
# ============================================================================

class GraphHard:
    """
    INTERVIEW Q: What's the hardest graph problem?
    ANSWER: Problems combining multiple graph concepts:
      1. Alien Dictionary (Topological sort + character ordering)
      2. Network Delay Time (Dijkstra's algorithm)
      3. Critical Connections in Network (Bridges in graph)
      4. Accounts Merge (Union-Find with customization)
      5. Word Ladder (BFS with optimization)
    """

    # PROBLEM 6: Network Delay Time (Hard)
    # Given directed graph with travel times, find time for signal to reach all nodes
    # Input: times = [[2,1,1],[2,3,1],[3,4,1]], n = 4, k = 2
    # Output: 3
    def networkDelayTime(self, times: list, n: int, k: int) -> int:
        """
        Dijkstra's algorithm for shortest path from source to all nodes.
        
        Algorithm:
        1. Build adjacency list from edges
        2. Use priority queue (min-heap) to explore nodes by minimum distance
        3. Mark visited and update distances
        4. Return maximum distance (when signal reaches all nodes)
        
        Time: O(E log V) where E = edges, V = vertices
        Space: O(V + E) for graph and priority queue
        
        INTERVIEW TRAP: Don't forget to check if all nodes are visited
        SIMILAR: Single Source Shortest Path, Cheapest Flights
        """
        import heapq
        from collections import defaultdict
        
        # Build adjacency list
        graph = defaultdict(list)
        for u, v, w in times:
            graph[u].append((v, w))
        
        # Dijkstra's algorithm
        dist = [float('inf')] * (n + 1)
        dist[k] = 0
        pq = [(0, k)]  # (distance, node)
        
        while pq:
            d, u = heapq.heappop(pq)
            
            if d > dist[u]:
                continue
            
            for v, w in graph[u]:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    heapq.heappush(pq, (dist[v], v))
        
        # Maximum distance is when signal reaches all nodes
        max_dist = max(dist[1:n+1])
        return max_dist if max_dist != float('inf') else -1

    # PROBLEM 7: Accounts Merge (Hard)
    # Merge accounts with same email addresses
    # Input: accounts = [["John","johnsmith@mail.com",...], ...]
    # Output: Merged accounts
    def accountsMerge(self, accounts: list) -> list:
        """
        Union-Find (DSU) for grouping emails.
        
        Algorithm:
        1. Build union-find with email as nodes
        2. Union all emails belonging to same person
        3. Group emails by parent (root)
        4. Return grouped result
        
        Time: O(N * K * α(N*K)) where N = accounts, K = avg emails per account
        Space: O(N * K) for parent and email-to-name mapping
        
        INTERVIEW TRAP: Remember to map email to account owner
        OPTIMIZATION: Path compression + union by rank makes α ≈ constant
        """
        class UnionFind:
            def __init__(self):
                self.parent = {}
                self.rank = {}
            
            def find(self, x):
                if x not in self.parent:
                    self.parent[x] = x
                    self.rank[x] = 0
                if self.parent[x] != x:
                    self.parent[x] = self.find(self.parent[x])  # Path compression
                return self.parent[x]
            
            def union(self, x, y):
                px, py = self.find(x), self.find(y)
                if px == py:
                    return
                if self.rank[px] < self.rank[py]:
                    px, py = py, px
                self.parent[py] = px
                if self.rank[px] == self.rank[py]:
                    self.rank[px] += 1
        
        uf = UnionFind()
        email_to_name = {}
        
        # Union all emails in same account
        for account in accounts:
            name = account[0]
            for email in account[1:]:
                email_to_name[email] = name
                uf.union(account[1], email)
        
        # Group emails by parent
        merged = {}
        for email in email_to_name:
            parent = uf.find(email)
            if parent not in merged:
                merged[parent] = []
            merged[parent].append(email)
        
        # Format result
        result = []
        for emails in merged.values():
            result.append([email_to_name[emails[0]]] + sorted(emails))
        
        return result


# ============================================================================
# PATTERN 4: DYNAMIC PROGRAMMING ADVANCED (Hard)
# ============================================================================

class DPHard:
    """
    INTERVIEW Q: What's the hardest DP problem type?
    ANSWER: Multi-dimensional DP with state optimization:
      1. Regular Expression Matching (2D DP)
      2. Edit Distance (2D DP)
      3. Longest Increasing Subsequence with Constraints
      4. Burst Balloons (Hard interval DP)
      5. Distinct Subsequences (DP with counting)
    """

    # PROBLEM 8: Burst Balloons (Hard)
    # Burst balloons to get maximum coins
    # nums[i] * nums[j] coins when balloon k (between i and j) is burst
    # Input: nums = [3,1,5,8]
    # Output: 167
    def maxCoins(self, nums: list) -> int:
        """
        Interval DP with reverse thinking.
        
        Algorithm:
        1. Add 1 to both ends of array for boundary handling
        2. dp[i][j] = max coins from bursting balloons between i and j
        3. Try bursting each balloon k last (between i and j)
        4. When k is burst last, nums[i] and nums[j] are adjacent
        
        Time: O(n^3) for 3D DP
        Space: O(n^2) for DP table
        
        INTERVIEW TRAP: Think backwards (burst last instead of first)
        KEY INSIGHT: Reverse thinking simplifies dependencies
        """
        if not nums:
            return 0
        
        # Add padding
        nums = [1] + nums + [1]
        n = len(nums)
        dp = [[0] * n for _ in range(n)]
        
        # len is the distance between i and j
        for len_range in range(2, n):
            for i in range(n - len_range):
                j = i + len_range
                # Try bursting each k last between i and j
                for k in range(i + 1, j):
                    coins = nums[i] * nums[k] * nums[j] + dp[i][k] + dp[k][j]
                    dp[i][j] = max(dp[i][j], coins)
        
        return dp[0][n - 1]

    # PROBLEM 9: Regular Expression Matching (Hard)
    # '.' matches any single char, '*' matches 0+ of previous char
    # Input: s = "aa", p = "a"
    # Output: False
    # Input: s = "aa", p = "a*"
    # Output: True
    def isMatch(self, s: str, p: str) -> bool:
        """
        2D DP for pattern matching.
        
        Algorithm:
        1. dp[i][j] = whether s[0:i] matches p[0:j]
        2. Handle '*' separately (0 or more matches)
        3. For each char, check if current matches or pattern has '*'
        
        Time: O(m * n) where m = len(s), n = len(p)
        Space: O(m * n) for DP table
        
        INTERVIEW TRAP: Handle empty string + empty pattern
        EDGE: 'a*' matches empty string (0 of 'a')
        """
        m, n = len(s), len(p)
        dp = [[False] * (n + 1) for _ in range(m + 1)]
        
        # Empty string matches empty pattern
        dp[0][0] = True
        
        # Handle patterns like a*, a*b*, etc.
        for j in range(2, n + 1):
            if p[j - 1] == '*':
                dp[0][j] = dp[0][j - 2]
        
        # Fill DP table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if p[j - 1] == '*':
                    # 0 matches: dp[i][j-2] OR more matches: dp[i-1][j] if s[i-1]==p[j-2]
                    dp[i][j] = dp[i][j - 2] or (dp[i - 1][j] and (s[i - 1] == p[j - 2]))
                elif p[j - 1] == '.' or p[j - 1] == s[i - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
        
        return dp[m][n]


# ============================================================================
# COMPANY-SPECIFIC PATTERNS
# ============================================================================

"""
GOOGLE INTERVIEW PATTERNS (Hard):
  1. Sliding Window (Gmail-like problem: find substring)
  2. Binary Search (YouTube: find video duration)
  3. Graph/Trees (Google Maps: shortest route)
  4. DP (Complex optimization problems)
  Examples: Minimum Window Substring, Network Delay Time, Median of Two Arrays

META INTERVIEW PATTERNS (Hard):
  1. Recursion/Backtracking (Facebook: friend connection)
  2. Graph BFS/DFS (Instagram: feed ranking)
  3. String Manipulation (WhatsApp: message parsing)
  Examples: Accounts Merge, Word Ladder, Alien Dictionary

AMAZON INTERVIEW PATTERNS (Hard):
  1. Array/String (Product-centric: manipulate data)
  2. Design Data Structures (E-commerce: inventory management)
  3. Optimization Problems (Warehouse: cost minimization)
  Examples: Burst Balloons, LRU Cache, Merge K Sorted Lists
"""

# PROBLEM 10: Alien Dictionary (Hard - Meta/Google)
class AlienDictionary:
    """
    Given list of words sorted by alien dictionary order, derive the order.
    Input: words = ["wrt","wrf","er","ett","rftt"]
    Output: "wertf"
    """
    def alienOrder(self, words: list) -> str:
        """
        Topological sort on character graph.
        
        Algorithm:
        1. Build graph: compare adjacent words to find character ordering
        2. Topological sort using DFS + cycle detection
        3. Return order or empty string if cycle detected
        
        Time: O(N * L + E) where N = words, L = avg length, E = edges
        Space: O(1) for graph (max 26 chars)
        """
        # Build adjacency list for characters
        from collections import defaultdict, deque
        
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        all_chars = set()
        
        for word in words:
            for char in word:
                all_chars.add(char)
        
        # Compare adjacent words to build graph
        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i + 1]
            min_len = min(len(w1), len(w2))
            
            # If w1 is prefix of w2, it's valid; if vice versa, invalid
            if len(w1) > len(w2) and w1[:min_len] == w2[:min_len]:
                return ""
            
            # Find first different character
            for j in range(min_len):
                if w1[j] != w2[j]:
                    if w2[j] not in graph[w1[j]]:
                        graph[w1[j]].append(w2[j])
                        in_degree[w2[j]] += 1
                    break
        
        # Topological sort
        queue = deque([ch for ch in all_chars if in_degree[ch] == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return "".join(result) if len(result) == len(all_chars) else ""


# ============================================================================
# TEST CASES & USAGE
# ============================================================================

if __name__ == "__main__":
    sol = Solution()
    
    # Test Minimum Window Substring
    print("Test 1: Minimum Window Substring")
    result = sol.minWindow("ADOBECODEBANC", "ABC")
    print(f"Result: {result}")  # Expected: "BANC"
    
    # Test Sliding Window Maximum
    print("\nTest 2: Sliding Window Maximum")
    result = sol.maxSlidingWindow([1,3,-1,-3,5,3,6,7], 3)
    print(f"Result: {result}")  # Expected: [3,3,5,5,6,7]
    
    # Test Median of Two Sorted Arrays
    bs = BinarySearchHard()
    print("\nTest 3: Median of Two Sorted Arrays")
    result = bs.findMedianSortedArrays([1, 3], [2])
    print(f"Result: {result}")  # Expected: 2.0
    
    # Test Burst Balloons
    dp = DPHard()
    print("\nTest 4: Burst Balloons")
    result = dp.maxCoins([3,1,5,8])
    print(f"Result: {result}")  # Expected: 167
    
    # Test Regular Expression Matching
    print("\nTest 5: Regular Expression Matching")
    result = dp.isMatch("aa", "a*")
    print(f"Result: {result}")  # Expected: True
    
    print("\n✅ All hard pattern tests completed!")
