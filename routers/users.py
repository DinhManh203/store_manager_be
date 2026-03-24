from fastapi import APIRouter, Depends
from models.user import UserResponse
from utils.dependencies import get_current_user, get_current_admin

router = APIRouter(prefix="/nguoi-dung", tags=["nguoi-dung"])

@router.get("/ho-so", response_model=UserResponse)
async def ho_so(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)

@router.get("/quan-tri/bang-dieu-khien")
async def bang_dieu_khien_quan_tri(current_admin: dict = Depends(get_current_admin)):
    return {
        "message": "Chào mừng sếp!",
        "admin_username": current_admin["username"]
    }
