from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProductCreate(BaseModel):
    name: str = Field(..., description="Tên sản phẩm")
    description: Optional[str] = Field(None, description="Mô tả sản phẩm")
    price: float = Field(..., gt=0, description="Giá sản phẩm")
    stock: int = Field(0, ge=0, description="Số lượng tồn kho")
    category: str = Field(..., description="Danh mục sản phẩm")
    image_url: Optional[str] = Field(None, description="URL hình ảnh sản phẩm")

class ProductResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category: str
    image_url: Optional[str] = None
    created_at: datetime
