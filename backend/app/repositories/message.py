from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.message import MessageCreate
from datetime import datetime
from sqlalchemy import select
from app.models.message import Message
from app.services.logger import logger


async def save_message(msg: MessageCreate, session: AsyncSession):
    try:
        message = Message(
            chat_id=msg.chat_id,
            sender_id=msg.sender_id,
            text=msg.text,
            timestamp=datetime.utcnow(),
            is_read=False,
            read_by=[],
            client_id=getattr(msg, "client_id", None)
        )

        session.add(message)
        await session.commit()
        await session.refresh(message)
        return message

    except SQLAlchemyError as e:
        logger.error(f"Error saving message: {e}")
        await session.rollback()
        raise e


async def get_messages_by_chat_id(session: AsyncSession, chat_id: str):
    result = await session.execute(
        select(Message).where(Message.chat_id == chat_id).order_by(Message.timestamp)
    )
    return result.scalars().all()


async def get_messages_with_pagination(session: AsyncSession, chat_id: int, limit: int = 50, offset: int = 0):
    result = await session.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.timestamp)
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()
