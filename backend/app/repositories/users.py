from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User


async def create_user(session: AsyncSession, email: str, hashed_password: str, role: str, name):
    new_user = User(
        email=email,
        password=hashed_password,
        role=role,
        name=name
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_all_users_from_db(session: AsyncSession):
    result = await session.execute(select(User))
    return result.scalars().all()
