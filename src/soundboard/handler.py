from __future__ import annotations

from typing import Callable, Optional
from dataclasses import dataclass

from httpx import AsyncClient

from soundboard.constants import settings
from soundboard.models import (
    ApplicationCommandOptionType,
    ApplicationCommandType,
    Interaction,
    InteractionResponseFlags,
    InteractionResponseType,
)


@dataclass
class Command:
    name: str
    description: str
    type: ApplicationCommandType
    options: list[Option]
    func: Callable


@dataclass
class Option:
    name: str
    type: ApplicationCommandOptionType
    description: str = "..."
    required: bool = False


class CommandHandler:
    def __init__(self):
        self.commands: dict[str, Command] = {}

    def register(
        self,
        name: str,
        description: str,
        application_command_type: ApplicationCommandType = ApplicationCommandType.chat_input,
        options: Optional[list[Option]] = None,
    ):
        if options is None:
            options = []

        if (
            application_command_type is ApplicationCommandType.message
            and description != ""
        ):
            raise ValueError(
                "description argument must be empty when creating Message Commands"
            )

        def inner(func):
            self.commands[name] = Command(
                name, description, application_command_type, options, func
            )
            return func

        return inner

    async def run(self, interaction: Interaction, http: AsyncClient):
        assert interaction.data is not None

        name = interaction.data.name
        func = self.commands.get(name)

        if func is None:
            raise ValueError(f"Invalid command: {name}")

        return await func.func(interaction, http)


handler = CommandHandler()


@handler.register("hello", "Say hello")
async def hello(interaction: Interaction, _: AsyncClient):
    user_id = interaction.member.user.id
    return {
        "type": InteractionResponseType.channel_message_with_source,
        "data": {
            "content": f"Hello <@!{user_id}>",
            "flags": InteractionResponseFlags.ephemeral,
        },
    }


@handler.register("sounds", "List sounds")
async def list_sounds(interaction: Interaction, http: AsyncClient):
    """List sounds available for play immediately."""

    r = await http.get(f"/guilds/{interaction.guild_id}/soundboard-sounds")
    headers = r.headers.items()
    print({k : v for k, v in headers if "x-ratelimit" in k})
    data = r.json()
    print(data)

    return {
        "type": InteractionResponseType.channel_message_with_source,
        "data": {"content": "e", "flags": InteractionResponseFlags.ephemeral},
    }
