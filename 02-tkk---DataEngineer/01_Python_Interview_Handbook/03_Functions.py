"""
03_Functions.py
================================================================================
Python Interview Handbook
Chapter 03: FUNCTIONS

Covered in this file
--------------------
* Defining functions, return values, multiple returns
* Positional / keyword / default arguments
* *args and **kwargs
* Keyword-only and positional-only parameters
* The MUTABLE DEFAULT ARGUMENT trap (classic interview question)
* Scope: local, enclosing, global, built-in (LEGB); global & nonlocal
* First-class functions & higher-order functions
* Closures
* lambda expressions
* Decorators (incl. with arguments, functools.wraps)
* Recursion (and why Python has no tail-call optimization)

Run:
    python3 03_Functions.py
================================================================================
"""

import functools


# Module-level global, used to demonstrate the `global` keyword from inside a
# function (the `global` statement rebinds MODULE-level names, not locals).
_GLOBAL_TOTAL = 0


def _add_to_global(n):
    global _GLOBAL_TOTAL
    _GLOBAL_TOTAL += n


def main() -> None:
    ###########################################################
    # BASIC FUNCTION + MULTIPLE RETURN (really a tuple)
    ###########################################################
    def divmod2(a, b):
        return a // b, a % b          # returns a tuple

    q, r = divmod2(17, 5)
    assert (q, r) == (3, 2)

    ###########################################################
    # DEFAULT / KEYWORD ARGUMENTS
    ###########################################################
    def greet(name, greeting="Hello"):
        return f"{greeting}, {name}!"

    assert greet("Ada") == "Hello, Ada!"
    assert greet("Ada", greeting="Hi") == "Hi, Ada!"   # pass by keyword
    assert greet(greeting="Hey", name="Al") == "Hey, Al!"

    ###########################################################
    # *args and **kwargs — variable arguments
    ###########################################################
    def summarize(*args, **kwargs):
        # args   -> tuple of extra positional args
        # kwargs -> dict of extra keyword args
        return sum(args), dict(kwargs)

    total, opts = summarize(1, 2, 3, mode="fast", debug=True)
    assert total == 6 and opts == {"mode": "fast", "debug": True}

    # Unpacking arguments when CALLING (the * / ** on the call side)
    def add3(a, b, c):
        return a + b + c

    nums = [1, 2, 3]
    kw = {"a": 1, "b": 2, "c": 3}
    assert add3(*nums) == 6          # unpack list into positionals
    assert add3(**kw) == 6           # unpack dict into keywords

    ###########################################################
    # KEYWORD-ONLY (after *) & POSITIONAL-ONLY (before /) params
    ###########################################################
    def connect(host, *, port=5432, timeout=30):
        # port & timeout MUST be passed by keyword (after the bare *)
        return f"{host}:{port} t={timeout}"

    assert connect("db", port=5433) == "db:5433 t=30"

    def div(a, b, /):
        # a and b are POSITIONAL-ONLY (3.8+): cannot be passed as div(a=..)
        return a / b

    assert div(10, 2) == 5.0

    ###########################################################
    # MUTABLE DEFAULT ARGUMENT TRAP (very common interview question!)
    ###########################################################
    # WRONG: default [] is created ONCE and shared across all calls.
    def append_bad(item, bucket=[]):
        bucket.append(item)
        return bucket

    assert append_bad(1) == [1]
    assert append_bad(2) == [1, 2]   # surprise! state persisted

    # RIGHT: use None sentinel and create a fresh list inside.
    def append_good(item, bucket=None):
        if bucket is None:
            bucket = []
        bucket.append(item)
        return bucket

    assert append_good(1) == [1]
    assert append_good(2) == [2]     # independent each call

    ###########################################################
    # SCOPE: LEGB, global, nonlocal
    ###########################################################
    counter = 0

    def increment():
        nonlocal counter             # bind to the enclosing 'counter'
        counter += 1

    increment()
    increment()
    assert counter == 2

    # 'global' rebinds a MODULE-LEVEL name from inside a function.
    # (_GLOBAL_TOTAL and _add_to_global are defined at module scope above.)
    _add_to_global(5)
    _add_to_global(10)
    assert _GLOBAL_TOTAL == 15

    ###########################################################
    # FIRST-CLASS FUNCTIONS — functions are objects
    ###########################################################
    def shout(text):
        return text.upper()

    fn = shout                       # assign a function to a variable
    assert fn("hi") == "HI"
    funcs = [str.upper, str.lower]   # store functions in a list
    assert funcs[0]("Hi") == "HI"

    # Higher-order function: takes/returns a function
    def apply_twice(f, value):
        return f(f(value))

    assert apply_twice(lambda x: x + 3, 10) == 16

    ###########################################################
    # CLOSURES — inner function captures enclosing variables
    ###########################################################
    def make_multiplier(factor):
        def multiply(x):
            return x * factor        # 'factor' is captured (closed over)
        return multiply

    triple = make_multiplier(3)
    assert triple(10) == 30
    # Inspect the captured free variable
    assert triple.__closure__[0].cell_contents == 3

    # CLASSIC GOTCHA: late binding in closures inside a loop
    # WRONG: all lambdas share the SAME 'i' (evaluated at call time -> last value)
    bad = [lambda: i for i in range(3)]
    assert [f() for f in bad] == [2, 2, 2]
    # RIGHT: bind the current value via a default argument
    good = [lambda i=i: i for i in range(3)]
    assert [f() for f in good] == [0, 1, 2]

    ###########################################################
    # LAMBDA — small anonymous functions
    ###########################################################
    add = lambda a, b: a + b
    assert add(2, 3) == 5
    # Best used inline as a key function (not assigned to a name — use def then).
    words = ["ccc", "a", "bb"]
    assert sorted(words, key=lambda w: len(w)) == ["a", "bb", "ccc"]

    ###########################################################
    # DECORATORS — wrap a function to add behavior
    ###########################################################
    def logged(func):
        @functools.wraps(func)       # preserves __name__/__doc__ of func
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            wrapper.calls += 1        # attach state to the wrapper
            return result
        wrapper.calls = 0
        return wrapper

    @logged
    def square(n):
        """Return n squared."""
        return n * n

    assert square(4) == 16
    assert square(5) == 25
    assert square.calls == 2
    assert square.__name__ == "square"        # thanks to functools.wraps
    assert square.__doc__ == "Return n squared."

    ###########################################################
    # DECORATOR WITH ARGUMENTS — a decorator factory (3 nested levels)
    ###########################################################
    def repeat(times):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                result = None
                for _ in range(times):
                    result = func(*args, **kwargs)
                return result
            return wrapper
        return decorator

    calls = {"n": 0}

    @repeat(times=3)
    def ping():
        calls["n"] += 1
        return "pong"

    assert ping() == "pong"
    assert calls["n"] == 3            # body ran 3 times

    ###########################################################
    # RECURSION — and Python's recursion limit (no TCO!)
    ###########################################################
    def factorial(n):
        return 1 if n <= 1 else n * factorial(n - 1)

    assert factorial(5) == 120

    @functools.lru_cache(maxsize=None)   # memoize -> turns exponential into linear
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    assert fib(30) == 832040
    # NOTE: Python has NO tail-call optimization; deep recursion raises
    # RecursionError (default limit ~1000). Prefer iteration for deep loops.

    print("All 03_Functions assertions passed ✅")


if __name__ == "__main__":
    main()
