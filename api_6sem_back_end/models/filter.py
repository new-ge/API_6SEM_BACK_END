from pydantic import BaseModel
from typing import Dict, Any

class Filtro(BaseModel):
    filtro: Dict[str, Any] = {}
