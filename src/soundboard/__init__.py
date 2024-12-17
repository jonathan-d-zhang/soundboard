from fastapi import FastAPI, HTTPException, Request

from soundboard.verify import verify_key

app = FastAPI()


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
        raise HTTPException(401)

    if not verify_key(signature, timestamp, body):
        raise HTTPException(401)

    response = await call_next(request)
    return response
