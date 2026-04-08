import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pymongo.errors import PyMongoError

from database import get_db
from models.user import UserRole
from utils.security import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="xac-thuc/dang-nhap")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin đăng nhập",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    env_admin_username = os.getenv("ADMIN_USER_NAME", "").strip()
    if payload.get("is_env_admin") and username == env_admin_username:
        return {
            "username": username,
            "role": UserRole.admin.value,
            "email": f"{username}@storemanager.app",
            "is_demo_admin": True,
        }

    db = get_db()
    try:
        user = await db.users.find_one({"username": username})
        if user is None:
            raise credentials_exception
        return user
    except PyMongoError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Không thể kết nối cơ sở dữ liệu. Vui lòng thử lại sau.",
        )


async def get_current_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != UserRole.admin.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện thao tác này. Chức năng yêu cầu quyền Admin.",
        )
    return current_user
