from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timezone

from database import get_db
from models.product import ProductCreate, ProductResponse, ProductUpdate
from routers.notifications import (
    create_product_created_notification,
    create_product_updated_notification,
)
from utils.dependencies import get_current_admin, get_current_user
from utils.helpers import convert_objectid_to_str, is_valid_objectid
from bson import ObjectId

router = APIRouter(prefix="/san-pham", tags=["san-pham"])

@router.post("/them-san-pham", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def them_san_pham(product: ProductCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    
    product_dict = product.model_dump()
    product_dict["created_at"] = datetime.now(timezone.utc)
    
    result = await db.products.insert_one(product_dict)
    
    created_product = await db.products.find_one({"_id": result.inserted_id})
    if created_product:
        try:
            await create_product_created_notification(current_user, created_product)
        except Exception:
            # Notification failure must not block product creation.
            pass
        return convert_objectid_to_str(created_product)
        
    raise HTTPException(status_code=500, detail="Không thể tạo sản phẩm")

@router.get("/danh-sach", response_model=List[ProductResponse])
async def danh_sach_san_pham():
    db = get_db()
    products = await db.products.find().to_list(1000)
    return [convert_objectid_to_str(p) for p in products]

@router.get("/tim-kiem", response_model=List[ProductResponse])
async def tim_kiem_san_pham(tu_khoa: Optional[str] = None, danh_muc: Optional[str] = None):
    db = get_db()
    query: dict = {}
    
    if tu_khoa:
        query["name"] = {"$regex": tu_khoa, "$options": "i"}
        
    if danh_muc:
        query["category"] = danh_muc
        
    products = await db.products.find(query).to_list(1000)
    return [convert_objectid_to_str(p) for p in products]

@router.get("/chi-tiet/{product_id}", response_model=ProductResponse)
async def chi_tiet_san_pham(product_id: str):
    db = get_db()
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="ID sản phẩm không hợp lệ")
    product = await db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
    return convert_objectid_to_str(product)

@router.put("/chinh-sua/{product_id}", response_model=ProductResponse)
async def chinh_sua_san_pham(
    product_id: str,
    product_update: ProductUpdate,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="ID sản phẩm không hợp lệ")
        
    update_data = {k: v for k, v in product_update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Không có dữ liệu gì để cập nhật")
        
    result = await db.products.update_one({"_id": ObjectId(product_id)}, {"$set": update_data})
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
        
    updated_product = await db.products.find_one({"_id": ObjectId(product_id)})
    if not updated_product:
        raise HTTPException(status_code=404, detail="KhÃ´ng tÃ¬m tháº¥y sáº£n pháº©m")

    try:
        await create_product_updated_notification(current_user, updated_product)
    except Exception:
        # Notification failure must not block product update.
        pass

    return convert_objectid_to_str(updated_product)

@router.delete("/xoa/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def xoa_san_pham(product_id: str, current_admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="ID sản phẩm không hợp lệ")
        
    result = await db.products.delete_one({"_id": ObjectId(product_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
