from pydantic import BaseModel
from typing import List


class GroupCreate(BaseModel):
    title: str
    creator_id: int
    member_ids: List[int]


class GroupResponse(BaseModel):
    id: int
    title: str
    creator_id: int
    member_ids: List[int]

    model_config = {
        "from_attributes": True
    }

class GroupOut(BaseModel):
    id: int
    title: str
    creator_id: int

    model_config = {"from_attributes": True}
