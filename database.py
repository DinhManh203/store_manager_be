import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_DETAILS = os.getenv("MONGO_DETAILS")

client_options = {
    "serverSelectionTimeoutMS": 30000,
}
if MONGO_DETAILS and MONGO_DETAILS.startswith("mongodb+srv://"):
    client_options["tls"] = True
    client_options["tlsCAFile"] = certifi.where()

client = AsyncIOMotorClient(MONGO_DETAILS, **client_options)
db = client.doan_thanh

def get_db():
    return db
