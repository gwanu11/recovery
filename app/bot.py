from __future__ import annotations

import asyncio
import logging

import discord
from discord.ext import commands

from app.config import get_settings
from app.storage import UserStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
intents = discord.Intents.default()
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)
storage = UserStorage()
_bot_started = False


@bot.event
async def on_ready() -> None:
    logger.info("Bot logged in as %s", bot.user)
    try:
        synced = await bot.tree.sync()
        logger.info("Synced %s app commands", len(synced))
    except Exception as exc:
        logger.exception("Failed to sync commands: %s", exc)


@bot.tree.command(name="ping", description="봇 상태 확인")
async def ping(interaction: discord.Interaction) -> None:
    await interaction.response.send_message("Pong!", ephemeral=True)


@bot.tree.command(name="linked_count", description="연결된 사용자 수 확인")
async def linked_count(interaction: discord.Interaction) -> None:
    count = len(storage.get_all_users())
    await interaction.response.send_message(f"현재 연결된 사용자 수: {count}", ephemeral=True)


async def start_bot() -> None:
    global _bot_started
    if _bot_started:
        return
    if not settings.discord_bot_token:
        logger.warning("DISCORD_BOT_TOKEN is missing, bot will not start.")
        return
    _bot_started = True
    asyncio.create_task(bot.start(settings.discord_bot_token))
