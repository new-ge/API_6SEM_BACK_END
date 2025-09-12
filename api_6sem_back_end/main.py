from fastapi import FastAPI
from api_6sem_back_end.routers import router_chamados  # ou o nome/caminho certo do seu arquivo de rotas

app = FastAPI()

app.include_router(router_chamados.router) 

@app.get("/")
async def root():
    return {"mensagem": "API está rodando! Use /docs para explorar os endpoints."}