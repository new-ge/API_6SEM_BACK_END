from pydantic import BaseModel
from typing import Dict, Any

class FilterModel(BaseModel):
    filtro: Dict[str, Any]