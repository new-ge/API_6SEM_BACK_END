from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("DB_URL_MONGO")

client = AsyncIOMotorClient(MONGO_URI)
db = client["bd6sem-luminia"]
collection = db["tickets"]
