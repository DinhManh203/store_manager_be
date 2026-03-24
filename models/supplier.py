from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SupplierCreate(BaseModel):
    name: str = Field(..., description="Tên nhà cung cấp")
    phone: Optional[str] = Field(None, description="Số điện thoại")
    email: Optional[str] = Field(None, description="Email")
    address: Optional[str] = Field(None, description="Địa chỉ")

class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Tên nhà cung cấp")
    phone: Optional[str] = Field(None, description="Số điện thoại")
    email: Optional[str] = Field(None, description="Email")
    address: Optional[str] = Field(None, description="Địa chỉ")

class SupplierResponse(BaseModel):
    id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime
