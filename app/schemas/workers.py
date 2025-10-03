from pydantic import BaseModel, Field, constr, field_validator
from datetime import date
from typing import Optional
from app.services.rut_validation import validar_rut_chileno

# ------------------------
# Sub-modelos anidados
# ------------------------

class CargoOut(BaseModel):
    id_cargo: int
    nombre: str
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True


class AfpOut(BaseModel):
    id_afp: int
    nombre: str
    porcentaje_descuento: float

    class Config:
        from_attributes = True


class SaludOut(BaseModel):
    id_salud: int
    nombre: str
    tipo: bool

    class Config:
        from_attributes = True


# ------------------------
# Bases de Trabajador
# ------------------------

class TrabajadorBase(BaseModel):
    id_afp: int = Field(..., description="ID de la AFP")
    id_territorial: int = Field(..., description="ID territorial")
    id_cargo: Optional[int] = Field(None, description="ID del cargo")
    id_salud: Optional[int] = Field(None, description="ID de la institución de salud")


class DatosTrabajadorBase(BaseModel):
    nombre: constr(min_length=2, max_length=40)
    apellido_paterno: constr(min_length=2, max_length=40)
    apellido_materno: constr(min_length=2, max_length=40)
    fecha_nacimiento: date
    rut: int = Field(..., description="Número de RUT sin dígito verificador")
    DV_rut: constr(min_length=1, max_length=1) = Field(..., description="Dígito verificador")
    nacionalidad: constr(min_length=2, max_length=50)
    direccion_real: str

    @field_validator("rut")
    @classmethod
    def validar_rut(cls, v):
        if v is None:
            return v
        if not validar_rut_chileno(v):
            raise ValueError("RUT inválido")
        return v


# ------------------------
# Modelos de entrada (Create/Update)
# ------------------------


class TrabajadorCreate(BaseModel):
    cargo: Optional[str] = Field(None, description="Nombre del cargo")
    afp: str = Field(..., description="Nombre de la AFP")
    salud: Optional[str] = Field(None, description="Nombre de la institución de salud")
    region: str = Field(..., description="Región del trabajador")
    comuna: str = Field(..., description="Comuna del trabajador")

    nombre: constr(min_length=2, max_length=40)
    apellido_paterno: constr(min_length=2, max_length=40)
    apellido_materno: constr(min_length=2, max_length=40)
    fecha_nacimiento: date
    rut: int = Field(..., description="Número de RUT sin dígito verificador")
    DV_rut: constr(min_length=1, max_length=1)
    nacionalidad: constr(min_length=2, max_length=50)
    direccion_real: str


    @field_validator("rut")
    @classmethod
    def validar_rut(cls, v):
        if v is None:
            return v
        if not validar_rut_chileno(v):
            raise ValueError("RUT inválido")
        return v


class TrabajadorUpdate(BaseModel):
    """Modelo para actualizar parcialmente un trabajador"""
    nombre: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    rut: Optional[int] = None
    DV_rut: Optional[str] = None
    nacionalidad: Optional[str] = None
    direccion_real: Optional[str] = None
    id_afp: Optional[int] = None
    id_cargo: Optional[int] = None
    id_salud: Optional[int] = None
    id_territorial: Optional[int] = None


# ------------------------
# Modelos de salida (Response)
# ------------------------

class DatosTrabajadorResponse(DatosTrabajadorBase):
    class Config:
        from_attributes = True


class TrabajadorResponse(TrabajadorBase):
    id_trabajador: int
    datos: DatosTrabajadorResponse
    cargo: Optional[CargoOut] = None
    afp: Optional[AfpOut] = None
    salud: Optional[SaludOut] = None

    class Config:
        from_attributes = True
