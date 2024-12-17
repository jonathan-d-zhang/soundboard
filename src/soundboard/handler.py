from __future__ import annotations

from typing import Callable
from dataclasses import dataclass

from httpx import Client

from soundboard.models import (
    ApplicationCommandData,
    ApplicationCommandOptionType,
    Interaction,
    InteractionResponseFlags,
    InteractionResponseType,
)


@dataclass
class Command:
    name: str
    description: str
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

    def register(self, name: str, description: str, options: list[Option]):
        def inner(func):
            self.commands[name] = Command(name, description, options, func)
            return func

        return inner

    def run(self, interaction: Interaction, http: Client):
        assert interaction.data is not None

        name = interaction.data.name
        func = self.commands.get(name)

        if func is None:
            raise ValueError(f"Invalid command: {name}")

        return func.func(interaction, http)


handler = CommandHandler()


@handler.register("hello", "Say hello", [])
def hello(interaction: Interaction, _: Client):
    user_id = interaction.member.user.id
    return {
        "type": InteractionResponseType.channel_message_with_source,
        "data": {
            "content": f"Hello <@!{user_id}>",
            "flags": InteractionResponseFlags.ephemeral,
        },
    }
