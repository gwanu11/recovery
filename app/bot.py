from __future__ import annotations

import asyncio
import logging

import discord
from discord.ext import commands

from app.config import get_settings
from app.oauth import DiscordOAuth
from app.storage import UserStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
intents = discord.Intents.default()
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)
storage = UserStorage()
oauth = DiscordOAuth()
_bot_started = False


@bot.event
async def on_ready() -> None:
    logger.info("Bot logged in as %s", bot.user)
    try:
        synced = await bot.tree.sync()
        logger.info("Synced %s app commands", len(synced))
    except Exception as exc:
        logger.exception("Failed to sync commands: %s", exc)


def is_allowed_admin(user_id: int) -> bool:
    return settings.allowed_admin_user_id and user_id == settings.allowed_admin_user_id


@bot.tree.command(name="핑", description="봇 상태 확인")
async def ping(interaction: discord.Interaction) -> None:
    await interaction.response.send_message("Pong!", ephemeral=True)


@bot.tree.command(name="연동수", description="연동된 사용자 수 확인")
async def linked_count(interaction: discord.Interaction) -> None:
    count = storage.count_users()
    await interaction.response.send_message(f"현재 연동된 사용자 수: {count}", ephemeral=True)


@bot.tree.command(name="복구", description="이 서버에 동의한 사용자들을 다시 추가 시도합니다")
async def restore_members(interaction: discord.Interaction) -> None:
    if not is_allowed_admin(interaction.user.id):
        await interaction.response.send_message("이 명령어를 사용할 권한이 없습니다.", ephemeral=True)
        return

    if interaction.guild_id is None:
        await interaction.response.send_message("서버 안에서만 사용할 수 있습니다.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True, thinking=True)

    users = storage.get_all_users()
    if not users:
        await interaction.followup.send("연동된 사용자가 없습니다.", ephemeral=True)
        return

    added = 0
    already_in = 0
    refreshed = 0
    failed = 0
    failed_users: list[str] = []

    for user in users:
        user_id = str(user["user_id"])
        access_token = user["access_token"]
        refresh_token = user.get("refresh_token")

        status = await oauth.add_user_to_guild(interaction.guild_id, user_id, access_token)

        if status in (201, 204):
            if status == 201:
                added += 1
            else:
                already_in += 1
            continue

        if status == 401 and refresh_token:
            try:
                token_data = await oauth.refresh_access_token(refresh_token)
                new_access_token = token_data["access_token"]
                new_refresh_token = token_data.get("refresh_token")
                storage.update_tokens(
                    user_id=user_id,
                    access_token=new_access_token,
                    refresh_token=new_refresh_token,
                    expires_in=token_data.get("expires_in"),
                    scope=token_data.get("scope"),
                    token_type=token_data.get("token_type"),
                )
                refreshed += 1
                status = await oauth.add_user_to_guild(interaction.guild_id, user_id, new_access_token)
                if status in (201, 204):
                    if status == 201:
                        added += 1
                    else:
                        already_in += 1
                    continue
            except Exception as exc:
                logger.warning("Refresh failed for user %s: %s", user_id, exc)

        failed += 1
        failed_users.append(user_id)

    msg = (
        f"복구 완료\n"
        f"- 새로 추가: {added}\n"
        f"- 이미 참가: {already_in}\n"
        f"- 토큰 갱신: {refreshed}\n"
        f"- 실패: {failed}"
    )
    if failed_users:
        msg += "\n실패한 일부 유저 ID: " + ", ".join(failed_users[:10])

    await interaction.followup.send(msg, ephemeral=True)


async def start_bot() -> None:
    global _bot_started
    if _bot_started:
        return
    if not settings.discord_bot_token:
        logger.warning("DISCORD_BOT_TOKEN is missing, bot will not start.")
        return
    _bot_started = True
    asyncio.create_task(bot.start(settings.discord_bot_token))
