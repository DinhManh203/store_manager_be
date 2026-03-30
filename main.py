from fastapi import FastAPI
from routers import auth, users, products, suppliers, inventory, imports, exports, roles, reports

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

@app.get("/")
def read_root():
    return {"message": "Backend is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
