from collections.abc import Sequence

from discord import ButtonStyle, Interaction, Member
from discord.ui import Button, View

from soundboard.models import Sound


class PlayView(View):
    """Container for soundboard play buttons."""

    def __init__(self, sounds: Sequence[Sound]):
        super().__init__(timeout=None)

        if len(sounds) > 25:
            raise ValueError(f"Can have at most 25 sounds ({len(sounds)} given).")

        for sound in sounds:
            self.add_item(PlayButton(sound))

    async def interaction_check(self, interaction: Interaction) -> bool:
        """Check that the user is connected to a voice channel in the same server."""
        if isinstance(interaction.user, Member) and interaction.user.voice:
            voice_state = interaction.user.voice
            assert voice_state.channel is not None

            if voice_state.channel.guild.id == interaction.guild_id:
                return True

        await interaction.response.send_message(
            "You must be connected to a voice channel in this server!", ephemeral=True
        )

        return False


class PlayButton(Button):
    """Button to play a sound."""

    def __init__(self, sound: Sound, *, style: ButtonStyle = ButtonStyle.secondary):
        self.sound = sound
        super().__init__(style=style, label=sound.filename, custom_id=sound.custom_id)

    async def callback(self, interaction: Interaction) -> None:
        """Play a sound."""
