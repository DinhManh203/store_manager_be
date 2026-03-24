from fastapi import FastAPI
from routers import auth, users, products

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)

@app.get("/")
def read_root():
    return {"message": "Hello World = Xin chào FastAPI"}