from datetime import datetime

from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    message: str
    actor_username: str
    actor_full_name: str | None = None
    actor_role: str | None = None
    product_id: str | None = None
    product_name: str | None = None
    created_at: datetime
    is_read: bool = False


class NotificationListResponse(BaseModel):
    unread_count: int = Field(default=0, ge=0)
    total: int = Field(default=0, ge=0)
    items: list[NotificationResponse] = Field(default_factory=list)


class NotificationMarkReadResponse(BaseModel):
    success: bool = True
    notification_id: str


class NotificationMarkAllReadResponse(BaseModel):
    success: bool = True
    updated_count: int = Field(default=0, ge=0)
