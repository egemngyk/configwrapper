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


if __name__ == "__main__":
    main()
