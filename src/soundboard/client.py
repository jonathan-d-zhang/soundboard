from httpx import AsyncClient

from soundboard.constants import settings

HEADERS = {"Authorization": f"Bot {settings.discord_token}"}


def http_client() -> AsyncClient:
    """Create an http client with auth headers and Discord API base URL."""
    return AsyncClient(headers=HEADERS, base_url=settings.discord_base_url)


