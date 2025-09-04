from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.generated import Empresa
from app.models.generated import Usuario
from app.models.generated import LoginUsuario
from app.schemas.register import Register
from app.services import auth
import secrets
from datetime import datetime, timedelta
from app.services.email_validation import send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register_user(data: Register, db: Session = Depends(get_db)):
    # 0. Validar que el correo no exista en login_usuario
    existing = db.query(LoginUsuario).filter(LoginUsuario.correo == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado"
        )

    # 1. Crear empresa vacía
    nueva_empresa = Empresa(
        id_territorial=None,
        rut_empresa=None,
        DV_rut=None,
        nombre_real="",
        nombre_fantasia="",
        razon_social="",
        giro="",
        fecha_constitucion=None,
        fecha_inicio_actividades=None,
        estado_suscripcion=0,
        direccion_fisica="",
        telefono="",
        correo=""
    )
    db.add(nueva_empresa)
    db.commit()
    db.refresh(nueva_empresa)

    # 2. Crear usuario ligado a la empresa
    nuevo_usuario = Usuario(
        nombre=data.name,
        apellido_paterno=data.paternal_surname,
        apellido_materno=data.maternal_surname,
        id_empresa=nueva_empresa.id_empresa
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    # 3. Crear login_usuario ligado al usuario
    hashed_password = auth.get_password_hash(data.password)
    verification_token = secrets.token_hex(32)  # 🔑 token único
    expiry_time = datetime.utcnow() + timedelta(hours=24)  # expira en 24h

    login_entry = LoginUsuario(
    telefono="",
    correo=data.email,
    password=hashed_password,
    id_usuario=nuevo_usuario.id_usuario,
    tipo_usuario=1,
    email_verificado_at=None,
    email_verificacion_hash=verification_token,
    email_verificacion_expira=expiry_time
    )
    db.add(login_entry)
    db.commit()
    db.refresh(login_entry)

    send_verification_email(login_entry.correo, login_entry.email_verificacion_hash) #enviar correo de verificación

    return {
        "msg": "Usuario registrado con éxito",
        "empresa_id": nueva_empresa.id_empresa,
        "usuario_id": nuevo_usuario.id_usuario,
        "login_id": login_entry.id_login,
        "email": login_entry.correo
    }