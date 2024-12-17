from dataclasses import dataclass

from soundboard.constants import Option


@dataclass
class SlashCommand:
    name: str
    description: str = "..."
    options: list[Option] = []

    async def respond(self, request): ...

    def to_dict(self):
        return dict(
            type=1, name=self.name, description=self.description, options=self.options
        )
