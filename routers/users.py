from fastapi import APIRouter, Depends
from models.user import UserResponse
from utils.dependencies import get_current_user, get_current_admin

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)

@router.get("/admin/dashboard")
async def admin_dashboard(current_admin: dict = Depends(get_current_admin)):
    return {
        "message": "Chào mừng sếp!",
        "admin_username": current_admin["username"]
    }
