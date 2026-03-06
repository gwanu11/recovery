from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "users.db"


class UserStorage:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
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
                    linked_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def save_user(self, user_data: dict[str, Any]) -> None:
        linked_at = datetime.now(timezone.utc).isoformat()

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO linked_users (
                    user_id, username, global_name,
                    access_token, refresh_token, token_type,
                    expires_in, scope, linked_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username=excluded.username,
                    global_name=excluded.global_name,
                    access_token=excluded.access_token,
                    refresh_token=excluded.refresh_token,
                    token_type=excluded.token_type,
                    expires_in=excluded.expires_in,
                    scope=excluded.scope,
                    linked_at=excluded.linked_at
                """,
                (
                    str(user_data.get("user_id")),
                    user_data.get("username"),
                    user_data.get("global_name"),
                    user_data.get("access_token"),
                    user_data.get("refresh_token"),
                    user_data.get("token_type"),
                    user_data.get("expires_in"),
                    user_data.get("scope"),
                    linked_at,
                ),
            )
            conn.commit()

    def count_users(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS count FROM linked_users").fetchone()
            return int(row["count"]) if row else 0

    def get_all_users(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    user_id, username, global_name,
                    access_token, refresh_token,
                    token_type, expires_in, scope, linked_at
                FROM linked_users
                ORDER BY linked_at DESC
                """
            ).fetchall()
            return [dict(row) for row in rows]

    def update_tokens(
        self,
        user_id: str,
        access_token: str,
        refresh_token: str | None = None,
        expires_in: int | None = None,
        scope: str | None = None,
        token_type: str | None = None,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE linked_users
                SET
                    access_token = ?,
                    refresh_token = COALESCE(?, refresh_token),
                    expires_in = COALESCE(?, expires_in),
                    scope = COALESCE(?, scope),
                    token_type = COALESCE(?, token_type)
                WHERE user_id = ?
                """,
                (
                    access_token,
                    refresh_token,
                    expires_in,
                    scope,
                    token_type,
                    str(user_id),
                ),
            )
            conn.commit()
