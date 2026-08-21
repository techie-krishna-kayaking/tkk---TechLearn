# Python Interview Handbook

> The most comprehensive, executable, beginner-to-senior reference for **Python**
> interviews. A companion to the *PySpark SQL vs DataFrame API Interview Handbook*.

Built for **Software Engineer, Data Engineer, Backend, Python Developer, SDET, and
Machine Learning Engineer** interviews.

Every concept in this handbook is:

- **Executable** — run any file directly with `python3`, no external dependencies.
- **Heavily commented** — each example explains *what*, *why it matters in interviews*,
  *common mistakes*, and *best practices*.
- **Pythonic-first** — where it helps, the code shows the **Non-Pythonic** way *and* the
  **Pythonic** way side by side (the Python analogue of "SQL vs DataFrame API").

---

## Repository structure

```
Python_Interview_Handbook/
│
├── README.md
│
├── 01_Basics.py                          # types, operators, strings, control flow, I/O
├── 02_Data_Structures.py                 # list, tuple, set, dict, comprehensions
├── 03_Functions.py                       # args, *args/**kwargs, lambda, closures, decorators
├── 04_OOP.py                             # classes, inheritance, polymorphism, dunder, dataclass
├── 05_Iterators_Generators.py            # iterators, generators, yield, itertools
├── 06_Exceptions_and_Context_Managers.py # try/except/finally, custom errors, with, contextlib
├── 07_Standard_Library.py                # collections, functools, itertools, datetime, re, math
├── 08_File_IO_and_Serialization.py       # files, pathlib, json, csv, pickle
├── 09_Functional_Programming.py          # map/filter/reduce, comprehensions, partial, lru_cache
├── 10_Concurrency_and_Parallelism.py     # threading, multiprocessing, asyncio, GIL
├── 11_Advanced_Python.py                 # metaclasses, descriptors, memory, GC, typing, slots
└── 12_Interview_Questions.py             # 150+ Q&A with answers, examples, best practices
```

---

## Prerequisites

- **Python 3.8+** (developed and tested on modern CPython). No third-party packages.

```bash
python3 --version
```

---

## How to run

Each file is standalone and prints its results:

```bash
python3 01_Basics.py
python3 05_Iterators_Generators.py
python3 12_Interview_Questions.py            # prints Q&A bank + runs live demos
python3 12_Interview_Questions.py --qa-only  # only prints the Q&A bank
```

Most files also contain `assert` statements so that **running them cleanly to the end is
itself a test** that the examples behave as documented.

---

## Learning path (Beginner → Senior)

1. **Beginner:** `01` → `02` → `03`
2. **Intermediate:** `04` → `05` → `06`
3. **Advanced:** `07` → `08` → `09`
4. **Senior:** `10` → `11`
5. **Interview prep:** `12` (revise everything as Q&A)

---

## Conventions used in the code

- Each concept gets a banner comment:

  ```python
  ###########################################################
  # LIST COMPREHENSION
  ###########################################################
  ```

- Where relevant, both styles are shown:

  ```python
  # Non-Pythonic
  result = []
  for x in items:
      result.append(x * 2)

  # Pythonic
  result = [x * 2 for x in items]
  ```

- Comments call out **interview relevance**, **common mistakes**, and **best practices**.

Happy learning — and good luck in your interviews!
