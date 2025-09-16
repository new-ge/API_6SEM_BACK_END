from fastapi import FastAPI
from api_6sem_back_end.routers import router_opened, router_average_time, router_by_period

app = FastAPI()

app.include_router(router_by_period.router)
app.include_router(router_average_time.router)
app.include_router(router_opened.router)

@app.get("/")
async def root():
    return {"mensagem": "API está rodando! Use /docs para explorar os endpoints."}