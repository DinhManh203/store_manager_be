from datetime import datetime, timezone
from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from database import get_db
from models.category import CategoryCreate, CategoryResponse, CategoryUpdate
from utils.dependencies import get_current_admin
from utils.helpers import convert_objectid_to_str, is_valid_objectid

router = APIRouter(prefix="/danh-muc", tags=["danh-muc"])

CATEGORY_NAME_MIN_LENGTH = 1
CATEGORY_NAME_MAX_LENGTH = 120


def normalize_text(value: Optional[str]) -> str:
    if value is None:
        return ""
    return " ".join(value.strip().split())


def normalize_category_key(value: str) -> str:
    return normalize_text(value).lower()


def validate_category_name(name: Optional[str]) -> str:
    normalized_name = normalize_text(name)
    if not normalized_name:
        raise HTTPException(status_code=400, detail="Tên danh mục là bắt buộc")

    if len(normalized_name) < CATEGORY_NAME_MIN_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Tên danh mục phải có ít nhất {CATEGORY_NAME_MIN_LENGTH} ký tự",
        )

    if len(normalized_name) > CATEGORY_NAME_MAX_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Tên danh mục tối đa {CATEGORY_NAME_MAX_LENGTH} ký tự",
        )

    return normalized_name


@router.post("/them", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def them_danh_muc(
    category: CategoryCreate,
    current_admin: dict = Depends(get_current_admin),
):
    db = get_db()
    normalized_name = validate_category_name(category.name)
    normalized_name_key = normalize_category_key(normalized_name)

    duplicated_category = await db.categories.find_one(
        {"name_normalized": normalized_name_key}
    )
    if duplicated_category:
        raise HTTPException(status_code=400, detail="Tên danh mục đã tồn tại")

    category_doc = {
        "name": normalized_name,
        "name_normalized": normalized_name_key,
        "created_at": datetime.now(timezone.utc),
    }

    result = await db.categories.insert_one(category_doc)
    created_category = await db.categories.find_one({"_id": result.inserted_id})
    if created_category:
        return convert_objectid_to_str(created_category)

    raise HTTPException(status_code=500, detail="Không thể tạo danh mục")


@router.get("/danh-sach", response_model=List[CategoryResponse])
async def danh_sach_danh_muc():
    db = get_db()
    categories = await db.categories.find().sort("name_normalized", 1).to_list(1000)
    return [convert_objectid_to_str(category) for category in categories]


@router.put("/chinh-sua/{category_id}", response_model=CategoryResponse)
async def chinh_sua_danh_muc(
    category_id: str,
    category_update: CategoryUpdate,
    current_admin: dict = Depends(get_current_admin),
):
    db = get_db()
    if not is_valid_objectid(category_id):
        raise HTTPException(status_code=400, detail="ID danh mục không hợp lệ")

    normalized_name = validate_category_name(category_update.name)
    normalized_name_key = normalize_category_key(normalized_name)

    duplicated_category = await db.categories.find_one(
        {
            "_id": {"$ne": ObjectId(category_id)},
            "name_normalized": normalized_name_key,
        }
    )
    if duplicated_category:
        raise HTTPException(status_code=400, detail="Tên danh mục đã tồn tại")

    result = await db.categories.update_one(
        {"_id": ObjectId(category_id)},
        {
            "$set": {
                "name": normalized_name,
                "name_normalized": normalized_name_key,
            }
        },
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy danh mục")

    updated_category = await db.categories.find_one({"_id": ObjectId(category_id)})
    if updated_category:
        return convert_objectid_to_str(updated_category)

    raise HTTPException(status_code=500, detail="Không thể cập nhật danh mục")


@router.delete("/xoa/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def xoa_danh_muc(
    category_id: str,
    current_admin: dict = Depends(get_current_admin),
):
    db = get_db()
    if not is_valid_objectid(category_id):
        raise HTTPException(status_code=400, detail="ID danh mục không hợp lệ")

    existing_category = await db.categories.find_one({"_id": ObjectId(category_id)})
    if not existing_category:
        raise HTTPException(status_code=404, detail="Không tìm thấy danh mục")

    result = await db.categories.delete_one({"_id": ObjectId(category_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy danh mục")
