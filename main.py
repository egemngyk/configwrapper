"""Example: Core + file + structure. Override core_config["debug"] from main."""
from pathlib import Path

from configwrap import Core, core_config

BASE = Path(__file__).parent
core_config["debug"] = False

CONFIG = BASE / "config" / "app.conf"
VARS = {
    "theme": "dark",
    "font_size": 14,
    "ui.accent_color": "#3498db",
    "ui.sidebar_width": 240,
}

CSS_BASE = BASE / "config" / "themes" / "base.css"
CSS_THEME = BASE / "config" / "themes" / "app.css"
CSS_VARS = {
    "theme": "dark",
    "font_size": 14,
    "ui.accent_color": "#3498db",
    "ui.sidebar_width": 240,
}


def main():
    c = Core(str(CONFIG), VARS)
    c.info("Config loaded: %s", c.file_path)

    c.set("theme", "light")
    c.set("ui.accent_color", "#e74c3c")
    c.save()

    c.add("version", 1)
    c.delete("font_size")
    c.delete("ui.debug", from_structure=True)
    c.save()


def main_css():
    """CSS vars: parent base.css, child app.css. Değerler Python get/set ile."""
    parent = Core(str(CSS_BASE), CSS_VARS, format="css")
    theme = Core(str(CSS_THEME), CSS_VARS, format="css", parent=str(CSS_BASE))

    theme.info("CSS theme (parent=base): %s", theme.file_path)
    theme.info("  theme = %s", theme.get("theme"))
    theme.info("  ui.accent_color = %s", theme.get("ui.accent_color"))

    theme.set("theme", "light")
    theme.set("ui.accent_color", "#e74c3c")
    theme.save()

    theme.info("Saved app.css (parent değerleri + override'lar) -> :root { --var: value; }")


if __name__ == "__main__":
    main()
    main_css()
