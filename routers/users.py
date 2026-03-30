import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from database import get_db
from models.user import EmployeeCreate, EmployeeCreateResponse, UserResponse
from utils.dependencies import get_current_admin, get_current_user
from utils.security import get_password_hash

router = APIRouter(prefix="/nguoi-dung", tags=["nguoi-dung"])


@router.get("/ho-so", response_model=UserResponse)
async def ho_so(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)


@router.get("/quan-tri/bang-dieu-khien")
async def bang_dieu_khien_quan_tri(current_admin: dict = Depends(get_current_admin)):
    return {
        "message": "Chào mừng sếp!",
        "admin_username": current_admin["username"],
    }


async def _generate_unique_username(db, email: str) -> str:
    local_part = email.split("@")[0].lower()
    base_username = re.sub(r"[^a-z0-9._-]", "", local_part) or "nhanvien"
    candidate = base_username
    suffix = 1

    while await db.users.find_one({"username": candidate}):
        suffix += 1
        candidate = f"{base_username}{suffix}"

    return candidate


@router.post(
    "/quan-tri/tao-nhan-vien",
    response_model=EmployeeCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def tao_nhan_vien(payload: EmployeeCreate, current_admin: dict = Depends(get_current_admin)):
    db = get_db()
    normalized_email = payload.email.lower()
    normalized_phone = payload.phone

    existing_user_email = await db.users.find_one({"email": normalized_email})
    if existing_user_email:
        raise HTTPException(status_code=400, detail="Email nay da duoc dang ky")

    existing_user_phone = await db.users.find_one({"phone": normalized_phone})
    if existing_user_phone:
        raise HTTPException(status_code=400, detail="So dien thoai nay da ton tai")

    generated_username = await _generate_unique_username(db, normalized_email)

    user_doc = {
        "username": generated_username,
        "full_name": payload.full_name,
        "email": normalized_email,
        "phone": normalized_phone,
        "password": get_password_hash(payload.temporary_password),
        "role": payload.role.value,
        "is_temporary_password": True,
        "created_by": current_admin["username"],
        "created_at": datetime.now(timezone.utc),
    }

    insert_result = await db.users.insert_one(user_doc)

    return EmployeeCreateResponse(
        id=str(insert_result.inserted_id),
        username=generated_username,
        full_name=payload.full_name,
        email=normalized_email,
        phone=normalized_phone,
        role=payload.role,
    )
