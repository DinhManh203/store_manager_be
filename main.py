import asyncio
import os
from datetime import datetime, timezone

from fastapi import FastAPI

from database import get_db
from models.user import UserRole
from routers import auth, users, products, suppliers, inventory, imports, exports, roles, reports
from utils.security import get_password_hash

app = FastAPI(title="Hệ thống Quản lý Kho", version="1.0.0")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(suppliers.router)
app.include_router(inventory.router)
app.include_router(imports.router)
app.include_router(exports.router)
app.include_router(roles.router)
app.include_router(reports.router)


async def ensure_demo_admin_account():
    admin_username = os.getenv("ADMIN_USER_NAME", "").strip()
    admin_password = os.getenv("ADMIN_PASSWORD", "").strip()

    if not admin_username or not admin_password:
        return

    db = get_db()
    existing_user = await db.users.find_one({"username": admin_username})

    if existing_user:
        update_fields = {
            "role": UserRole.admin.value,
            "password": get_password_hash(admin_password),
            "is_demo_admin": True,
            "updated_at": datetime.now(timezone.utc),
        }
        if not existing_user.get("full_name"):
            update_fields["full_name"] = "System Admin"
        await db.users.update_one({"_id": existing_user["_id"]}, {"$set": update_fields})
        return

    demo_admin_email = f"{admin_username}@demo.local"
    email_suffix = 1
    while await db.users.find_one({"email": demo_admin_email}):
        demo_admin_email = f"{admin_username}{email_suffix}@demo.local"
        email_suffix += 1

    demo_admin_user = {
        "username": admin_username,
        "email": demo_admin_email,
        "password": get_password_hash(admin_password),
        "role": UserRole.admin.value,
        "full_name": "Demo Admin",
        "is_demo_admin": True,
        "created_at": datetime.now(timezone.utc),
    }
    await db.users.insert_one(demo_admin_user)


@app.on_event("startup")
async def startup_event():
    async def seed_demo_admin():
        try:
            await asyncio.wait_for(ensure_demo_admin_account(), timeout=5)
        except asyncio.TimeoutError:
            print("[startup] Skip demo admin seed: database timeout")
        except Exception as error:
            print(f"[startup] Skip demo admin seed: {error}")

    asyncio.create_task(seed_demo_admin())


@app.get("/")
def read_root():
    return {"message": "Backend is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
