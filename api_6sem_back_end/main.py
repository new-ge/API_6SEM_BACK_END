from fastapi import FastAPI
from api_6sem_back_end.routers import router_chamados
from api_6sem_back_end.routers import router_average_time

app = FastAPI()

app.include_router(router_chamados.router)
app.include_router(router_average_time.router)  

@app.get("/")
async def root():
    return {"mensagem": "API está rodando! Use /docs para explorar os endpoints."}

