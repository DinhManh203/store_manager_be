from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime, timezone

from database import get_db
from models.export_order import ExportOrderCreate, ExportOrderResponse, ExportItemResponse
from utils.dependencies import get_current_admin
from utils.helpers import convert_objectid_to_str, is_valid_objectid
from bson import ObjectId

router = APIRouter(prefix="/xuat-kho", tags=["xuat-kho"])

@router.post("/tao-phieu", response_model=ExportOrderResponse, status_code=status.HTTP_201_CREATED)
async def tao_phieu_xuat(order: ExportOrderCreate, current_admin: dict = Depends(get_current_admin)):
    db = get_db()

    if not is_valid_objectid(order.target_branch_id):
        raise HTTPException(status_code=400, detail="ID chi nhánh không hợp lệ")

    branch = await db.branches.find_one({"_id": ObjectId(order.target_branch_id)})
    if not branch:
        raise HTTPException(status_code=404, detail="Không tìm thấy chi nhánh đích")

    items_data = []

    for item in order.items:
        if not is_valid_objectid(item.product_id):
            raise HTTPException(status_code=400, detail=f"ID sản phẩm không hợp lệ: {item.product_id}")
        if item.quantity <= 0:
            raise HTTPException(status_code=400, detail="Số lượng xuất phải lớn hơn 0")

        product = await db.products.find_one({"_id": ObjectId(item.product_id)})
        if not product:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy sản phẩm: {item.product_id}")

        stock_before = product.get("stock", 0)
        if item.quantity > stock_before:
            raise HTTPException(
                status_code=400,
                detail=f"Sản phẩm '{product['name']}' không đủ tồn kho. Hiện có: {stock_before}, yêu cầu xuất: {item.quantity}"
            )

        stock_after = stock_before - item.quantity

        await db.products.update_one(
            {"_id": ObjectId(item.product_id)},
            {"$set": {"stock": stock_after}}
        )

        await db.inventory_history.insert_one({
            "product_id": item.product_id,
            "product_name": product["name"],
            "change_type": "xuat",
            "quantity": item.quantity,
            "stock_before": stock_before,
            "stock_after": stock_after,
            "note": order.note,
            "created_by": current_admin["username"],
            "created_at": datetime.now(timezone.utc)
        })

        items_data.append({
            "product_id": item.product_id,
            "product_name": product["name"],
            "quantity": item.quantity
        })

    export_doc = {
        "items": items_data,
        "reason": order.reason,
        "note": order.note,
        "target_branch_id": order.target_branch_id,
        "target_branch_name": branch["name"],
        "created_by": current_admin["username"],
        "created_at": datetime.now(timezone.utc)
    }

    result = await db.export_orders.insert_one(export_doc)
    created = await db.export_orders.find_one({"_id": result.inserted_id})
    return convert_objectid_to_str(created)

@router.get("/danh-sach", response_model=List[ExportOrderResponse])
async def danh_sach_phieu_xuat():
    db = get_db()
    orders = await db.export_orders.find().sort("created_at", -1).to_list(1000)
    return [convert_objectid_to_str(o) for o in orders]

@router.get("/chi-tiet/{order_id}", response_model=ExportOrderResponse)
async def chi_tiet_phieu_xuat(order_id: str):
    db = get_db()
    if not is_valid_objectid(order_id):
        raise HTTPException(status_code=400, detail="ID phiếu xuất không hợp lệ")

    order = await db.export_orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiếu xuất")
    return convert_objectid_to_str(order)
