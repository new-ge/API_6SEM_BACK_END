from pydantic import BaseModel

class Tickets(BaseModel):
    title: str
    description: str
