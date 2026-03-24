from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime, timezone

from database import get_db
from utils.helpers import convert_objectid_to_str

router = APIRouter(prefix="/bao-cao", tags=["bao-cao"])

@router.get("/ton-kho-thap")
async def bao_cao_ton_kho_thap(nguong: int = Query(10, description="Ngưỡng tồn kho thấp")):
    db = get_db()
    products = await db.products.find({"stock": {"$lte": nguong}}).sort("stock", 1).to_list(1000)
    result = []
    for p in products:
        result.append({
            "id": str(p["_id"]),
            "name": p["name"],
            "stock": p.get("stock", 0),
            "category": p.get("category", ""),
        })
    return result

@router.get("/san-pham-nhap-nhieu")
async def bao_cao_san_pham_nhap_nhieu():
    db = get_db()
    pipeline = [
        {"$match": {"change_type": "nhap"}},
        {"$group": {
            "_id": "$product_id",
            "product_name": {"$first": "$product_name"},
            "total_imported": {"$sum": "$quantity"},
            "import_count": {"$sum": 1}
        }},
        {"$sort": {"total_imported": -1}},
        {"$limit": 20}
    ]
    results = await db.inventory_history.aggregate(pipeline).to_list(20)
    return [{"product_id": r["_id"], "product_name": r["product_name"], "total_imported": r["total_imported"], "import_count": r["import_count"]} for r in results]

@router.get("/san-pham-xuat-nhieu")
async def bao_cao_san_pham_xuat_nhieu():
    db = get_db()
    pipeline = [
        {"$match": {"change_type": "xuat"}},
        {"$group": {
            "_id": "$product_id",
            "product_name": {"$first": "$product_name"},
            "total_exported": {"$sum": "$quantity"},
            "export_count": {"$sum": 1}
        }},
        {"$sort": {"total_exported": -1}},
        {"$limit": 20}
    ]
    results = await db.inventory_history.aggregate(pipeline).to_list(20)
    return [{"product_id": r["_id"], "product_name": r["product_name"], "total_exported": r["total_exported"], "export_count": r["export_count"]} for r in results]

@router.get("/tong-quan-ton-kho")
async def bao_cao_tong_quan_ton_kho():
    db = get_db()
    products = await db.products.find().to_list(10000)
    total_products = len(products)
    total_stock = sum(p.get("stock", 0) for p in products)
    out_of_stock = sum(1 for p in products if p.get("stock", 0) == 0)
    low_stock = sum(1 for p in products if 0 < p.get("stock", 0) <= 10)

    return {
        "tong_san_pham": total_products,
        "tong_ton_kho": total_stock,
        "het_hang": out_of_stock,
        "sap_het_hang": low_stock,
    }

@router.get("/lich-su-bien-dong")
async def bao_cao_lich_su_bien_dong(loai: Optional[str] = None, gioi_han: int = Query(50, le=500)):
    db = get_db()
    query: dict = {}
    if loai:
        query["change_type"] = loai

    histories = await db.inventory_history.find(query).sort("created_at", -1).to_list(gioi_han)
    return [convert_objectid_to_str(h) for h in histories]
