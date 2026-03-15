"""Variable manager. debug=core_config or override; info/warn/error/critical always on."""
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

from configwrap.structure import Structure
from configwrap.formats import JsonFormat, ConfFormat, get_format_for_path, FormatHandler

core_config: Dict[str, Any] = {"debug": False}

_log = logging.getLogger("configwrap.core")
if not _log.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(levelname)s [%(name)s] %(message)s"))
    _log.addHandler(h)
    _log.setLevel(logging.DEBUG)


def _fmt(format_or_none: Union[str, None], path: Path) -> FormatHandler:
    if format_or_none == "json":
        return JsonFormat()
    if format_or_none == "conf":
        return ConfFormat()
    return get_format_for_path(path)


class Core:
    """File + structure. format=None → from extension. debug=None → core_config."""

    def __init__(
        self,
        file_path: str,
        structure: Union[Structure, Dict[str, Any]],
        format: Union[str, None] = None,
        debug: Union[bool, None] = None,
    ):
        self._path = Path(file_path)
        self._structure = Structure(structure) if isinstance(structure, dict) else structure
        self._handler = _fmt(format, self._path)
        self._debug = debug if debug is not None else core_config.get("debug", False)
        self._data: Dict[str, Any] = {}
        self.load()

    def _d(self, msg: str) -> None:
        if self._debug:
            _log.debug(msg)

    @property
    def debug(self) -> bool:
        return self._debug

    @debug.setter
    def debug(self, v: bool) -> None:
        self._debug = bool(v)

    def log_debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        if self._debug:
            _log.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        _log.info(msg, *args, **kwargs)

    def warn(self, msg: str, *args: Any, **kwargs: Any) -> None:
        _log.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        _log.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        _log.critical(msg, *args, **kwargs)

    def load(self) -> None:
        if self._path.exists():
            self._data = self._structure.validate(self._handler.load(self._path))
            self._d(f"load {self._path} -> {len(self._data)}")
        else:
            self._data = self._structure.defaults().copy()
            self._d(f"load (missing) -> default {len(self._data)}")

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._handler.save(self._path, self._data)
        self._d(f"save {self._path} ({len(self._data)})")

    def get(self, name: str) -> Any:
        self._structure.get_field(name)
        v = self._data[name]
        self._d(f"get {name!r} -> {v!r}")
        return v

    def set(self, name: str, value: Any) -> None:
        f = self._structure.get_field(name)
        if value is not None and not isinstance(value, f.type):
            try:
                value = f.type(value)
            except (TypeError, ValueError):
                raise TypeError(f"{name!r}: expected {f.type}")
        self._data[name] = value
        self._d(f"set {name!r} = {value!r}")

    def get_all(self) -> Dict[str, Any]:
        self._d("get_all")
        return self._data.copy()

    def set_all(self, data: Dict[str, Any]) -> None:
        self._data = self._structure.validate({**self._data, **data})
        self._d(f"set_all {list(data.keys())}")

    def list(self) -> List[str]:
        self._d("list")
        return list(self._data.keys())

    def keys(self) -> List[str]:
        return self.list()

    def has(self, name: str) -> bool:
        out = name in self._data
        self._d(f"has {name!r} -> {out}")
        return out

    def items(self) -> List[Tuple[str, Any]]:
        self._d("items")
        return list(self._data.items())

    def values(self) -> List[Any]:
        self._d("values")
        return list(self._data.values())

    def clear(self) -> None:
        self._data = self._structure.defaults().copy()
        self._d("clear")

    def reload(self) -> None:
        self.load()

    def add(self, name: str, value: Any) -> None:
        self._structure.add_field(name, value)
        self._data[name] = value
        self._d(f"add {name!r} = {value!r}")

    def delete(self, name: str, from_structure: bool = False) -> None:
        if name in self._data:
            del self._data[name]
        if from_structure and self._structure.has_field(name):
            self._structure.remove_field(name)
        self._d(f"delete {name!r} from_structure={from_structure}")

    @property
    def file_path(self) -> Path:
        return self._path

    @property
    def structure(self) -> Structure:
        return self._structure
