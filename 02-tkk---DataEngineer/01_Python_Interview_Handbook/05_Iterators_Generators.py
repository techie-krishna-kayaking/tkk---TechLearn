"""
05_Iterators_Generators.py
================================================================================
Python Interview Handbook
Chapter 05: ITERATORS & GENERATORS

Covered in this file
--------------------
* Iterable vs Iterator (__iter__ / __next__)
* Building a custom iterator class
* Generators with yield (lazy evaluation)
* Generator expressions vs list comprehensions (memory!)
* yield from (delegation)
* Infinite generators
* send / throw / close (coroutine-ish generator protocol)
* itertools power tools (count, cycle, islice, chain, groupby, combinations, ...)
* Pipelines with generators (memory-efficient ETL)

Run:
    python3 05_Iterators_Generators.py
================================================================================
"""

import itertools
import sys


def main() -> None:
    ###########################################################
    # ITERABLE vs ITERATOR
    ###########################################################
    # Iterable: has __iter__ (can produce an iterator). e.g. list, str, dict.
    # Iterator: has __next__ (produces the next value, raises StopIteration).
    nums = [1, 2, 3]
    it = iter(nums)                  # get an iterator from an iterable
    assert next(it) == 1
    assert next(it) == 2
    assert next(it) == 3
    try:
        next(it)                     # exhausted
        raise AssertionError("should have raised")
    except StopIteration:
        pass

    ###########################################################
    # CUSTOM ITERATOR CLASS
    ###########################################################
    class Countdown:
        def __init__(self, start):
            self.current = start

        def __iter__(self):
            return self              # the object is its own iterator

        def __next__(self):
            if self.current <= 0:
                raise StopIteration
            self.current -= 1
            return self.current + 1

    assert list(Countdown(3)) == [3, 2, 1]

    ###########################################################
    # GENERATOR FUNCTION — yield produces values lazily
    ###########################################################
    def countdown(start):
        while start > 0:
            yield start              # pauses here, resumes on next()
            start -= 1

    gen = countdown(3)
    assert next(gen) == 3
    assert list(gen) == [2, 1]       # continues from where it paused
    # A generator function returns a generator (an iterator) when called.
    assert list(countdown(3)) == [3, 2, 1]

    ###########################################################
    # GENERATOR EXPRESSION vs LIST COMPREHENSION (MEMORY!)
    ###########################################################
    # List comp builds the WHOLE list in memory.
    squares_list = [k * k for k in range(1000)]
    # Generator expression is LAZY — computes on demand, tiny memory footprint.
    squares_gen = (k * k for k in range(1000))
    assert sys.getsizeof(squares_gen) < sys.getsizeof(squares_list)
    assert sum(squares_gen) == sum(squares_list)   # same result, less memory
    # INTERVIEW TIP: use a generator when you only iterate once / stream large data.

    ###########################################################
    # yield from — delegate to a sub-generator
    ###########################################################
    def flatten(nested):
        for item in nested:
            if isinstance(item, list):
                yield from flatten(item)     # recurse & delegate
            else:
                yield item

    assert list(flatten([1, [2, [3, 4], 5], 6])) == [1, 2, 3, 4, 5, 6]

    ###########################################################
    # INFINITE GENERATOR + take() pattern
    ###########################################################
    def naturals():
        n = 1
        while True:                  # infinite — safe because it's lazy
            yield n
            n += 1

    first_five = list(itertools.islice(naturals(), 5))
    assert first_five == [1, 2, 3, 4, 5]

    ###########################################################
    # GENERATOR .send() / .close() (advanced protocol)
    ###########################################################
    def accumulator():
        total = 0
        while True:
            value = yield total      # receive value sent in; yield running total
            if value is not None:
                total += value

    acc = accumulator()
    next(acc)                        # prime the generator (advance to first yield)
    assert acc.send(10) == 10
    assert acc.send(5) == 15
    acc.close()                      # stop the generator

    ###########################################################
    # ITERTOOLS — the interview power tools
    ###########################################################
    # count / cycle / repeat (infinite)
    assert list(itertools.islice(itertools.count(10, 2), 3)) == [10, 12, 14]
    assert list(itertools.islice(itertools.cycle("AB"), 5)) == ["A", "B", "A", "B", "A"]
    assert list(itertools.repeat("x", 3)) == ["x", "x", "x"]

    # chain — concatenate iterables lazily
    assert list(itertools.chain([1, 2], [3, 4])) == [1, 2, 3, 4]

    # accumulate — running totals (or any binary op)
    assert list(itertools.accumulate([1, 2, 3, 4])) == [1, 3, 6, 10]

    # combinations / permutations / product
    assert list(itertools.combinations([1, 2, 3], 2)) == [(1, 2), (1, 3), (2, 3)]
    assert len(list(itertools.permutations([1, 2, 3], 2))) == 6
    assert list(itertools.product([0, 1], repeat=2)) == [(0, 0), (0, 1), (1, 0), (1, 1)]

    # groupby — group CONSECUTIVE equal keys (sort first for full grouping!)
    data = [("fruit", "apple"), ("fruit", "pear"), ("veg", "kale")]
    grouped = {k: [v for _, v in g] for k, g in itertools.groupby(data, key=lambda t: t[0])}
    assert grouped == {"fruit": ["apple", "pear"], "veg": ["kale"]}

    # takewhile / dropwhile
    assert list(itertools.takewhile(lambda x: x < 3, [1, 2, 3, 1])) == [1, 2]
    assert list(itertools.dropwhile(lambda x: x < 3, [1, 2, 3, 1])) == [3, 1]

    # pairwise (3.10+): consecutive pairs
    if hasattr(itertools, "pairwise"):
        assert list(itertools.pairwise([1, 2, 3])) == [(1, 2), (2, 3)]

    ###########################################################
    # GENERATOR PIPELINE — memory-efficient ETL (compose lazily)
    ###########################################################
    def read_numbers(n):             # "source"
        for i in range(n):
            yield i

    def keep_even(source):           # "filter" stage
        for x in source:
            if x % 2 == 0:
                yield x

    def square(source):              # "map" stage
        for x in source:
            yield x * x

    # Nothing is computed until we consume the pipeline — constant memory.
    pipeline = square(keep_even(read_numbers(10)))
    assert list(pipeline) == [0, 4, 16, 36, 64]

    print("All 05_Iterators_Generators assertions passed ✅")


if __name__ == "__main__":
    main()
