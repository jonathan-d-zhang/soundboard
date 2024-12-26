from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App config."""

    discord_token: str
    discord_base_url: str = "https://discord.com/api/v10"

    discord_guild_id: str
    discord_soundboard_channel_id: int

    sound_max_size: int = 1 << 17  # 128 KiB
    sound_data_dir: str = "/var/soundboard"

    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="soundboard_", extra="ignore")


MAX_BUTTONS_PER_MESSAGE = 25
settings = Settings()  # pyright: ignore[reportCallIssue]
