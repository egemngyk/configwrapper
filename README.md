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
├── main.py                     # Example / entry point
├── config/                     # Data files (.json, .conf, .css)
│   ├── app.conf
│   ├── theme.json
│   └── themes/
│       ├── base.css           # Base CSS variables (parent)
│       └── app.css            # App theme (child, overrides)
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

| Concept        | Description                                                                                                  |
| -------------- | ------------------------------------------------------------------------------------------------------------ |
| **File**       | Where values are stored (e.g. `config/app.conf`). JSON, conf or CSS vars file.                              |
| **Structure**  | Which variables exist and their defaults. A Python `dict`: `{"theme": "dark", "size": 14}`.                  |
| **Core**       | Ties file and structure together. All operations (`get`, `set`, `save`, etc.) go through Core.              |
| **Parent Core**| Optional parent file/Core. Parent values are merged first; child file overrides only what it defines.       |
| **CSS vars**   | CSS custom properties (`:root { --name: value; }`) mapped to keys like `ui.accent_color`, `font_size`, etc. |

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

| Extension      | Format   | Description                                                              |
| -------------- | -------- | ------------------------------------------------------------------------ |
| `.json`        | JSON     | Key–value.                                                               |
| `.conf` / none | Conf     | `key=value` or `key: value`, `[section]`, `#` / `;` comments.            |
| `.css`         | CSS vars | `:root { --var-name: value; }` custom properties as config key–values.  |

To force a format:

```python
c = Core("config/settings.conf", VARS, format="conf")
c = Core("config/settings.json", VARS, format="json")
c = Core("config/theme.css", VARS, format="css")
```

Sectioned conf: use `"ui.theme": "dark"` in structure → file has `[ui]` and `theme=dark`.

### 9. Parent configs (inheritance)

You can give a Core a **parent** file or another Core. Parent data is loaded first; the child file only overrides keys it defines:

```python
from pathlib import Path
from configwrap import Core

BASE = Path(__file__).parent

PARENT_CONF = BASE / "config" / "base.conf"
CHILD_CONF = BASE / "config" / "app.conf"
VARS = {"theme": "dark", "font_size": 14}

parent = Core(str(PARENT_CONF), VARS)
child = Core(str(CHILD_CONF), VARS, parent=str(PARENT_CONF))  # or parent=parent

# Reads from child if present, otherwise from parent
print(child.get("theme"))

# Only overrides child's file
child.set("theme", "light")
child.save()
```

### 10. CSS variables for themes

`CssVarsFormat` lets you manage **CSS custom properties** (`--var`) from Python using the same API:

```python
from pathlib import Path
from configwrap import Core

BASE = Path(__file__).parent

CSS_BASE = BASE / "config" / "themes" / "base.css"  # parent
CSS_APP = BASE / "config" / "themes" / "app.css"    # child

CSS_VARS = {
    "theme": "dark",
    "font_size": 14,
    "ui.accent_color": "#3498db",
    "ui.sidebar_width": 240,
}

# Parent theme (base variables)
base_theme = Core(str(CSS_BASE), CSS_VARS, format="css")

# App theme inherits from base.css, overrides selected values
app_theme = Core(str(CSS_APP), CSS_VARS, format="css", parent=str(CSS_BASE))

app_theme.info("Theme file: %s", app_theme.file_path)
app_theme.info("  theme = %s", app_theme.get("theme"))
app_theme.info("  ui.accent_color = %s", app_theme.get("ui.accent_color"))

# Only override what you need; the rest stays from the parent
app_theme.set("theme", "light")
app_theme.set("ui.accent_color", "#e74c3c")
app_theme.save()
```

This produces a CSS file like:

```css
:root {
  --font-size: 14;
  --theme: light;
  --ui-accent-color: #e74c3c;
  --ui-sidebar-width: 240;
}
```

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
