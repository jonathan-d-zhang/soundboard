import asyncio
import itertools
import logging
from collections.abc import Sequence
from pathlib import Path

import aiosqlite
import discord
import httpx
from discord.ext import commands

from soundboard.constants import settings
from soundboard.models import Sound
from soundboard.play_button import PlayView

discord.utils.setup_logging(level=logging.getLevelNamesMapping()[settings.log_level])
logger = logging.getLogger(__file__)


SQL_SETUP_SCRIPT = Path("./setup.sql").read_text()
MAX_BUTTONS_PER_MESSAGE = 25
DATA_DIR = Path(settings.sound_data_dir)


class SoundBoard(commands.Cog):
    """Soundboard cog."""

    def __init__(self, bot: commands.Bot, db: aiosqlite.Connection) -> None:
        self.bot = bot
        self.client = httpx.AsyncClient()
        self.db = db
        self.sounds: list[Sound] = []

    async def _load_metadata(self) -> list[Sound]:
        """Load sound metadata from db."""
        async with self.db.execute("SELECT id, custom_id, filename, size, added_by, message_id from sound") as cursor:
            sounds = [Sound(**row) async for row in cursor]
            logger.debug(f"Sounds at startup: {sounds}")
            return sounds

    async def _assign_sounds_to_message(self, sounds: Sequence[Sound], message: discord.Message) -> None:
        sound_ids = [sound.id for sound in sounds]

        # `sqlite3` doesn't support parameterizing lists, so manually insert
        # a bunch of `?` into the query. the max amount of parameters is 250_000 on
        # my machine, and there will probably be less than that many sounds.
        # safety: only adding `"?"`, not any user values
        args = ",".join("?" * len(sounds))
        query = f"update sound set message_id = ? where id in ({args})"  # noqa: S608
        await self.db.execute(query, [message.id, *sound_ids])
        await self.db.commit()

    @commands.Cog.listener("on_ready")
    async def send_button_messages(self) -> None:
        """
        Send messages on startup with buttons to trigger sounds.

        Sends a new set of messages if any sounds are missing messages. This
        may duplicate sounds to multiple messages.
        """
        logger.debug("Beginning startup.")

        self.sounds = await self._load_metadata()

        if len(self.sounds) == 0:
            logger.debug("No sounds: skipping.")
        elif any(sound.message_id is None for sound in self.sounds):
            # send new messages
            logger.debug("Sending play buttons.")
            channel = self.bot.get_channel(settings.discord_soundboard_channel_id)
            assert channel is not None and isinstance(channel, discord.TextChannel)

            for chunk in itertools.batched(self.sounds, n=MAX_BUTTONS_PER_MESSAGE):
                msg = await channel.send(view=PlayView(chunk))
                await self._assign_sounds_to_message(chunk, msg)
        else:
            logger.debug("Messages already present: skipping.")

        logger.info("Startup finished.")

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        """Ping command for testing."""
        await ctx.send("pong")

    async def _save_sound(self, attachment: discord.Attachment, added_by: int) -> None:
        """Persist sound and sound metadata."""
        # need to set custom_id in order to make persistent views. just use the filename
        await attachment.save(DATA_DIR / "sounds" / attachment.filename)
        await self.db.execute(
            "INSERT INTO sound (custom_id, filename, size, added_by) VALUES (?, ?, ?, ?)",
            [attachment.filename, attachment.filename, attachment.size, str(added_by)],
        )
        await self.db.commit()

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
                    logger.debug(f"Skipping {attachment.filename}: too large ({attachment.size}).")
                    continue

                logger.debug(f"Saving {attachment.filename} sent by {ctx.author.name} ({ctx.author.id}).")
                await self._save_sound(attachment, ctx.author.id)
                embed.add_field(name=attachment.filename, value="Added successfully.")

            # TODO: update soundboard play views

        await ctx.send(embed=embed)


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)


async def _db_setup(path: str | Path) -> aiosqlite.Connection:
    # I would like to have autocommit=False here, but I can't set the
    # journal_mode from within a transaction. just set it later
    db = await aiosqlite.connect(path, check_same_thread=False)
    db.row_factory = aiosqlite.Row

    await db.executescript(SQL_SETUP_SCRIPT)
    await db.commit()

    # aiosqlite does not proxy the autocommit property...
    db._conn.autocommit = False

    return db


async def main() -> None:
    """Main function."""
    db = await _db_setup(DATA_DIR / "metadata.db")

    sounds_dir = DATA_DIR / "sounds"
    sounds_dir.mkdir(exist_ok=True)

    async with bot:
        await bot.add_cog(SoundBoard(bot, db))
        await bot.start(settings.discord_token)


asyncio.run(main())
