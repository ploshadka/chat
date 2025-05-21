import asyncio
from app.config.db import get_session_with_context
from app.models.user import User
from app.models.chat import Chat, ChatType
from app.services.users import Role
from sqlalchemy import text


async def seed():
    async with get_session_with_context() as session:

        # Вставляем пользователей без id
        user1 = User(name="Артур", email="artur@gmail.com", password="$2b$12$16Y0wIsnCWfakLq9uWtNWufVUVHM42FOL96kpOGASjGx4L11FBsaq", role=Role.USER)
        user2 = User(name="Маша", email="masha@gmail.com", password="$2b$12$16Y0wIsnCWfakLq9uWtNWufVUVHM42FOL96kpOGASjGx4L11FBsaq", role=Role.USER)
        user3 = User(name="Анна", email="ann@gmail.com", password="$2b$12$16Y0wIsnCWfakLq9uWtNWufVUVHM42FOL96kpOGASjGx4L11FBsaq", role=Role.USER)


        chat = Chat(title="Встреча", type=ChatType.private)

        session.add_all([user1, user2, user3, chat])

        # Все остальное, чтобы не ломать автоинкремент
        await session.flush()

        # Обновляем id после вставки
        await session.execute(text("UPDATE users SET id = 1 WHERE email = 'artur@gmail.com'"))
        await session.execute(text("UPDATE users SET id = 2 WHERE email = 'masha@gmail.com'"))
        await session.execute(text("UPDATE users SET id = 3 WHERE email = 'anna@gmail.com'"))
        await session.execute(text("UPDATE chats SET id = 1 WHERE title = 'Встреча'"))

        # Обновляем автоинкрементные последовательности
        await session.execute(text("SELECT setval('users_id_seq', GREATEST((SELECT MAX(id) FROM users), 1))"))
        await session.execute(text("SELECT setval('chats_id_seq', GREATEST((SELECT MAX(id) FROM chats), 1))"))

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
