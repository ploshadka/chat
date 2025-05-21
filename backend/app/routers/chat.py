from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.db import get_async_session
from app.repositories.chat import get_or_create_private_chat_in_db
from app.schemas.chat import PrivateChatCreate

router = APIRouter()


@router.post("/chats/private")
async def get_or_create_private_chat(
        data: PrivateChatCreate,
        session: AsyncSession = Depends(get_async_session)
):
    return await get_or_create_private_chat_in_db(data.user1_id, data.user2_id, session)
