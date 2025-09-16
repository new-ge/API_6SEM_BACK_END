from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv  

load_dotenv() 
MONGO_URL = "mongodb+srv://luminia:6O3oH7hyJv5y47pJ@bd6sem-luminia.yllfoxm.mongodb.net/?retryWrites=true&w=majority&appName=bd6sem-luminia"
MONGO_DB_NAME = "bd6sem-luminia"

client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB_NAME]  