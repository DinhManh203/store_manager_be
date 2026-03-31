from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pymongo.errors import PyMongoError

from database import get_db
from models.notification import (
    NotificationListResponse,
    NotificationMarkAllReadResponse,
    NotificationMarkReadResponse,
    NotificationResponse,
)
from utils.dependencies import get_current_user
from utils.helpers import convert_objectid_to_str, is_valid_objectid

router = APIRouter(prefix="/thong-bao", tags=["thong-bao"])


def _read_string(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def _read_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _build_notification_response(doc: dict, current_username: str) -> NotificationResponse:
    doc_copy = convert_objectid_to_str(dict(doc))
    read_by = _read_string_list(doc_copy.get("read_by"))

    created_at = doc_copy.get("created_at")
    if not isinstance(created_at, datetime):
        created_at = datetime.now(timezone.utc)

    return NotificationResponse(
        id=_read_string(doc_copy.get("id")),
        type=_read_string(doc_copy.get("type")) or "product_created",
        title=_read_string(doc_copy.get("title")) or "Thong bao",
        message=_read_string(doc_copy.get("message")),
        actor_username=_read_string(doc_copy.get("actor_username")),
        actor_full_name=_read_string(doc_copy.get("actor_full_name")) or None,
        actor_role=_read_string(doc_copy.get("actor_role")) or None,
        product_id=_read_string(doc_copy.get("product_id")) or None,
        product_name=_read_string(doc_copy.get("product_name")) or None,
        created_at=created_at,
        is_read=current_username in read_by,
    )


async def create_product_created_notification(actor: dict, product_doc: dict) -> None:
    db = get_db()

    actor_username = _read_string(actor.get("username"))
    actor_full_name = _read_string(actor.get("full_name"))
    actor_display_name = actor_full_name or actor_username or "Mot nhan vien"

    product_name = _read_string(product_doc.get("name")) or "San pham moi"
    raw_product_id = product_doc.get("_id", product_doc.get("id"))
    product_id = str(raw_product_id).strip() if raw_product_id is not None else ""

    notification_doc = {
        "type": "product_created",
        "title": "San pham moi",
        "message": f"{actor_display_name} vua them san pham {product_name} vao kho.",
        "actor_username": actor_username,
        "actor_full_name": actor_full_name or None,
        "actor_role": _read_string(actor.get("role")) or None,
        "product_id": product_id or None,
        "product_name": product_name,
        # Every employee should see this as unread first.
        "read_by": [],
        "created_at": datetime.now(timezone.utc),
    }
    await db.notifications.insert_one(notification_doc)


async def create_product_updated_notification(actor: dict, product_doc: dict) -> None:
    db = get_db()

    actor_username = _read_string(actor.get("username"))
    actor_full_name = _read_string(actor.get("full_name"))
    actor_display_name = actor_full_name or actor_username or "Mot nhan vien"

    product_name = _read_string(product_doc.get("name")) or "San pham"
    raw_product_id = product_doc.get("_id", product_doc.get("id"))
    product_id = str(raw_product_id).strip() if raw_product_id is not None else ""

    notification_doc = {
        "type": "product_updated",
        "title": "Cap nhat san pham",
        "message": f"{actor_display_name} vua chinh sua san pham {product_name}.",
        "actor_username": actor_username,
        "actor_full_name": actor_full_name or None,
        "actor_role": _read_string(actor.get("role")) or None,
        "product_id": product_id or None,
        "product_name": product_name,
        # Every employee should see this as unread first.
        "read_by": [],
        "created_at": datetime.now(timezone.utc),
    }
    await db.notifications.insert_one(notification_doc)


@router.get("/danh-sach", response_model=NotificationListResponse)
async def danh_sach_thong_bao(
    only_unread: bool = Query(default=False, alias="onlyUnread"),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    username = _read_string(current_user.get("username"))
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Khong the xac dinh tai khoan dang nhap.",
        )

    db = get_db()
    query: dict = {"read_by": {"$ne": username}} if only_unread else {}

    try:
        cursor = db.notifications.find(query).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)

        unread_count = await db.notifications.count_documents({"read_by": {"$ne": username}})
        total = await db.notifications.count_documents(query)

        items = [_build_notification_response(doc, username) for doc in docs]

        return NotificationListResponse(unread_count=unread_count, total=total, items=items)
    except PyMongoError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Khong the ket noi co so du lieu. Vui long thu lai sau.",
        )


@router.put(
    "/danh-dau-da-doc/{notification_id}",
    response_model=NotificationMarkReadResponse,
)
async def danh_dau_da_doc(notification_id: str, current_user: dict = Depends(get_current_user)):
    if not is_valid_objectid(notification_id):
        raise HTTPException(status_code=400, detail="ID thong bao khong hop le")

    username = _read_string(current_user.get("username"))
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Khong the xac dinh tai khoan dang nhap.",
        )

    db = get_db()
    try:
        result = await db.notifications.update_one(
            {"_id": ObjectId(notification_id)},
            {
                "$addToSet": {"read_by": username},
                "$set": {"updated_at": datetime.now(timezone.utc)},
            },
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Khong tim thay thong bao")

        return NotificationMarkReadResponse(notification_id=notification_id)
    except HTTPException:
        raise
    except PyMongoError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Khong the ket noi co so du lieu. Vui long thu lai sau.",
        )


@router.put("/danh-dau-tat-ca-da-doc", response_model=NotificationMarkAllReadResponse)
async def danh_dau_tat_ca_da_doc(current_user: dict = Depends(get_current_user)):
    username = _read_string(current_user.get("username"))
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Khong the xac dinh tai khoan dang nhap.",
        )

    db = get_db()
    try:
        result = await db.notifications.update_many(
            {"read_by": {"$ne": username}},
            {
                "$addToSet": {"read_by": username},
                "$set": {"updated_at": datetime.now(timezone.utc)},
            },
        )
        return NotificationMarkAllReadResponse(updated_count=result.modified_count)
    except PyMongoError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Khong the ket noi co so du lieu. Vui long thu lai sau.",
        )
