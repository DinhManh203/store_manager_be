from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timezone

from database import get_db
from models.inventory import InventoryResponse, InventoryUpdate, InventoryHistoryResponse
from utils.dependencies import get_current_admin, get_current_user
from utils.helpers import convert_objectid_to_str, is_valid_objectid
from bson import ObjectId

router = APIRouter(prefix="/ton-kho", tags=["ton-kho"])

@router.get("/danh-sach", response_model=List[InventoryResponse])
async def danh_sach_ton_kho():
    db = get_db()
    products = await db.products.find().to_list(1000)
    result = []
    for p in products:
        result.append(InventoryResponse(
            id=str(p["_id"]),
            product_id=str(p["_id"]),
            product_name=p["name"],
            stock=p.get("stock", 0),
            updated_at=p.get("created_at", datetime.now(timezone.utc))
        ))
    return result

@router.get("/chi-tiet/{product_id}", response_model=InventoryResponse)
async def chi_tiet_ton_kho(product_id: str):
    db = get_db()
    if not is_valid_objectid(product_id):
        raise HTTPException(status_code=400, detail="ID sản phẩm không hợp lệ")

    product = await db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")

    return InventoryResponse(
        id=str(product["_id"]),
        product_id=str(product["_id"]),
        product_name=product["name"],
        stock=product.get("stock", 0),
        updated_at=product.get("created_at", datetime.now(timezone.utc))
    )

@router.put("/cap-nhat/{product_id}", response_model=InventoryResponse)
async def cap_nhat_ton_kho(product_id: str, inventory_update: InventoryUpdate, current_admin: dict = Depends(get_current_admin)):
    db = get_db()
    if not is_valid_objectid(product_id):
        raise HTTPException(status_code=400, detail="ID sản phẩm không hợp lệ")

    product = await db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")

    stock_before = product.get("stock", 0)
    stock_after = inventory_update.stock

    await db.products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"stock": stock_after}}
    )

    await db.inventory_history.insert_one({
        "product_id": product_id,
        "product_name": product["name"],
        "change_type": "chinh_sua",
        "quantity": abs(stock_after - stock_before),
        "stock_before": stock_before,
        "stock_after": stock_after,
        "note": f"Cập nhật tồn kho thủ công: {stock_before} → {stock_after}",
        "created_by": current_admin["username"],
        "created_at": datetime.now(timezone.utc)
    })

    updated = await db.products.find_one({"_id": ObjectId(product_id)})
    return InventoryResponse(
        id=str(updated["_id"]),
        product_id=str(updated["_id"]),
        product_name=updated["name"],
        stock=updated.get("stock", 0),
        updated_at=datetime.now(timezone.utc)
    )

@router.get("/lich-su", response_model=List[InventoryHistoryResponse])
async def lich_su_ton_kho():
    db = get_db()
    histories = await db.inventory_history.find().sort("created_at", -1).to_list(1000)
    return [convert_objectid_to_str(h) for h in histories]

@router.get("/lich-su/{product_id}", response_model=List[InventoryHistoryResponse])
async def lich_su_ton_kho_san_pham(product_id: str):
    db = get_db()
    if not is_valid_objectid(product_id):
        raise HTTPException(status_code=400, detail="ID sản phẩm không hợp lệ")

    histories = await db.inventory_history.find({"product_id": product_id}).sort("created_at", -1).to_list(1000)
    return [convert_objectid_to_str(h) for h in histories]
