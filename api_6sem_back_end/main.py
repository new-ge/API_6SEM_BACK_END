from fastapi import FastAPI
from api_6sem_back_end.router.ticket_router import router 

app = FastAPI()

@app.get("/")
async def root():
    return "Back"

#Controller Tickets
app.include_router(router)
