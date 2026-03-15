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


def get_format_for_path(path: Path) -> FormatHandler:
    return JsonFormat() if path.suffix.lower() == ".json" else ConfFormat()
