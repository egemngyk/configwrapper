"""Schema: field name, type, default."""
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Type, Dict, List, Union


@dataclass
class Field:
    name: str
    type: Type
    default: Any = None

    def __post_init__(self):
        if self.default is None and self.type in (int, float, bool):
            self.default = {int: 0, float: 0.0, bool: False}[self.type]


class Structure:
    """Variable schema. Dict or list of Field."""

    def __init__(self, fields: Union[List[Field], Dict[str, Any]]):
        self._fields: Dict[str, Field] = {}
        if isinstance(fields, dict):
            for name, default in fields.items():
                t = type(default) if default is not None else str
                self._fields[name] = Field(name=name, type=t, default=default)
        else:
            for f in fields:
                self._fields[f.name] = f

    @property
    def names(self) -> List[str]:
        return list(self._fields.keys())

    def get_field(self, name: str) -> Field:
        if name not in self._fields:
            raise KeyError(f"Not in schema: {name!r}")
        return self._fields[name]

    def has_field(self, name: str) -> bool:
        return name in self._fields

    def add_field(self, name: str, default: Any) -> None:
        t = type(default) if default is not None else str
        self._fields[name] = Field(name=name, type=t, default=default)

    def remove_field(self, name: str) -> None:
        if name in self._fields:
            del self._fields[name]

    def defaults(self) -> Dict[str, Any]:
        return {n: f.default for n, f in self._fields.items()}

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        out = {}
        for name, field in self._fields.items():
            val = data.get(name, field.default)
            if val is not None and not isinstance(val, field.type):
                try:
                    val = field.type(val)
                except (TypeError, ValueError):
                    raise TypeError(f"{name!r}: expected {field.type}")
            out[name] = val
        for name, val in data.items():
            if name not in self._fields:
                out[name] = val
        return out

    @classmethod
    def from_file(cls, path: str) -> "Structure":
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(path)
        with open(p, "r", encoding="utf-8") as f:
            return cls(json.load(f))
