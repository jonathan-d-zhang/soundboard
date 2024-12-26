import logging
from collections.abc import Sequence

from discord import ButtonStyle, FFmpegPCMAudio, Interaction, Member, PCMVolumeTransformer, VoiceClient
from discord.ui import Button, View

from soundboard.constants import DATA_DIR, MAX_BUTTONS_PER_MESSAGE
from soundboard.models import Sound

logger = logging.getLogger(__file__)


class PlayView(View):
    """Container for soundboard play buttons."""

    def __init__(self, sounds: Sequence[Sound]):
        super().__init__(timeout=None)

        if len(sounds) > MAX_BUTTONS_PER_MESSAGE:
            raise ValueError(f"Can have at most 25 sounds ({len(sounds)} given).")

        for sound in sounds:
            self.add_item(PlayButton(sound))

    async def interaction_check(self, interaction: Interaction) -> bool:
        """Check that the user is connected to a voice channel in the same server."""
        if isinstance(interaction.user, Member) and interaction.user.voice is not None:
            voice_state = interaction.user.voice
            assert voice_state.channel is not None

            if voice_state.channel.guild.id == interaction.guild_id:
                return True

        await interaction.response.send_message(
            "You must be connected to a voice channel in this server!", ephemeral=True
        )

        return False

    def add_sound(self, sound: Sound) -> None:
        """Helper method to add a sound."""
        self.add_item(PlayButton(sound))

    def is_full(self) -> bool:
        """Check if the view is full."""
        return len(self.children) < MAX_BUTTONS_PER_MESSAGE


class PlayButton(Button):
    """Button to play a sound."""

    def __init__(self, sound: Sound, *, style: ButtonStyle = ButtonStyle.secondary):
        self.sound = sound
        super().__init__(style=style, label=sound.filename, custom_id=sound.custom_id)

    async def callback(self, interaction: Interaction) -> None:
        """Play a sound."""
        # because of `PlayView.interaction_check`, we know the user is
        # connected to a voice channel

        logger.debug(f"Playing {self.sound.filename} requested by {interaction.user.name}.")

        assert (
            isinstance(interaction.user, Member)
            and interaction.user.voice is not None
            and interaction.user.voice.channel is not None
        )
        assert interaction.guild is not None

        if interaction.guild.voice_client is None:
            logger.debug("Not connected to voice channel: connecting.")
            voice_client = await interaction.user.voice.channel.connect()
        else:
            logger.debug("Already connected to voice channel.")
            voice_client = interaction.guild.voice_client
            assert isinstance(voice_client, VoiceClient)

        audio_source = PCMVolumeTransformer(FFmpegPCMAudio(str(DATA_DIR / "sounds" / self.sound.filename)))
        voice_client.play(audio_source, after=lambda e: logger.error(f"Player error: {e}") if e else None)

        await interaction.response.edit_message()
