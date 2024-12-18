from contextlib import asynccontextmanager
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from httpx import AsyncClient

from soundboard.constants import settings
from soundboard.dependencies import http_client
from soundboard.handler import handler
from soundboard.models import (
    Interaction,
    InteractionResponseType,
    InteractionType,
    MessageResponseFlags,
)
from soundboard.verify import verify_key


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with httpx.AsyncClient(
        headers={"Authorization": f"Bot {settings.discord_token}"},
        base_url=settings.discord_base_url,
    ) as client:
        json = [
            {
                "name": command.name,
                "description": command.description,
                "options": command.options,
                "type": command.type,
            }
            for command in handler.commands.values()
        ]
        print(f"Registering: {json}")
        resp = await client.put(
            f"/applications/{settings.discord_application_id}/guilds/{settings.discord_guild_id}/commands",
            json=json,
        )
        print(f"Registration response: {resp.json()}")

    yield


app = FastAPI(lifespan=lifespan)


async def set_body(request: Request, body: bytes) -> None:
    async def receive():
        return {"type": "http.request", "body": body}

    request._receive = receive


async def get_body(request: Request) -> bytes:
    body = await request.body()
    await set_body(request, body)
    return body


@app.middleware("http")
async def verify(request: Request, call_next):
    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")

    body = await get_body(request)

    if signature is None or timestamp is None:
        return Response(status_code=401)

    if not verify_key(signature, timestamp, body):
        return Response(status_code=401)

    response = await call_next(request)
    return response


@app.post("/")
async def interaction(request: Request, http: Annotated[AsyncClient, Depends(http_client)]):
    json = await request.json()
    print(json)
    interaction = Interaction.model_validate(json)
    print(f"{interaction = }")

    if interaction.type == InteractionType.ping:
        return {"type": InteractionResponseType.pong}

    if interaction.type == InteractionType.application_command:
        if interaction.data is None:
            raise HTTPException(400)
        resp = await handler.run(interaction, http)
        if resp is not None:
            return resp

    return dict(
        type=InteractionResponseType.channel_message_with_source,
        data=dict(content="Unrecognized Interaction", flags=MessageResponseFlags.ephemeral),
    )
