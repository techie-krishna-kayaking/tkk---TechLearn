"""
12_Interview_Questions.py
================================================================================
Python Interview Handbook
Chapter 12: 150+ INTERVIEW QUESTIONS

Structure
---------
1. QUESTIONS : a curated bank of 150+ Q&A entries. Each entry has:
       q       -> the question
       a       -> the answer / explanation
       example -> a short code snippet illustrating the answer
       best    -> best practice
       mistake -> common mistake to avoid
   Running this file PRINTS the whole bank as a study guide.

2. LIVE_DEMOS : a set of the most important questions executed for real, so you
   can see the actual output.

Run:
    python3 12_Interview_Questions.py            # prints Q&A bank + runs live demos
    python3 12_Interview_Questions.py --qa-only  # only prints the Q&A bank
================================================================================
"""

import sys


# =============================================================================
# 1) THE QUESTION BANK (150+)
# =============================================================================
QUESTIONS = [
    # ------------------------------- Language core ---------------------------
    {
        "q": "Is Python compiled or interpreted?",
        "a": "Both: CPython compiles source to bytecode (.pyc), then the interpreter (a "
             "virtual machine) executes that bytecode.",
        "example": "import dis; dis.dis(lambda x: x+1)",
        "best": "Ship source; let CPython cache bytecode in __pycache__.",
        "mistake": "Calling Python 'purely interpreted' in an interview.",
    },
    {
        "q": "What is the difference between is and ==?",
        "a": "'is' compares identity (same object in memory); '==' compares value (calls "
             "__eq__).",
        "example": "a=[1]; b=[1]; a==b  # True; a is b  # False",
        "best": "Use 'is' only for None/True/False/sentinels; '==' for values.",
        "mistake": "Using 'is' to compare strings/ints (works by luck via interning).",
    },
    {
        "q": "Mutable vs immutable types?",
        "a": "Immutable: int, float, str, tuple, frozenset, bytes. Mutable: list, dict, "
             "set, bytearray. Immutables are hashable and safe as dict keys.",
        "example": "s='hi'; s[0]='H'  # TypeError (immutable)",
        "best": "Use immutable keys; return new objects instead of mutating.",
        "mistake": "Trying to mutate a string/tuple in place.",
    },
    {
        "q": "Explain Python's dynamic typing.",
        "a": "Types belong to objects, not variables. A name can be rebound to any type; "
             "type checks happen at runtime.",
        "example": "x=1; x='now a string'",
        "best": "Use type hints + mypy for large codebases.",
        "mistake": "Assuming annotations are enforced at runtime.",
    },
    {
        "q": "What are Python's numeric types and integer precision?",
        "a": "int (arbitrary precision), float (double), complex. Ints never overflow.",
        "example": "2**100  # exact big integer",
        "best": "Use decimal.Decimal for money (avoid float rounding).",
        "mistake": "Using float for currency and hitting 0.1+0.2 != 0.3.",
    },
    {
        "q": "How does Python manage memory?",
        "a": "Reference counting frees objects at refcount 0; a cyclic garbage collector "
             "handles reference cycles. Memory is managed by CPython's allocator.",
        "example": "import sys; sys.getrefcount(obj)",
        "best": "Break cycles or use weakref for caches/observers.",
        "mistake": "Assuming del frees memory immediately in all cases (cycles).",
    },
    {
        "q": "What is the GIL and why does it matter?",
        "a": "Global Interpreter Lock: only one thread runs Python bytecode at a time in "
             "CPython. Threads help I/O-bound but not CPU-bound work.",
        "example": "# CPU-bound -> multiprocessing; I/O-bound -> threading/asyncio",
        "best": "multiprocessing for CPU parallelism; asyncio/threads for I/O.",
        "mistake": "Using threads to speed up CPU-bound code.",
    },
    {
        "q": "Difference between deep copy and shallow copy?",
        "a": "Shallow copies the outer container but shares inner objects; deep recursively "
             "copies everything.",
        "example": "import copy; copy.deepcopy(nested)",
        "best": "deepcopy only when nested mutation must be isolated.",
        "mistake": "Shallow-copying a nested list then mutating an inner list.",
    },
    {
        "q": "What does the walrus operator := do?",
        "a": "Assignment expression (3.8+): assigns AND returns a value inside an "
             "expression.",
        "example": "while (line := f.readline()): ...",
        "best": "Use to avoid computing/reading a value twice.",
        "mistake": "Overusing it and hurting readability.",
    },
    {
        "q": "What are *args and **kwargs?",
        "a": "*args collects extra positional args into a tuple; **kwargs collects extra "
             "keyword args into a dict.",
        "example": "def f(*args, **kwargs): ...",
        "best": "Use for flexible APIs and forwarding arguments.",
        "mistake": "Confusing definition-site (* collects) vs call-site (* unpacks).",
    },

    # ------------------------------- Data model ------------------------------
    {
        "q": "The mutable default argument trap?",
        "a": "Default values are evaluated ONCE at definition, so a mutable default (e.g. "
             "[]) is shared across calls.",
        "example": "def f(x, acc=[]): acc.append(x); return acc  # accumulates!",
        "best": "Use None sentinel: def f(x, acc=None): acc = acc or []",
        "mistake": "Using [] or {} as a default parameter value.",
    },
    {
        "q": "How do list comprehensions differ from generator expressions?",
        "a": "List comp builds the whole list in memory ([...]); genexp is lazy ((...)) and "
             "yields one item at a time.",
        "example": "sum(x*x for x in range(10**6))  # low memory",
        "best": "Use genexp when iterating once / over large data.",
        "mistake": "Building a giant list just to iterate it once.",
    },
    {
        "q": "What are __str__ and __repr__?",
        "a": "__str__ is the readable/user form (str/print); __repr__ is the unambiguous/"
             "developer form (repr/debug). repr should ideally be eval-able.",
        "example": "def __repr__(self): return f'Point({self.x},{self.y})'",
        "best": "Always define __repr__; define __str__ for user output.",
        "mistake": "Only defining __str__ and getting ugly debug output.",
    },
    {
        "q": "How do you make an object hashable?",
        "a": "Define __hash__ and __eq__ consistently (equal objects must have equal "
             "hashes). Immutability recommended.",
        "example": "def __hash__(self): return hash((self.x, self.y))",
        "best": "Base hash & eq on the same immutable fields.",
        "mistake": "Defining __eq__ without __hash__ (makes it unhashable).",
    },
    {
        "q": "What are dunder (magic) methods?",
        "a": "Special methods (__init__, __len__, __getitem__, __add__, __iter__, ...) that "
             "let objects integrate with built-in syntax/operators.",
        "example": "def __len__(self): return len(self.items)",
        "best": "Implement the protocol methods your type logically supports.",
        "mistake": "Reinventing operators instead of implementing dunders.",
    },
    {
        "q": "Difference between __new__ and __init__?",
        "a": "__new__ creates & returns the instance (allocation); __init__ initializes an "
             "already-created instance. __new__ matters for immutables/singletons.",
        "example": "def __new__(cls): return super().__new__(cls)",
        "best": "Override __new__ only for immutables/metaclass/singletons.",
        "mistake": "Trying to set state in __new__ instead of __init__.",
    },
    {
        "q": "What is duck typing?",
        "a": "An object's suitability is determined by the methods/attributes it has, not "
             "its type. 'If it quacks like a duck...'",
        "example": "def total(x): return sum(x)  # any iterable of numbers",
        "best": "Program to behavior/protocols, not concrete classes.",
        "mistake": "Excessive isinstance checks instead of relying on protocols.",
    },
    {
        "q": "What is monkey patching?",
        "a": "Modifying a class/module at runtime (e.g. replacing a method).",
        "example": "SomeClass.method = new_method",
        "best": "Use for testing/mocking; document heavily.",
        "mistake": "Patching third-party internals in production.",
    },
    {
        "q": "What are metaclasses?",
        "a": "The class of a class. type is the default metaclass. Customize class creation "
             "(validation, registration) via metaclass=...",
        "example": "class Meta(type): ...",
        "best": "Prefer class decorators / __init_subclass__ unless you truly need a metaclass.",
        "mistake": "Reaching for metaclasses when a decorator suffices.",
    },
    {
        "q": "What are descriptors?",
        "a": "Objects implementing __get__/__set__/__delete__ that control attribute access. "
             "@property, methods, classmethod are descriptors.",
        "example": "class D: def __get__(self, obj, t): return 42",
        "best": "Use descriptors to reuse attribute logic across classes.",
        "mistake": "Duplicating validation in every property instead of a descriptor.",
    },
    {
        "q": "What is __slots__?",
        "a": "A class attribute restricting instance attributes to a fixed set; removes the "
             "per-instance __dict__, saving memory.",
        "example": "class P: __slots__=('x','y')",
        "best": "Use for many small objects to cut memory.",
        "mistake": "Expecting to add arbitrary attributes to a slotted class.",
    },

    # ------------------------------- Functions -------------------------------
    {
        "q": "What is a closure?",
        "a": "A nested function that captures variables from its enclosing scope, which "
             "outlive the enclosing call.",
        "example": "def outer(n): return lambda x: x+n",
        "best": "Use for factories/decorators/callbacks.",
        "mistake": "Late-binding loop closures capturing the final value.",
    },
    {
        "q": "Late binding closure bug in loops — how to fix?",
        "a": "Closures capture the variable, not its value; by call time the loop variable "
             "holds its last value. Bind via a default arg or functools.partial.",
        "example": "[lambda i=i: i for i in range(3)]",
        "best": "Capture current value with a default argument.",
        "mistake": "[lambda: i for i in range(3)] -> all return 2.",
    },
    {
        "q": "What is a decorator?",
        "a": "A callable that takes a function and returns a modified function, applied with "
             "@syntax to add behavior (logging, caching, auth).",
        "example": "@functools.lru_cache\ndef f(n): ...",
        "best": "Use functools.wraps to preserve metadata.",
        "mistake": "Forgetting @wraps -> lost __name__/__doc__.",
    },
    {
        "q": "How do you write a decorator that takes arguments?",
        "a": "A three-level nested function: outer(args) -> decorator(func) -> wrapper(*a,**k).",
        "example": "def repeat(n): def d(f): def w(*a): ...",
        "best": "Keep the wrapper signature generic (*args, **kwargs).",
        "mistake": "Confusing decorator-with-args vs plain decorator nesting.",
    },
    {
        "q": "What does functools.wraps do?",
        "a": "Copies __name__, __doc__, __wrapped__ etc. from the wrapped function onto the "
             "wrapper so introspection still works.",
        "example": "@functools.wraps(func)\ndef wrapper(...): ...",
        "best": "Always apply @wraps in decorators.",
        "mistake": "Omitting it and breaking help()/debuggers.",
    },
    {
        "q": "What is functools.lru_cache?",
        "a": "A memoization decorator caching results by arguments; speeds up pure, "
             "repeated calls.",
        "example": "@lru_cache(maxsize=None)\ndef fib(n): ...",
        "best": "Cache pure functions with hashable args.",
        "mistake": "Caching functions with side effects or unhashable args.",
    },
    {
        "q": "What is functools.partial?",
        "a": "Creates a new callable with some arguments pre-filled (partial application).",
        "example": "int2 = partial(int, base=2)",
        "best": "Use to specialize general functions for callbacks.",
        "mistake": "Rewriting wrapper lambdas where partial is cleaner.",
    },
    {
        "q": "Positional-only and keyword-only parameters?",
        "a": "'/' marks preceding params positional-only; '*' marks following params "
             "keyword-only.",
        "example": "def f(a, /, b, *, c): ...",
        "best": "Use keyword-only for optional flags to improve call clarity.",
        "mistake": "Relying on positional order for boolean flags.",
    },
    {
        "q": "Difference between a function and a method?",
        "a": "A method is a function bound to an instance/class; it receives self/cls "
             "automatically.",
        "example": "obj.method()  # passes obj as self",
        "best": "Use @staticmethod when you need neither self nor cls.",
        "mistake": "Forgetting self as the first parameter of an instance method.",
    },
    {
        "q": "What is the difference between return and yield?",
        "a": "return exits and returns once; yield pauses the function, producing a "
             "generator that resumes on next().",
        "example": "def gen(): yield 1; yield 2",
        "best": "yield for lazy streams; return for single results.",
        "mistake": "Building a list when a generator would stream lazily.",
    },

    # ------------------------------ Data structures --------------------------
    {
        "q": "list vs tuple — when to use each?",
        "a": "list: mutable, variable-length collections. tuple: immutable, fixed records; "
             "hashable so usable as keys.",
        "example": "point = (x, y)  # fixed record",
        "best": "Tuples for heterogeneous records; lists for homogeneous sequences.",
        "mistake": "Using a list as a dict key (unhashable).",
    },
    {
        "q": "How is a dict implemented and why is lookup O(1)?",
        "a": "An open-addressing hash table: keys are hashed to buckets, giving average "
             "O(1) get/set (O(n) worst case with collisions).",
        "example": "d = {}; d[key] = value",
        "best": "Use dict/set for membership tests instead of scanning a list.",
        "mistake": "Using 'x in list' (O(n)) in a hot loop.",
    },
    {
        "q": "Are dicts ordered?",
        "a": "Yes — insertion order is preserved since Python 3.7 (guaranteed language "
             "feature).",
        "example": "list({'a':1,'b':2})  # ['a','b']",
        "best": "Rely on insertion order; use OrderedDict for move_to_end/reordering.",
        "mistake": "Assuming dict ordering on Python < 3.7.",
    },
    {
        "q": "How do you merge two dicts?",
        "a": "{**a, **b} (3.5+) or a | b (3.9+); later keys win.",
        "example": "merged = a | b",
        "best": "Use | for readability on 3.9+.",
        "mistake": "Expecting the first dict's value to win on key collision.",
    },
    {
        "q": "set vs frozenset?",
        "a": "set is mutable/unhashable; frozenset is immutable/hashable (usable as a key "
             "or set member).",
        "example": "cache = {frozenset({1,2}): 'x'}",
        "best": "frozenset for hashable set values.",
        "mistake": "Trying to put a mutable set inside another set.",
    },
    {
        "q": "How do you remove duplicates but keep order?",
        "a": "dict.fromkeys(seq) preserves first-seen order; set() does not.",
        "example": "list(dict.fromkeys([1,2,1,3]))  # [1,2,3]",
        "best": "dict.fromkeys for order-preserving dedup.",
        "mistake": "Using set() when order must be preserved.",
    },
    {
        "q": "What is collections.defaultdict?",
        "a": "A dict that auto-creates a default value (via a factory) for missing keys.",
        "example": "defaultdict(list)",
        "best": "Use for grouping/counting without key checks.",
        "mistake": "Accessing a missing key on a plain dict -> KeyError.",
    },
    {
        "q": "What is collections.Counter?",
        "a": "A dict subclass for counting hashable items, with most_common and arithmetic.",
        "example": "Counter('banana').most_common(1)",
        "best": "Use for frequency/histogram problems.",
        "mistake": "Hand-rolling counts with dict.get in a loop.",
    },
    {
        "q": "When would you use collections.deque?",
        "a": "For O(1) appends/pops at both ends (queues, sliding windows, BFS).",
        "example": "deque(maxlen=3)  # ring buffer",
        "best": "deque for FIFO queues; list.pop(0) is O(n).",
        "mistake": "Using list as a queue with pop(0).",
    },
    {
        "q": "Why does [[0]*3]*3 misbehave?",
        "a": "The outer * duplicates the SAME inner list reference, so all rows are the same "
             "object.",
        "example": "[[0]*3 for _ in range(3)]  # correct",
        "best": "Build nested lists with a comprehension.",
        "mistake": "[[0]*3]*3 then mutating one row changes all.",
    },
    {
        "q": "How do you sort a list of dicts by a key?",
        "a": "sorted(data, key=itemgetter('field')) or a lambda.",
        "example": "sorted(users, key=lambda u: u['age'])",
        "best": "operator.itemgetter is faster/clearer than a lambda.",
        "mistake": "Calling list.sort() and expecting a returned list.",
    },
    {
        "q": "Is Python's sort stable?",
        "a": "Yes — Timsort is stable, so equal elements keep their relative order (enables "
             "multi-pass sorting).",
        "example": "sorted(data, key=lambda x:(-x.score, x.name))",
        "best": "Sort by least-significant key first when chaining passes.",
        "mistake": "Assuming instability and adding tie-breakers unnecessarily.",
    },

    # ------------------------------ Strings ----------------------------------
    {
        "q": "Why are strings immutable and why does concatenation in a loop hurt?",
        "a": "Each += builds a new string (O(n) each) -> O(n^2) overall.",
        "example": "''.join(parts)  # O(n)",
        "best": "Build a list and ''.join() it once.",
        "mistake": "s += x inside a big loop.",
    },
    {
        "q": "f-string vs .format vs %?",
        "a": "f-strings (3.6+) are fastest and most readable; .format is flexible; % is "
             "legacy.",
        "example": "f'{name}: {value:.2f}'",
        "best": "Prefer f-strings.",
        "mistake": "Using % formatting in new code.",
    },
    {
        "q": "How do you reverse a string?",
        "a": "Slicing with a -1 step.",
        "example": "s[::-1]",
        "best": "s[::-1] is idiomatic and fast.",
        "mistake": "Manual loops or reversed()+join when slicing suffices.",
    },
    {
        "q": "str.split() vs str.split(' ')?",
        "a": "split() with no args splits on any run of whitespace and drops empties; "
             "split(' ') splits on single spaces (keeps empties).",
        "example": "'a  b'.split()  # ['a','b']",
        "best": "Use bare split() to normalize whitespace.",
        "mistake": "split(' ') producing empty strings from double spaces.",
    },
    {
        "q": "encode vs decode / str vs bytes?",
        "a": "str is Unicode text; bytes is raw bytes. encode: str->bytes; decode: "
             "bytes->str, both with a codec (usually utf-8).",
        "example": "'é'.encode('utf-8')",
        "best": "Decode at input, work in str, encode at output.",
        "mistake": "Mixing str and bytes -> TypeError.",
    },

    # ------------------------------ Iterators/gen ----------------------------
    {
        "q": "Iterable vs iterator?",
        "a": "Iterable has __iter__ (can make an iterator); iterator has __next__ (produces "
             "values, raises StopIteration).",
        "example": "it = iter([1,2]); next(it)",
        "best": "Implement __iter__ returning a fresh iterator for reusable iterables.",
        "mistake": "Making a one-shot iterable that can't be re-iterated.",
    },
    {
        "q": "What are generators good for?",
        "a": "Lazy, memory-efficient sequences and pipelines; represent infinite streams.",
        "example": "def naturals(): n=1; while True: yield n; n+=1",
        "best": "Stream large data instead of materializing lists.",
        "mistake": "Reusing an exhausted generator (yields nothing).",
    },
    {
        "q": "What does yield from do?",
        "a": "Delegates iteration to a sub-iterator/sub-generator, forwarding values (and "
             "send/throw).",
        "example": "def flat(xs): for x in xs: yield from x",
        "best": "Use for recursive/nested generators.",
        "mistake": "Manually looping to re-yield when yield from is cleaner.",
    },
    {
        "q": "How do you get the first N items of an infinite generator?",
        "a": "itertools.islice(gen, N).",
        "example": "list(islice(count(), 5))",
        "best": "islice for lazy slicing without materializing.",
        "mistake": "list(infinite_gen) -> hangs / OOM.",
    },

    # ------------------------------ Exceptions -------------------------------
    {
        "q": "EAFP vs LBYL?",
        "a": "EAFP (try/except) is the Pythonic default and avoids race conditions; LBYL "
             "checks conditions first.",
        "example": "try: d[k] except KeyError: ...",
        "best": "Prefer EAFP for attribute/key/file access.",
        "mistake": "Checking then acting (TOCTOU races).",
    },
    {
        "q": "try/except/else/finally — what runs when?",
        "a": "try runs; except on error; else if NO error; finally ALWAYS (cleanup).",
        "example": "try:... except:... else:... finally:...",
        "best": "Put cleanup in finally; success-only code in else.",
        "mistake": "Cleanup only in try -> skipped on exception.",
    },
    {
        "q": "Why avoid a bare except:?",
        "a": "It also catches SystemExit/KeyboardInterrupt and hides bugs. Catch specific "
             "exceptions (or at least Exception).",
        "example": "except (ValueError, KeyError): ...",
        "best": "Catch the narrowest exception you can handle.",
        "mistake": "except: pass swallowing everything silently.",
    },
    {
        "q": "What is exception chaining (raise ... from ...)?",
        "a": "Preserves the original cause (__cause__) while raising a new exception, "
             "keeping context in the traceback.",
        "example": "raise ConfigError(...) from exc",
        "best": "Chain to a domain exception at boundaries.",
        "mistake": "Swallowing the original cause and losing the traceback.",
    },
    {
        "q": "When should you use assert?",
        "a": "For internal invariants/sanity checks during development — NOT for validating "
             "user input (stripped under -O).",
        "example": "assert n >= 0",
        "best": "Validate untrusted input with explicit raises.",
        "mistake": "Using assert for security/validation in production.",
    },

    # ---------------------------- Context managers ---------------------------
    {
        "q": "What does the with statement do?",
        "a": "Runs a context manager: __enter__ on entry, __exit__ on exit (even on "
             "exception) -> deterministic cleanup.",
        "example": "with open(p) as f: ...",
        "best": "Use with for files/locks/connections.",
        "mistake": "Manually open/close and leaking resources on error.",
    },
    {
        "q": "How do you write a context manager?",
        "a": "Class with __enter__/__exit__, or a generator decorated with "
             "@contextlib.contextmanager (yield splits enter/exit).",
        "example": "@contextmanager\ndef ctx(): yield res",
        "best": "Use contextmanager for simple setup/teardown.",
        "mistake": "Forgetting try/finally around yield in a contextmanager.",
    },
    {
        "q": "How does __exit__ suppress exceptions?",
        "a": "Return True from __exit__ to swallow the exception; False/None propagates it.",
        "example": "def __exit__(self, et, ev, tb): return et is ValueError",
        "best": "Only suppress exceptions you intend to.",
        "mistake": "Accidentally returning True and hiding errors.",
    },

    # ---------------------------- OOP ----------------------------------------
    {
        "q": "Explain the four OOP pillars in Python.",
        "a": "Encapsulation (conventions/properties), Inheritance (super), Polymorphism "
             "(duck typing/overriding), Abstraction (ABCs).",
        "example": "class Dog(Animal): def speak(self): ...",
        "best": "Prefer composition over deep inheritance.",
        "mistake": "Deep inheritance hierarchies that are hard to change.",
    },
    {
        "q": "instance vs class vs static method?",
        "a": "instance (self) accesses instance state; classmethod (cls) is an alt "
             "constructor/class state; staticmethod is a namespaced plain function.",
        "example": "@classmethod def from_str(cls, s): ...",
        "best": "classmethod for alternative constructors.",
        "mistake": "Using staticmethod when you actually need cls/self.",
    },
    {
        "q": "What is the MRO?",
        "a": "Method Resolution Order — the C3-linearized order Python searches base classes "
             "for attributes (Class.__mro__).",
        "example": "D.__mro__",
        "best": "Use super() cooperatively so the MRO chain runs once.",
        "mistake": "Calling Base.__init__ directly, breaking cooperative super().",
    },
    {
        "q": "What does super() do?",
        "a": "Returns a proxy delegating to the next class in the MRO — enables cooperative "
             "multiple inheritance.",
        "example": "super().__init__(...)",
        "best": "Always use super() (no explicit parent names).",
        "mistake": "Hardcoding the parent class name in multiple inheritance.",
    },
    {
        "q": "Name mangling: what does __name (double underscore) do?",
        "a": "Attributes prefixed with __ (no trailing __) are renamed _ClassName__name to "
             "avoid subclass clashes.",
        "example": "self.__x -> self._Cls__x",
        "best": "Use single _ for 'protected'; __ only to avoid subclass collisions.",
        "mistake": "Expecting __x to be truly private/inaccessible.",
    },
    {
        "q": "What is a property?",
        "a": "A descriptor letting a method be accessed like an attribute, with getter/"
             "setter/deleter for validation or computed values.",
        "example": "@property def area(self): ...",
        "best": "Expose attributes directly; add @property only when logic is needed.",
        "mistake": "Writing Java-style getX()/setX() instead of properties.",
    },
    {
        "q": "What are dataclasses?",
        "a": "A decorator (3.7+) that auto-generates __init__/__repr__/__eq__ (and ordering/"
             "frozen) from annotated fields.",
        "example": "@dataclass\nclass P: x:int; y:int",
        "best": "Use for simple data containers; field(default_factory=list) for mutables.",
        "mistake": "Using a plain mutable default in a dataclass field.",
    },
    {
        "q": "Composition vs inheritance?",
        "a": "Inheritance models 'is-a'; composition models 'has-a'. Composition is more "
             "flexible and avoids fragile base classes.",
        "example": "class Car: def __init__(self): self.engine = Engine()",
        "best": "Favor composition; inherit for genuine subtype relationships.",
        "mistake": "Inheriting just to reuse code (leads to tight coupling).",
    },

    # ---------------------------- Concurrency --------------------------------
    {
        "q": "Threading vs multiprocessing vs asyncio — when to use each?",
        "a": "I/O-bound: threading or asyncio. CPU-bound: multiprocessing. asyncio for "
             "massive concurrent I/O on one thread.",
        "example": "ProcessPoolExecutor for CPU work",
        "best": "Match the model to the workload (I/O vs CPU).",
        "mistake": "Threads for CPU-bound work (GIL blocks parallelism).",
    },
    {
        "q": "What is a race condition and how do you prevent it?",
        "a": "Two threads interleave on shared mutable state, corrupting it. Prevent with "
             "locks/atomic ops/immutable data/queues.",
        "example": "with lock: counter += 1",
        "best": "Guard shared mutable state with a Lock (or avoid sharing).",
        "mistake": "Assuming += is atomic across threads.",
    },
    {
        "q": "What is a deadlock?",
        "a": "Threads each hold a lock the other needs, so none proceed.",
        "example": "# acquire locks in a consistent global order",
        "best": "Acquire multiple locks in a fixed order; use timeouts.",
        "mistake": "Nested locks acquired in inconsistent orders.",
    },
    {
        "q": "What is async/await?",
        "a": "Coroutine syntax: async def defines a coroutine; await suspends it, yielding "
             "control to the event loop until the awaited result is ready.",
        "example": "await asyncio.gather(a(), b())",
        "best": "await I/O; use asyncio.gather for concurrency.",
        "mistake": "Calling blocking (sync) code inside a coroutine.",
    },
    {
        "q": "Why doesn't asyncio speed up CPU-bound code?",
        "a": "It's single-threaded cooperative concurrency; CPU work blocks the event loop. "
             "Offload to a process pool.",
        "example": "await loop.run_in_executor(pool, cpu_fn)",
        "best": "run_in_executor(ProcessPool) for CPU-bound work.",
        "mistake": "Doing heavy computation directly in a coroutine.",
    },
    {
        "q": "concurrent.futures vs raw threads/processes?",
        "a": "Executors (ThreadPoolExecutor/ProcessPoolExecutor) provide a high-level, "
             "uniform pool + Future API — less boilerplate.",
        "example": "with ThreadPoolExecutor() as ex: ex.map(f, items)",
        "best": "Prefer executors over manual thread/process management.",
        "mistake": "Manually managing thread lifecycles unnecessarily.",
    },

    # ------------------------------- Modules ---------------------------------
    {
        "q": "What is the if __name__ == '__main__' guard?",
        "a": "Runs code only when the file is executed directly, not when imported. Required "
             "for multiprocessing on spawn platforms.",
        "example": "if __name__=='__main__': main()",
        "best": "Wrap script entry points in it.",
        "mistake": "Top-level side effects that run on import.",
    },
    {
        "q": "Module vs package?",
        "a": "A module is a .py file; a package is a directory of modules (historically with "
             "__init__.py).",
        "example": "from pkg.mod import func",
        "best": "Organize related modules into packages.",
        "mistake": "Circular imports between modules.",
    },
    {
        "q": "How does Python import system caching work?",
        "a": "Imported modules are cached in sys.modules; re-import returns the cached module "
             "(use importlib.reload to force).",
        "example": "import sys; sys.modules['x']",
        "best": "Rely on caching; avoid re-running import side effects.",
        "mistake": "Expecting re-import to re-execute a module.",
    },
    {
        "q": "Absolute vs relative imports?",
        "a": "Absolute: from package.module import x. Relative: from .module import x "
             "(within a package).",
        "example": "from . import helpers",
        "best": "Prefer absolute imports for clarity.",
        "mistake": "Relative imports in a top-level script (no parent package).",
    },

    # ------------------------------- Performance -----------------------------
    {
        "q": "How do you profile Python code?",
        "a": "cProfile/profile for function-level; timeit for microbenchmarks; line_profiler "
             "for line-level; tracemalloc for memory.",
        "example": "python -m cProfile script.py",
        "best": "Profile before optimizing; target the real hotspot.",
        "mistake": "Guessing at bottlenecks and micro-optimizing the wrong code.",
    },
    {
        "q": "Why is 'x in set' faster than 'x in list'?",
        "a": "Set/dict membership is O(1) average (hashing); list is O(n) (linear scan).",
        "example": "if x in myset: ...",
        "best": "Convert to a set for repeated membership tests.",
        "mistake": "Repeated 'in list' checks in a loop.",
    },
    {
        "q": "How do you make string building efficient?",
        "a": "Collect pieces in a list and ''.join() once (O(n)) instead of += in a loop.",
        "example": "''.join(chunks)",
        "best": "join over repeated concatenation.",
        "mistake": "s += piece inside a large loop (O(n^2)).",
    },
    {
        "q": "What is memoization?",
        "a": "Caching function results by arguments to avoid recomputation (functools."
             "lru_cache/cache).",
        "example": "@cache\ndef f(n): ...",
        "best": "Memoize pure, expensive, repeated calls.",
        "mistake": "Memoizing impure functions or with unbounded cache growth.",
    },
    {
        "q": "Generators vs lists for large data?",
        "a": "Generators use O(1) memory (lazy); lists materialize everything.",
        "example": "sum(x for x in big_iter)",
        "best": "Stream with generators for large/infinite data.",
        "mistake": "Materializing a huge list just to reduce it.",
    },

    # ------------------------------- Testing ---------------------------------
    {
        "q": "How do you write unit tests in Python?",
        "a": "unittest (stdlib) or pytest (popular). Arrange-Act-Assert; isolate with mocks/"
             "fixtures.",
        "example": "def test_add(): assert add(2,3)==5",
        "best": "Keep tests fast, isolated, deterministic.",
        "mistake": "Tests that depend on order/network/global state.",
    },
    {
        "q": "What is mocking?",
        "a": "Replacing real dependencies (DB/HTTP) with controllable fakes "
             "(unittest.mock) to isolate the unit under test.",
        "example": "with patch('mod.api') as m: m.return_value=...",
        "best": "Mock at boundaries; assert on interactions.",
        "mistake": "Over-mocking internals -> brittle tests.",
    },
    {
        "q": "What are fixtures?",
        "a": "Reusable setup/teardown providing test dependencies (pytest fixtures / "
             "setUp/tearDown).",
        "example": "@pytest.fixture\ndef db(): ...",
        "best": "Scope fixtures appropriately (function/module/session).",
        "mistake": "Shared mutable fixture state leaking between tests.",
    },

    # ------------------------------- Typing ----------------------------------
    {
        "q": "Are type hints enforced at runtime?",
        "a": "No — they're metadata for tooling (mypy, IDEs). CPython ignores them at "
             "runtime.",
        "example": "def f(x: int) -> int: ...",
        "best": "Run a static checker (mypy/pyright) in CI.",
        "mistake": "Assuming hints prevent wrong-type arguments at runtime.",
    },
    {
        "q": "Optional[X] meaning?",
        "a": "Optional[X] == Union[X, None] — the value may be X or None.",
        "example": "def f() -> Optional[int]: ...",
        "best": "Return Optional and handle None explicitly.",
        "mistake": "Forgetting to handle the None case.",
    },
    {
        "q": "What is a Protocol (structural typing)?",
        "a": "typing.Protocol defines an interface by structure (methods/attrs) — duck "
             "typing checked statically.",
        "example": "class Sized(Protocol): def __len__(self)->int: ...",
        "best": "Use Protocols to type duck-typed APIs.",
        "mistake": "Forcing nominal inheritance where structural fits.",
    },

    # ------------------------------- Misc/idioms -----------------------------
    {
        "q": "What does enumerate do and why prefer it?",
        "a": "Yields (index, value) pairs — avoids range(len(...)) indexing.",
        "example": "for i, v in enumerate(xs): ...",
        "best": "enumerate over manual index tracking.",
        "mistake": "for i in range(len(xs)): xs[i]",
    },
    {
        "q": "What does zip do (and zip(*m))?",
        "a": "zip pairs elements across iterables; zip(*matrix) transposes rows/cols.",
        "example": "list(zip(a, b))",
        "best": "zip for parallel iteration; strict=True to catch length mismatch (3.10+).",
        "mistake": "Assuming zip pads — it stops at the shortest.",
    },
    {
        "q": "What is the difference between sort() and sorted()?",
        "a": "list.sort() mutates in place and returns None; sorted() returns a new sorted "
             "list from any iterable.",
        "example": "new = sorted(data)",
        "best": "sorted() when you need a new list / non-list input.",
        "mistake": "x = list.sort() -> x is None.",
    },
    {
        "q": "How does Python handle very large numbers?",
        "a": "int is arbitrary precision; it grows as needed with no overflow.",
        "example": "math.factorial(100)",
        "best": "Trust int for big integer math.",
        "mistake": "Expecting C-style overflow wraparound.",
    },
    {
        "q": "What is unpacking (including star)?",
        "a": "Assign sequence items to names; * captures the rest into a list.",
        "example": "a, *rest = [1,2,3,4]",
        "best": "Use for clean multi-return and slicing-free splits.",
        "mistake": "Unpacking mismatched lengths -> ValueError.",
    },
    {
        "q": "How do you swap two variables?",
        "a": "Tuple unpacking: a, b = b, a — no temp variable needed.",
        "example": "a, b = b, a",
        "best": "Idiomatic and atomic in one statement.",
        "mistake": "Using a temp variable unnecessarily.",
    },
    {
        "q": "What is the ternary/conditional expression?",
        "a": "value_if_true if condition else value_if_false.",
        "example": "'even' if n%2==0 else 'odd'",
        "best": "Use for simple inline choices.",
        "mistake": "Nesting many ternaries -> unreadable.",
    },
    {
        "q": "What does the else clause on a loop do?",
        "a": "Runs only if the loop finished WITHOUT hitting break (useful in search loops).",
        "example": "for x in xs: ... else: not_found()",
        "best": "Use for 'search then default' patterns.",
        "mistake": "Thinking else runs after every loop (it doesn't run after break).",
    },
    {
        "q": "How do you flatten a nested list?",
        "a": "Nested comprehension, itertools.chain.from_iterable, or recursion for "
             "arbitrary depth.",
        "example": "[x for row in m for x in row]",
        "best": "chain.from_iterable for one level of nesting.",
        "mistake": "sum(lists, []) which is O(n^2).",
    },
    {
        "q": "What is the difference between append and extend?",
        "a": "append adds one element; extend adds each element of an iterable.",
        "example": "a.extend([1,2]); a.append([1,2])",
        "best": "extend to concatenate; append for single items.",
        "mistake": "append(list) adding a nested list unintentionally.",
    },
    {
        "q": "What are truthy and falsy values?",
        "a": "Falsy: 0, 0.0, '', [], {}, set(), None, False. Everything else is truthy.",
        "example": "if not items: ...",
        "best": "Use 'if seq:' for emptiness checks.",
        "mistake": "if len(seq) > 0 instead of if seq.",
    },
    {
        "q": "How do you check the type of an object?",
        "a": "isinstance(obj, Type) (respects inheritance) — prefer over type(obj) == Type.",
        "example": "isinstance(x, (int, float))",
        "best": "isinstance for type checks; better yet, duck-type.",
        "mistake": "type(x) == int failing for bool/int subclasses.",
    },
    {
        "q": "What is __init__ vs __call__?",
        "a": "__init__ initializes a new instance; __call__ makes an existing instance "
             "callable like a function.",
        "example": "class F: def __call__(self,x): ...",
        "best": "Use __call__ for stateful function-like objects.",
        "mistake": "Confusing constructing (init) with invoking (call).",
    },
    {
        "q": "How do you reverse-iterate?",
        "a": "reversed(seq) (lazy) or seq[::-1] (new list).",
        "example": "for x in reversed(xs): ...",
        "best": "reversed() to avoid building a copy.",
        "mistake": "Reversing a huge list just to iterate backwards.",
    },
    {
        "q": "What does *args unpacking at the call site do?",
        "a": "Spreads an iterable/dict into positional/keyword arguments.",
        "example": "f(*[1,2,3]); g(**{'a':1})",
        "best": "Use to forward collected arguments.",
        "mistake": "Confusing ** (keywords) with * (positionals).",
    },
    {
        "q": "How do you handle configuration/secrets?",
        "a": "Environment variables (os.environ), config files, or a secrets manager — never "
             "hardcode secrets.",
        "example": "os.environ['API_KEY']",
        "best": "Load secrets from the environment; keep them out of VCS.",
        "mistake": "Committing credentials in source code.",
    },
    {
        "q": "What is the difference between shallow == and deep equality?",
        "a": "== recursively compares values for containers; 'is' compares identity. For "
             "nested structures == still compares by value.",
        "example": "[[1],[2]] == [[1],[2]]  # True",
        "best": "Use == for value comparison.",
        "mistake": "Using 'is' to compare container contents.",
    },
    {
        "q": "What does dict.get vs dict[key] do?",
        "a": "[] raises KeyError if missing; .get returns None (or a supplied default).",
        "example": "d.get('k', 0)",
        "best": ".get with a default to avoid KeyError.",
        "mistake": "Assuming d[k] returns None for missing keys.",
    },
    {
        "q": "How do you iterate a dict's keys and values together?",
        "a": "for k, v in d.items().",
        "example": "for k, v in d.items(): ...",
        "best": ".items() for key+value; .values() when keys unused.",
        "mistake": "for k in d: d[k]  (extra lookups).",
    },
    {
        "q": "What is list slicing assignment?",
        "a": "You can replace a slice with a different-length iterable, changing the list "
             "size.",
        "example": "a[1:3] = [9, 9, 9]",
        "best": "Use for in-place bulk edits.",
        "mistake": "Assigning a non-iterable to a slice.",
    },
    {
        "q": "How do you count occurrences efficiently?",
        "a": "collections.Counter(iterable).",
        "example": "Counter(words)['the']",
        "best": "Counter over manual dict incrementing.",
        "mistake": "Nested loops counting (O(n^2)).",
    },
    {
        "q": "What is the difference between remove, pop, and del on a list?",
        "a": "remove(value) deletes first matching value; pop(i) removes & returns by index; "
             "del removes by index/slice.",
        "example": "x.pop(); del x[0]; x.remove(9)",
        "best": "pop for stack/queue ops; remove for value; del for slices.",
        "mistake": "remove on a missing value -> ValueError.",
    },
    {
        "q": "How do you create a shallow copy of a dict/list?",
        "a": "dict(d)/d.copy() and list(l)/l[:]/l.copy().",
        "example": "d2 = d.copy()",
        "best": "copy() for a one-level copy; deepcopy for nested.",
        "mistake": "b = a then mutating b, also mutating a (alias).",
    },
    {
        "q": "What is the purpose of __all__ in a module?",
        "a": "Defines the public names exported by 'from module import *'.",
        "example": "__all__ = ['func1', 'Class2']",
        "best": "Declare __all__ to control the public API.",
        "mistake": "Assuming import * always imports everything (it respects __all__).",
    },
    {
        "q": "What is a lambda's limitation?",
        "a": "It's a single expression (no statements/assignments/annotations) and "
             "anonymous.",
        "example": "key=lambda x: x[1]",
        "best": "Use lambdas inline as keys/callbacks; def for anything non-trivial.",
        "mistake": "Assigning a lambda to a name instead of using def.",
    },
    {
        "q": "How do you merge/iterate multiple lists elementwise with an index?",
        "a": "enumerate(zip(a, b)).",
        "example": "for i,(x,y) in enumerate(zip(a,b)): ...",
        "best": "Combine zip + enumerate for index + parallel values.",
        "mistake": "Manual indexing into multiple lists.",
    },
    {
        "q": "Difference between a generator and a coroutine?",
        "a": "A generator produces values (yield); a coroutine (async def) consumes/awaits "
             "and cooperates with an event loop.",
        "example": "async def c(): await x()",
        "best": "Use async coroutines for concurrent I/O.",
        "mistake": "Mixing generator send-based coroutines with async/await confusingly.",
    },
    {
        "q": "What is a namedtuple and when to use it?",
        "a": "An immutable, memory-light tuple with named fields — readable records without "
             "a full class.",
        "example": "Point = namedtuple('Point', 'x y')",
        "best": "Use for simple immutable records; dataclass if you need methods/mutability.",
        "mistake": "Using raw tuples and indexing by position everywhere.",
    },
    {
        "q": "How do you implement a singleton in Python?",
        "a": "Module-level instance (simplest), a metaclass, or __new__ caching. Modules are "
             "already singletons.",
        "example": "# put the instance at module scope",
        "best": "Prefer a module-level object over singleton machinery.",
        "mistake": "Over-engineering a singleton when a module global suffices.",
    },
    {
        "q": "What is the difference between == and hash for dict keys?",
        "a": "Keys must be hashable; lookups use hash to find the bucket then == to confirm "
             "the key.",
        "example": "d = {(1,2): 'a'}",
        "best": "Ensure __eq__ and __hash__ are consistent.",
        "mistake": "Mutating a key object after insertion (breaks lookup).",
    },
    {
        "q": "How do you time a piece of code?",
        "a": "time.perf_counter() for wall-clock; timeit for repeated microbenchmarks.",
        "example": "timeit.timeit('sum(range(100))', number=1000)",
        "best": "timeit for small snippets; perf_counter for blocks.",
        "mistake": "Using time.time() (lower resolution) for benchmarks.",
    },
    {
        "q": "What is the difference between a class variable and an instance variable?",
        "a": "Class variable is shared across all instances; instance variable is per-object "
             "(set on self).",
        "example": "class C: shared=0",
        "best": "Use class vars for constants/shared state; instance vars for per-object data.",
        "mistake": "Mutating a shared mutable class variable per instance unintentionally.",
    },
    {
        "q": "How do you make a class iterable?",
        "a": "Implement __iter__ (return an iterator) — optionally __next__ if it's its own "
             "iterator.",
        "example": "def __iter__(self): return iter(self._items)",
        "best": "Return a fresh iterator for re-iterable containers.",
        "mistake": "Making __iter__ return self without resetting state.",
    },
    {
        "q": "What is the difference between range and a list?",
        "a": "range is a lazy immutable sequence (O(1) memory); list materializes all "
             "elements.",
        "example": "range(10**9)  # tiny memory",
        "best": "Iterate range directly; avoid list(range(huge)).",
        "mistake": "list(range(10**9)) -> MemoryError.",
    },
    {
        "q": "What does the global keyword do?",
        "a": "Declares that assignments to a name inside a function bind the module-level "
             "variable.",
        "example": "def f(): global x; x = 1",
        "best": "Avoid globals; pass state explicitly / return values.",
        "mistake": "Relying on global mutable state (hard to test).",
    },
    {
        "q": "What does nonlocal do?",
        "a": "Binds a name to the nearest enclosing (non-global) scope — used to mutate a "
             "closure variable.",
        "example": "def outer(): n=0\n def inner(): nonlocal n; n+=1",
        "best": "Use for stateful closures/counters.",
        "mistake": "Expecting inner assignment to affect the enclosing var without nonlocal.",
    },
    {
        "q": "How do you read a large file without loading it all?",
        "a": "Iterate the file object line-by-line (lazy) or read in chunks.",
        "example": "for line in f: process(line)",
        "best": "Stream lines; use generators for pipelines.",
        "mistake": "f.read()/readlines() on a multi-GB file.",
    },
    {
        "q": "What is pathlib and why prefer it over os.path?",
        "a": "An object-oriented path API (Path) with operator overloading (/) and rich "
             "methods — more readable and cross-platform.",
        "example": "Path('a') / 'b' / 'c.txt'",
        "best": "Prefer pathlib for new code.",
        "mistake": "String-concatenating paths with os-specific separators.",
    },
    {
        "q": "Why is unpickling untrusted data dangerous?",
        "a": "pickle can execute arbitrary code during load — a remote code execution risk.",
        "example": "# never pickle.load() untrusted bytes",
        "best": "Use JSON for untrusted interchange; pickle only for trusted data.",
        "mistake": "Unpickling data received over the network.",
    },
    {
        "q": "How do you handle JSON round-trip type loss?",
        "a": "JSON has no tuple/set/datetime; use default= encoders and object_hook decoders "
             "to convert.",
        "example": "json.dumps(obj, default=str)",
        "best": "Define explicit encoders/decoders for custom types.",
        "mistake": "Assuming tuples survive a JSON round-trip (become lists).",
    },
    {
        "q": "What is the difference between multiprocessing 'fork' and 'spawn'?",
        "a": "fork (Linux) copies the parent process; spawn (macOS/Windows default) starts a "
             "fresh interpreter that re-imports the module.",
        "example": "multiprocessing.set_start_method('spawn')",
        "best": "Keep worker functions at module level; guard with __main__.",
        "mistake": "Nested/lambda worker functions failing to pickle on spawn.",
    },
    {
        "q": "What are Python's scopes (LEGB)?",
        "a": "Name resolution order: Local -> Enclosing -> Global -> Built-in.",
        "example": "len  # found in Built-in scope",
        "best": "Understand LEGB to reason about closures/shadowing.",
        "mistake": "Shadowing built-ins (list = [...]) then calling list().",
    },
    {
        "q": "How do you implement caching with expiry?",
        "a": "functools.lru_cache has no TTL; use a custom dict with timestamps or a library "
             "(cachetools).",
        "example": "cachetools.TTLCache(maxsize=100, ttl=60)",
        "best": "Bound cache size and expiry to prevent memory growth.",
        "mistake": "Unbounded lru_cache(maxsize=None) leaking memory.",
    },
    {
        "q": "What is __init_subclass__?",
        "a": "A hook called when a class is subclassed — a lightweight alternative to a "
             "metaclass for subclass registration/validation.",
        "example": "def __init_subclass__(cls, **kw): register(cls)",
        "best": "Prefer over metaclasses for subclass hooks.",
        "mistake": "Writing a full metaclass for simple subclass registration.",
    },
    {
        "q": "How do you compare floating point numbers safely?",
        "a": "Use math.isclose(a, b) with tolerances instead of ==.",
        "example": "math.isclose(0.1+0.2, 0.3)",
        "best": "Compare floats with a tolerance.",
        "mistake": "0.1 + 0.2 == 0.3 (False due to binary rounding).",
    },
    {
        "q": "What is the difference between a shallow module import and 'from x import *'?",
        "a": "import x keeps the namespace; from x import * dumps names into the current "
             "namespace (risking clashes).",
        "example": "import math; math.sqrt(4)",
        "best": "Import the module or specific names; avoid *.",
        "mistake": "from module import * shadowing built-ins/other names.",
    },
    {
        "q": "How do you ensure a resource is always released?",
        "a": "Use a context manager (with) or try/finally.",
        "example": "with lock: ...",
        "best": "Prefer context managers for deterministic cleanup.",
        "mistake": "Releasing only on the happy path.",
    },
    {
        "q": "What are keyword arguments' evaluation and ordering rules?",
        "a": "Positional args first, then keyword args; you can't put positional after "
             "keyword; defaults evaluate once at def time.",
        "example": "f(1, b=2)",
        "best": "Use keyword args for clarity on optional params.",
        "mistake": "f(a=1, 2) -> SyntaxError.",
    },
    {
        "q": "How do you dynamically create/access attributes?",
        "a": "setattr/getattr/hasattr and the __dict__ mapping.",
        "example": "setattr(obj, 'x', 1); getattr(obj, 'x')",
        "best": "Use getattr with a default for optional attributes.",
        "mistake": "Direct obj.x access on possibly-missing attributes.",
    },
    {
        "q": "What is the difference between iterator protocol and sequence protocol?",
        "a": "Iterator: __iter__/__next__. Sequence: __len__/__getitem__ (indexable, and "
             "iterable via integer indexing fallback).",
        "example": "class Seq: def __getitem__(self,i): ...",
        "best": "Implement the protocol matching how the object is used.",
        "mistake": "Implementing __getitem__ but expecting StopIteration semantics.",
    },
    {
        "q": "How do you avoid circular imports?",
        "a": "Restructure modules, import inside functions (lazy import), or move shared code "
             "to a third module.",
        "example": "def f(): from .other import g",
        "best": "Design a clean dependency direction.",
        "mistake": "Two modules importing each other at top level.",
    },
    {
        "q": "What is the difference between .py, .pyc, and __pycache__?",
        "a": ".py is source; .pyc is compiled bytecode cached in __pycache__ to speed up "
             "subsequent imports.",
        "example": "__pycache__/module.cpython-311.pyc",
        "best": "Let Python manage bytecode caches; add __pycache__ to .gitignore.",
        "mistake": "Committing __pycache__ to version control.",
    },
    {
        "q": "How do you make an immutable class?",
        "a": "@dataclass(frozen=True), a NamedTuple, or override __setattr__ to block "
             "mutation.",
        "example": "@dataclass(frozen=True)\nclass P: x:int",
        "best": "frozen dataclass for immutable, hashable records.",
        "mistake": "Assuming a normal class is immutable.",
    },
    {
        "q": "What is the difference between async concurrency and parallelism?",
        "a": "Concurrency = many tasks in progress (interleaved); parallelism = many tasks "
             "literally running at once (multiple cores).",
        "example": "asyncio (concurrency) vs multiprocessing (parallelism)",
        "best": "Pick concurrency for I/O overlap, parallelism for CPU throughput.",
        "mistake": "Conflating the two in interviews.",
    },
    {
        "q": "How do you gracefully handle optional dependencies?",
        "a": "try/except ImportError and degrade or raise a helpful message.",
        "example": "try: import ujson as json\nexcept ImportError: import json",
        "best": "Fall back cleanly when an optional package is missing.",
        "mistake": "Hard-importing an optional dependency and crashing at import.",
    },
    {
        "q": "What is the difference between @staticmethod and a module-level function?",
        "a": "Functionally similar; a staticmethod lives in the class namespace (logical "
             "grouping, inheritable) while a module function is global.",
        "example": "class M: @staticmethod\n def util(): ...",
        "best": "staticmethod when the helper conceptually belongs to the class.",
        "mistake": "Making everything a staticmethod instead of a plain function.",
    },
    {
        "q": "How do you implement an LRU cache from scratch?",
        "a": "An OrderedDict: move_to_end on access, popitem(last=False) to evict the oldest "
             "when over capacity.",
        "example": "od.move_to_end(k); od.popitem(last=False)",
        "best": "Use functools.lru_cache unless you need custom eviction.",
        "mistake": "Using a plain dict and scanning to find the LRU item.",
    },
    {
        "q": "What is the difference between __getattr__ and __getattribute__?",
        "a": "__getattribute__ is called for EVERY attribute access; __getattr__ is called "
             "ONLY when normal lookup fails (missing attribute).",
        "example": "def __getattr__(self, name): return default",
        "best": "Override __getattr__ for fallbacks/proxies; __getattribute__ rarely.",
        "mistake": "Infinite recursion by accessing self.x inside __getattribute__.",
    },
    {
        "q": "How do you merge/deep-merge nested dictionaries?",
        "a": "Shallow: {**a, **b} or a|b. Deep: recurse, merging nested dicts key by key.",
        "example": "def deep_merge(a,b): ... recurse ...",
        "best": "Write a small recursive helper for nested config merges.",
        "mistake": "a|b overwriting nested dicts wholesale (no deep merge).",
    },
    {
        "q": "What is the difference between a shallow list*n and copy semantics?",
        "a": "[obj]*n repeats the SAME reference n times; mutating one affects all if obj is "
             "mutable.",
        "example": "row=[0]*3  # ints are immutable, safe",
        "best": "Safe for immutables; use comprehension for mutable elements.",
        "mistake": "[[]]*n creating n aliases of one list.",
    },
    {
        "q": "How do you implement retry logic cleanly?",
        "a": "A decorator that loops, catches exceptions, backs off, and re-raises after N "
             "attempts.",
        "example": "@retry(times=3)\ndef call(): ...",
        "best": "Add exponential backoff + jitter for network retries.",
        "mistake": "Retrying non-idempotent operations blindly.",
    },
    {
        "q": "What is the difference between sync and async generators?",
        "a": "A sync generator uses yield; an async generator (async def + yield) is iterated "
             "with 'async for' and can await inside.",
        "example": "async def g(): yield await fetch()",
        "best": "Use async generators to stream async I/O results.",
        "mistake": "Using 'for' instead of 'async for' on an async generator.",
    },
    {
        "q": "How do you validate data at boundaries?",
        "a": "Explicit checks with clear exceptions at input boundaries (not asserts); "
             "consider dataclasses/pydantic-style validation.",
        "example": "if not email: raise ValueError('email required')",
        "best": "Validate untrusted input explicitly; fail fast with helpful messages.",
        "mistake": "Using assert for input validation (stripped under -O).",
    },
    {
        "q": "What does the @property setter enable?",
        "a": "Validation or side effects on assignment while keeping attribute-style access.",
        "example": "@radius.setter\ndef radius(self, v): validate(v)",
        "best": "Add a setter only when assignment needs logic.",
        "mistake": "Exposing a raw attribute then later breaking the API to add validation.",
    },
    {
        "q": "How do you profile memory usage?",
        "a": "tracemalloc (stdlib) snapshots allocations; sys.getsizeof for single objects; "
             "memory_profiler for line-level.",
        "example": "tracemalloc.start(); snapshot = tracemalloc.take_snapshot()",
        "best": "Use tracemalloc to find allocation hotspots.",
        "mistake": "Guessing memory usage without measuring.",
    },
    {
        "q": "What is the difference between copy.copy and assignment?",
        "a": "Assignment binds another name to the SAME object; copy.copy creates a new "
             "(shallow) object.",
        "example": "b = a          # alias\nc = copy.copy(a)  # new object",
        "best": "Copy when you need independence; alias when sharing is intended.",
        "mistake": "Expecting b = a to be a copy.",
    },
    {
        "q": "How do you make a generator that supports clean shutdown?",
        "a": "Wrap the yield in try/finally so .close()/GeneratorExit runs cleanup.",
        "example": "def g():\n  try: yield\n  finally: cleanup()",
        "best": "Release resources in the generator's finally block.",
        "mistake": "Leaking resources when a generator is closed early.",
    },
    {
        "q": "Final: what makes code 'Pythonic'?",
        "a": "Readable, idiomatic use of comprehensions, unpacking, context managers, EAFP, "
             "built-ins, and the standard library — 'There should be one obvious way.'",
        "example": "import this  # The Zen of Python",
        "best": "Favor clarity and idioms over cleverness.",
        "mistake": "Writing C/Java-style code in Python.",
    },
]


def print_qa_bank() -> None:
    """Pretty-print the full question bank as a study guide."""
    print("=" * 80)
    print(f"PYTHON INTERVIEW QUESTION BANK — {len(QUESTIONS)} questions")
    print("=" * 80)
    for i, item in enumerate(QUESTIONS, start=1):
        print(f"\nQ{i}. {item['q']}")
        print(f"  Answer         : {item['a']}")
        print(f"  Example        : {item['example']}")
        print(f"  Best practice  : {item['best']}")
        print(f"  Common mistake : {item['mistake']}")


# =============================================================================
# 2) LIVE DEMOS — a subset executed for real
# =============================================================================
def run_live_demos() -> None:
    import copy
    import functools
    from collections import Counter, defaultdict

    print("\n" + "=" * 80)
    print("LIVE DEMOS")
    print("=" * 80)

    # --- is vs == ---
    a, b = [1, 2, 3], [1, 2, 3]
    print("\n[Live] is vs ==:")
    print(f"  a == b -> {a == b}   a is b -> {a is b}")
    assert a == b and a is not b

    # --- mutable default argument trap ---
    def append_bad(x, acc=[]):
        acc.append(x)
        return acc

    print("\n[Live] mutable default argument trap:")
    print(f"  append_bad(1) -> {append_bad(1)}")
    print(f"  append_bad(2) -> {append_bad(2)}  (state leaked!)")

    # --- shallow vs deep copy ---
    nested = [[1, 2], [3, 4]]
    shallow = copy.copy(nested)
    shallow[0].append(99)
    print("\n[Live] shallow copy shares inner lists:")
    print(f"  original after shallow mutation -> {nested}")
    assert nested[0] == [1, 2, 99]

    # --- comprehension vs loop ---
    squares = [x * x for x in range(6)]
    print("\n[Live] list comprehension:")
    print(f"  {squares}")

    # --- Counter ---
    words = "the cat sat on the mat the".split()
    print("\n[Live] Counter.most_common:")
    print(f"  {Counter(words).most_common(2)}")

    # --- defaultdict grouping ---
    groups = defaultdict(list)
    for name in ["Ada", "Alan", "Grace", "Ben"]:
        groups[name[0]].append(name)
    print("\n[Live] defaultdict grouping by first letter:")
    print(f"  {dict(groups)}")

    # --- closure factory ---
    def multiplier(n):
        return lambda x: x * n

    triple = multiplier(3)
    print("\n[Live] closure (triple):")
    print(f"  triple(10) -> {triple(10)}")
    assert triple(10) == 30

    # --- decorator with memoization ---
    @functools.lru_cache(maxsize=None)
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    print("\n[Live] lru_cache fib(30):")
    print(f"  {fib(30)}  cache_info -> {fib.cache_info()}")

    # --- generator pipeline (lazy) ---
    def evens(src):
        for x in src:
            if x % 2 == 0:
                yield x

    pipeline = (x * x for x in evens(range(10)))
    print("\n[Live] generator pipeline (squares of evens):")
    print(f"  {list(pipeline)}")

    # --- unpacking & swap ---
    first, *middle, last = [1, 2, 3, 4, 5]
    x, y = 10, 20
    x, y = y, x
    print("\n[Live] star-unpacking & swap:")
    print(f"  first={first} middle={middle} last={last}; swapped=({x},{y})")

    # --- dedup preserving order ---
    seq = [3, 1, 3, 2, 1, 4]
    print("\n[Live] order-preserving dedup via dict.fromkeys:")
    print(f"  {list(dict.fromkeys(seq))}")

    print("\nAll live demos ran successfully ✅")


def main() -> None:
    qa_only = "--qa-only" in sys.argv
    print_qa_bank()
    if qa_only:
        return
    run_live_demos()


if __name__ == "__main__":
    main()
