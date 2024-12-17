from __future__ import annotations

from typing import Optional
from pydantic import BaseModel
from enum import IntEnum


class InteractionType(IntEnum):
    ping = 1
    application_command = 2
    message_component = 3
    application_command_autocomplete = 4
    modal_submit = 5


class InteractionResponseType(IntEnum):
    pong = 1
    channel_message_with_source = 4
    deferred_channel_message_with_source = 5
    deferred_update_message = 6
    update_message = 7
    application_command_autocomplete_result = 8
    modal = 9


class InteractionResponseFlags(IntEnum):
    ephemeral = 1 << 6


class ApplicationCommandType(IntEnum):
    chat_input = 1
    user = 2
    message = 3
    primary_entry_point = 4


class ApplicationCommandOptionType(IntEnum):
    sub_command = 1
    sub_command_group = 2
    string = 3
    integer = 4
    boolean = 5
    user = 6
    channel = 7
    role = 8


class Interaction(BaseModel):
    type: InteractionType
    data: Optional[ApplicationCommandData]
    resolved: Optional[ResolvedData] = None
    member: Member

    # guild_id is listed as Optional in the reference
    # (https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object-interaction-structure)
    # but i'm pretty sure it's always present for us, because the commands
    # cannot be invoked in DMs
    guild_id: str


class Member(BaseModel):
    user: User


class User(BaseModel):
    id: str


class ResolvedData(BaseModel):
    attachments: Optional[dict[int, Attachment]] = None


class ApplicationCommandData(BaseModel):
    name: str
    options: list[ApplicationCommandInteractionDataOption] = []


class ApplicationCommandInteractionDataOption(BaseModel):
    name: str
    type: ApplicationCommandOptionType
    value: str | int | float | bool


class Attachment(BaseModel):
    filename: str
    size: int
