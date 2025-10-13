from fastapi import APIRouter
from pydantic import BaseModel
from api_6sem_back_end.services.service_predict import predict_category

# Schema de entrada da requisição
class PredictRequest(BaseModel):
    title: str
    description: str
    category_encoded: int

router = APIRouter()

@router.post("/predict")
def predict(data: PredictRequest):
    categoria = predict_category(data.title, data.description, data.category_encoded)
    return {"categoria_prevista": categoria}
