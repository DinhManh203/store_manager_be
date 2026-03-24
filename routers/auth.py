from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Dict, Any

from database import get_db
from models.user import UserCreate, UserResponse, Token
from utils.security import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/xac-thuc", tags=["xac-thuc"])

@router.post("/dang-ky", response_model=UserResponse)
async def dang_ky(user: UserCreate):
    db = get_db()
    
    existing_user_email = await db.users.find_one({"email": user.email})
    if existing_user_email:
        raise HTTPException(status_code=400, detail="Email này đã được đăng ký.")
        
    existing_user_name = await db.users.find_one({"username": user.username})
    if existing_user_name:
        raise HTTPException(status_code=400, detail="Tên người dùng này đã tồn tại.")

    hashed_password = get_password_hash(user.password)
    
    user_dict = user.model_dump()
    user_dict["password"] = hashed_password

    user_dict["role"] = user.role.value
    
    await db.users.insert_one(user_dict)
    
    return UserResponse(username=user.username, email=user.email, role=user.role)

@router.post("/dang-nhap", response_model=Token)
async def dang_nhap(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_db()
    
    user_in_db = await db.users.find_one({"username": form_data.username})
    
    if not user_in_db:
         user_in_db = await db.users.find_one({"email": form_data.username})
         
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not verify_password(form_data.password, user_in_db["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai mật khẩu.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_in_db["username"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
