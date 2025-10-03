from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services import auth

bearer_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    payload = auth.decode_access_token(token)

    # Debug (opcional, solo mientras pruebas)
    print("DEBUG PAYLOAD:", payload)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validar campos requeridos
    if not payload.get("sub") or not payload.get("empresa_id") or not payload.get("rol"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no contiene los campos necesarios (sub, empresa_id, rol)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return {
            "usuario_id": int(payload["sub"]),
            "empresa_id": int(payload["empresa_id"]),
            "rol": int(payload["rol"])
        }
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Los datos del token no son válidos",
            headers={"WWW-Authenticate": "Bearer"},
        )
