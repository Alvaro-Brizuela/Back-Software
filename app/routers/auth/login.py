from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
import secrets
from app.database import get_db
from app.models.generated import LoginUsuario, Usuario
from app.models.generated import Sesiones
from app.services import auth
from app.schemas.login import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
def login_user(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    # 1. Buscar login por correo
    login_entry = db.query(LoginUsuario).filter(LoginUsuario.correo == data.email).first()
    if not login_entry or not auth.verify_password(data.password, login_entry.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not login_entry.email_verificado_at:
        raise HTTPException(status_code=403, detail="Correo no verificado")

    # 2. Traer empresa asociada al usuario
    usuario = db.query(Usuario).filter(Usuario.id_usuario == login_entry.id_usuario).first()
    empresa_id = usuario.id_empresa if usuario else None

    # 3. Crear Access Token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={
            "sub": str(login_entry.id_usuario),
            "empresa_id": str(empresa_id),
            "rol": str(login_entry.tipo_usuario)
        },
        expires_delta=access_token_expires
    )

    # 4. Crear Refresh Token y guardarlo en tabla sesiones
    refresh_token = secrets.token_urlsafe(64)
    sesion = Sesiones(
        idusuario=login_entry.id_login,
        tokenrefresh_hash=refresh_token,
        fecha_sesion=datetime.now(timezone.utc),
        limite_sesion=datetime.now(timezone.utc) + timedelta(days=auth.REFRESH_TOKEN_EXPIRE_DAYS),
        revoked_at=None,
        user_agent=request.headers.get("user-agent"),
        ip=request.client.host
    )
    db.add(sesion)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "usuario_id": login_entry.id_usuario,
        "empresa_id": empresa_id,
        "rol": login_entry.tipo_usuario
    }
