from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class InventoryResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    stock: int
    updated_at: datetime

class InventoryUpdate(BaseModel):
    stock: int = Field(..., ge=0, description="Số lượng tồn kho mới")

class HistoryType(str, Enum):
    nhap = "nhap"
    xuat = "xuat"
    chinh_sua = "chinh_sua"

class InventoryHistoryResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    change_type: HistoryType
    quantity: int
    stock_before: int
    stock_after: int
    note: Optional[str] = None
    created_by: str
    created_at: datetime
