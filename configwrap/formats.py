"""File formats: JSON, conf (key=value, [section])."""
import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, Protocol


class FormatHandler(Protocol):
    def load(self, path: Path) -> Dict[str, Any]: ...
    def save(self, path: Path, data: Dict[str, Any]) -> None: ...


class JsonFormat:
    def load(self, path: Path) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, path: Path, data: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


class ConfFormat:
    """key: value or key=value; [section]; # ; comment."""
    KEY_VALUE = re.compile(r"^([^#;=:\s]+)\s*[:=]\s*(.*)$")

    def load(self, path: Path) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        section: Optional[str] = None
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                raw = line.strip()
                if not raw or raw[:1] in "#;":
                    continue
                if raw.startswith("[") and raw.endswith("]"):
                    section = raw[1:-1].strip()
                    continue
                m = self.KEY_VALUE.match(raw)
                if m:
                    k, v = m.group(1).strip(), m.group(2).strip()
                    full = f"{section}.{k}" if section else k
                    result[full] = self._cast(v)
        return result

    def _cast(self, raw: str) -> Any:
        raw = raw.strip()
        if raw.lower() in ("true", "yes", "on"):
            return True
        if raw.lower() in ("false", "no", "off"):
            return False
        for fn in (int, float):
            try:
                return fn(raw)
            except ValueError:
                pass
        return raw

    def save(self, path: Path, data: Dict[str, Any]) -> None:
        by_sec: Dict[str, Dict[str, Any]] = {}
        for k, v in data.items():
            if "." in k:
                sec, name = k.split(".", 1)
                by_sec.setdefault(sec, {})[name] = v
            else:
                by_sec.setdefault("", {})[k] = v
        lines = []
        if "" in by_sec:
            lines.extend(f"{k}={self._fmt(v)}" for k, v in by_sec[""].items())
        for sec in sorted(by_sec.keys()):
            if sec:
                lines.append(f"\n[{sec}]")
                lines.extend(f"{k}={self._fmt(v)}" for k, v in by_sec[sec].items())
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines).strip() + "\n")

    def _fmt(self, value: Any) -> str:
        return "true" if value is True else "false" if value is False else str(value)


def _css_var_to_key(css_name: str) -> str:
    """--ui-accent-color -> ui.accent_color, --font-size -> font_size."""
    name = css_name.strip()
    if name.startswith("--"):
        name = name[2:]
    parts = name.split("-")
    if len(parts) <= 1:
        return name.replace("-", "_")
    if len(parts) == 2:
        return "_".join(parts)
    return parts[0] + "." + "_".join(parts[1:])


def _key_to_css_var(key: str) -> str:
    """ui.accent_color -> --ui-accent-color, accent_color -> --accent-color."""
    name = key.replace(".", "-").replace("_", "-")
    return "--" + name


class CssVarsFormat:
    """CSS custom properties: :root { --var-name: value; }. Keys as ui.accent_color."""

    ROOT_BLOCK = re.compile(
        r":root\s*\{([^}]*)\}",
        re.DOTALL | re.IGNORECASE,
    )
    VAR_LINE = re.compile(
        r"--([a-zA-Z0-9_-]+)\s*:\s*([^;]+);",
    )

    def load(self, path: Path) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        if not path.exists():
            return result
        text = path.read_text(encoding="utf-8")
        for block in self.ROOT_BLOCK.finditer(text):
            for m in self.VAR_LINE.finditer(block.group(1)):
                css_name = "--" + m.group(1)
                raw = m.group(2).strip().strip('"\'')
                result[_css_var_to_key(css_name)] = self._cast(raw)
        return result

    def _cast(self, raw: str) -> Any:
        raw = raw.strip()
        if raw.lower() in ("true", "yes", "on"):
            return True
        if raw.lower() in ("false", "no", "off"):
            return False
        for fn in (int, float):
            try:
                return fn(raw)
            except ValueError:
                pass
        return raw

    def save(self, path: Path, data: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [":root {"]
        for k, v in sorted(data.items()):
            var_name = _key_to_css_var(k)
            lines.append(f"  {var_name}: {self._fmt(v)};")
        lines.append("}")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _fmt(self, value: Any) -> str:
        if isinstance(value, str) and (" " in value or ";" in value or value.startswith("var(")):
            return f'"{value}"'
        return "true" if value is True else "false" if value is False else str(value)


def get_format_for_path(path: Path) -> FormatHandler:
    suf = path.suffix.lower()
    if suf == ".json":
        return JsonFormat()
    if suf == ".css":
        return CssVarsFormat()
    return ConfFormat()
