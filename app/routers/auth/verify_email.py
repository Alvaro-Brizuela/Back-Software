from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database import get_db
from app.models.generated import LoginUsuario

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/verify-email/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    # 1. Buscar usuario con ese token
    login_entry = db.query(LoginUsuario).filter(
        LoginUsuario.email_verificacion_hash == token
    ).first()

    if not login_entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido"
        )

    # 2. Verificar si el token expiró
    if login_entry.email_verificacion_expira < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expirado"
        )

    # 3. Marcar correo como verificado
    login_entry.email_verificado_at = datetime.now(timezone.utc)
    login_entry.email_verificacion_hash = None   # evitar reutilización del token
    login_entry.email_verificacion_expira = None # limpiar expiración

    db.commit()

    return {
        "msg": "Correo verificado con éxito ✅",
        "email": login_entry.correo
    }
