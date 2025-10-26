import os
import re
import joblib
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from api_6sem_back_end.ml.faq_inference import search_similar_questions
from api_6sem_back_end.db.de import db_data


# ---------------------- [1] Pré-processamento (igual ao treinamento) ---------------------- #
def preprocess_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r'[^\w\s]', ' ', text)        # remove pontuação
    text = re.sub(r'\s+', ' ', text).strip()    # remove espaços extras
    return text

# ---------------------- [2] Carregamento dos Artefatos ---------------------- #
APP_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ARTIFACTS_DIR = os.path.join(APP_ROOT_DIR, "ml", "artifacts")

try:
    model = joblib.load(os.path.join(ARTIFACTS_DIR, 'faq_classifier_model.pkl'))
    le = joblib.load(os.path.join(ARTIFACTS_DIR, 'faq_label_encoder.pkl'))
    print("🤖 Modelo de Classificação FAQ carregado com sucesso!")
except FileNotFoundError as e:
    print(f"❌ Erro ao carregar artefatos: {e}")
    model = le = None

# Carregar embedder do SentenceTransformer
try:
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    print("🤖 Embedder carregado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao carregar embedder: {e}")
    embedder = None

# ---------------------- [3] Definições do Router ---------------------- #
router = APIRouter(prefix="/faq", tags=["FAQ Classifier"])

# ---------------------- [4] Schemas ---------------------- #
class QuestionRequest(BaseModel):
    question: str

class AnswerRequest(BaseModel):
    answer: str

# ---------------------- [5] Endpoint: Predição baseada na PERGUNTA ---------------------- #
@router.post("/predict_by_question")
def predict_topic_from_question(request: QuestionRequest):
    if not model or not embedder or not le:
        raise HTTPException(status_code=503, detail="Modelo ou embedder não carregados no servidor.")

    processed_text = preprocess_text(request.question)
    X_vec = embedder.encode([processed_text], convert_to_numpy=True)

    pred_label = model.predict(X_vec)[0]
    pred_category = le.inverse_transform([pred_label])[0]

    return {
        "input_type": "question",
        "input_text": request.question,
        "predicted_category": pred_category,
        "category_label_id": int(pred_label),
        "message": "Predição baseada em embeddings semânticos (SentenceTransformer)."
    }

# ---------------------- [6] Endpoint: Predição baseada na RESPOSTA ---------------------- #
@router.post("/predict_by_answer")
def predict_topic_from_answer(request: AnswerRequest):
    if not model or not embedder or not le:
        raise HTTPException(status_code=503, detail="Modelo ou embedder não carregados no servidor.")

    processed_text = preprocess_text(request.answer)
    X_vec = embedder.encode([processed_text], convert_to_numpy=True)

    pred_label = model.predict(X_vec)[0]
    pred_category = le.inverse_transform([pred_label])[0]

    return {
        "input_type": "answer",
        "input_text": request.answer,
        "predicted_category": pred_category,
        "category_label_id": int(pred_label),
        "message": "Predição baseada em embeddings semânticos (SentenceTransformer)."
    }

# ---------------------- [7] Endpoint: Teste de Saúde ---------------------- #
@router.get("/healthcheck")
def health_check():
    status = {
        "model_loaded": model is not None,
        "embedder_loaded": embedder is not None,
        "label_encoder_loaded": le is not None
    }

    if all(status.values()):
        return {"status": "ok", "details": status}
    else:
        raise HTTPException(status_code=500, detail=status)

# ---------------------- [8] Endpoint: Busca de Perguntas Semelhantes ---------------------- #
@router.get("/search")
def search_faq(question: str = Query(..., description="Pergunta do usuário")):
    try:
        results = search_similar_questions(question)
        return {"query": question, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
