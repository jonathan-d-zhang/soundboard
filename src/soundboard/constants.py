from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App config."""

    discord_application_id: str
    discord_public_key: str
    discord_token: str
    discord_base_url: str = "https://discord.com/api/v10"
    discord_guild_id: str

    model_config = SettingsConfigDict(env_file=".env", env_prefix="soundboard_")


settings = Settings()  # pyright: ignore[reportCallIssue]
