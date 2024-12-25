from typing import Optional

from pydantic import BaseModel


class Sound(BaseModel):
    """Represents a sound."""

    id: str
    custom_id: str
    filename: str
    size: int
    added_by: str
    message_id: Optional[str] = None
