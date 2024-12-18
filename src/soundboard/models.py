from __future__ import annotations

from enum import IntEnum, IntFlag

from pydantic import BaseModel


class InteractionType(IntEnum):
    """
    Kind of interaction.

    https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object-interaction-type
    """

    ping = 1
    application_command = 2
    message_component = 3
    application_command_autocomplete = 4
    modal_submit = 5


class InteractionResponseType(IntEnum):
    """
    Kind of interaction response.

    https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-option-type
    """

    pong = 1
    channel_message_with_source = 4
    deferred_channel_message_with_source = 5
    deferred_update_message = 6
    update_message = 7
    application_command_autocomplete_result = 8
    modal = 9


class MessageResponseFlags(IntFlag):
    """
    Flags for message responses.

    https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-option-type
    """

    suppress_embeds = 1 << 2
    ephemeral = 1 << 6
    suppress_notifications = 1 << 12


class ApplicationCommandType(IntEnum):
    """
    Kind of application command.

    https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-types
    """

    chat_input = 1
    user = 2
    message = 3
    primary_entry_point = 4


class ApplicationCommandOptionType(IntEnum):
    """
    Kind of application command parameter.

    https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-option-type
    """

    sub_command = 1
    sub_command_group = 2
    string = 3
    integer = 4
    boolean = 5
    user = 6
    channel = 7
    role = 8


class Interaction(BaseModel):
    """
    Interaction object.

    https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object-interaction-structure
    """

    type: InteractionType
    data: ApplicationCommandData | None
    resolved: ResolvedData | None = None
    member: Member

    # guild_id is listed as Optional in the reference but i'm pretty sure it's
    # always present for us, because the commands cannot be invoked in DMs
    guild_id: str


class Member(BaseModel):
    """
    Guild member object.

    https://discord.com/developers/docs/resources/guild#guild-member-object-guild-member-structure
    """

    user: User


class User(BaseModel):
    """
    User object.

    https://discord.com/developers/docs/resources/user#user-object-user-structure
    """

    id: str


class ResolvedData(BaseModel):
    """
    Resolved data.

    https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object-resolved-data-structure
    """

    attachments: dict[int, Attachment] | None = None


class ApplicationCommandData(BaseModel):
    """
    Application command data.

    https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object-application-command-data-structure
    """

    name: str
    options: list[ApplicationCommandInteractionDataOption] = []


class ApplicationCommandInteractionDataOption(BaseModel):
    """
    Parameters for application commands.

    https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-object-application-command-interaction-data-option-structure
    """

    name: str
    type: ApplicationCommandOptionType
    value: str | int | float | bool


class Attachment(BaseModel):
    """
    Attachment object.

    https://discord.com/developers/docs/resources/message#attachment-object-attachment-structure
    """

    filename: str
    size: int
