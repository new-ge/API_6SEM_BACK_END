from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
<<<<<<< HEAD
from api_6sem_back_end.routers import router_opened, router_average_time, router_by_period, router_tag_filter, router_sla, router_priority_filter
=======
from api_6sem_back_end.routers import router_opened, router_average_time, router_by_period, router_tag_filter, router_sla, router_recurring_tickets

>>>>>>> 929b237d97b9989c7390bab993e3d3dbc41952b5
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
    allow_headers=["Content-Type"],
)

app.include_router(router_by_period.router)
app.include_router(router_average_time.router)
app.include_router(router_opened.router)
app.include_router(router_tag_filter.router)
app.include_router(router_sla.router)
<<<<<<< HEAD
app.include_router(router_priority_filter.router)
=======
app.include_router(router_recurring_tickets.router)
>>>>>>> 929b237d97b9989c7390bab993e3d3dbc41952b5

@app.get("/")
async def root():
    return {"mensagem": "API está rodando! Use /docs para explorar os endpoints."}
