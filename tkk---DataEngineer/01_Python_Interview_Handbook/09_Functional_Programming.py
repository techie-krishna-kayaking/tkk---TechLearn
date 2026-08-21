"""
09_Functional_Programming.py
================================================================================
Python Interview Handbook
Chapter 09: FUNCTIONAL PROGRAMMING

Covered in this file
--------------------
* map / filter / reduce (and why comprehensions are often preferred)
* zip / enumerate / any / all / sorted with key
* Pure functions & immutability
* functools.partial, functools.reduce
* functools.lru_cache / cache (memoization)
* functools.singledispatch (function overloading by type)
* operator module (function forms of operators)
* Currying / composition
* Comprehensions as the Pythonic map/filter

Run:
    python3 09_Functional_Programming.py
================================================================================
"""

import functools
import operator


def main() -> None:
    ###########################################################
    # map — apply a function to every element (returns a lazy iterator)
    ###########################################################
    nums = [1, 2, 3, 4]
    doubled = list(map(lambda x: x * 2, nums))
    assert doubled == [2, 4, 6, 8]
    # Pythonic alternative: a comprehension (usually clearer)
    assert [x * 2 for x in nums] == doubled
    # map over multiple iterables in parallel
    assert list(map(operator.add, [1, 2], [10, 20])) == [11, 22]

    ###########################################################
    # filter — keep elements where predicate is truthy
    ###########################################################
    evens = list(filter(lambda x: x % 2 == 0, range(10)))
    assert evens == [0, 2, 4, 6, 8]
    # Pythonic comprehension equivalent
    assert [x for x in range(10) if x % 2 == 0] == evens
    # filter(None, iterable) drops falsy values
    assert list(filter(None, [0, 1, "", "a", None, 2])) == [1, "a", 2]

    ###########################################################
    # reduce — fold a sequence to a single value
    ###########################################################
    assert functools.reduce(operator.mul, [1, 2, 3, 4]) == 24         # product
    assert functools.reduce(operator.add, [1, 2, 3], 100) == 106      # with initial
    # Find max via reduce (illustrative; use built-in max in real code)
    assert functools.reduce(lambda a, b: a if a > b else b, [3, 7, 2]) == 7

    ###########################################################
    # any / all — short-circuiting boolean aggregation
    ###########################################################
    assert all(x > 0 for x in [1, 2, 3])
    assert any(x < 0 for x in [1, -2, 3])
    assert all([]) is True           # vacuous truth (empty -> all True)
    assert any([]) is False          # empty -> any False

    ###########################################################
    # sorted with key — the workhorse of interview coding
    ###########################################################
    people = [("Ada", 36), ("Alan", 41), ("Grace", 36)]
    # Sort by age asc, then name asc
    assert sorted(people, key=lambda p: (p[1], p[0])) == [
        ("Ada", 36), ("Grace", 36), ("Alan", 41),
    ]
    # operator.itemgetter is faster & clearer than a lambda for indexing
    from operator import itemgetter, attrgetter
    assert sorted(people, key=itemgetter(1))[0] == ("Ada", 36)

    ###########################################################
    # PURE FUNCTIONS & IMMUTABILITY
    ###########################################################
    # Pure: output depends only on inputs, no side effects. Easier to test/parallelize.
    def add_pure(a, b):
        return a + b                 # no mutation, no I/O

    # Impure (mutates external state) — avoid where possible
    log = []

    def add_impure(a, b):
        log.append((a, b))           # side effect!
        return a + b

    assert add_pure(2, 3) == add_impure(2, 3) == 5
    assert log == [(2, 3)]

    # Prefer building NEW data over mutating (functional style)
    original = (1, 2, 3)             # tuple is immutable
    extended = original + (4,)       # new tuple, original unchanged
    assert original == (1, 2, 3) and extended == (1, 2, 3, 4)

    ###########################################################
    # functools.partial — partial application / currying
    ###########################################################
    def volume(length, width, height):
        return length * width * height

    # Fix some arguments to specialize the function
    base_area = functools.partial(volume, height=1)
    assert base_area(2, 3) == 6
    int_from_bin = functools.partial(int, base=2)
    assert int_from_bin("1010") == 10

    ###########################################################
    # functools.lru_cache — memoization for expensive/pure functions
    ###########################################################
    call_count = {"n": 0}

    @functools.lru_cache(maxsize=128)
    def slow_square(x):
        call_count["n"] += 1
        return x * x

    assert slow_square(4) == 16
    assert slow_square(4) == 16       # served from cache
    assert call_count["n"] == 1       # body ran only once
    assert slow_square.cache_info().hits == 1

    ###########################################################
    # functools.singledispatch — overload by first-arg type
    ###########################################################
    @functools.singledispatch
    def describe(value):
        return f"generic: {value}"

    @describe.register
    def _(value: int):
        return f"int: {value}"

    @describe.register
    def _(value: list):
        return f"list of {len(value)}"

    assert describe(10) == "int: 10"
    assert describe([1, 2, 3]) == "list of 3"
    assert describe("hi") == "generic: hi"

    ###########################################################
    # operator module — function versions of operators
    ###########################################################
    assert operator.add(3, 4) == 7
    assert operator.mul(3, 4) == 12
    assert operator.itemgetter(1)([10, 20, 30]) == 20

    class Obj:
        def __init__(self, v):
            self.v = v

    assert attrgetter("v")(Obj(99)) == 99
    # methodcaller
    assert operator.methodcaller("upper")("hi") == "HI"

    ###########################################################
    # FUNCTION COMPOSITION (compose f∘g)
    ###########################################################
    def compose(*funcs):
        # compose(f, g, h)(x) == f(g(h(x)))
        def composed(x):
            for fn in reversed(funcs):
                x = fn(x)
            return x
        return composed

    inc = lambda x: x + 1
    dbl = lambda x: x * 2
    pipeline = compose(inc, dbl)     # inc(dbl(x))
    assert pipeline(5) == 11         # dbl(5)=10 -> inc=11

    ###########################################################
    # COMPREHENSIONS AS map+filter (the Pythonic default)
    ###########################################################
    data = range(10)
    # map + filter
    fp_style = list(map(lambda x: x ** 2, filter(lambda x: x % 2, data)))
    # comprehension (clearer)
    comp_style = [x ** 2 for x in data if x % 2]
    assert fp_style == comp_style == [1, 9, 25, 49, 81]

    print("All 09_Functional_Programming assertions passed ✅")


if __name__ == "__main__":
    main()
