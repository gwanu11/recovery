from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.config import get_settings


class UserStorage:
    def __init__(self) -> None:
        self.path = Path(get_settings().data_file)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")

    def _read(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def save_user(self, discord_user_id: str, payload: dict[str, Any]) -> None:
        data = self._read()
        data[discord_user_id] = payload
        self._write(data)

    def get_all_users(self) -> dict[str, Any]:
        return self._read()
