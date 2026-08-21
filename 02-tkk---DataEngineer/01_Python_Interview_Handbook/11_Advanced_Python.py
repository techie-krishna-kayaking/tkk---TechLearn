"""
11_Advanced_Python.py
================================================================================
Python Interview Handbook
Chapter 11: ADVANCED PYTHON

Covered in this file
--------------------
* Everything is an object; id / type / is
* Mutability & how assignment binds names (references)
* Variable-length ints, interning
* __slots__ recap (memory)
* Descriptors (__get__/__set__) — how @property works under the hood
* Metaclasses (customizing class creation)
* Class decorators
* Monkey patching
* Garbage collection & reference counting (gc, weakref)
* Type hints & typing (Optional, Union, Generic, TypeVar, Protocol)
* Enum
* The __call__ protocol (callable objects)
* Shallow inspection: getattr/setattr/hasattr, __dict__

Run:
    python3 11_Advanced_Python.py
================================================================================
"""

import gc
import sys
import weakref
from enum import Enum, auto
from typing import Generic, Optional, TypeVar, Union


def main() -> None:
    ###########################################################
    # EVERYTHING IS AN OBJECT
    ###########################################################
    assert isinstance(42, object)
    assert isinstance(int, object)
    assert isinstance(len, object)   # even functions are objects
    # id() returns a unique identifier (the memory address in CPython).
    a = [1, 2]
    assert id(a) == id(a)

    ###########################################################
    # NAMES ARE REFERENCES — "pass by object reference"
    ###########################################################
    def mutate(lst):
        lst.append(99)               # mutates the SAME object the caller sees

    def rebind(lst):
        lst = [0]                    # rebinds the LOCAL name only

    data = [1, 2, 3]
    mutate(data)
    assert data == [1, 2, 3, 99]     # caller sees the mutation
    rebind(data)
    assert data == [1, 2, 3, 99]     # rebinding did NOT affect the caller

    ###########################################################
    # INTERNING (implementation detail — don't rely on it)
    ###########################################################
    assert sys.intern("hello") is sys.intern("hello")

    ###########################################################
    # DESCRIPTORS — the mechanism behind @property, methods, classmethod
    ###########################################################
    class Positive:
        """A data descriptor enforcing a positive value."""
        def __set_name__(self, owner, name):
            self.private = f"_{name}"

        def __get__(self, obj, objtype=None):
            if obj is None:
                return self
            return getattr(obj, self.private)

        def __set__(self, obj, value):
            if value <= 0:
                raise ValueError("must be positive")
            setattr(obj, self.private, value)

    class Product:
        price = Positive()           # descriptor instance at class level

        def __init__(self, price):
            self.price = price        # triggers Positive.__set__

    prod = Product(10)
    assert prod.price == 10
    prod.price = 20
    assert prod.price == 20
    try:
        prod.price = -5
        raise AssertionError("should have raised")
    except ValueError:
        pass

    ###########################################################
    # METACLASSES — classes are instances of their metaclass (type)
    ###########################################################
    # type() with 3 args creates a class dynamically.
    Dynamic = type("Dynamic", (), {"greet": lambda self: "hi"})
    assert Dynamic().greet() == "hi"

    # Custom metaclass: auto-register subclasses / enforce rules at class creation.
    registry = {}

    class AutoRegister(type):
        def __new__(mcs, name, bases, namespace):
            cls = super().__new__(mcs, name, bases, namespace)
            if bases:                # skip the base itself
                registry[name] = cls
            return cls

    class Plugin(metaclass=AutoRegister):
        pass

    class JSONPlugin(Plugin):
        pass

    class CSVPlugin(Plugin):
        pass

    assert set(registry) == {"JSONPlugin", "CSVPlugin"}
    assert isinstance(Plugin, AutoRegister)      # a class IS an instance of its metaclass

    ###########################################################
    # CLASS DECORATORS — simpler alternative to many metaclasses
    ###########################################################
    def add_repr(cls):
        cls.__repr__ = lambda self: f"{cls.__name__}({self.__dict__})"
        return cls

    @add_repr
    class Box:
        def __init__(self, w, h):
            self.w, self.h = w, h

    assert repr(Box(2, 3)) == "Box({'w': 2, 'h': 3})"

    ###########################################################
    # MONKEY PATCHING — modify classes/modules at runtime
    ###########################################################
    class Service:
        def greet(self):
            return "hello"

    def patched(self):
        return "patched!"

    Service.greet = patched          # replace the method at runtime
    assert Service().greet() == "patched!"
    # Useful for testing/mocking; risky in production (surprising behavior).

    ###########################################################
    # __call__ — make instances callable like functions
    ###########################################################
    class Adder:
        def __init__(self, n):
            self.n = n

        def __call__(self, x):        # instance() invokes this
            return x + self.n

    add5 = Adder(5)
    assert callable(add5) and add5(10) == 15

    ###########################################################
    # GARBAGE COLLECTION — refcounting + cyclic collector
    ###########################################################
    # CPython frees objects immediately when their refcount hits 0.
    x = [1, 2, 3]
    assert sys.getrefcount(x) >= 2   # (name x + the argument to getrefcount)
    # Reference CYCLES need the cyclic GC (refcount alone can't free them).
    a = {}
    b = {}
    a["b"] = b
    b["a"] = a                       # cycle a <-> b
    del a, b
    collected = gc.collect()         # force a collection
    assert collected >= 0

    # weakref — reference an object WITHOUT keeping it alive
    class Node:
        pass

    n = Node()
    ref = weakref.ref(n)
    assert ref() is n                # still alive
    del n
    assert ref() is None             # target was collected

    ###########################################################
    # TYPE HINTS & typing
    ###########################################################
    def greet(name: str, times: int = 1) -> str:
        return (name + " ") * times

    assert greet("hi", 2) == "hi hi "
    # Hints are metadata, not enforced at runtime:
    assert greet.__annotations__ == {"name": str, "times": int, "return": str}

    # Optional[X] == Union[X, None]
    def find(items: list, target: int) -> Optional[int]:
        return items.index(target) if target in items else None

    assert find([1, 2, 3], 2) == 1
    assert find([1, 2, 3], 9) is None

    # Generic container with a TypeVar
    T = TypeVar("T")

    class Stack(Generic[T]):
        def __init__(self) -> None:
            self._items: list[T] = []

        def push(self, item: T) -> None:
            self._items.append(item)

        def pop(self) -> T:
            return self._items.pop()

    st: "Stack[int]" = Stack()
    st.push(1)
    st.push(2)
    assert st.pop() == 2

    # Union example
    def to_int(x: Union[int, str]) -> int:
        return int(x)

    assert to_int("5") == 5 and to_int(7) == 7

    ###########################################################
    # ENUM — named constants
    ###########################################################
    class Color(Enum):
        RED = auto()
        GREEN = auto()
        BLUE = auto()

    assert Color.RED.name == "RED"
    assert Color.RED.value == 1
    assert Color(2) is Color.GREEN
    assert list(Color)[0] is Color.RED

    ###########################################################
    # DYNAMIC ATTRIBUTE ACCESS
    ###########################################################
    class Bag:
        pass

    bag = Bag()
    setattr(bag, "flavor", "vanilla")
    assert getattr(bag, "flavor") == "vanilla"
    assert hasattr(bag, "flavor")
    assert getattr(bag, "missing", "default") == "default"
    assert bag.__dict__ == {"flavor": "vanilla"}

    print("All 11_Advanced_Python assertions passed ✅")


if __name__ == "__main__":
    main()
