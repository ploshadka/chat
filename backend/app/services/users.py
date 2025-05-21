import os
import jwt
from enum import Enum
from typing import Optional
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.services.logger import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Данные только для Dev, на Prod они будут подтянуты из переменной окружения
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key_change_me")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "super_secret_refresh_key_change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 30


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "sub": data.get("sub"),
        "role": data.get("role", "user"),
        "name": data.get("name"),
        "id": data.get("id")
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "sub": data.get("sub"),
        "role": data.get("role", "user"),
        "name": data.get("name"),
        "id": data.get("id")
    })
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Декодирует access токен, возвращает payload"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as e:
        logger.warning(f"Access token decode error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def decode_refresh_token(token: str) -> dict:
    """Декодирует refresh токен, возвращает payload"""
    try:
        return jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as e:
        logger.warning(f"Refresh token decode error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


async def get_current_user_role(token: str = Depends(oauth2_scheme)):
    """Получает текущего пользователя по JWT и возвращает его роль."""

    payload = decode_access_token(token)
    email = payload.get("sub")
    role = payload.get("role")

    if email is None or role is None:
        logger.warning("Invalid token payload: missing 'sub' or 'role'")
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return role


def require_role(allowed_roles: list[Role]):
    async def _role_checker(user_role: str = Depends(get_current_user_role)):
        if user_role not in [r.value for r in allowed_roles]:
            logger.warning(f"Access denied: role '{user_role}' is not in allowed roles: {allowed_roles}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user_role

    return _role_checker
