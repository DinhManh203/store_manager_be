from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SupplierCreate(BaseModel):
    name: str = Field(..., description="Tên nhà cung cấp")
    phone: Optional[str] = Field(None, description="Số điện thoại")
    email: Optional[str] = Field(None, description="Email")
    address: Optional[str] = Field(None, description="Địa chỉ")
    is_active: bool = Field(True, description="Trạng thái cung cấp")


class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Tên nhà cung cấp")
    phone: Optional[str] = Field(None, description="Số điện thoại")
    email: Optional[str] = Field(None, description="Email")
    address: Optional[str] = Field(None, description="Địa chỉ")
    is_active: Optional[bool] = Field(None, description="Trạng thái cung cấp")


class SupplierResponse(BaseModel):
    id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True
    created_at: datetime
