from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv  

load_dotenv() 
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("testluminia")  

client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB_NAME]  