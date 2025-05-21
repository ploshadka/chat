from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.models import Chat
from app.models.chat import ChatType
from app.models.group import Group, group_members
from app.models.user import User
from app.schemas.group import GroupCreate
from app.services.logger import logger


async def create_group_in_db(data: GroupCreate, session: AsyncSession):
    try:
        creator = await session.get(User, data.creator_id)
        if not creator:
            logger.warning(f"Creator with ID {data.creator_id} not found")
            raise HTTPException(status_code=404, detail="Creator not found")

        new_chat = Chat(title=data.title, type=ChatType.group)
        session.add(new_chat)
        await session.flush()

        group = Group(id=new_chat.id, title=data.title, creator_id=data.creator_id)
        session.add(group)
        await session.flush()

        member_ids = set(data.member_ids)
        member_ids.add(data.creator_id)

        for user_id in member_ids:
            user = await session.get(User, user_id)
            if not user:
                logger.warning(f"❗ User with ID {user_id} not found — skipping group creation")
                raise HTTPException(status_code=404, detail=f"User {user_id} not found")
            await session.execute(group_members.insert().values(group_id=group.id, user_id=user_id))

        await session.commit()

        return {
            "id": group.id,
            "title": group.title,
            "creator_id": group.creator_id,
            "member_ids": list(member_ids)
        }

    except SQLAlchemyError as e:
        logger.error(f"DB error during group creation: {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Database error during group creation")

    except Exception as e:
        logger.error(f"Unexpected error in create_group_in_db: {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail="Unexpected server error during group creation")


async def get_user_groups_from_db(user_id: int, session: AsyncSession):
    try:
        stmt = (
            select(Group)
            .join(group_members)
            .where(group_members.c.user_id == user_id)
        )
        result = await session.execute(stmt)
        groups = result.scalars().all()

        response = []
        for group in groups:
            member_stmt = select(group_members.c.user_id).where(group_members.c.group_id == group.id)
            members_result = await session.execute(member_stmt)
            member_ids = [row[0] for row in members_result]
            response.append({
                "id": group.id,
                "title": group.title,
                "creator_id": group.creator_id,
                "member_ids": member_ids
            })

        return response

    except Exception as e:
        logger.error(f"Error while fetching groups for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def delete_group_from_db(group_id: int, session: AsyncSession):
    group = await session.get(Group, group_id)
    if not group:
        logger.warning(f"❗ Attempt to delete non-existent group ID {group_id}")
        raise HTTPException(status_code=404, detail="Group not found")

    # Удаляем связи участников
    await session.execute(group_members.delete().where(group_members.c.group_id == group_id))

    # Удаляем группу
    await session.delete(group)
    # Важно сразу сделать коммит
    await session.commit()

    # Теперь можно безопасно удалить чат
    chat = await session.get(Chat, group_id)
    if chat:
        await session.delete(chat)
        await session.commit()
