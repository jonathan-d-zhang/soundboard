from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from soundboard.constants import settings

verifier = VerifyKey(bytes.fromhex(settings.discord_public_key))


def verify_key(signature: str, timestamp: str, raw_body: bytes) -> bool:
    """Verify signature of timestamp and body."""
    body = raw_body.decode(encoding="utf-8")

    try:
        verifier.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))
    except BadSignatureError:
        return False
    else:
        return True
