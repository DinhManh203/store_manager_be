from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BranchCreate(BaseModel):
    name: str = Field(..., description="Tên chi nhánh/cửa hàng phụ")
    address: Optional[str] = Field(None, description="Địa chỉ")
    phone: Optional[str] = Field(None, description="Số điện thoại")
    manager: Optional[str] = Field(None, description="Người quản lý (tuỳ chọn)")
    is_active: bool = Field(True, description="Trạng thái hoạt động")

class BranchUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Tên chi nhánh/cửa hàng phụ")
    address: Optional[str] = Field(None, description="Địa chỉ")
    phone: Optional[str] = Field(None, description="Số điện thoại")
    manager: Optional[str] = Field(None, description="Người quản lý (tuỳ chọn)")
    is_active: Optional[bool] = Field(None, description="Trạng thái hoạt động")

class BranchResponse(BaseModel):
    id: str
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    manager: Optional[str] = None
    is_active: bool
    created_at: datetime
