from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from app.models.chat import Chat, ChatType
from app.services.logger import logger


async def get_or_create_private_chat_in_db(user1_id: int, user2_id: int, session: AsyncSession) -> Chat:
    u1, u2 = sorted([user1_id, user2_id])

    try:
        query = select(Chat).where(
            and_(
                Chat.type == ChatType.private,
                Chat.user1_id == u1,
                Chat.user2_id == u2
            )
        )
        result = await session.execute(query)
        existing_chat = result.scalar_one_or_none()

        if existing_chat:
            return existing_chat

        new_chat = Chat(
            title=f"Чат {u1}-{u2}",
            type=ChatType.private,
            user1_id=u1,
            user2_id=u2
        )
        session.add(new_chat)
        await session.commit()
        await session.refresh(new_chat)

        return new_chat

    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Error creating private chat {u1}-{u2}: {e}")
        raise HTTPException(status_code=500, detail="Error creating private chat")
