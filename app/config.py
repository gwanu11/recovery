from functools import lru_cache
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseModel):
    discord_client_id: str = os.getenv("DISCORD_CLIENT_ID", "")
    discord_client_secret: str = os.getenv("DISCORD_CLIENT_SECRET", "")
    discord_bot_token: str = os.getenv("DISCORD_BOT_TOKEN", "")
    discord_redirect_uri: str = os.getenv("DISCORD_REDIRECT_URI", "http://localhost:10000/callback")
    base_url: str = os.getenv("BASE_URL", "http://localhost:10000")
    session_secret: str = os.getenv("SESSION_SECRET", "dev_secret_change_me")
    bot_guild_id: str = os.getenv("BOT_GUILD_ID", "")
    data_file: str = os.getenv("DATA_FILE", "data/users.json")


@lru_cache
def get_settings() -> Settings:
    return Settings()
