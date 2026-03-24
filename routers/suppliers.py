from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timezone

from database import get_db
from models.supplier import SupplierCreate, SupplierUpdate, SupplierResponse
from utils.dependencies import get_current_admin
from utils.helpers import convert_objectid_to_str, is_valid_objectid
from bson import ObjectId

router = APIRouter(prefix="/nha-cung-cap", tags=["nha-cung-cap"])

@router.post("/them", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def them_nha_cung_cap(supplier: SupplierCreate, current_admin: dict = Depends(get_current_admin)):
    db = get_db()
    supplier_dict = supplier.model_dump()
    supplier_dict["created_at"] = datetime.now(timezone.utc)

    result = await db.suppliers.insert_one(supplier_dict)
    created = await db.suppliers.find_one({"_id": result.inserted_id})
    if created:
        return convert_objectid_to_str(created)
    raise HTTPException(status_code=500, detail="Không thể tạo nhà cung cấp")

@router.get("/danh-sach", response_model=List[SupplierResponse])
async def danh_sach_nha_cung_cap():
    db = get_db()
    suppliers = await db.suppliers.find().to_list(1000)
    return [convert_objectid_to_str(s) for s in suppliers]

@router.put("/chinh-sua/{supplier_id}", response_model=SupplierResponse)
async def chinh_sua_nha_cung_cap(supplier_id: str, supplier_update: SupplierUpdate, current_admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not is_valid_objectid(supplier_id):
        raise HTTPException(status_code=400, detail="ID nhà cung cấp không hợp lệ")

    update_data = {k: v for k, v in supplier_update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Không có dữ liệu gì để cập nhật")

    result = await db.suppliers.update_one({"_id": ObjectId(supplier_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhà cung cấp")

    updated = await db.suppliers.find_one({"_id": ObjectId(supplier_id)})
    return convert_objectid_to_str(updated)

@router.delete("/xoa/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def xoa_nha_cung_cap(supplier_id: str, current_admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not is_valid_objectid(supplier_id):
        raise HTTPException(status_code=400, detail="ID nhà cung cấp không hợp lệ")

    result = await db.suppliers.delete_one({"_id": ObjectId(supplier_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhà cung cấp")
