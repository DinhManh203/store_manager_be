import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRole(str, Enum):
    admin = "admin"
    user = "user"


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.user
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    username: str
    email: EmailStr
    role: UserRole
    full_name: Optional[str] = None
    phone: Optional[str] = None


class EmployeeCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=9, max_length=15)
    role: UserRole = UserRole.user
    temporary_password: str = Field(min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("Tên nhân viên không được để trống")
        return normalized

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        normalized = value.strip().replace(" ", "")
        if not re.fullmatch(r"^\+?[0-9]{9,15}$", normalized):
            raise ValueError("Số điện thoại không hợp lệ")
        return normalized


class EmployeeCreateResponse(BaseModel):
    id: str
    username: str
    full_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    role: UserRole


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=9, max_length=15)
    role: Optional[UserRole] = None
    temporary_password: Optional[str] = Field(default=None, min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def normalize_full_name_update(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("Tên nhân viên không được để trống")
        return normalized

    @field_validator("phone")
    @classmethod
    def validate_phone_update(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.strip().replace(" ", "")
        if not re.fullmatch(r"^\+?[0-9]{9,15}$", normalized):
            raise ValueError("Số điện thoại không hợp lệ")
        return normalized


class EmployeeDeleteResponse(BaseModel):
    message: str
    deleted_user_id: str
    deleted_username: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
