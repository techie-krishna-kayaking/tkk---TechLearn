"""
06_Exceptions_and_Context_Managers.py
================================================================================
Python Interview Handbook
Chapter 06: EXCEPTIONS & CONTEXT MANAGERS

Covered in this file
--------------------
* try / except / else / finally
* Catching multiple exception types
* Exception hierarchy & catching order
* raise, re-raise, exception chaining (raise ... from ...)
* Custom exception classes
* EAFP vs LBYL (Pythonic error philosophy)
* assert (and when NOT to use it)
* Context managers: the with statement
* Writing a context manager (class-based __enter__/__exit__)
* contextlib.contextmanager (generator-based)
* contextlib.suppress, closing, ExitStack

Run:
    python3 06_Exceptions_and_Context_Managers.py
================================================================================
"""

import contextlib


def main() -> None:
    ###########################################################
    # try / except / else / finally
    ###########################################################
    def safe_divide(a, b):
        try:
            result = a / b
        except ZeroDivisionError:
            return "cannot divide by zero"
        else:
            # runs ONLY if no exception was raised in try
            return result
        finally:
            # ALWAYS runs (cleanup) — success, exception, or return
            pass

    assert safe_divide(10, 2) == 5.0
    assert safe_divide(10, 0) == "cannot divide by zero"

    ###########################################################
    # CATCHING MULTIPLE EXCEPTION TYPES
    ###########################################################
    def parse_int(text):
        try:
            return int(text)
        except (ValueError, TypeError) as exc:   # tuple of types; bind to 'exc'
            return f"bad input: {type(exc).__name__}"

    assert parse_int("42") == 42
    assert parse_int("abc") == "bad input: ValueError"
    assert parse_int(None) == "bad input: TypeError"

    ###########################################################
    # EXCEPTION HIERARCHY & CATCHING ORDER
    ###########################################################
    # Catch MORE SPECIFIC exceptions BEFORE more general ones.
    def lookup(d, key):
        try:
            return d[key]
        except KeyError:                 # specific
            return "no such key"
        except Exception:                # general (catch-all) — comes last
            return "other error"

    assert lookup({"a": 1}, "a") == 1
    assert lookup({"a": 1}, "z") == "no such key"
    # NOTE: bare `except:` also catches SystemExit/KeyboardInterrupt — avoid it.

    ###########################################################
    # raise, RE-RAISE, and EXCEPTION CHAINING
    ###########################################################
    class ConfigError(Exception):
        """Raised when configuration is invalid."""

    def load_config(raw):
        try:
            return int(raw)
        except ValueError as exc:
            # Chain the original cause -> preserves the traceback context.
            raise ConfigError(f"invalid config: {raw!r}") from exc

    try:
        load_config("oops")
        raise AssertionError("should have raised")
    except ConfigError as exc:
        assert "invalid config" in str(exc)
        assert isinstance(exc.__cause__, ValueError)   # chained cause

    ###########################################################
    # CUSTOM EXCEPTION with extra data
    ###########################################################
    class ValidationError(Exception):
        def __init__(self, field, message):
            super().__init__(f"{field}: {message}")
            self.field = field
            self.message = message

    try:
        raise ValidationError("email", "is required")
    except ValidationError as exc:
        assert exc.field == "email"
        assert str(exc) == "email: is required"

    ###########################################################
    # EAFP vs LBYL — the Pythonic philosophy
    ###########################################################
    d = {"a": 1}
    # LBYL (Look Before You Leap) — check first
    lbyl = d["a"] if "a" in d else 0
    # EAFP (Easier to Ask Forgiveness than Permission) — try & handle (Pythonic)
    try:
        eafp = d["a"]
    except KeyError:
        eafp = 0
    assert lbyl == eafp == 1
    # EAFP avoids race conditions and is idiomatic in Python.

    ###########################################################
    # assert — sanity checks (NOT for user-facing validation!)
    ###########################################################
    def average(values):
        assert len(values) > 0, "values must be non-empty"   # internal invariant
        return sum(values) / len(values)

    assert average([2, 4]) == 3
    # WARNING: asserts are stripped when Python runs with -O. Never use them to
    # validate untrusted input or enforce security.

    ###########################################################
    # CONTEXT MANAGERS — the with statement (deterministic cleanup)
    ###########################################################
    # 'with' guarantees teardown even if an exception occurs.
    # File example (self-contained temp file):
    import tempfile
    import os

    path = os.path.join(tempfile.gettempdir(), "_handbook_ctx.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("hello")
        # file auto-closes at end of the block (even on exception)
    with open(path, encoding="utf-8") as f:
        assert f.read() == "hello"
    os.remove(path)

    ###########################################################
    # CLASS-BASED CONTEXT MANAGER (__enter__ / __exit__)
    ###########################################################
    class Timer:
        def __enter__(self):
            self.entered = True
            return self               # value bound to 'as'

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.exited = True
            # Return True to SUPPRESS an exception; False/None to propagate it.
            return False

    with Timer() as timer:
        assert timer.entered is True
    assert timer.exited is True

    # __exit__ receives exception info and can suppress it:
    class Suppressor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return exc_type is ValueError   # swallow ValueError only

    with Suppressor():
        raise ValueError("silenced")        # suppressed -> no error escapes
    # execution continues here

    ###########################################################
    # GENERATOR-BASED CONTEXT MANAGER (contextlib.contextmanager)
    ###########################################################
    @contextlib.contextmanager
    def tag(name):
        # code before yield == __enter__; after yield == __exit__
        opened.append(f"<{name}>")
        try:
            yield name
        finally:
            opened.append(f"</{name}>")

    opened = []
    with tag("b") as t:
        assert t == "b"
        opened.append("content")
    assert opened == ["<b>", "content", "</b>"]

    ###########################################################
    # contextlib helpers: suppress, closing, ExitStack
    ###########################################################
    # suppress — swallow specified exceptions concisely
    with contextlib.suppress(ZeroDivisionError):
        _ = 1 / 0                    # ignored
    # ExitStack — manage a dynamic number of context managers
    with contextlib.ExitStack() as stack:
        managers = [stack.enter_context(tag(x)) for x in ("x", "y")]
        assert managers == ["x", "y"]

    print("All 06_Exceptions_and_Context_Managers assertions passed ✅")


if __name__ == "__main__":
    main()
