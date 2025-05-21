from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.config.db import Base

group_members = Table(
    "group_members",
    Base.metadata,
    Column("group_id", ForeignKey("groups.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, ForeignKey("chats.id"), primary_key=True)

    title = Column(String, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"))

    creator = relationship("User", back_populates="created_groups")
    members = relationship("User", secondary=group_members, backref="groups")
