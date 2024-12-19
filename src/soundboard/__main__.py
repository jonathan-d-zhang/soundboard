import asyncio
import logging
import discord
from discord.ext import commands

from soundboard.constants import settings

discord.utils.setup_logging(level=logging.getLevelNamesMapping()[settings.log_level])
logger = logging.getLogger(__file__)


class SoundBoard(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        await ctx.send("pong")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)

async def main():
    async with bot:
        await bot.add_cog(SoundBoard(bot))
        await bot.start(settings.discord_token)

asyncio.run(main())
