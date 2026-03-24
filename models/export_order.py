from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ExportItem(BaseModel):
    product_id: str = Field(..., description="ID sản phẩm")
    quantity: int = Field(..., gt=0, description="Số lượng xuất")

class ExportOrderCreate(BaseModel):
    items: List[ExportItem] = Field(..., min_length=1, description="Danh sách sản phẩm xuất")
    reason: Optional[str] = Field(None, description="Lý do xuất kho")
    note: Optional[str] = Field(None, description="Ghi chú")

class ExportItemResponse(BaseModel):
    product_id: str
    product_name: str
    quantity: int

class ExportOrderResponse(BaseModel):
    id: str
    items: List[ExportItemResponse]
    reason: Optional[str] = None
    note: Optional[str] = None
    created_by: str
    created_at: datetime
