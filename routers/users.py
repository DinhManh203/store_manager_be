import re
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from database import get_db
from models.user import (
    EmployeeCreate,
    EmployeeCreateResponse,
    EmployeeDeleteResponse,
    EmployeeUpdate,
    UserResponse,
    UserRole,
)
from utils.dependencies import get_current_admin, get_current_user
from utils.helpers import is_valid_objectid
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


def _employee_response_from_doc(user_doc: dict) -> EmployeeCreateResponse:
    role_value = user_doc.get("role", UserRole.user.value)
    try:
        role = UserRole(role_value)
    except ValueError:
        role = UserRole.user

    return EmployeeCreateResponse(
        id=str(user_doc["_id"]),
        username=user_doc["username"],
        full_name=user_doc.get("full_name"),
        email=user_doc["email"],
        phone=user_doc.get("phone"),
        role=role,
    )


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
        raise HTTPException(status_code=400, detail="Email này đã được đăng ký")

    existing_user_phone = await db.users.find_one({"phone": normalized_phone})
    if existing_user_phone:
        raise HTTPException(status_code=400, detail="Số điện thoại này đã tồn tại")

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
    user_doc["_id"] = insert_result.inserted_id

    return _employee_response_from_doc(user_doc)


@router.put("/quan-tri/chinh-sua-nhan-vien/{user_id}", response_model=EmployeeCreateResponse)
async def chinh_sua_nhan_vien(
    user_id: str,
    payload: EmployeeUpdate,
    current_admin: dict = Depends(get_current_admin),
):
    db = get_db()

    if not is_valid_objectid(user_id):
        raise HTTPException(status_code=400, detail="ID nguoi dung khong hop le")

    object_id = ObjectId(user_id)
    existing_user = await db.users.find_one({"_id": object_id})
    if not existing_user:
        raise HTTPException(status_code=404, detail="Khong tim thay nhan vien")
    if existing_user.get("is_demo_admin"):
        if payload.role is not None and payload.role != UserRole.admin:
            raise HTTPException(
                status_code=400,
                detail="Khong the ha quyen tai khoan admin he thong",
            )

    update_fields = {}

    if payload.full_name is not None:
        update_fields["full_name"] = payload.full_name

    if payload.email is not None:
        normalized_email = payload.email.lower()
        duplicated_email = await db.users.find_one(
            {"email": normalized_email, "_id": {"$ne": object_id}}
        )
        if duplicated_email:
            raise HTTPException(status_code=400, detail="Email này đã được đăng ký")
        update_fields["email"] = normalized_email

    if payload.phone is not None:
        normalized_phone = payload.phone
        duplicated_phone = await db.users.find_one(
            {"phone": normalized_phone, "_id": {"$ne": object_id}}
        )
        if duplicated_phone:
            raise HTTPException(status_code=400, detail="Số điện thoại này đã tồn tại")
        update_fields["phone"] = normalized_phone

    if payload.role is not None:
        current_admin_id = str(current_admin.get("_id")) if current_admin.get("_id") else None
        if current_admin_id == user_id and payload.role != UserRole.admin:
            raise HTTPException(
                status_code=400,
                detail="Khong the tu ha quyen tai khoan admin dang dang nhap",
            )
        update_fields["role"] = payload.role.value

    if payload.temporary_password is not None:
        update_fields["password"] = get_password_hash(payload.temporary_password)
        update_fields["is_temporary_password"] = True

    if not update_fields:
        raise HTTPException(status_code=400, detail="Khong co du lieu de cap nhat")

    update_fields["updated_by"] = current_admin["username"]
    update_fields["updated_at"] = datetime.now(timezone.utc)

    await db.users.update_one({"_id": object_id}, {"$set": update_fields})
    updated_user = await db.users.find_one({"_id": object_id})

    return _employee_response_from_doc(updated_user)


@router.delete("/quan-tri/xoa-nhan-vien/{user_id}", response_model=EmployeeDeleteResponse)
async def xoa_nhan_vien(user_id: str, current_admin: dict = Depends(get_current_admin)):
    db = get_db()

    if not is_valid_objectid(user_id):
        raise HTTPException(status_code=400, detail="ID nguoi dung khong hop le")

    current_admin_id = str(current_admin.get("_id")) if current_admin.get("_id") else None
    if current_admin_id == user_id:
        raise HTTPException(status_code=400, detail="Khong the tu xoa tai khoan dang dang nhap")

    object_id = ObjectId(user_id)
    existing_user = await db.users.find_one({"_id": object_id})
    if not existing_user:
        raise HTTPException(status_code=404, detail="Khong tim thay nhan vien")
    if existing_user.get("is_demo_admin"):
        raise HTTPException(
            status_code=400,
            detail="Khong the xoa tai khoan admin he thong",
        )

    await db.users.delete_one({"_id": object_id})

    return EmployeeDeleteResponse(
        message=f"Da xoa nhan vien '{existing_user['username']}'",
        deleted_user_id=user_id,
        deleted_username=existing_user["username"],
    )
