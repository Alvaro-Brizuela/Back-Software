from pydantic import BaseModel, EmailStr, Field, field_validator

class Register(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Nombre del usuario")
    paternal_surname: str = Field(..., min_length=2, max_length=50, description="Apellido paterno")
    maternal_surname: str = Field(..., min_length=2, max_length=50, description="Apellido materno")
    email: EmailStr = Field(..., description="Correo electrónico válido")
    password: str = Field(
        ...,
        min_length=8,
        max_length=20,
        description="Contraseña (8-20 caracteres, al menos 1 mayúscula, 1 minúscula y 1 número)"
    )
    confirm_password: str

    # Validar password segura
    @field_validator("password")
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe tener al menos una mayúscula")
        if not any(c.islower() for c in v):
            raise ValueError("La contraseña debe tener al menos una minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe tener al menos un número")
        return v

    # Validar que confirm_password coincida con password
    @field_validator("confirm_password")
    def passwords_match(cls, v, info):
        password = info.data.get("password")
        if password and v != password:
            raise ValueError("Las contraseñas no coinciden")
        return v
