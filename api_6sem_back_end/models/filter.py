from pydantic import BaseModel
from typing import Optional, Dict, Any

class Filter(BaseModel):
    filtro: Optional[Dict[str, Any]]
