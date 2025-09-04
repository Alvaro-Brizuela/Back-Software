from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.models.generated import Sesiones
from app.services import auth

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/refresh")
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    # 1. Buscar sesión por el refresh token
    sesion = db.query(Sesiones).filter(Sesiones.tokenrefresh_hash == refresh_token).first()

    if not sesion:
        raise HTTPException(status_code=401, detail="Refresh token inválido")

    # 2. Revisar si está revocado
    if sesion.revoked_at is not None:
        raise HTTPException(status_code=401, detail="Refresh token revocado")

    # 3. Revisar si expiró
    if sesion.limite_sesion < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expirado")

    # 4. Generar nuevo Access Token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": str(sesion.idusuario)}, 
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
