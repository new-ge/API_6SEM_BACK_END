from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class AnswerInput(BaseModel):
    answer: str

@router.post("/predict_topic_by_answer")
async def predict_topic_by_answer(input_data: AnswerInput):
    text = input_data.answer

    # Exemplo usando seu pipeline de predição (vectorizer + modelo)
    vectorized_text = vectorizer.transform([text])
    pred = model.predict(vectorized_text)[0]

    # Opcional: pegar o label do tema pela sua função de mapeamento
    topic_label = map_to_theme(pred)

    return {
        "input_text": text,
        "predicted_topic": topic_label,
        "topic_label_id": pred,
        "message": "Predição baseada na classificação da Decision Tree.",
        "confidence_note": "Tópico específico. O modelo está funcionando corretamente para este tipo de classe."
    }
