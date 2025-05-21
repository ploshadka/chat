from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class MessageCreate(BaseModel):
    chat_id: int
    sender_id: int
    text: str
    # для защиты от дубликатов
    client_id: Optional[str] = None
    read_by: List[int] = Field(default_factory=list)


class MessageResponse(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    text: str
    timestamp: datetime
    is_read: bool
    read_by: List[int] = Field(default_factory=list)
    client_id: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
