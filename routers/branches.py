import re
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timezone

from database import get_db
from models.branch import BranchCreate, BranchUpdate, BranchResponse
from utils.dependencies import get_current_admin
from utils.helpers import convert_objectid_to_str, is_valid_objectid
from bson import ObjectId

router = APIRouter(prefix="/chi-nhanh", tags=["chi-nhanh"])

BRANCH_NAME_MIN_LENGTH = 2
BRANCH_NAME_MAX_LENGTH = 120
PHONE_PATTERN = re.compile(r"^\+?[0-9][0-9\s\-().]{6,19}$")


def normalize_text(value: Optional[str]) -> str:
    if value is None:
        return ""
    return " ".join(value.strip().split())


def normalize_optional_text(value: Optional[str]) -> Optional[str]:
    cleaned = normalize_text(value)
    return cleaned if cleaned else None


def normalize_branch_name(value: Optional[str]) -> str:
    return normalize_text(value).lower()


def validate_branch_name(name: Optional[str]) -> str:
    cleaned_name = normalize_text(name)
    if not cleaned_name:
        raise HTTPException(status_code=400, detail="Tên chi nhánh là bắt buộc")

    if len(cleaned_name) < BRANCH_NAME_MIN_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Tên chi nhánh phải có ít nhất {BRANCH_NAME_MIN_LENGTH} ký tự",
        )

    if len(cleaned_name) > BRANCH_NAME_MAX_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Tên chi nhánh tối đa {BRANCH_NAME_MAX_LENGTH} ký tự",
        )

    return cleaned_name


def validate_phone(phone: Optional[str]) -> Optional[str]:
    normalized_phone = normalize_optional_text(phone)
    if not normalized_phone:
        return None

    if not PHONE_PATTERN.fullmatch(normalized_phone):
        raise HTTPException(
            status_code=400,
            detail="Số điện thoại chi nhánh không hợp lệ",
        )

    return normalized_phone

@router.post("/them", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
async def them_chi_nhanh(branch: BranchCreate, current_admin: dict = Depends(get_current_admin)):
    db = get_db()
    normalized_name = validate_branch_name(branch.name)
    normalized_name_key = normalize_branch_name(normalized_name)

    duplicated_branch = await db.branches.find_one(
        {
            "$or": [
                {"name_normalized": normalized_name_key},
                {"name": {"$regex": f"^{re.escape(normalized_name)}$", "$options": "i"}},
            ]
        }
    )
    if duplicated_branch:
        raise HTTPException(status_code=400, detail="Tên chi nhánh đã tồn tại")

    branch_dict = {
        "name": normalized_name,
        "name_normalized": normalized_name_key,
        "address": normalize_optional_text(branch.address),
        "phone": validate_phone(branch.phone),
        "manager": normalize_optional_text(branch.manager),
        "is_active": bool(branch.is_active),
        "created_at": datetime.now(timezone.utc),
    }

    result = await db.branches.insert_one(branch_dict)
    created = await db.branches.find_one({"_id": result.inserted_id})
    if created:
        return convert_objectid_to_str(created)
    raise HTTPException(status_code=500, detail="Không thể tạo chi nhánh")

@router.get("/danh-sach", response_model=List[BranchResponse])
async def danh_sach_chi_nhanh():
    db = get_db()
    branches = await db.branches.find().to_list(1000)
    return [convert_objectid_to_str(b) for b in branches]

@router.put("/chinh-sua/{branch_id}", response_model=BranchResponse)
async def chinh_sua_chi_nhanh(branch_id: str, branch_update: BranchUpdate, current_admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not is_valid_objectid(branch_id):
        raise HTTPException(status_code=400, detail="ID chi nhánh không hợp lệ")

    raw_update_data = branch_update.model_dump()
    model_fields_set = set(branch_update.model_fields_set)
    update_data = {}

    if "name" in model_fields_set:
        normalized_name = validate_branch_name(raw_update_data.get("name"))
        normalized_name_key = normalize_branch_name(normalized_name)

        duplicated_branch = await db.branches.find_one(
            {
                "_id": {"$ne": ObjectId(branch_id)},
                "$or": [
                    {"name_normalized": normalized_name_key},
                    {"name": {"$regex": f"^{re.escape(normalized_name)}$", "$options": "i"}},
                ],
            }
        )
        if duplicated_branch:
            raise HTTPException(status_code=400, detail="Tên chi nhánh đã tồn tại")

        update_data["name"] = normalized_name
        update_data["name_normalized"] = normalized_name_key

    if "address" in model_fields_set:
        update_data["address"] = normalize_optional_text(raw_update_data.get("address"))

    if "phone" in model_fields_set:
        update_data["phone"] = validate_phone(raw_update_data.get("phone"))

    if "manager" in model_fields_set:
        update_data["manager"] = normalize_optional_text(raw_update_data.get("manager"))

    if "is_active" in model_fields_set:
        if raw_update_data.get("is_active") is None:
            raise HTTPException(status_code=400, detail="Trạng thái hoạt động không hợp lệ")
        update_data["is_active"] = bool(raw_update_data["is_active"])

    if not update_data:
        raise HTTPException(status_code=400, detail="Không có dữ liệu gì để cập nhật")

    result = await db.branches.update_one({"_id": ObjectId(branch_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy chi nhánh")

    updated = await db.branches.find_one({"_id": ObjectId(branch_id)})
    return convert_objectid_to_str(updated)

@router.delete("/xoa/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def xoa_chi_nhanh(branch_id: str, current_admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not is_valid_objectid(branch_id):
        raise HTTPException(status_code=400, detail="ID chi nhánh không hợp lệ")

    existing_branch = await db.branches.find_one({"_id": ObjectId(branch_id)})
    if not existing_branch:
        raise HTTPException(status_code=404, detail="Không tìm thấy chi nhánh")

    if bool(existing_branch.get("is_active", True)):
        raise HTTPException(
            status_code=400,
            detail="Chỉ có thể xóa chi nhánh đang ngừng hoạt động",
        )

    result = await db.branches.delete_one({"_id": ObjectId(branch_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy chi nhánh")
