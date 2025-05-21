from app.models.user import User
from app.models.chat import Chat, ChatType
from app.models.message import Message
from app.models.group import Group, group_members

# Для порядка импорта всех моделей и таблиц
__all__ = [
    "User",
    "Chat",
    "ChatType",
    "Message",
    "Group",
    "group_members"
]