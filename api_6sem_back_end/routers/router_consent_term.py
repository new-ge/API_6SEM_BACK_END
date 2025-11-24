from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from api_6sem_back_end.repositories.repository_login_security import verify_token
from api_6sem_back_end.db.db_configuration import db_data

router = APIRouter(prefix="/users", tags=["Users"])
collection = db_data["users"]

@router.put("/consent")
def set_consent(consent_data: dict, payload=Depends(verify_token)):
    try:
        user_id = consent_data.get("agent_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="agent_id é obrigatório")

        consent = bool(consent_data.get("consent", False))

        result = collection.update_one(
            {"agent_id": user_id},
            {"$set": {"consent": consent}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        return {
            "message": "Consentimento registrado com sucesso!",
            "user_id": user_id,
            "consent": consent
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ConsentStatusResponse(BaseModel):
    consent: bool

@router.get("/consent-status", response_model=ConsentStatusResponse, payload=Depends(verify_token))
async def get_consent_status(agent_id: int):
    user = collection.find_one({"agent_id": agent_id})

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    consent_status = user.get("consent", False)

    return {"consent": consent_status}
