from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.config.db import get_async_session
from app.schemas.message import MessageResponse
from app.repositories.message import get_messages_with_pagination

router = APIRouter()


@router.get("/history/{chat_id}", response_model=List[MessageResponse])
async def get_history(chat_id: int, limit: int = 50, offset: int = 0, session: AsyncSession = Depends(get_async_session)):
    return await get_messages_with_pagination(session, chat_id, limit, offset)
