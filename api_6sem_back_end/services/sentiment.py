import os
import joblib

from api_6sem_back_end.db_configuration import db

collection = db["your_collection_name"]  # ajuste o nome da sua collection

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../ml/sentiment_model.pkl")
model = joblib.load(MODEL_PATH)

def classify_ticket_sentiment(ticket_id: int):
    ticket = collection.find_one({"ticket_id": ticket_id})

    if not ticket:
        return {"error": "Ticket not found."}

    text = ticket["title"] + " " + ticket["description"]
    predicted_sentiment = model.predict([text])[0]

    collection.update_one(
        {"ticket_id": ticket_id},
        {"$set": {"sentiment": predicted_sentiment}}
    )

    return {
        "ticket_id": ticket_id,
        "sentiment": predicted_sentiment
    }
