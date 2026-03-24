from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime, timezone

from database import get_db
from models.import_order import ImportOrderCreate, ImportOrderResponse, ImportItemResponse
from utils.dependencies import get_current_admin
from utils.helpers import convert_objectid_to_str, is_valid_objectid
from bson import ObjectId

router = APIRouter(prefix="/nhap-kho", tags=["nhap-kho"])

@router.post("/tao-phieu", response_model=ImportOrderResponse, status_code=status.HTTP_201_CREATED)
async def tao_phieu_nhap(order: ImportOrderCreate, current_admin: dict = Depends(get_current_admin)):
    db = get_db()

    if order.supplier_id:
        if not is_valid_objectid(order.supplier_id):
            raise HTTPException(status_code=400, detail="ID nhà cung cấp không hợp lệ")
        supplier = await db.suppliers.find_one({"_id": ObjectId(order.supplier_id)})
        if not supplier:
            raise HTTPException(status_code=404, detail="Không tìm thấy nhà cung cấp")

    items_data = []
    total_amount = 0.0

    for item in order.items:
        if not is_valid_objectid(item.product_id):
            raise HTTPException(status_code=400, detail=f"ID sản phẩm không hợp lệ: {item.product_id}")
        if item.quantity <= 0:
            raise HTTPException(status_code=400, detail="Số lượng nhập phải lớn hơn 0")

        product = await db.products.find_one({"_id": ObjectId(item.product_id)})
        if not product:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy sản phẩm: {item.product_id}")

        stock_before = product.get("stock", 0)
        stock_after = stock_before + item.quantity

        await db.products.update_one(
            {"_id": ObjectId(item.product_id)},
            {"$set": {"stock": stock_after}}
        )

        await db.inventory_history.insert_one({
            "product_id": item.product_id,
            "product_name": product["name"],
            "change_type": "nhap",
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
            "quantity": item.quantity,
            "unit_price": item.unit_price
        })
        total_amount += item.quantity * item.unit_price

    supplier_name = None
    if order.supplier_id:
        supplier = await db.suppliers.find_one({"_id": ObjectId(order.supplier_id)})
        if supplier:
            supplier_name = supplier["name"]

    import_doc = {
        "supplier_id": order.supplier_id,
        "supplier_name": supplier_name,
        "items": items_data,
        "total_amount": total_amount,
        "note": order.note,
        "created_by": current_admin["username"],
        "created_at": datetime.now(timezone.utc)
    }

    result = await db.import_orders.insert_one(import_doc)
    created = await db.import_orders.find_one({"_id": result.inserted_id})
    return convert_objectid_to_str(created)

@router.get("/danh-sach", response_model=List[ImportOrderResponse])
async def danh_sach_phieu_nhap():
    db = get_db()
    orders = await db.import_orders.find().sort("created_at", -1).to_list(1000)
    return [convert_objectid_to_str(o) for o in orders]

@router.get("/chi-tiet/{order_id}", response_model=ImportOrderResponse)
async def chi_tiet_phieu_nhap(order_id: str):
    db = get_db()
    if not is_valid_objectid(order_id):
        raise HTTPException(status_code=400, detail="ID phiếu nhập không hợp lệ")

    order = await db.import_orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiếu nhập")
    return convert_objectid_to_str(order)
