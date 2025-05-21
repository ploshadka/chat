from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.config.db import get_async_session
from app.schemas.users import UserResponse
from app.repositories.users import get_all_users_from_db

router = APIRouter()


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(session: AsyncSession = Depends(get_async_session)):
    return await get_all_users_from_db(session)
