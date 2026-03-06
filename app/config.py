from __future__ import annotations

from functools import lru_cache
import os

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    discord_client_id: str = os.getenv("DISCORD_CLIENT_ID", "")
    discord_client_secret: str = os.getenv("DISCORD_CLIENT_SECRET", "")
    discord_bot_token: str = os.getenv("DISCORD_BOT_TOKEN", "")
    discord_redirect_uri: str = os.getenv("DISCORD_REDIRECT_URI", "http://localhost:10000/callback")
    base_url: str = os.getenv("BASE_URL", "http://localhost:10000")
    session_secret: str = os.getenv("SESSION_SECRET", "change_me")
    allowed_admin_user_id: int = int(os.getenv("ALLOWED_ADMIN_USER_ID", "0"))
    database_path: str = os.getenv("DATABASE_PATH", "data/app.db")


@lru_cache
def get_settings() -> Settings:
    return Settings()
