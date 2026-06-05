"""Small JSON persistence helpers for ACV backend services."""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable, Mapping
from datetime import datetime
from pathlib import Path
from typing import Any


class JsonStorageService:
    """Read/write JSON files with atomic replace and optional backups."""

    def __init__(self, root_dir: str | Path = "data"):
        self.root_dir = Path(root_dir)

    def read_json(self, path: str | Path, default: Any | None = None) -> Any:
        json_path = self._resolve(path)
        if not json_path.exists():
            if default is None:
                raise FileNotFoundError(json_path)
            self.write_json(json_path, default)
            return default

        with json_path.open("r", encoding="utf-8") as json_file:
            return json.load(json_file)

    def write_json(
        self,
        path: str | Path,
        payload: Any,
        *,
        backup: bool = False,
        validator: Callable[[Mapping[str, Any]], object] | None = None,
    ) -> Path:
        json_path = self._resolve(path)
        if validator is not None:
            if not isinstance(payload, Mapping):
                raise ValueError("JSON payload must be an object for validation")
            validator(payload)

        json_path.parent.mkdir(parents=True, exist_ok=True)
        if backup and json_path.exists():
            backup_dir = json_path.parent / ".backup"
            backup_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2(json_path, backup_dir / f"{json_path.stem}.{stamp}{json_path.suffix}")

        temp_path = json_path.with_suffix(json_path.suffix + ".tmp")
        with temp_path.open("w", encoding="utf-8") as json_file:
            json.dump(payload, json_file, ensure_ascii=False, indent=2)
            json_file.write("\n")
        temp_path.replace(json_path)
        return json_path

    def delete_json(self, path: str | Path, *, backup: bool = True) -> bool:
        json_path = self._resolve(path)
        if not json_path.exists():
            return False
        if backup:
            self.write_json(json_path, self.read_json(json_path), backup=True)
        json_path.unlink()
        return True

    def _resolve(self, path: str | Path) -> Path:
        resolved = Path(path)
        if resolved.is_absolute() or str(resolved).startswith(str(self.root_dir)):
            return resolved
        return self.root_dir / resolved


storage_service = JsonStorageService()
