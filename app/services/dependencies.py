from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.services import auth

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login_api")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = auth.decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "usuario_id": int(payload.get("sub")),
        "empresa_id": int(payload.get("empresa_id")),
        "rol": int(payload.get("rol"))
    }
