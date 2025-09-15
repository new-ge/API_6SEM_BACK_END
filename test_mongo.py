import motor.motor_asyncio
import asyncio
import certifi

async def test_connection():
    client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb+srv://luminia:McdvG8uWGdMX14bZ@bd6sem-luminia.yllfoxm.mongodb.net/?retryWrites=true&w=majority&appName=bd6sem-luminia",
        tlsCAFile=certifi.where()
    )
    try:
        print(await client.server_info())
        print("✅ Conectado com sucesso ao MongoDB")
    except Exception as e:
        print("❌ Erro ao conectar:", e)

asyncio.run(test_connection())
