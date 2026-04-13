from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., description="Tên danh mục")


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Tên danh mục")


class CategoryResponse(BaseModel):
    id: str
    name: str
    created_at: datetime
