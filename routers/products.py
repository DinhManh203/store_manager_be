from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime, timezone

from database import get_db
from models.product import ProductCreate, ProductResponse
from utils.dependencies import get_current_admin

router = APIRouter(prefix="/san-pham", tags=["san-pham"])

def convert_objectid_to_str(item: dict) -> dict:
    if "_id" in item:
        item["id"] = str(item["_id"])
        del item["_id"]
    return item

@router.post("/them-san-pham", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def them_san_pham(product: ProductCreate, current_admin: dict = Depends(get_current_admin)):
    db = get_db()
    
    product_dict = product.model_dump()
    product_dict["created_at"] = datetime.now(timezone.utc)
    
    result = await db.products.insert_one(product_dict)
    
    created_product = await db.products.find_one({"_id": result.inserted_id})
    if created_product:
        return convert_objectid_to_str(created_product)
        
    raise HTTPException(status_code=500, detail="Không thể tạo sản phẩm")
