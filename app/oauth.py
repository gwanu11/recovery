from __future__ import annotations

from urllib.parse import urlencode

import httpx

from app.config import get_settings

DISCORD_API_BASE = "https://discord.com/api/v10"


class DiscordOAuth:
    def __init__(self) -> None:
        self.settings = get_settings()

    def get_authorize_url(self, state: str) -> str:
        params = {
            "client_id": self.settings.discord_client_id,
            "response_type": "code",
            "redirect_uri": self.settings.discord_redirect_uri,
            "scope": "identify guilds.join",
            "state": state,
            "prompt": "consent",
        }
        return f"{DISCORD_API_BASE}/oauth2/authorize?{urlencode(params)}"

    async def exchange_code(self, code: str) -> dict:
        data = {
            "client_id": self.settings.discord_client_id,
            "client_secret": self.settings.discord_client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.settings.discord_redirect_uri,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{DISCORD_API_BASE}/oauth2/token",
                data=data,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()

    async def refresh_access_token(self, refresh_token: str) -> dict:
        data = {
            "client_id": self.settings.discord_client_id,
            "client_secret": self.settings.discord_client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{DISCORD_API_BASE}/oauth2/token",
                data=data,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()

    async def get_current_user(self, access_token: str) -> dict:
        headers = {"Authorization": f"Bearer {access_token}"}

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                f"{DISCORD_API_BASE}/users/@me",
                headers=headers,
            )
            response.raise_for_status()
            return response.json()

    async def add_user_to_guild(self, guild_id: int, user_id: str, access_token: str) -> int:
        headers = {
            "Authorization": f"Bot {self.settings.discord_bot_token}",
            "Content-Type": "application/json",
        }
        payload = {"access_token": access_token}

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.put(
                f"{DISCORD_API_BASE}/guilds/{guild_id}/members/{user_id}",
                headers=headers,
                json=payload,
            )
            return response.status_code
