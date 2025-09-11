from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["nome_do_seu_banco"]
collection = db["chamados"]
