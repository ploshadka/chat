from fastapi import APIRouter, Depends, HTTPException, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from jwt import PyJWTError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from app.config.db import get_async_session
from app.services.logger import logger
from app.services.users import (
    create_access_token, create_refresh_token, decode_refresh_token,
    hash_password, verify_password
)
from app.repositories.users import get_user_by_email, create_user
from app.schemas.users import UserResponse, UserCreate

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, session: AsyncSession = Depends(get_async_session)):
    try:
        existing_user = await get_user_by_email(session, user.email)
        if existing_user:
            logger.warning(f"Registration attempt with existing email: {user.email}")
            raise HTTPException(status_code=400, detail="Email already registered")

        password = hash_password(user.password)
        new_user = await create_user(session, user.email, password, role="user", name=user.name)
        return new_user

    except SQLAlchemyError as e:
        logger.error(f"Database error during registration: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal database error")

    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected registration error")


@router.post("/token")
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        user = await get_user_by_email(session, form_data.username)
        if not user or not verify_password(form_data.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        access_token = create_access_token(data={
            "sub": user.email,
            "role": user.role,
            "name": user.name,
            "id": user.id
        })
        refresh_token = create_refresh_token(data={"sub": user.email})

        response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
        response.set_cookie("refresh_token", refresh_token, httponly=True, max_age=60 * 60 * 24 * 7)
        return response

    except SQLAlchemyError as e:
        logger.error(f"DB error during login: {e}")
        raise HTTPException(status_code=500, detail="Database error during login")

    except Exception as e:
        logger.error(f"Unexpected login error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error during login")


@router.post("/refresh")
async def refresh_token(
        refresh_token: str = Cookie(None),
        session: AsyncSession = Depends(get_async_session)
):
    if refresh_token is None:
        logger.warning("Refresh token not provided")
        raise HTTPException(status_code=401, detail="No refresh token provided")

    try:
        payload = decode_refresh_token(refresh_token)
        email = payload.get("sub")

        if not email:
            logger.warning("Invalid refresh token: no 'sub'")
            raise HTTPException(status_code=401, detail="Invalid token: 'sub' not found")

        user = await get_user_by_email(session, email)
        if not user:
            logger.warning(f"User not found for refresh token: {email}")
            raise HTTPException(status_code=401, detail="User not found")

        new_access_token = create_access_token(data={
            "sub": email,
            "role": user.role,
            "name": user.name,
            "id": user.id
        })
        return {"access_token": new_access_token}

    except PyJWTError as e:
        logger.error(f"Failed to decode refresh token: {e}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    except Exception as e:
        logger.error(f"Unexpected error in refresh_token: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/logout")
async def logout():
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("refresh_token")
    return response
