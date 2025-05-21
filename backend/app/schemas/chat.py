from pydantic import BaseModel


class PrivateChatCreate(BaseModel):
    user1_id: int
    user2_id: int
