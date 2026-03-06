from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from app.config import get_settings


class UserStorage:
    def __init__(self) -> None:
        self.db_path = Path(get_settings().database_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS linked_users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT,
                    global_name TEXT,
                    access_token TEXT NOT NULL,
                    refresh_token TEXT,
                    token_type TEXT,
                    expires_in INTEGER,
                    scope TEXT,
                    linked_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def save_user(self, payload: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO linked_users (
                    user_id, username, global_name, access_token, refresh_token,
                    token_type, expires_in, scope
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username=excluded.username,
                    global_name=excluded.global_name,
                    access_token=excluded.access_token,
                    refresh_token=excluded.refresh_token,
                    token_type=excluded.token_type,
                    expires_in=excluded.expires_in,
                    scope=excluded.scope,
                    linked_at=CURRENT_TIMESTAMP
                """,
                (
                    payload["user_id"],
                    payload.get("username"),
                    payload.get("global_name"),
                    payload["access_token"],
                    payload.get("refresh_token"),
                    payload.get("token_type"),
                    payload.get("expires_in"),
                    payload.get("scope"),
                ),
            )
            conn.commit()

    def update_tokens(self, user_id: str, access_token: str, refresh_token: str | None, expires_in: int | None, scope: str | None, token_type: str | None) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE linked_users
                SET access_token = ?,
                    refresh_token = COALESCE(?, refresh_token),
                    expires_in = COALESCE(?, expires_in),
                    scope = COALESCE(?, scope),
                    token_type = COALESCE(?, token_type)
                WHERE user_id = ?
                """,
                (access_token, refresh_token, expires_in, scope, token_type, user_id),
            )
            conn.commit()

    def get_all_users(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT user_id, username, global_name, access_token, refresh_token,
                       token_type, expires_in, scope, linked_at
                FROM linked_users
                ORDER BY linked_at DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def count_users(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS count FROM linked_users").fetchone()
        return int(row["count"])
