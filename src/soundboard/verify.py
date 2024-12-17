from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from soundboard.constants import settings

verifier = VerifyKey(bytes.fromhex(settings.discord_public_key))


def verify_key(signature: str, timestamp: str, raw_body: bytes) -> bool:
    body = raw_body.decode(encoding="utf-8")

    try:
        verifier.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))
    except BadSignatureError:
        return False
    else:
        return True
