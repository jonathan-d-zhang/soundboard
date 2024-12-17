from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    discord_application_id: str
    discord_public_key: str
    discord_token: str
    discord_base_url: str = "https://discord.com/api/v10"

    model_config = SettingsConfigDict(env_prefix="soundboard")


settings = Settings()  # pyright: ignore


class InteractionType:
    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5


class InteractionResponseType:
    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7
    APPLICATION_COMMAND_AUTOCOMPLETE_RESULT = 8
    MODAL = 9


class InteractionResponseFlags:
    EPHEMERAL = 1 << 6


class ApplicationCommandOptionType(Enum):
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
