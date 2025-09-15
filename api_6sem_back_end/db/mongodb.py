from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv  

load_dotenv() 
MONGO_URL = os.getenv("mongodb+srv://luminia:McdvG8uWGdMX14bZ@bd6sem-luminia.yllfoxm.mongodb.net/?retryWrites=true&w=majority&appName=bd6sem-luminia")
MONGO_DB_NAME = os.getenv("bd6sem-luminia")  

client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB_NAME]  