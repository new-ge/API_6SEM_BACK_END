from fastapi import FastAPI
from controllers.ticket_controller import router 

app = FastAPI()

@app.get("/")
async def root():
    return "Back"

#Controller Tickets
app.include_router(router)
