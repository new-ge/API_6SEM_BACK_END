from glob import glob
import threading
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from api_6sem_back_end.db.db_mongo_manipulate_data import monitorar_backup
from api_6sem_back_end.routers import router_create_users, router_find_user, router_get_all_logs, router_get_all_users, router_login, router_opened, router_average_time, router_by_period, router_predict_faq, router_exceeded_sla, router_recurring_tickets, router_primary_themes, router_sentiment, router_delete_users, router_update_user

allow_origins = [
    "http://localhost:5173",
    "https://localhost:5173",
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = threading.Thread(target=monitorar_backup, daemon=True)
    thread.start()
    print("Thread de monitoramento iniciada.")
    yield 

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"]
)

app.include_router(router_by_period.router)
app.include_router(router_average_time.router)
app.include_router(router_opened.router)
app.include_router(router_exceeded_sla.router)
app.include_router(router_recurring_tickets.router)
app.include_router(router_sentiment.router)
app.include_router(router_primary_themes.router)
app.include_router(router_sentiment.router)
app.include_router(router_predict_faq.router)
app.include_router(router_login.router)
app.include_router(router_find_user.router)
app.include_router(router_update_user.router)
app.include_router(router_delete_users.router)
app.include_router(router_create_users.router)
app.include_router(router_get_all_users.router)
app.include_router(router_get_all_logs.router)

@app.get("/")
async def root():
    return {"mensagem": "API está rodando! Use /docs para explorar os endpoints."}