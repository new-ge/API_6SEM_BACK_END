from fastapi import FastAPI

from api_6sem_back_end.routers.router_chamados import router as router_chamados
from api_6sem_back_end.routers.router_tag_filter import router as router_tag_filter
from api_6sem_back_end.routers.router_average_time import router as router_average_time

app = FastAPI()

app.include_router(router_chamados)      
app.include_router(router_tag_filter)    
app.include_router(router_average_time)

@app.get("/")
async def root():
    return {"mensagem": "API está rodando! Use /docs para explorar os endpoints."}