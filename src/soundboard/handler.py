from __future__ import annotations

from typing import Callable
from dataclasses import dataclass

from soundboard.constants import ApplicationCommandOptionType


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

    def register(
        self, name: str, description: str, options: list[Option], func: Callable
    ):
        self.commands[name] = Command(name, description, options, func)
        return func

    def run(self, data: dict):
        name = data["data"]["name"]
        func = self.commands.get(name)

        if func is None:
            raise ValueError(f"Invalid command: {name}")

        return func


handler = CommandHandler()
