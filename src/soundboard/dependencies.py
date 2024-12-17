import httpx
from soundboard.constants import settings


HEADERS = {"Authorization": f"Bot {settings.discord_token}"}


async def http_client():
    async with httpx.AsyncClient(
        headers=HEADERS, base_url=settings.discord_base_url
    ) as client:
        yield client
