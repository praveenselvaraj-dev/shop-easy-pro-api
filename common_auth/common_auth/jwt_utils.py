# common_auth/jwt_utils.py
import os
from datetime import datetime, timedelta
from typing import Dict, Any

import jwt  

SECRET_KEY = os.getenv("JWT_SECRET", "supersecret123")
ALGORITHM = os.getenv("JWT_ALGO", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

def create_access_token(subject: str, extra: Dict[str, Any] = None, expires_minutes: int = None) -> str:
    expire = datetime.utcnow() + timedelta(minutes=(expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": subject, "exp": expire}
    if extra:
        payload.update(extra)
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

def decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("token_expired")
    except jwt.PyJWTError:
        raise Exception("token_invalid")
