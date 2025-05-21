import enum
from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.config.db import Base


class ChatType(str, enum.Enum):
    private = "private"
    group = "group"


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    type = Column(Enum(ChatType), nullable=False)

    user1_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user2_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
