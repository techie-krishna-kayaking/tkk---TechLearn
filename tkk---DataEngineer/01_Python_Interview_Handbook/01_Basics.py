"""
01_Basics.py
================================================================================
Python Interview Handbook
Chapter 01: BASICS

Covered in this file
--------------------
* Variables & dynamic typing
* Numeric types (int, float, complex), integer division, overflow-free ints
* Booleans & truthiness
* Strings: creation, indexing, slicing, immutability, f-strings, methods
* None & the identity operator (is vs ==)
* Type conversion / casting
* Operators: arithmetic, comparison, logical, bitwise, membership, identity
* Control flow: if/elif/else, ternary, for/while, break/continue/else, match
* Input / output (print, formatting)

Running this file prints results and asserts documented behavior.

Run:
    python3 01_Basics.py
================================================================================
"""


def main() -> None:
    ###########################################################
    # VARIABLES & DYNAMIC TYPING
    ###########################################################
    # Python is dynamically typed: a name is just a label bound to an object.
    x = 10          # int
    x = "ten"       # now bound to a str — perfectly legal
    assert isinstance(x, str)
    # Variable annotations are hints only; they are NOT enforced at runtime.
    age: int = 30
    assert age == 30

    ###########################################################
    # NUMERIC TYPES
    ###########################################################
    i = 7
    f = 3.5
    c = 2 + 3j                       # complex literal
    assert i / 2 == 3.5              # true division always returns float
    assert i // 2 == 3               # floor division
    assert i % 2 == 1                # modulo
    assert 2 ** 10 == 1024           # exponent
    assert c.real == 2 and c.imag == 3
    # Python ints are arbitrary precision (no overflow) — a classic interview point.
    assert 2 ** 100 == 1267650600228229401496703205376
    # Float precision gotcha:
    assert 0.1 + 0.2 != 0.3          # binary float rounding!
    assert round(0.1 + 0.2, 10) == 0.3

    ###########################################################
    # BOOLEANS & TRUTHINESS
    ###########################################################
    # bool is a subclass of int: True == 1, False == 0.
    assert True + True == 2
    # "Falsy" values: 0, 0.0, '', [], {}, set(), None, False.
    falsy = [0, 0.0, "", [], {}, set(), None, False]
    assert all(not bool(v) for v in falsy)
    assert bool("anything") and bool([0])   # non-empty is truthy

    ###########################################################
    # STRINGS — immutability, indexing, slicing
    ###########################################################
    s = "Python"
    assert s[0] == "P"               # index
    assert s[-1] == "n"              # negative index
    assert s[0:3] == "Pyt"           # slice [start:stop)
    assert s[::-1] == "nohtyP"       # reverse via slice (interview favorite)
    assert s[::2] == "Pto"           # step
    # Strings are IMMUTABLE — you cannot do s[0] = 'J'; build a new string instead.
    s2 = "J" + s[1:]
    assert s2 == "Jython"

    ###########################################################
    # STRING FORMATTING — prefer f-strings
    ###########################################################
    name, score = "Ada", 95.5
    # Non-Pythonic (older styles)
    old1 = "%s scored %.1f" % (name, score)
    old2 = "{} scored {:.1f}".format(name, score)
    # Pythonic (f-string, Python 3.6+)
    new = f"{name} scored {score:.1f}"
    assert old1 == old2 == new == "Ada scored 95.5"
    # f-string debugging shortcut (3.8+): '=' prints "expr=value"
    debug = f"{score=}"
    assert debug == "score=95.5"

    ###########################################################
    # COMMON STRING METHODS
    ###########################################################
    assert "  hi  ".strip() == "hi"
    assert "a,b,c".split(",") == ["a", "b", "c"]
    assert "-".join(["a", "b", "c"]) == "a-b-c"
    assert "Hello".upper() == "HELLO" and "Hello".lower() == "hello"
    assert "hello world".title() == "Hello World"
    assert "abcabc".replace("a", "X") == "XbcXbc"
    assert "hello".startswith("he") and "hello".endswith("lo")
    assert "hello".find("l") == 2 and "hello".index("l") == 2
    assert "42".isdigit() and "abc".isalpha() and "abc123".isalnum()
    assert "Hello".count("l") == 2

    ###########################################################
    # None & IDENTITY (is vs ==)
    ###########################################################
    # 'is' compares IDENTITY (same object); '==' compares VALUE.
    a = None
    assert a is None                 # ALWAYS use 'is' for None
    x1 = [1, 2, 3]
    x2 = [1, 2, 3]
    assert x1 == x2                  # equal values
    assert x1 is not x2              # different objects
    # CPython caches small ints (-5..256) — an implementation detail, not a rule:
    p = 256
    q = 256
    assert p is q                    # cached (do NOT rely on this in code)

    ###########################################################
    # TYPE CONVERSION / CASTING
    ###########################################################
    assert int("42") == 42
    assert int("101", 2) == 5        # base-2 parse
    assert float("3.14") == 3.14
    assert str(42) == "42"
    assert list("abc") == ["a", "b", "c"]
    assert set([1, 1, 2]) == {1, 2}
    assert tuple([1, 2]) == (1, 2)
    assert bool(0) is False

    ###########################################################
    # OPERATORS — bitwise, membership, identity, walrus
    ###########################################################
    assert 5 & 3 == 1                # AND
    assert 5 | 2 == 7                # OR
    assert 5 ^ 1 == 4                # XOR
    assert ~5 == -6                  # NOT (two's complement)
    assert 1 << 4 == 16             # left shift
    assert 32 >> 2 == 8             # right shift
    assert "y" in "Python"          # membership
    assert 3 not in [1, 2]
    # Walrus operator := (3.8+) assigns within an expression.
    if (n := len("hello")) > 3:
        assert n == 5

    ###########################################################
    # CHAINED COMPARISON (Pythonic)
    ###########################################################
    y = 5
    # Non-Pythonic
    assert (0 < y) and (y < 10)
    # Pythonic — chained comparison
    assert 0 < y < 10

    ###########################################################
    # CONTROL FLOW: if / elif / else + ternary
    ###########################################################
    def classify(num: int) -> str:
        if num > 0:
            return "positive"
        elif num < 0:
            return "negative"
        return "zero"

    assert classify(3) == "positive"
    assert classify(-1) == "negative"
    assert classify(0) == "zero"
    # Ternary expression
    label = "even" if 10 % 2 == 0 else "odd"
    assert label == "even"

    ###########################################################
    # LOOPS: for, while, range, enumerate, zip
    ###########################################################
    total = 0
    for k in range(1, 6):            # 1..5
        total += k
    assert total == 15

    # enumerate — Pythonic index+value (avoid range(len(...)))
    letters = ["a", "b", "c"]
    # Non-Pythonic
    pairs = []
    for idx in range(len(letters)):
        pairs.append((idx, letters[idx]))
    # Pythonic
    pairs2 = list(enumerate(letters))
    assert pairs == pairs2 == [(0, "a"), (1, "b"), (2, "c")]

    # zip — iterate multiple sequences together
    names = ["Ada", "Alan"]
    scores = [95, 88]
    assert list(zip(names, scores)) == [("Ada", 95), ("Alan", 88)]

    ###########################################################
    # LOOP else + break/continue
    ###########################################################
    # The for/while 'else' runs only if the loop was NOT broken.
    def is_prime(num: int) -> bool:
        if num < 2:
            return False
        for d in range(2, int(num ** 0.5) + 1):
            if num % d == 0:
                return False          # break out of "primeness"
        else:
            return True               # loop completed without finding a divisor
        return True

    assert is_prime(7) and not is_prime(8)

    ###########################################################
    # MATCH STATEMENT (structural pattern matching, 3.10+)
    ###########################################################
    def http_label(code: int) -> str:
        match code:
            case 200:
                return "OK"
            case 404:
                return "Not Found"
            case 500 | 502 | 503:     # OR pattern
                return "Server Error"
            case _:                   # wildcard (default)
                return "Unknown"

    assert http_label(200) == "OK"
    assert http_label(503) == "Server Error"
    assert http_label(999) == "Unknown"

    ###########################################################
    # OUTPUT / print options
    ###########################################################
    print("=== 01_Basics demo ===")
    print("comma", "separated", sep=" | ")          # custom separator
    print("no newline...", end=" ")                  # custom end
    print("continued on same line")
    print(f"2**100 has {len(str(2 ** 100))} digits")

    print("\nAll 01_Basics assertions passed ✅")


if __name__ == "__main__":
    main()
