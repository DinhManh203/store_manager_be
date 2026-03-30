from datetime import timedelta
import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.errors import PyMongoError

from database import get_db
from models.user import Token
from utils.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    verify_password,
)

router = APIRouter(prefix="/xac-thuc", tags=["xac-thuc"])


@router.post("/dang-nhap", response_model=Token)
async def dang_nhap(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_db()
    env_admin_username = os.getenv("ADMIN_USER_NAME", "").strip()
    env_admin_password = os.getenv("ADMIN_PASSWORD", "").strip()
    login_identifier = form_data.username.strip()

    if (
        env_admin_username
        and env_admin_password
        and login_identifier == env_admin_username
        and form_data.password == env_admin_password
    ):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": env_admin_username,
                "role": "admin",
                "is_env_admin": True,
            },
            expires_delta=access_token_expires,
        )
        return {"access_token": access_token, "token_type": "bearer"}

    try:
        user_in_db = await db.users.find_one({"username": login_identifier})

        if not user_in_db:
            user_in_db = await db.users.find_one({"email": login_identifier})

        if not user_in_db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tai khoan khong ton tai.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(form_data.password, user_in_db["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sai mat khau.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_in_db["username"]},
            expires_delta=access_token_expires,
        )

        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except PyMongoError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Khong the ket noi co so du lieu. Vui long thu lai sau.",
        )
