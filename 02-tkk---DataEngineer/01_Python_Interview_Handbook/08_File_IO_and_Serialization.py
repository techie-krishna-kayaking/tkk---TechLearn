"""
08_File_IO_and_Serialization.py
================================================================================
Python Interview Handbook
Chapter 08: FILE I/O & SERIALIZATION

Covered in this file
--------------------
* Reading / writing text files (with statement, encodings)
* File modes (r, w, a, x, b, +)
* Reading strategies: read, readline, readlines, iterate line-by-line
* pathlib (modern path handling)
* json  : dumps/loads, dump/load, custom encoding
* csv   : reader/writer, DictReader/DictWriter
* pickle: object serialization (and its security warning)
* tempfile for safe, self-contained examples

All examples use a temp directory so the file is fully self-contained & runnable.

Run:
    python3 08_File_IO_and_Serialization.py
================================================================================
"""

import csv
import json
import os
import pickle
import tempfile
from pathlib import Path


def main() -> None:
    # Work inside a temp directory so nothing pollutes the repo.
    tmp = Path(tempfile.mkdtemp(prefix="handbook_io_"))

    ###########################################################
    # WRITING & READING TEXT — always use 'with' + explicit encoding
    ###########################################################
    text_path = tmp / "notes.txt"
    # 'w' truncates/creates; ALWAYS specify encoding for portability.
    with open(text_path, "w", encoding="utf-8") as f:
        f.write("line1\n")
        f.writelines(["line2\n", "line3\n"])
    # 'with' guarantees the file is closed even if an exception occurs.
    with open(text_path, encoding="utf-8") as f:
        content = f.read()
    assert content == "line1\nline2\nline3\n"

    ###########################################################
    # FILE MODES
    ###########################################################
    # 'a' appends; 'x' fails if the file already exists; 'b' is binary; '+' read+write
    with open(text_path, "a", encoding="utf-8") as f:
        f.write("line4\n")
    with open(text_path, encoding="utf-8") as f:
        assert f.read().count("\n") == 4
    try:
        with open(text_path, "x", encoding="utf-8"):   # 'x' -> exclusive create
            pass
        raise AssertionError("should have raised")
    except FileExistsError:
        pass

    ###########################################################
    # READING STRATEGIES
    ###########################################################
    # Pythonic: iterate the file object line-by-line (memory efficient, lazy).
    lines = []
    with open(text_path, encoding="utf-8") as f:
        for line in f:               # does NOT load the whole file at once
            lines.append(line.rstrip("\n"))
    assert lines == ["line1", "line2", "line3", "line4"]
    # readlines() loads ALL lines into a list (avoid for huge files).
    with open(text_path, encoding="utf-8") as f:
        assert len(f.readlines()) == 4

    ###########################################################
    # pathlib — modern, OS-independent paths (prefer over os.path)
    ###########################################################
    p = tmp / "sub" / "data.txt"
    p.parent.mkdir(parents=True, exist_ok=True)   # like mkdir -p
    p.write_text("hello pathlib", encoding="utf-8")   # one-liner write
    assert p.read_text(encoding="utf-8") == "hello pathlib"
    assert p.name == "data.txt"
    assert p.suffix == ".txt"
    assert p.stem == "data"
    assert p.exists() and p.is_file()
    assert p.parent.is_dir()
    # Glob for files
    txt_files = list(tmp.glob("**/*.txt"))
    assert any(f.name == "data.txt" for f in txt_files)

    ###########################################################
    # JSON — the universal data interchange format
    ###########################################################
    obj = {"name": "Ada", "skills": ["python", "math"], "age": 36, "active": True}
    # dumps: object -> JSON string; loads: JSON string -> object
    text = json.dumps(obj, indent=2, sort_keys=True)
    back = json.loads(text)
    assert back == obj
    # dump/load: write/read directly to/from a file
    json_path = tmp / "person.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(obj, f)
    with open(json_path, encoding="utf-8") as f:
        assert json.load(f) == obj
    # Type mapping gotcha: JSON has no tuple; tuples become lists on round-trip.
    assert json.loads(json.dumps((1, 2))) == [1, 2]

    # Custom encoding for non-JSON-native types (e.g. datetime/set)
    from datetime import date

    def encoder(o):
        if isinstance(o, date):
            return o.isoformat()
        if isinstance(o, set):
            return sorted(o)
        raise TypeError(f"not serializable: {type(o)}")

    payload = {"d": date(2024, 1, 1), "tags": {"b", "a"}}
    encoded = json.dumps(payload, default=encoder, sort_keys=True)
    assert json.loads(encoded) == {"d": "2024-01-01", "tags": ["a", "b"]}

    ###########################################################
    # CSV — reader/writer and the DictReader/DictWriter (Pythonic)
    ###########################################################
    csv_path = tmp / "people.csv"
    rows = [
        {"name": "Ada", "age": 36},
        {"name": "Alan", "age": 41},
    ]
    # DictWriter maps dict keys to columns; newline='' avoids blank rows on Windows.
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "age"])
        writer.writeheader()
        writer.writerows(rows)
    # DictReader yields an OrderedDict-like row per line (values are strings!)
    with open(csv_path, newline="", encoding="utf-8") as f:
        read_rows = list(csv.DictReader(f))
    assert read_rows[0]["name"] == "Ada"
    assert read_rows[0]["age"] == "36"          # CSV values are always strings
    assert int(read_rows[1]["age"]) == 41

    # Plain reader/writer (list-of-lists)
    with open(csv_path, newline="", encoding="utf-8") as f:
        header, *body = list(csv.reader(f))
    assert header == ["name", "age"]
    assert body[0] == ["Ada", "36"]

    ###########################################################
    # PICKLE — serialize arbitrary Python objects (binary)
    ###########################################################
    # SECURITY WARNING: never unpickle data from an untrusted source — it can
    # execute arbitrary code. Use JSON for interchange; pickle for trusted caches.
    data = {"nums": [1, 2, 3], "nested": {"x": (4, 5)}}
    pkl_path = tmp / "cache.pkl"
    with open(pkl_path, "wb") as f:              # binary mode!
        pickle.dump(data, f)
    with open(pkl_path, "rb") as f:
        restored = pickle.load(f)
    assert restored == data
    assert restored["nested"]["x"] == (4, 5)     # pickle preserves tuples (unlike JSON)

    # dumps/loads to/from bytes
    blob = pickle.dumps([1, 2, 3])
    assert pickle.loads(blob) == [1, 2, 3]

    ###########################################################
    # CLEANUP
    ###########################################################
    # Remove the temp tree (best-effort).
    for child in sorted(tmp.rglob("*"), reverse=True):
        child.rmdir() if child.is_dir() else child.unlink()
    tmp.rmdir()
    assert not tmp.exists()

    print("All 08_File_IO_and_Serialization assertions passed ✅")


if __name__ == "__main__":
    main()
