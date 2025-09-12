from pydantic import BaseModel, EmailStr, Field, field_validator

# ------------------------------
# Request
# ------------------------------

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico válido del usuario")
    password: str = Field(
        ...,
        min_length=8,
        max_length=20,
        description="Contraseña (8-20 caracteres, al menos 1 mayúscula, 1 minúscula y 1 número)"
    )

    # Validar seguridad de contraseña
    @field_validator("password")
    def validar_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe tener al menos una mayúscula")
        if not any(c.islower() for c in v):
            raise ValueError("La contraseña debe tener al menos una minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe tener al menos un número")
        return v

# ------------------------------
# Response
# ------------------------------

class LoginResponse(BaseModel):
    access_token: str = Field(..., description="JWT de acceso")
    refresh_token: str = Field(..., description="JWT de actualización")
    token_type: str = Field(..., description="Tipo de token, normalmente 'bearer'")
    usuario_id: int = Field(..., ge=1, description="ID interno del usuario autenticado")
    empresa_id: int = Field(..., ge=1, description="ID de la empresa asociada")
    rol: int = Field(
        ...,
        ge=1,
        le=3,
        description="Rol del usuario en la empresa (1=Admin, 2=Contador, 3=rrhh)"
    )
