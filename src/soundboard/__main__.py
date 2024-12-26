import asyncio
import itertools
import logging
from collections.abc import Sequence
from pathlib import Path

import aiosqlite
import discord
import httpx
from discord.ext import commands

from soundboard.constants import MAX_BUTTONS_PER_MESSAGE, settings
from soundboard.models import Sound
from soundboard.play_button import PlayView

discord.utils.setup_logging(level=logging.getLevelNamesMapping()[settings.log_level])
logger = logging.getLogger(__file__)


SQL_SETUP_SCRIPT = Path("./setup.sql").read_text()
DATA_DIR = Path(settings.sound_data_dir)


class SoundBoard(commands.Cog):
    """Soundboard cog."""

    def __init__(self, bot: commands.Bot, db: aiosqlite.Connection) -> None:
        self.bot = bot
        self.client = httpx.AsyncClient()
        self.db = db
        self.messages: dict[int, PlayView] = {}

    @property
    def channel(self) -> discord.TextChannel:
        """Get the channel object for the soundboard button channel."""
        channel = self.bot.get_channel(settings.discord_soundboard_channel_id)
        assert channel is not None and isinstance(channel, discord.TextChannel)
        return channel

    async def _load_metadata(self) -> list[Sound]:
        """Load sound metadata from db."""
        async with self.db.execute("SELECT id, custom_id, filename, size, added_by, message_id from sound") as cursor:
            sounds = [Sound(**row) async for row in cursor]
            logger.debug(f"Sounds at startup: {sounds}")
            return sounds

    async def create_button_messages(self, sounds: Sequence[Sound]) -> None:
        """
        Add buttons to soundboard.

        Adds to existing messages if there is space, otherwise sends new messages.
        """
        i = 0
        for msg_id, view in self.messages.items():
            num_to_add = MAX_BUTTONS_PER_MESSAGE - len(view.children)
            for sound in sounds[i : i + num_to_add]:
                view.add_sound(sound)
            await self._assign_sounds_to_message(sounds, msg_id)
            msg = await self.channel.fetch_message(msg_id)

            await msg.edit(view=view)
            i += num_to_add

        # left over
        for chunk in itertools.batched(sounds[i:], n=MAX_BUTTONS_PER_MESSAGE):
            view = PlayView(chunk)
            msg = await self.channel.send(view=view)
            self.messages[msg.id] = view
            await self._assign_sounds_to_message(chunk, msg.id)

    async def _assign_sounds_to_message(self, sounds: Sequence[Sound], message_id: int) -> None:
        sound_ids = [sound.id for sound in sounds]
        # `sqlite3` doesn't support parameterizing lists, so manually insert
        # a bunch of `?` into the query. the max amount of parameters is 250_000 on
        # my machine, and there will probably be less than that many sounds.
        # safety: only adding `"?"`, not any user values
        args = ",".join("?" * len(sounds))
        query = f"update sound set message_id = ? where id in ({args})"  # noqa: S608
        await self.db.execute(query, (message_id, *sound_ids))
        await self.db.commit()

    @commands.Cog.listener("on_ready")
    async def send_startup_messages(self) -> None:
        """Send messages on startup with buttons to trigger sounds."""
        logger.debug("Beginning startup.")

        sounds = await self._load_metadata()

        if len(sounds) == 0:
            logger.debug("No sounds: skipping.")
        elif len(to_send := [sound for sound in sounds if sound.message_id is None]) > 0:
            # send new messages
            logger.debug(f"Sending play buttons for {to_send}.")
            await self.create_button_messages(to_send)
        else:
            logger.debug("Messages already present: skipping.")

        logger.info("Startup finished.")

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        """Ping command for testing."""
        await ctx.send("pong")

    async def _save_sound(self, attachment: discord.Attachment, added_by: int) -> Sound:
        """Persist sound and sound metadata."""
        # need to set custom_id in order to make persistent views. just use the filename
        await attachment.save(DATA_DIR / "sounds" / attachment.filename)
        async with self.db.execute(
            "INSERT INTO sound (custom_id, filename, size, added_by) VALUES (?, ?, ?, ?) RETURNING id",
            (attachment.filename, attachment.filename, attachment.size, str(added_by)),
        ) as cursor:
            row = await cursor.fetchone()
            assert row is not None
            id = row["id"]
            return Sound(id=id, custom_id=attachment.filename, filename=attachment.filename, size=attachment.size, added_by = str(added_by))

    @commands.command()
    async def add(self, ctx: commands.Context) -> None:
        """Add sounds to the soundboard."""
        embed = discord.Embed(title="Adding Sounds")

        if len(ctx.message.attachments) == 0:
            embed.description = "No audio files provided"
        elif len(ctx.message.attachments) > MAX_BUTTONS_PER_MESSAGE:
            embed.description = "Can only add up to 25 sounds at once."
        else:
            for attachment in ctx.message.attachments:
                if attachment.size > settings.sound_max_size:
                    embed.add_field(name=attachment.filename, value=f"Skipping: too large ({attachment.size}).")
                    logger.debug(f"Skipping {attachment.filename}: too large ({attachment.size}).")
                    continue

                logger.debug(f"Saving {attachment.filename} sent by {ctx.author.name} ({ctx.author.id}).")
                sound = await self._save_sound(attachment, ctx.author.id)
                embed.add_field(name=attachment.filename, value="Added successfully.")

                await self.create_button_messages([sound])

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
