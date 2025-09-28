import joblib
from fastapi import APIRouter
from api_6sem_back_end.db.db_configuration import db

router = APIRouter(prefix="/tickets", tags=["Tickets"])
collection = db["tickets"]

model_path = "api_6sem_back_end/ml/sentiment_model.pkl"
pipeline = joblib.load(model_path)

@router.get("/sentiment_counts")
def sentiment_counts():
    docs = collection.find({}, {"description": 1, "_id": 0})
    descriptions = [doc.get("description", "").strip() for doc in docs if doc.get("description")]

    if not descriptions:
        return {"message": "Nenhuma descrição encontrada para classificar."}

    predictions = pipeline.predict(descriptions)

    counts = {"positivo": 0, "negativo": 0}
    for pred in predictions:
        if pred in counts:
            counts[pred] += 1
        else:
            counts[pred] = 1  

    return counts
