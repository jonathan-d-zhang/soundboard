import httpx
from soundboard.constants import settings


HEADERS = {"Authorization": f"Bearer: {settings.discord_token}"}


def http_client():
    with httpx.Client(headers=HEADERS, base_url=settings.discord_base_url) as client:
        yield client
