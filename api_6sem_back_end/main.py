from glob import glob
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api_6sem_back_end.routers import router_opened, router_average_time, router_by_period, router_predict_faq, router_simulate_login, router_sla, router_recurring_tickets, router_primary_themes, router_sentiment
from api_6sem_back_end.routers.router_login import validate_login
import os
from dotenv import load_dotenv
import os

dotenv_path = glob(os.path.join(os.path.dirname(__file__), "*.env"))
load_dotenv(dotenv_path[0])

app = FastAPI()

allow_origins = [
    "http://localhost:5173",
    "https://localhost:5173",
]

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
app.include_router(router_sla.router)
app.include_router(router_recurring_tickets.router)
app.include_router(router_sentiment.router)
app.include_router(router_primary_themes.router)
app.include_router(router_sentiment.router)
app.include_router(router_predict_faq.router)
app.include_router(router_simulate_login.router)

@app.get("/")
async def root():
    return {"mensagem": "API está rodando! Use /docs para explorar os endpoints."}


