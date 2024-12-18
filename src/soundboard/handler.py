from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from httpx import AsyncClient

from soundboard.models import (
    ApplicationCommandOptionType,
    ApplicationCommandType,
    Interaction,
    InteractionResponseType,
    MessageResponseFlags,
)


@dataclass
class Command:
    """Represents a registered command."""

    name: str
    description: str
    type: ApplicationCommandType
    options: list[Option]
    func: CommandFunction


@dataclass
class Option:
    """Parameter for a command."""

    name: str
    type: ApplicationCommandOptionType
    description: str = "..."
    required: bool = False


type CommandFunction = Callable[[Interaction, AsyncClient], Awaitable[dict]]


class CommandHandler:
    """Dispatches commands to command functions by name."""

    def __init__(self):
        self.commands: dict[str, Command] = {}

    def register(
        self,
        name: str,
        description: str,
        application_command_type: ApplicationCommandType = ApplicationCommandType.chat_input,
        options: list[Option] | None = None,
    ) -> Callable[[CommandFunction], CommandFunction]:
        """
        Register a function as a command function.

        When creating a Message Command, `description` must be an empty string.
        """
        if options is None:
            options = []

        if application_command_type is ApplicationCommandType.message and description != "":
            raise ValueError("description argument must be empty when creating Message Commands")

        def inner(func: CommandFunction) -> CommandFunction:
            self.commands[name] = Command(name, description, application_command_type, options, func)
            return func

        return inner

    async def run(self, interaction: Interaction, http: AsyncClient) -> dict:
        """Lookup and run a command function from an interaction."""
        assert interaction.data is not None

        name = interaction.data.name
        func = self.commands.get(name)

        if func is None:
            raise ValueError(f"Invalid command: {name}")

        return await func.func(interaction, http)


handler = CommandHandler()


@handler.register("hello", "Say hello")
async def hello(interaction: Interaction, _: AsyncClient) -> dict:
    """
    Say hello.

    Test function.
    """
    user_id = interaction.member.user.id
    return {
        "type": InteractionResponseType.channel_message_with_source,
        "data": {
            "content": f"Hello <@!{user_id}>",
            "flags": MessageResponseFlags.ephemeral,
        },
    }


@handler.register("sounds", "List sounds")
async def list_sounds(interaction: Interaction, http: AsyncClient) -> dict:
    """List sounds available for play immediately."""
    r = await http.get(f"/guilds/{interaction.guild_id}/soundboard-sounds")
    data = r.json()

    return {
        "type": InteractionResponseType.channel_message_with_source,
        "data": {"content": f"```\n{data}\n```", "flags": MessageResponseFlags.ephemeral},
    }
