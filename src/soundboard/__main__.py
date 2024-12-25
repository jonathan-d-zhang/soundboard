import asyncio
import logging
from pathlib import Path

import aiosqlite
import discord
import httpx
from discord.ext import commands

from soundboard.constants import settings

discord.utils.setup_logging(level=logging.getLevelNamesMapping()[settings.log_level])
logger = logging.getLogger(__file__)


SQL_SETUP_SCRIPT = Path("./setup.sql").read_text()


class SoundBoard(commands.Cog):
    """Soundboard cog."""

    def __init__(self, bot: commands.Bot, db: aiosqlite.Connection) -> None:
        self.bot = bot
        self.client = httpx.AsyncClient()
        self.db = db

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        """Ping command for testing."""
        await ctx.send("pong")

    async def _save_sound(self, attachment: discord.Attachment, added_by: int) -> None:
        """Persist sound and sound metadata."""
        # need to set custom_id in order to make persistent views. just use the filename
        await attachment.save(Path(settings.sound_location) / attachment.filename)
        async with self.db.execute(
            "INSERT INTO sounds (custom_id, filename, size, added_by) VALUES (?, ?, ?, ?)",
            [attachment.filename, attachment.filename, attachment.size, str(added_by)],
        ):
            pass

    @commands.command()
    async def add(self, ctx: commands.Context) -> None:
        """Add sounds to the soundboard."""
        embed = discord.Embed(title="Adding Sounds")

        if len(ctx.message.attachments) == 0:
            embed.description = "No audio files provided"
        elif len(ctx.message.attachments) > 25:
            embed.description = "Can only add up to 25 sounds at once."
        else:
            for attachment in ctx.message.attachments:
                if attachment.size > settings.sound_max_size:
                    embed.add_field(name=attachment.filename, value=f"Skipping: too large ({attachment.size}).")
                    continue

                await self._save_sound(attachment, ctx.author.id)
                embed.add_field(name=attachment.filename, value="Added successfully.")

        await ctx.send(embed=embed)


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)


async def _db_setup(path: str | Path) -> aiosqlite.Connection:
    db = aiosqlite.connect(path)

    async with db.executescript(SQL_SETUP_SCRIPT) as _:
        pass

    return db


async def main() -> None:
    """Main function."""
    db = await _db_setup(settings.sound_metadata_db_location)

    async with bot:
        await bot.add_cog(SoundBoard(bot, db))
        await bot.start(settings.discord_token)


asyncio.run(main())
