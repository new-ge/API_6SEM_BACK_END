import glob
import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
import datetime
import jwt
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

dotenv_path = glob.glob(os.path.join(os.path.dirname(__file__), "*.env"))
load_dotenv(dotenv_path[0])

security = HTTPBearer()
SECRET_KEY = os.getenv("KEY_JWT")

def create_jwt_token(username, role):
    payload = {
        "username": username,
        "role": role,
        "iat": int(datetime.datetime.now().timestamp()),
        "exp": int((datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp())
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return token

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")