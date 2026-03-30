from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from database import get_db
from models.user import UserRole
from utils.dependencies import get_current_admin
from utils.helpers import is_valid_objectid

router = APIRouter(prefix="/phan-quyen", tags=["phan-quyen"])


@router.get("/danh-sach-quyen")
async def danh_sach_quyen():
    return [{"role": role.value, "description": role.name} for role in UserRole]


@router.post("/them-quyen")
async def them_quyen(role_name: str, current_admin: dict = Depends(get_current_admin)):
    existing_roles = [r.value for r in UserRole]
    if role_name in existing_roles:
        raise HTTPException(status_code=400, detail="Quyền này đã tồn tại")
    return {
        "message": (
            f"Quyền '{role_name}' đã được ghi nhận. "
            "Lưu ý: cần cập nhật Enum UserRole trong code để áp dụng vĩnh viễn."
        ),
        "role": role_name,
    }


@router.put("/cap-nhat-quyen/{user_id}")
async def cap_nhat_quyen_nguoi_dung(
    user_id: str,
    role: str,
    current_admin: dict = Depends(get_current_admin),
):
    db = get_db()
    if not is_valid_objectid(user_id):
        raise HTTPException(status_code=400, detail="ID người dùng không hợp lệ")

    valid_roles = [r.value for r in UserRole]
    if role not in valid_roles:
        raise HTTPException(
            status_code=400,
            detail=f"Quyền không hợp lệ. Các quyền cho phép: {', '.join(valid_roles)}",
        )

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    if user.get("is_demo_admin") and role != UserRole.admin.value:
        raise HTTPException(status_code=400, detail="Không thể hạ quyền tài khoản admin hệ thống")

    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": role}})
    return {"message": f"Đã cập nhật quyền của '{user['username']}' thành '{role}'"}
