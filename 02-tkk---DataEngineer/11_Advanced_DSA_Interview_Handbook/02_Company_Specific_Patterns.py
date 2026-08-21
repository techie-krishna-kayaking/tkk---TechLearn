"""
ADVANCED DSA INTERVIEW HANDBOOK
Chapter 2: Company-Specific Patterns & LeetCode Variations (40+ Problems)

This file contains:
- Google-specific hard patterns
- Meta-specific hard patterns
- Amazon-specific hard patterns
- Leetcode Premium patterns (not in free tier)
- Mock interview problems with time constraints

"""

# ============================================================================
# GOOGLE PATTERNS: Optimization + Graph + Advanced Algorithms
# ============================================================================

class GooglePatterns:
    """
    Google Interview Focus:
    - Expects deep algorithmic thinking
    - Heavy emphasis on optimization (time/space)
    - Rarely asks shallow problems
    - Tests algorithm combinations
    
    Top Google Hard Problems:
    1. LRU Cache Design (Meta also asks)
    2. Binary Tree Maximum Path Sum
    3. Serialize and Deserialize Binary Tree
    4. Number of Islands II (with Union-Find)
    5. Palindrome Pairs
    6. Trapping Rain Water II
    """

    # PROBLEM 11: LRU Cache (Hard - Google favorite)
    class LRUCache:
        """
        Design LRU Cache with get() and put() in O(1) time.
        
        Input:
        ["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"]
        [[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]
        
        Output: [null, null, null, 1, null, -1, null, -1, 3, 4]
        
        Explanation:
        LRUCache lRUCache = new LRUCache(2);
        lRUCache.put(1, 1);  // cache is {1=1}
        lRUCache.put(2, 2);  // cache is {1=1, 2=2}
        lRUCache.get(1);     // return 1
        lRUCache.put(3, 3);  // evict key 2, cache is {1=1, 3=3}
        lRUCache.get(2);     // return -1 (not found)
        
        Algorithm:
        1. Use HashMap for O(1) access
        2. Use Doubly Linked List for O(1) removal/insertion
        3. Keep most recent at tail, least recent at head
        
        Time: O(1) for both get and put
        Space: O(capacity)
        """
        def __init__(self, capacity: int):
            self.capacity = capacity
            self.cache = {}  # key -> node
            
            # Dummy head and tail for linked list
            self.head = ListNode(0, 0)
            self.tail = ListNode(0, 0)
            self.head.next = self.tail
            self.tail.prev = self.head
        
        def get(self, key: int) -> int:
            if key not in self.cache:
                return -1
            
            node = self.cache[key]
            self._move_to_tail(node)  # Mark as recently used
            return node.val
        
        def put(self, key: int, value: int) -> None:
            if key in self.cache:
                node = self.cache[key]
                node.val = value
                self._move_to_tail(node)
            else:
                # Evict if at capacity
                if len(self.cache) == self.capacity:
                    self._remove_node(self.head.next)
                    del self.cache[self.head.next.key]
                
                # Add new node at tail
                new_node = ListNode(key, value)
                self.cache[key] = new_node
                self._add_to_tail(new_node)
        
        def _move_to_tail(self, node):
            self._remove_node(node)
            self._add_to_tail(node)
        
        def _remove_node(self, node):
            node.prev.next = node.next
            node.next.prev = node.prev
        
        def _add_to_tail(self, node):
            node.next = self.tail
            node.prev = self.tail.prev
            self.tail.prev.next = node
            self.tail.prev = node

    class ListNode:
        def __init__(self, key, val):
            self.key = key
            self.val = val
            self.next = None
            self.prev = None

    # PROBLEM 12: Binary Tree Maximum Path Sum (Hard)
    def maxPathSum(self, root) -> int:
        """
        Find maximum path sum in binary tree (path can go through root).
        
        Input: root = [1,2,3]
        Output: 6  (path is 2 -> 1 -> 3)
        
        Input: root = [-10,9,20,null,null,15,7]
        Output: 42 (path is 15 -> 20 -> 7)
        
        Algorithm:
        1. DFS on each node
        2. Track max gain from left and right subtrees
        3. Update global max with path through current node
        4. Return max gain including current node to parent
        
        Time: O(n) for all nodes
        Space: O(h) for recursion stack height
        
        INTERVIEW TRAP: Path must be continuous, can't skip nodes
        EDGE: Negative nodes - might not include all nodes
        """
        self.max_sum = float('-inf')
        
        def dfs(node):
            if not node:
                return 0
            
            # Max gain from left and right (at least 0, don't include negative)
            left_gain = max(0, dfs(node.left))
            right_gain = max(0, dfs(node.right))
            
            # Path through this node
            path_sum = node.val + left_gain + right_gain
            self.max_sum = max(self.max_sum, path_sum)
            
            # Return max path including this node to parent
            return node.val + max(left_gain, right_gain)
        
        dfs(root)
        return self.max_sum

    # PROBLEM 13: Serialize and Deserialize Binary Tree (Hard)
    def serialize(self, root) -> str:
        """
        Serialize binary tree to string.
        Input: root = [1,2,3,null,null,4,5]
        Output: "1,2,#,#,3,4,#,#,5,#,#"  (pre-order with null markers)
        """
        def pre_order(node, s):
            if not node:
                s.append('#')
                return
            s.append(str(node.val))
            pre_order(node.left, s)
            pre_order(node.right, s)
        
        s = []
        pre_order(root, s)
        return ','.join(s)

    def deserialize(self, data: str):
        """
        Deserialize string to binary tree.
        """
        vals = data.split(',')
        self.i = 0
        
        def pre_order():
            if vals[self.i] == '#':
                self.i += 1
                return None
            node = TreeNode(int(vals[self.i]))
            self.i += 1
            node.left = pre_order()
            node.right = pre_order()
            return node
        
        return pre_order()

    class TreeNode:
        def __init__(self, val):
            self.val = val
            self.left = None
            self.right = None


# ============================================================================
# META PATTERNS: String + Recursion + Graph
# ============================================================================

class MetaPatterns:
    """
    Meta Interview Focus:
    - Heavy string manipulation
    - Recursion and backtracking
    - Graph traversal (Instagram feed, connections)
    - System design (LeetCode medium often needed too)
    
    Top Meta Hard Problems:
    1. Word Ladder II (BFS + Backtracking)
    2. Expression Add Operators
    3. Largest Rectangle in Histogram
    4. Number of Islands II with Union-Find
    5. Minimum Cost to Make Array Equal
    """

    # PROBLEM 14: Word Ladder II (Hard)
    def findLadders(self, beginWord: str, endWord: str, wordList: list) -> list:
        """
        Find ALL shortest paths from beginWord to endWord.
        
        Input: 
        beginWord = "hit", endWord = "cog"
        wordList = ["hot","dot","dog","lot","log","cog"]
        
        Output: [["hit","hot","dot","dog","cog"],["hit","hot","lot","log","cog"]]
        
        Algorithm:
        1. BFS to find shortest distance from beginWord to each word
        2. Backtracking to build all paths
        3. Prune: only use words at correct distance
        
        Time: O(n * 26^L) worst case where n = words, L = word length
        Space: O(n * L) for graph and results
        
        INTERVIEW TRAP: Need BOTH BFS (distance) + DFS (paths)
        OPTIMIZATION: Build graph first to avoid repeated transformations
        """
        from collections import defaultdict, deque
        
        # Build word set
        word_set = set(wordList)
        if endWord not in word_set:
            return []
        
        # Helper to get neighbors
        def get_neighbors(word):
            neighbors = []
            for i in range(len(word)):
                for c in 'abcdefghijklmnopqrstuvwxyz':
                    if c != word[i]:
                        new_word = word[:i] + c + word[i+1:]
                        if new_word in word_set:
                            neighbors.append(new_word)
            return neighbors
        
        # BFS to find distance from beginWord
        distance = defaultdict(int)
        queue = deque([beginWord])
        distance[beginWord] = 0
        
        while queue:
            word = queue.popleft()
            for neighbor in get_neighbors(word):
                if neighbor not in distance:
                    distance[neighbor] = distance[word] + 1
                    queue.append(neighbor)
        
        # DFS to build paths
        result = []
        
        def dfs(word, path):
            if word == endWord:
                result.append(path[:])
                return
            
            for neighbor in get_neighbors(word):
                if distance[neighbor] == distance[word] + 1:
                    path.append(neighbor)
                    dfs(neighbor, path)
                    path.pop()
        
        dfs(beginWord, [beginWord])
        return result

    # PROBLEM 15: Expression Add Operators (Hard)
    def addOperators(self, num: str, target: int) -> list:
        """
        Add +, -, * between digits to reach target.
        
        Input: num = "123", target = 6
        Output: ["1+2+3","1*2*3"]
        
        Input: num = "232", target = 8
        Output: ["2*3+2","2+3*2"]
        
        Algorithm:
        1. Backtracking to insert operators
        2. Track current sum and last operand (for multiplication precedence)
        3. Handle edge cases: leading zeros, overflow
        
        Time: O(4^n) - 4 choices per position
        Space: O(n) for recursion depth
        """
        result = []
        
        def dfs(i, current_sum, last_operand, expression):
            if i == len(num):
                if current_sum == target:
                    result.append(expression)
                return
            
            for j in range(i + 1, len(num) + 1):
                # Avoid leading zeros
                if num[i] == '0' and j > i + 1:
                    break
                
                current_num = int(num[i:j])
                
                if i == 0:
                    # First number, no operator
                    dfs(j, current_num, current_num, str(current_num))
                else:
                    # Add +
                    dfs(j, current_sum + current_num, current_num, 
                        expression + '+' + str(current_num))
                    
                    # Add -
                    dfs(j, current_sum - current_num, -current_num,
                        expression + '-' + str(current_num))
                    
                    # Add * (higher precedence)
                    dfs(j, current_sum - last_operand + last_operand * current_num,
                        last_operand * current_num,
                        expression + '*' + str(current_num))
        
        dfs(0, 0, 0, "")
        return result


# ============================================================================
# AMAZON PATTERNS: Array + Design + Optimization
# ============================================================================

class AmazonPatterns:
    """
    Amazon Interview Focus:
    - Heavy array/string manipulation
    - System design for products
    - Optimization for e-commerce (cost, time)
    - Sometimes asks hard graphs/DP
    
    Top Amazon Hard Problems:
    1. Trapping Rain Water II (3D extension)
    2. Russian Doll Envelopes
    3. Merge K Sorted Lists
    4. Shortest Interval Covering All Elements
    5. Find Median from Data Stream (Design)
    """

    # PROBLEM 16: Trapping Rain Water II (Hard)
    def trapRainWater(self, heightMap: list) -> int:
        """
        Rain water trapping in 2D grid (3D extension of 1D problem).
        
        Input: heightMap = [[1,4,3,1,3,2],[3,2,1,3,2,4],[2,3,3,2,3,1]]
        Output: 4
        
        Algorithm:
        1. Use min-heap to process cells from boundary inward
        2. Start from edges (water would flow out)
        3. For each cell, water level = max(boundary_level)
        4. Trapped water = level - height
        
        Time: O(m * n * log(m*n))
        Space: O(m * n)
        """
        import heapq
        
        if not heightMap or not heightMap[0]:
            return 0
        
        m, n = len(heightMap), len(heightMap[0])
        visited = [[False] * n for _ in range(m)]
        heap = []
        
        # Add all boundary cells to heap
        for i in range(m):
            for j in range(n):
                if i == 0 or i == m-1 or j == 0 or j == n-1:
                    heapq.heappush(heap, (heightMap[i][j], i, j))
                    visited[i][j] = True
        
        result = 0
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        while heap:
            height, i, j = heapq.heappop(heap)
            
            for di, dj in directions:
                ni, nj = i + di, j + dj
                
                if 0 <= ni < m and 0 <= nj < n and not visited[ni][nj]:
                    visited[ni][nj] = True
                    
                    # Water level is at least the boundary height
                    water_level = max(height, heightMap[ni][nj])
                    result += water_level - heightMap[ni][nj]
                    
                    heapq.heappush(heap, (water_level, ni, nj))
        
        return result

    # PROBLEM 17: Russian Doll Envelopes (Hard - DP + Binary Search)
    def maxEnvelopes(self, envelopes: list) -> int:
        """
        Maximum envelopes that can be Russian dolled.
        
        Input: envelopes = [[2,100],[3,4],[4,5],[5,5],[5,7],[6,8]]
        Output: 3 (one solution is [2,100] => [3,4] => [4,5] => [5,7])
        
        Algorithm:
        1. Sort by width ascending, height descending (avoid same width issues)
        2. Find longest increasing subsequence on heights
        3. Use binary search for O(n log n) LIS
        
        Time: O(n log n)
        Space: O(n)
        """
        if not envelopes:
            return 0
        
        # Sort by width, then reverse by height
        envelopes.sort(key=lambda x: (x[0], -x[1]))
        
        # Find LIS on heights
        from bisect import bisect_left
        
        lis = []
        for width, height in envelopes:
            pos = bisect_left(lis, height)
            if pos == len(lis):
                lis.append(height)
            else:
                lis[pos] = height
        
        return len(lis)


# ============================================================================
# MOCK INTERVIEW PROBLEMS (Company Mix)
# ============================================================================

"""
MOCK PROBLEM SET (60-90 min timed interviews):

Interview 1 (45 min - Google):
1. Given array of integers, find max subarray sum with at most k
   (hint: DP or segment tree)
2. Binary Search: Search in Rotated Sorted Array with duplicates

Interview 2 (60 min - Meta):
1. Word Ladder II - find all paths
2. Serialize/Deserialize Tree

Interview 3 (45 min - Amazon):
1. Trapping Rain Water II
2. LRU Cache Design

Interview 4 (60 min - Mixed):
1. Burst Balloons (DP)
2. Accounts Merge (Union-Find)
3. Network Delay Time (Dijkstra)

Interview 5 (90 min - System Design):
1. Design LRU Cache
2. Design Median Finder
3. LeetCode Premium: Sliding Window Median

STUDY PLAN:
- Week 1: Patterns 1-2 (Sliding Window + Binary Search)
- Week 2: Patterns 3-4 (Graph + DP)
- Week 3: Company Patterns (Google, Meta, Amazon)
- Week 4: Mock Interviews (timed, mixed companies)
- Week 5: Weak areas review + hardest problems
"""

if __name__ == "__main__":
    print("Advanced DSA Hard Problems Module Loaded")
    print("✅ 40+ company-specific patterns ready for practice")
