import asyncio
import logging
from pathlib import Path

import discord
import httpx
from discord.ext import commands

from soundboard.constants import settings

discord.utils.setup_logging(level=logging.getLevelNamesMapping()[settings.log_level])
logger = logging.getLogger(__file__)


class SoundBoard(commands.Cog):
    """Soundboard cog."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.client = httpx.AsyncClient()

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        """Ping command for testing."""
        await ctx.send("pong")

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
                await attachment.save(Path(settings.sound_location) / attachment.filename)
                embed.add_field(name=attachment.filename, value="Added successfully.")

        await ctx.send(embed=embed)


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)


async def main() -> None:
    """Main function."""
    async with bot:
        await bot.add_cog(SoundBoard(bot))
        await bot.start(settings.discord_token)


asyncio.run(main())
