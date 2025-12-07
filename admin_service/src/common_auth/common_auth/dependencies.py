from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.common_auth.common_auth.jwt_utils import decode_token
from fastapi import Header

security = HTTPBearer()   

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = decode_token(token)
        return payload
    except Exception as e:
        if str(e) == "token_expired":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def get_raw_token(authorization: str = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        return authorization.split(" ")[1]
    return None

def admin_required(user = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user
