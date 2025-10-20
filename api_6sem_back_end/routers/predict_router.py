import os
import joblib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# ---------------------- [1] Pré-processamento (igual ao treinamento) ---------------------- #
def preprocess_text(text: str):
    text = str(text).lower()
    text = text.replace(r'[^\w\s]', '')
    return text


# ---------------------- [2] Carregamento dos Artefatos ---------------------- #
APP_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ARTIFACTS_DIR = os.path.join(APP_ROOT_DIR, "ml", "artifacts")

try:
    model = joblib.load(os.path.join(ARTIFACTS_DIR, 'faq_classifier_model.pkl'))
    vectorizer = joblib.load(os.path.join(ARTIFACTS_DIR, 'faq_tfidf_vectorizer.pkl'))
    le = joblib.load(os.path.join(ARTIFACTS_DIR, 'faq_label_encoder.pkl'))
    print("🤖 Modelo de Classificação FAQ carregado com sucesso!")
except FileNotFoundError as e:
    print(f"❌ Erro ao carregar artefatos: {e}")
    model = vectorizer = le = None


# ---------------------- [3] Definições do Router ---------------------- #
router = APIRouter(prefix="/faq", tags=["FAQ Classifier"])


# ---------------------- [4] Schemas ---------------------- #
class QuestionRequest(BaseModel):
    """Entrada com uma pergunta (texto)."""
    question: str

class AnswerRequest(BaseModel):
    """Entrada com uma resposta (texto)."""
    answer: str


# ---------------------- [5] Endpoint: Predição baseada na PERGUNTA ---------------------- #
@router.post("/predict_by_question")
def predict_topic_from_question(request: QuestionRequest):
    """
    Classifica o tema da pergunta enviada, com base no modelo de FAQ treinado.
    """
    if not model or not vectorizer or not le:
        raise HTTPException(status_code=503, detail="Modelo não carregado no servidor.")

    processed_text = preprocess_text(request.question)
    X_vec = vectorizer.transform([processed_text])

    # Predição
    pred_label = model.predict(X_vec)[0]
    pred_category = le.inverse_transform([pred_label])[0]

    return {
        "input_type": "question",
        "input_text": request.question,
        "predicted_category": pred_category,
        "category_label_id": int(pred_label),
        "message": "Predição baseada no modelo Logistic Regression (FAQ Training)."
    }


# ---------------------- [6] Endpoint: Predição baseada na RESPOSTA ---------------------- #
@router.post("/predict_by_answer")
def predict_topic_from_answer(request: AnswerRequest):
    """
    Classifica o tema da resposta fornecida (útil para análise inversa de FAQs).
    """
    if not model or not vectorizer or not le:
        raise HTTPException(status_code=503, detail="Modelo não carregado no servidor.")

    processed_text = preprocess_text(request.answer)
    X_vec = vectorizer.transform([processed_text])

    pred_label = model.predict(X_vec)[0]
    pred_category = le.inverse_transform([pred_label])[0]

    return {
        "input_type": "answer",
        "input_text": request.answer,
        "predicted_category": pred_category,
        "category_label_id": int(pred_label),
        "message": "Predição baseada no modelo Logistic Regression (FAQ Training)."
    }


# ---------------------- [7] Endpoint Opcional: Teste de Saúde ---------------------- #
@router.get("/healthcheck")
def health_check():
    """
    Verifica se o modelo e os artefatos estão devidamente carregados.
    """
    status = {
        "model_loaded": model is not None,
        "vectorizer_loaded": vectorizer is not None,
        "label_encoder_loaded": le is not None
    }

    if all(status.values()):
        return {"status": "ok", "details": status}
    else:
        raise HTTPException(status_code=500, detail=status)
