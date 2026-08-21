"""
07_Standard_Library.py
================================================================================
Python Interview Handbook
Chapter 07: THE STANDARD LIBRARY (batteries included)

Covered in this file
--------------------
* collections : Counter, defaultdict, OrderedDict, deque, namedtuple, ChainMap
* functools   : reduce, partial, lru_cache, cache, cmp_to_key, wraps, reduce
* itertools   : (recap of the essentials)
* datetime    : date, time, timedelta, strftime/strptime
* re          : match, search, findall, sub, groups, named groups
* math / statistics
* heapq       : priority queue / top-k
* bisect      : binary search / sorted insertion

Run:
    python3 07_Standard_Library.py
================================================================================
"""

import bisect
import functools
import heapq
import math
import re
import statistics
from collections import Counter, defaultdict, deque, ChainMap, OrderedDict
from datetime import date, datetime, timedelta


def main() -> None:
    ###########################################################
    # collections.Counter — frequency counting made trivial
    ###########################################################
    words = "the cat sat on the mat the cat".split()
    counts = Counter(words)
    assert counts["the"] == 3
    assert counts.most_common(2) == [("the", 3), ("cat", 2)]
    # Counters support arithmetic
    assert (Counter("aab") + Counter("abc"))["a"] == 3
    # Non-Pythonic frequency count vs Pythonic Counter
    manual = {}
    for w in words:
        manual[w] = manual.get(w, 0) + 1
    assert manual == dict(counts)

    ###########################################################
    # collections.defaultdict — auto-initialize missing keys
    ###########################################################
    groups = defaultdict(list)       # missing key -> new empty list
    for name in ["Ada", "Alan", "Grace"]:
        groups[name[0]].append(name)
    assert groups["A"] == ["Ada", "Alan"]
    assert groups["G"] == ["Grace"]
    # int factory for counting
    freq = defaultdict(int)
    for ch in "banana":
        freq[ch] += 1
    assert freq == {"b": 1, "a": 3, "n": 2}

    ###########################################################
    # collections.deque — O(1) appends/pops at BOTH ends
    ###########################################################
    dq = deque([2, 3])
    dq.appendleft(1)                 # O(1) (list.insert(0,..) is O(n)!)
    dq.append(4)
    assert list(dq) == [1, 2, 3, 4]
    assert dq.popleft() == 1
    dq.rotate(1)                     # rotate right
    assert list(dq) == [4, 2, 3]
    # deque as a fixed-size sliding window / ring buffer
    window = deque(maxlen=3)
    for x in [1, 2, 3, 4, 5]:
        window.append(x)
    assert list(window) == [3, 4, 5]

    ###########################################################
    # OrderedDict & ChainMap
    ###########################################################
    od = OrderedDict([("a", 1), ("b", 2)])
    od.move_to_end("a")
    assert list(od) == ["b", "a"]
    # ChainMap — layered lookup (e.g. overrides -> defaults)
    defaults = {"color": "black", "size": "M"}
    overrides = {"color": "red"}
    settings = ChainMap(overrides, defaults)
    assert settings["color"] == "red" and settings["size"] == "M"

    ###########################################################
    # functools — reduce, partial, lru_cache, cmp_to_key
    ###########################################################
    # reduce: fold a sequence into a single value
    product = functools.reduce(lambda acc, x: acc * x, [1, 2, 3, 4], 1)
    assert product == 24

    # partial: pre-bind arguments to create a specialized function
    def power(base, exp):
        return base ** exp

    square = functools.partial(power, exp=2)
    assert square(5) == 25

    # lru_cache / cache: memoization
    @functools.lru_cache(maxsize=None)
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    assert fib(20) == 6765
    assert fib.cache_info().hits > 0

    # cmp_to_key: use an old-style comparator as a sort key
    def cmp(a, b):
        return (a > b) - (a < b)

    assert sorted([3, 1, 2], key=functools.cmp_to_key(cmp)) == [1, 2, 3]

    ###########################################################
    # datetime — dates, deltas, parsing & formatting
    ###########################################################
    d1 = date(2024, 1, 1)
    d2 = date(2024, 3, 1)
    delta = d2 - d1
    assert isinstance(delta, timedelta) and delta.days == 60
    future = d1 + timedelta(days=7)
    assert future == date(2024, 1, 8)
    # Format (date -> string) and parse (string -> datetime)
    dt = datetime(2024, 12, 25, 14, 30)
    assert dt.strftime("%Y-%m-%d %H:%M") == "2024-12-25 14:30"
    parsed = datetime.strptime("2024-12-25", "%Y-%m-%d")
    assert parsed.year == 2024 and parsed.month == 12
    assert d1.weekday() == 0         # Monday == 0

    ###########################################################
    # re — regular expressions
    ###########################################################
    # search finds the first match anywhere; match anchors at the start.
    m = re.search(r"\d+", "abc123def456")
    assert m.group() == "123"
    assert re.findall(r"\d+", "a1b22c333") == ["1", "22", "333"]
    # groups & named groups
    m = re.search(r"(?P<year>\d{4})-(?P<month>\d{2})", "2024-12")
    assert m.group("year") == "2024" and m.group("month") == "12"
    # substitution
    assert re.sub(r"\s+", "_", "a  b   c") == "a_b_c"
    # compile for reuse (performance when applied many times)
    email_re = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")
    assert email_re.match("me@example.com")
    assert not email_re.match("not-an-email")

    ###########################################################
    # math / statistics
    ###########################################################
    assert math.gcd(12, 18) == 6
    assert math.factorial(5) == 120
    assert math.isclose(math.hypot(3, 4), 5.0)
    assert math.floor(3.7) == 3 and math.ceil(3.2) == 4
    assert statistics.mean([1, 2, 3, 4]) == 2.5
    assert statistics.median([1, 3, 2]) == 2
    assert statistics.mode([1, 1, 2, 3]) == 1

    ###########################################################
    # heapq — min-heap / priority queue / top-k
    ###########################################################
    heap = [5, 1, 3, 2, 4]
    heapq.heapify(heap)              # in-place -> min-heap
    assert heap[0] == 1              # smallest always at index 0
    heapq.heappush(heap, 0)
    assert heapq.heappop(heap) == 0  # pop smallest
    # Top-k without a full sort (efficient for large data)
    nums = [9, 1, 8, 2, 7, 3]
    assert heapq.nlargest(3, nums) == [9, 8, 7]
    assert heapq.nsmallest(2, nums) == [1, 2]
    # Max-heap trick: negate the values
    max_heap = [-x for x in nums]
    heapq.heapify(max_heap)
    assert -heapq.heappop(max_heap) == 9

    ###########################################################
    # bisect — binary search in a sorted list (O(log n))
    ###########################################################
    sorted_nums = [1, 3, 5, 7, 9]
    assert bisect.bisect_left(sorted_nums, 5) == 2
    assert bisect.bisect_right(sorted_nums, 5) == 3
    bisect.insort(sorted_nums, 4)    # insert keeping it sorted
    assert sorted_nums == [1, 3, 4, 5, 7, 9]

    print("All 07_Standard_Library assertions passed ✅")


if __name__ == "__main__":
    main()
