from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api_6sem_back_end.routers import router_login, router_opened, router_average_time, router_by_period, router_tag_filter, router_sla, router_recurring_tickets, router_sentiment, router_primary_themes, router_login
import os
from dotenv import load_dotenv
import glob
from api_6sem_back_end.routers.router_login import validate_login

dotenv_path = glob.glob(os.path.join(os.path.dirname(__file__), "*.env"))
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
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(router_by_period.router)
app.include_router(router_average_time.router)
app.include_router(router_opened.router)
app.include_router(router_tag_filter.router)
app.include_router(router_sla.router)
app.include_router(router_recurring_tickets.router)
app.include_router(router_sentiment.router)
app.include_router(router_primary_themes.router)
app.include_router(router_login.router)


@app.get("/")
def auto_login():
    token = validate_login(os.getenv("USERNAME_GESTOR"), os.getenv("PASSWORD_GESTOR"))
    if token:
        return {"token": token}
    return {"error": "Não foi possível gerar token"}
