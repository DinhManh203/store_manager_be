from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ImportItem(BaseModel):
    product_id: str = Field(..., description="ID sản phẩm")
    quantity: int = Field(..., gt=0, description="Số lượng nhập")
    unit_price: float = Field(..., gt=0, description="Đơn giá nhập")

class ImportOrderCreate(BaseModel):
    supplier_id: Optional[str] = Field(None, description="ID nhà cung cấp")
    items: List[ImportItem] = Field(..., min_length=1, description="Danh sách sản phẩm nhập")
    note: Optional[str] = Field(None, description="Ghi chú")

class ImportItemResponse(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    unit_price: float

class ImportOrderResponse(BaseModel):
    id: str
    supplier_id: Optional[str] = None
    supplier_name: Optional[str] = None
    items: List[ImportItemResponse]
    total_amount: float
    note: Optional[str] = None
    created_by: str
    created_at: datetime
