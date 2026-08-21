"""
02_Data_Structures.py
================================================================================
Python Interview Handbook
Chapter 02: DATA STRUCTURES

Covered in this file
--------------------
* list      : mutable ordered sequence, methods, slicing, sorting, copying
* tuple     : immutable ordered sequence, packing/unpacking, namedtuple
* set       : unique unordered, set algebra, frozenset
* dict      : key-value mapping, methods, merging, ordering, comprehensions
* Comprehensions: list / set / dict / nested / conditional
* Shallow vs deep copy
* Time complexity cheat-sheet (interview essential)

Running this file prints results and asserts documented behavior.

Run:
    python3 02_Data_Structures.py
================================================================================
"""

import copy
from collections import namedtuple


def main() -> None:
    ###########################################################
    # LIST — mutable, ordered, allows duplicates
    ###########################################################
    nums = [3, 1, 2, 1]
    nums.append(5)                   # add to end -> O(1)
    nums.insert(0, 9)                # insert at index -> O(n)
    nums.extend([6, 7])              # add many
    assert nums == [9, 3, 1, 2, 1, 5, 6, 7]
    nums.remove(1)                   # remove FIRST occurrence of value
    popped = nums.pop()              # remove & return last -> O(1)
    assert popped == 7
    assert nums.index(3) == 1        # first index of value
    assert nums.count(1) == 1        # occurrences

    # Slicing (works on any sequence)
    a = [0, 1, 2, 3, 4, 5]
    assert a[1:4] == [1, 2, 3]
    assert a[::-1] == [5, 4, 3, 2, 1, 0]
    assert a[::2] == [0, 2, 4]
    a[1:3] = [10, 20, 30]            # slice assignment can change length
    assert a == [0, 10, 20, 30, 3, 4, 5]

    ###########################################################
    # SORTING — sorted() vs list.sort(), key, reverse
    ###########################################################
    data = [("Ada", 95), ("Alan", 88), ("Grace", 95)]
    # sorted() returns a NEW list; .sort() mutates in place and returns None.
    by_score_desc = sorted(data, key=lambda t: t[1], reverse=True)
    assert by_score_desc[0][1] == 95
    # Multi-key sort: score desc, then name asc (stable sort makes this reliable).
    multi = sorted(data, key=lambda t: (-t[1], t[0]))
    assert multi == [("Ada", 95), ("Grace", 95), ("Alan", 88)]
    # COMMON MISTAKE: x = mylist.sort() -> x is None (sort mutates, returns None).
    tmp = [3, 1, 2]
    ret = tmp.sort()
    assert ret is None and tmp == [1, 2, 3]

    ###########################################################
    # LIST COPYING — Non-Pythonic vs Pythonic + the aliasing trap
    ###########################################################
    original = [1, 2, 3]
    alias = original                 # NOT a copy — same object!
    alias.append(99)
    assert original == [1, 2, 3, 99]  # mutating alias mutated original
    # Real (shallow) copies:
    c1 = original[:]                 # slice copy
    c2 = list(original)              # constructor copy
    c3 = original.copy()             # .copy() method
    assert c1 == c2 == c3 == original and c1 is not original

    ###########################################################
    # SHALLOW vs DEEP COPY (nested structures)
    ###########################################################
    nested = [[1, 2], [3, 4]]
    shallow = copy.copy(nested)      # inner lists are SHARED
    shallow[0].append(99)
    assert nested[0] == [1, 2, 99]   # inner mutation leaks!
    deep = copy.deepcopy(nested)     # fully independent
    deep[0].append(1000)
    assert nested[0] == [1, 2, 99]   # unaffected by deep copy mutation

    ###########################################################
    # TUPLE — immutable, hashable (usable as dict keys / set members)
    ###########################################################
    point = (3, 4)
    assert point[0] == 3
    # Packing / unpacking
    x, y = point
    assert x == 3 and y == 4
    # Star unpacking (3.0+)
    first, *middle, last = [1, 2, 3, 4, 5]
    assert first == 1 and middle == [2, 3, 4] and last == 5
    # Swap without a temp variable (Pythonic)
    m, n = 1, 2
    m, n = n, m
    assert (m, n) == (2, 1)
    # Single-element tuple needs a trailing comma!
    not_a_tuple = (5)
    a_tuple = (5,)
    assert isinstance(not_a_tuple, int) and isinstance(a_tuple, tuple)

    ###########################################################
    # namedtuple — readable, lightweight, immutable records
    ###########################################################
    Person = namedtuple("Person", ["name", "age"])
    p = Person("Ada", 36)
    assert p.name == "Ada" and p.age == 36
    assert p[0] == "Ada"             # still index-accessible
    p2 = p._replace(age=37)          # returns a new namedtuple
    assert p2.age == 37 and p.age == 36

    ###########################################################
    # SET — unique elements, fast membership (O(1) average)
    ###########################################################
    s = {1, 2, 3, 3, 2}
    assert s == {1, 2, 3}            # duplicates removed
    s.add(4)
    s.discard(10)                    # discard: no error if missing
    assert 4 in s
    # Deduplicate a list while checking membership fast:
    dupes = [1, 1, 2, 3, 3, 3]
    assert set(dupes) == {1, 2, 3}
    # Set algebra
    a_set, b_set = {1, 2, 3, 4}, {3, 4, 5, 6}
    assert a_set | b_set == {1, 2, 3, 4, 5, 6}     # union
    assert a_set & b_set == {3, 4}                 # intersection
    assert a_set - b_set == {1, 2}                 # difference
    assert a_set ^ b_set == {1, 2, 5, 6}           # symmetric difference
    assert {1, 2} <= {1, 2, 3}                     # subset
    # frozenset — immutable & hashable set
    fs = frozenset([1, 2, 3])
    assert fs in {fs: "ok"}          # usable as a dict key

    ###########################################################
    # DICT — key -> value mapping (insertion-ordered since 3.7)
    ###########################################################
    d = {"a": 1, "b": 2}
    d["c"] = 3                        # insert / update
    assert d["a"] == 1
    # .get avoids KeyError and supplies a default
    assert d.get("z", 0) == 0
    # setdefault: get-or-insert
    d.setdefault("d", 4)
    assert d["d"] == 4
    # Iteration
    assert list(d.keys()) == ["a", "b", "c", "d"]
    assert list(d.values()) == [1, 2, 3, 4]
    assert ("a", 1) in d.items()
    # pop with default
    assert d.pop("missing", -1) == -1
    # Merge dicts
    d1, d2 = {"a": 1, "b": 2}, {"b": 20, "c": 3}
    merged_old = {**d1, **d2}         # unpacking merge (3.5+)
    merged_new = d1 | d2              # union operator (3.9+); later wins
    assert merged_old == merged_new == {"a": 1, "b": 20, "c": 3}

    ###########################################################
    # COMPREHENSIONS — Non-Pythonic loop vs Pythonic comprehension
    ###########################################################
    # List comprehension
    squares_loop = []
    for k in range(6):
        squares_loop.append(k * k)
    squares = [k * k for k in range(6)]
    assert squares_loop == squares == [0, 1, 4, 9, 16, 25]

    # Conditional (filter) in a comprehension
    evens = [k for k in range(10) if k % 2 == 0]
    assert evens == [0, 2, 4, 6, 8]

    # Conditional EXPRESSION inside comprehension
    parity = ["even" if k % 2 == 0 else "odd" for k in range(4)]
    assert parity == ["even", "odd", "even", "odd"]

    # Set & dict comprehensions
    unique_lengths = {len(w) for w in ["hi", "hey", "yo"]}
    assert unique_lengths == {2, 3}
    square_map = {k: k * k for k in range(4)}
    assert square_map == {0: 0, 1: 1, 2: 4, 3: 9}

    # Nested comprehension: flatten a matrix
    matrix = [[1, 2, 3], [4, 5, 6]]
    flat = [val for row in matrix for val in row]
    assert flat == [1, 2, 3, 4, 5, 6]

    # Transpose a matrix (Pythonic with zip)
    transposed = [list(col) for col in zip(*matrix)]
    assert transposed == [[1, 4], [2, 5], [3, 6]]

    ###########################################################
    # COMMON GOTCHA: mutable default & shared references in nested lists
    ###########################################################
    # WRONG: [[0]*3]*2 creates 2 references to the SAME inner list
    bad = [[0] * 3] * 2
    bad[0][0] = 9
    assert bad == [[9, 0, 0], [9, 0, 0]]   # both rows changed!
    # RIGHT: build independent rows with a comprehension
    good = [[0] * 3 for _ in range(2)]
    good[0][0] = 9
    assert good == [[9, 0, 0], [0, 0, 0]]

    ###########################################################
    # TIME COMPLEXITY CHEAT-SHEET (say these in interviews)
    ###########################################################
    complexity = {
        "list index a[i]": "O(1)",
        "list append/pop end": "O(1) amortized",
        "list insert/pop front": "O(n)",
        "value in list": "O(n)",
        "value in set/dict": "O(1) average",
        "dict get/set": "O(1) average",
        "sort": "O(n log n)",
    }
    for op, big_o in complexity.items():
        print(f"{op:28s} -> {big_o}")

    print("\nAll 02_Data_Structures assertions passed ✅")


if __name__ == "__main__":
    main()
