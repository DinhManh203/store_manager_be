import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_DETAILS = os.getenv("MONGO_DETAILS")
MONGO_TIMEOUT_MS = int(os.getenv("MONGO_SERVER_SELECTION_TIMEOUT_MS", "5000"))

client_options = {
    "serverSelectionTimeoutMS": MONGO_TIMEOUT_MS,
}
if MONGO_DETAILS and MONGO_DETAILS.startswith("mongodb+srv://"):
    client_options["tls"] = True
    client_options["tlsCAFile"] = certifi.where()

client = AsyncIOMotorClient(MONGO_DETAILS, **client_options)
db = client.doan_thanh

def get_db():
    return db
