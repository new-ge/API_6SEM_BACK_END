from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

client = AsyncIOMotorClient(
    "mongodb+srv://luminia:McdvG8uWGdMX14bZ@bd6sem-luminia.yllfoxm.mongodb.net/?retryWrites=true&w=majority&appName=bd6sem-luminia",
    tlsAllowInvalidCertificates=True
)
db = client["bd6sem-luminia"]
collection = db["tikets"]


load_dotenv()  # Isso carrega as variáveis do .env automaticamente
