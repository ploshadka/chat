from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.db import get_async_session
from app.schemas.group import GroupCreate
from app.repositories.group import (
    create_group_in_db,
    get_user_groups_from_db,
    delete_group_from_db
)

router = APIRouter()


@router.post("/groups")
async def create_group(data: GroupCreate, session: AsyncSession = Depends(get_async_session)):
    return await create_group_in_db(data, session)


@router.get("/groups/by_user/{user_id}")
async def get_user_groups(user_id: int, session: AsyncSession = Depends(get_async_session)):
    return await get_user_groups_from_db(user_id, session)


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(group_id: int, session: AsyncSession = Depends(get_async_session)):
    await delete_group_from_db(group_id, session)
