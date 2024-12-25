from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App config."""

    discord_token: str
    discord_base_url: str = "https://discord.com/api/v10"
    discord_guild_id: str

    sound_max_size: int = 1 << 17  # 128 KiB

    sound_metadata_db_location: str = "/var/soundboard/metadata.db"
    sound_location: str = "/var/soundboard/sounds"

    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="soundboard_", extra="ignore")


settings = Settings()  # pyright: ignore[reportCallIssue]
