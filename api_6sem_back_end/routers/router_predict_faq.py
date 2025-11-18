from fastapi import APIRouter, Depends, HTTPException, Query
from api_6sem_back_end.ml.ml_faq_inference import search_similar_questions
from api_6sem_back_end.repositories.repository_login_security import verify_token

router = APIRouter(prefix="/faq", tags=["FAQ Classifier"])

@router.get("/search")
def search_faq(payload=Depends(verify_token), question: str = Query(..., description="Pergunta do usuário")):
    if payload.get("role") == "N1":
        try:
            results = search_similar_questions(question)
            return {"query": question, "results": results}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))