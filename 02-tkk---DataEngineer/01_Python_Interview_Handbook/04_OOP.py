"""
04_OOP.py
================================================================================
Python Interview Handbook
Chapter 04: OBJECT-ORIENTED PROGRAMMING

Covered in this file
--------------------
* Classes, __init__, instance vs class attributes
* Instance / class / static methods (@classmethod, @staticmethod)
* Encapsulation & name mangling (_protected, __private)
* Properties (@property, getters/setters)
* Inheritance, super(), method overriding
* Multiple inheritance & the MRO (C3 linearization)
* Polymorphism & duck typing
* Abstract base classes (abc)
* Dunder / magic methods (__str__, __repr__, __eq__, __lt__, __len__, __add__, ...)
* dataclasses
* __slots__ (memory optimization)

Run:
    python3 04_OOP.py
================================================================================
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import total_ordering


def main() -> None:
    ###########################################################
    # CLASS BASICS — instance vs class attributes
    ###########################################################
    class Counter:
        population = 0                # CLASS attribute (shared by all instances)

        def __init__(self, name):
            self.name = name          # INSTANCE attribute (per object)
            Counter.population += 1

    a = Counter("a")
    b = Counter("b")
    assert a.name == "a" and b.name == "b"
    assert Counter.population == 2    # shared class state

    ###########################################################
    # INSTANCE / CLASS / STATIC METHODS
    ###########################################################
    class Temperature:
        def __init__(self, celsius):
            self.celsius = celsius

        def to_fahrenheit(self):          # instance method: needs self
            return self.celsius * 9 / 5 + 32

        @classmethod
        def from_fahrenheit(cls, f):      # class method: alt constructor, gets cls
            return cls((f - 32) * 5 / 9)

        @staticmethod
        def is_freezing(celsius):         # static method: no self/cls
            return celsius <= 0

    t = Temperature(100)
    assert t.to_fahrenheit() == 212
    assert Temperature.from_fahrenheit(32).celsius == 0
    assert Temperature.is_freezing(-5) is True

    ###########################################################
    # ENCAPSULATION & NAME MANGLING
    ###########################################################
    class Account:
        def __init__(self, balance):
            self._balance = balance       # _single: "protected" by convention
            self.__pin = 1234             # __double: name-mangled to _Account__pin

        def check(self, pin):
            return pin == self.__pin

    acc = Account(100)
    assert acc._balance == 100            # accessible, but "don't touch" by convention
    assert acc.check(1234)
    # __pin is name-mangled — not directly accessible as acc.__pin
    assert not hasattr(acc, "__pin")
    assert acc._Account__pin == 1234      # the mangled name (avoid using this!)

    ###########################################################
    # PROPERTIES — computed / validated attributes
    ###########################################################
    class Circle:
        def __init__(self, radius):
            self._radius = radius

        @property
        def radius(self):                 # getter: access like an attribute
            return self._radius

        @radius.setter
        def radius(self, value):          # setter: validate on assignment
            if value < 0:
                raise ValueError("radius must be non-negative")
            self._radius = value

        @property
        def area(self):                   # read-only computed property
            return 3.14159 * self._radius ** 2

    c = Circle(2)
    assert round(c.area, 2) == 12.57
    c.radius = 3                          # calls the setter
    assert c.radius == 3
    try:
        c.radius = -1
        raise AssertionError("should have raised")
    except ValueError:
        pass

    ###########################################################
    # INHERITANCE, super(), OVERRIDING
    ###########################################################
    class Animal:
        def __init__(self, name):
            self.name = name

        def speak(self):
            return "..."

        def describe(self):
            return f"{self.name} says {self.speak()}"

    class Dog(Animal):
        def __init__(self, name, breed):
            super().__init__(name)        # call parent __init__
            self.breed = breed

        def speak(self):                  # override
            return "Woof"

    d = Dog("Rex", "Lab")
    assert d.describe() == "Rex says Woof"   # polymorphic dispatch
    assert isinstance(d, Animal) and issubclass(Dog, Animal)

    ###########################################################
    # MULTIPLE INHERITANCE & MRO (C3 linearization)
    ###########################################################
    class A:
        def who(self):
            return "A"

    class B(A):
        def who(self):
            return "B"

    class C(A):
        def who(self):
            return "C"

    class D(B, C):                        # diamond inheritance
        pass

    # MRO decides which who() wins: D -> B -> C -> A -> object
    assert D().who() == "B"
    assert [cls.__name__ for cls in D.__mro__] == ["D", "B", "C", "A", "object"]

    ###########################################################
    # POLYMORPHISM & DUCK TYPING
    ###########################################################
    # "If it walks like a duck and quacks like a duck..." — no shared base needed.
    class Cat:
        def speak(self):
            return "Meow"

    def make_it_speak(thing):
        return thing.speak()             # works for anything with .speak()

    assert make_it_speak(Dog("X", "Y")) == "Woof"
    assert make_it_speak(Cat()) == "Meow"

    ###########################################################
    # ABSTRACT BASE CLASSES
    ###########################################################
    class Shape(ABC):
        @abstractmethod
        def area(self):
            ...

    class Square(Shape):
        def __init__(self, side):
            self.side = side

        def area(self):
            return self.side ** 2

    assert Square(4).area() == 16
    try:
        Shape()                          # cannot instantiate an abstract class
        raise AssertionError("should have raised")
    except TypeError:
        pass

    ###########################################################
    # DUNDER / MAGIC METHODS — make objects behave like built-ins
    ###########################################################
    @total_ordering                      # fills in <=, >, >= from __eq__ & __lt__
    class Money:
        def __init__(self, cents):
            self.cents = cents

        def __repr__(self):              # unambiguous, for developers/debugging
            return f"Money({self.cents})"

        def __str__(self):               # readable, for end users
            return f"${self.cents / 100:.2f}"

        def __eq__(self, other):
            return self.cents == other.cents

        def __lt__(self, other):
            return self.cents < other.cents

        def __add__(self, other):        # supports the + operator
            return Money(self.cents + other.cents)

        def __len__(self):               # supports len()
            return self.cents

        def __hash__(self):              # needed to keep it hashable after __eq__
            return hash(self.cents)

    m1, m2 = Money(150), Money(250)
    assert str(m1) == "$1.50"
    assert repr(m2) == "Money(250)"
    assert (m1 + m2) == Money(400)       # __add__ + __eq__
    assert m1 < m2 and m2 >= m1          # total_ordering
    assert len(m1) == 150                # __len__
    assert m1 == Money(150)

    ###########################################################
    # DATACLASSES — boilerplate-free classes (3.7+)
    ###########################################################
    @dataclass(order=True)               # auto __init__/__repr__/__eq__/ordering
    class Point:
        x: int
        y: int
        tags: list = field(default_factory=list)   # mutable default done right

    p1 = Point(1, 2)
    p2 = Point(1, 2)
    assert p1 == p2                      # value equality for free
    # NOTE: dataclass __repr__ uses __qualname__, so a class defined inside a
    # function reprs as 'main.<locals>.Point(...)'. endswith() keeps this robust.
    assert repr(p1).endswith("Point(x=1, y=2, tags=[])")
    p1.tags.append("a")
    assert p2.tags == []                 # independent (default_factory)

    @dataclass(frozen=True)              # immutable & hashable
    class RGB:
        r: int
        g: int
        b: int

    color = RGB(255, 0, 0)
    assert color in {RGB(255, 0, 0): "red"}   # usable as a dict key

    ###########################################################
    # __slots__ — restrict attributes & save memory
    ###########################################################
    class Slotted:
        __slots__ = ("x", "y")           # no per-instance __dict__
        def __init__(self, x, y):
            self.x, self.y = x, y

    sp = Slotted(1, 2)
    assert sp.x == 1
    assert not hasattr(sp, "__dict__")   # memory saved; no arbitrary attrs
    try:
        sp.z = 3                         # cannot add attributes not in __slots__
        raise AssertionError("should have raised")
    except AttributeError:
        pass

    print("All 04_OOP assertions passed ✅")


if __name__ == "__main__":
    main()
