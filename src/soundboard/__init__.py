from contextlib import asynccontextmanager
import dataclasses
from typing import Annotated
from fastapi import Depends, FastAPI, Request, Response
from httpx import Client
import httpx

from soundboard.constants import (
    InteractionResponseFlags,
    InteractionResponseType,
    InteractionType,
)
from soundboard.dependencies import http_client
from soundboard.handler import handler
from soundboard.verify import verify_key

from soundboard.constants import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    with httpx.Client(headers={"Authorization": f"Bearer: {settings.discord_token}"}, base_url=settings.discord_base_url) as client:
        json = [dataclasses.asdict(command) for command in handler.commands.values()]
        print(f"Registering: {json}")
        resp = client.put(
            f"/applications/{settings.discord_application_id}/commands",
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
async def interaction(request: Request, http: Annotated[Client, Depends(http_client)]):
    data = await request.json()

    if data["type"] == InteractionType.PING:
        return {"type": InteractionResponseType.PONG}

    if data["type"] == InteractionType.APPLICATION_COMMAND:
        handler.run(data, http)

    return dict(
        type=InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
        data=dict(
            content="Unrecognized Interaction", flags=InteractionResponseFlags.EPHEMERAL
        ),
    )


@app.get("/ping")
async def ping() -> str:
    return "pong"
