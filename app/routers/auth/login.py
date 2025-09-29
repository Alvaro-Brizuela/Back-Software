from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from hashlib import sha256
from datetime import timedelta, datetime, timezone
import secrets
from jose import jwt, JWTError

from app.database import get_db
from app.models.generated import LoginUsuario, Usuario, Sesiones
from app.services import auth
from app.schemas.login import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

# ---------------------------
# 1. LOGIN API (JSON)
# ---------------------------
@router.post("/login_api", response_model=LoginResponse)
def login_user(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    login_entry = db.query(LoginUsuario).filter(LoginUsuario.correo == data.email).first()
    if not login_entry or not auth.verify_password(data.password, login_entry.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not login_entry.email_verificado_at:
        raise HTTPException(status_code=403, detail="Correo no verificado")

    usuario = db.query(Usuario).filter(Usuario.id_usuario == login_entry.id_usuario).first()
    empresa_id = usuario.id_empresa if usuario else None

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={
            "sub": str(login_entry.id_usuario),
            "empresa_id": str(empresa_id),
            "rol": str(login_entry.tipo_usuario)
        },
        expires_delta=access_token_expires
    )

    refresh_token = secrets.token_urlsafe(64)
    sesion = Sesiones(
        idusuario=login_entry.id_login,
        tokenrefresh_hash=sha256(refresh_token.encode()).hexdigest(),
        fecha_sesion=datetime.now(timezone.utc),
        limite_sesion=datetime.now(timezone.utc) + timedelta(days=auth.REFRESH_TOKEN_EXPIRE_DAYS),
        revoked_at=None,
        user_agent=request.headers.get("user-agent"),
        ip=request.client.host
    )
    db.add(sesion)
    db.commit()

    role_map = {
    1: {"nombre": "admin", "redirect": "../datos_empresa/view_datos_empresa.html"},
    2: {"nombre": "contador", "redirect": "/dashboard/contabilidad"},
    3: {"nombre": "rrhh", "redirect": "/dashboard/rrhh"}
}
    rol_info = role_map.get(login_entry.tipo_usuario, {"nombre": "desconocido", "redirect": "/empresa"})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "usuario_id": login_entry.id_usuario,
        "empresa_id": empresa_id,
        "rol": login_entry.tipo_usuario,
        "rol_nombre": rol_info["nombre"],
        "redirect_url": rol_info["redirect"]
    }


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    # 👇 ruta relativa a app/templates
    return templates.TemplateResponse("views/Login/view_login.html", {"request": request})

@router.post("/login")
def login_html(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        data = LoginRequest(email=email, password=password)
        api_response = login_user(data=data, request=request, db=db)

        resp = RedirectResponse(url="/empresa", status_code=303)
        resp.set_cookie(
            key="access_token",
            value=api_response["access_token"],
            httponly=True,
            secure=False,  # ⚠️ cambia a True en producción
            samesite="lax"
        )
        return resp
    except Exception:
        return RedirectResponse(url="/login", status_code=303)

@router.get("/logout")
def logout():
    resp = RedirectResponse(url="/login", status_code=303)
    resp.delete_cookie("access_token")
    return resp
