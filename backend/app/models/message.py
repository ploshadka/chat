from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, Boolean, ARRAY
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.db import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Для одиночных чатов
    is_read = Column(Boolean, default=False)

    # Для групповых
    read_by = Column(
        MutableList.as_mutable(ARRAY(Integer)),
        nullable=False,
        default=list
    )

    # Уникальный идентификатор, чтобы исключить задвоения
    client_id = Column(String, unique=True, nullable=True)

    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", back_populates="messages")
