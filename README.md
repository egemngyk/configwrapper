# configwrap

Python library to manage variables in config and settings files through a single API. You provide a file path and a variable schema (structure); read, write, add, and delete operations all use the same interface.

---

## Table of contents

- [Project structure](#project-structure)
- [Concepts](#concepts)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Tutorial](#tutorial)
  - [1. Import and create Core](#1-import-and-create-core)
  - [2. Read and write values](#2-read-and-write-values)
  - [3. Get all / bulk write](#3-get-all--bulk-write)
  - [4. List and check](#4-list-and-check)
  - [5. Add and delete](#5-add-and-delete)
  - [6. Reset and reload](#6-reset-and-reload)
  - [7. Logging](#7-logging)
  - [8. File formats](#8-file-formats)
- [Command reference](#command-reference)
- [Full example](#full-example)
- [Pushing to GitHub](#pushing-to-github)
- [License](#license)

**Turkish:** [README.tr.md](README.tr.md)

---

## Project structure

```text
configwrap/
├── main.py                 # Example / entry point
├── config/                 # Data files (.json, .conf)
│   ├── app.conf
│   └── theme.json
├── configwrap/             # Package
│   ├── __init__.py
│   ├── core.py
│   ├── structure.py
│   └── formats.py
├── LICENSE
├── .gitignore
└── README.md
```

---

## Concepts

| Concept       | Description                                                                                    |
| ------------- | ---------------------------------------------------------------------------------------------- |
| **File**      | Where values are stored (e.g. `config/app.conf`). JSON or conf format.                         |
| **Structure** | Which variables exist and their defaults. A Python `dict`: `{"theme": "dark", "size": 14}`.    |
| **Core**      | Ties file and structure together. All operations (`get`, `set`, `save`, etc.) go through Core. |

> **Summary:** You define a structure (“these variables, these defaults”); Core reads/writes the file and manages the variables.

---

## Installation

No external dependencies. Import the package directly:

```bash
git clone https://github.com/egemngyk/configwrap.git
cd configwrap
python main.py
```

To use in another project, copy the `configwrap` folder into it or add it to `PYTHONPATH`.

---

## Quick start

```python
from pathlib import Path
from configwrap import Core, core_config

CONFIG = Path(__file__).parent / "config" / "app.conf"
VARS = {"theme": "dark", "font_size": 14}

c = Core(str(CONFIG), VARS)
c.set("theme", "light")
c.save()
```

---

## Tutorial

### 1. Import and create Core

```python
from pathlib import Path
from configwrap import Core, core_config

CONFIG = Path(__file__).parent / "config" / "app.conf"
VARS = {
    "theme": "dark",
    "font_size": 14,
    "accent_color": "#3498db",
}

c = Core(str(CONFIG), VARS)
```

- **If the file does not exist:** Only in-memory defaults are used until you call `c.save()` to create the file.
- **If the file exists:** Its contents are read and merged with the structure; missing keys get default values.

### 2. Read and write values

```python
theme = c.get("theme")      # read
c.set("theme", "light")     # write (in memory)
c.set("font_size", 16)
c.save()                    # persist to file
```

- **get:** Read only. Raises if the variable is not in the structure.
- **set:** Updates in memory; call **save()** to persist.

### 3. Get all / bulk write

```python
all_vals = c.get_all()
c.set_all({"theme": "dark", "font_size": 12})
c.save()
```

### 4. List and check

```python
names = c.list()            # or c.keys()
if c.has("theme"):
    print(c.get("theme"))
c.items()                   # (name, value) pairs
c.values()                  # values only
```

### 5. Add and delete

```python
c.add("version", 1)
c.add("debug_mode", False)
c.save()

# Remove from data only; reload brings back default
c.delete("font_size")

# Remove from data and structure; permanent
c.delete("debug_mode", from_structure=True)
c.save()
```

### 6. Reset and reload

```python
c.clear()       # reset all to structure defaults
c.save()

c.reload()      # re-read from file
```

### 7. Logging

```python
c.info("Config loaded")
c.warn("Warning: old format")
c.error("Could not write file")
c.critical("Critical error")

# Only when debug is on
core_config["debug"] = True   # all Core instances
c.debug = True                # this Core only
c.log_debug("theme = %s", c.get("theme"))
```

### 8. File formats

| Extension      | Format | Description                                                   |
| -------------- | ------ | ------------------------------------------------------------- |
| `.json`        | JSON   | Key–value.                                                    |
| `.conf` / none | Conf   | `key=value` or `key: value`, `[section]`, `#` / `;` comments. |

To force a format:

```python
c = Core("config/settings.conf", VARS, format="conf")
c = Core("config/settings.json", VARS, format="json")
```

Sectioned conf: use `"ui.theme": "dark"` in structure → file has `[ui]` and `theme=dark`.

---

## Command reference

| Action            | Command                                                              |
| ----------------- | -------------------------------------------------------------------- |
| Get value         | `c.get("name")`                                                      |
| Set value         | `c.set("name", value)`                                               |
| Get all           | `c.get_all()`                                                        |
| Set all           | `c.set_all({"a": 1})`                                                |
| List names        | `c.list()` / `c.keys()`                                              |
| Has key?          | `c.has("name")`                                                      |
| Pairs / values    | `c.items()`, `c.values()`                                            |
| Add variable      | `c.add("name", default)`                                             |
| Delete            | `c.delete("name")` / `c.delete("name", from_structure=True)`         |
| Reset to defaults | `c.clear()`                                                          |
| Reload from file  | `c.reload()`                                                         |
| Save to file      | `c.save()`                                                           |
| Log               | `c.info()`, `c.warn()`, `c.error()`, `c.critical()`, `c.log_debug()` |
| Debug             | `core_config["debug"] = True/False` or `c.debug = True/False`        |

---

## Full example

```python
from pathlib import Path
from configwrap import Core, core_config

core_config["debug"] = False
CONFIG = Path(__file__).parent / "config" / "app.conf"
VARS = {"theme": "dark", "lang": "en", "sound": True}

c = Core(str(CONFIG), VARS)
c.info("Started: %s", c.file_path)

c.set("theme", "light")
c.set("lang", "tr")
c.save()

print("Current:", c.get_all())
```

This creates or updates `config/app.conf` with `theme`, `lang`, and `sound` according to the structure types.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
