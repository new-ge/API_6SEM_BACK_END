from fastapi import FastAPI
from api_6sem_back_end.routers import router_chamados  # ou o nome/caminho certo do seu arquivo de rotas

app = FastAPI()

app.include_router(router_chamados.router)  # ajuste conforme o nome do seu roteador


