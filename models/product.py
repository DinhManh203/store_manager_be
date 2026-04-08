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
    supplier_id: str = Field(..., description="ID nhà cung cấp")
    supplier_name: str = Field(..., description="Tên nhà cung cấp")

class ProductResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category: str
    image_url: Optional[str] = None
    supplier_id: str
    supplier_name: str
    created_at: datetime

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Tên sản phẩm")
    description: Optional[str] = Field(None, description="Mô tả sản phẩm")
    price: Optional[float] = Field(None, gt=0, description="Giá sản phẩm")
    stock: Optional[int] = Field(None, ge=0, description="Số lượng tồn kho")
    category: Optional[str] = Field(None, description="Danh mục sản phẩm")
    image_url: Optional[str] = Field(None, description="URL hình ảnh sản phẩm")
    supplier_id: Optional[str] = Field(None, description="ID nhà cung cấp")
    supplier_name: Optional[str] = Field(None, description="Tên nhà cung cấp")
