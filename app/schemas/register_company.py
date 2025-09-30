from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from app.services.rut_validation import validar_rut_chileno

# ------------------------------
# Subschemas con validaciones (para Update)
# ------------------------------

class DireccionEmpresa(BaseModel):
    region: str = Field(..., min_length=2, max_length=50, description="Nombre de la región")
    comuna: str = Field(..., min_length=2, max_length=50, description="Nombre de la comuna")
    provincia: str = Field(..., min_length=2, max_length=50, description="Nombre de la provincia")
    direccion: str = Field(..., min_length=5, max_length=100, description="Dirección detallada")


class RepresentanteLegal(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=60, description="Nombre completo del representante")
    rut: str = Field(..., min_length=9, max_length=12, description="RUT válido en formato XX.XXX.XXX-X")
    genero: Optional[str] = Field(None, description="Género del representante legal")


class DatosLegales(BaseModel):
    fecha_constitucion: date = Field(..., description="Fecha de constitución de la empresa")
    fecha_inicio_actividades: date = Field(..., description="Fecha de inicio de actividades")
    representante: RepresentanteLegal
    tipo_sociedad: str = Field(..., min_length=3, max_length=50, description="Tipo de sociedad (SpA, Ltda, etc.)")


class ActividadEconomicaTributaria(BaseModel):
    giro: str = Field(..., min_length=3, max_length=100, description="Giro principal de la empresa")
    regimen_tributario: str = Field(..., description="Régimen tributario aplicable")
    actividades: Optional[List[str]] = Field(default=None, max_items=7, description="Lista de actividades económicas")


class SeguridadPrevision(BaseModel):
    mutual_seguridad: str = Field(..., description="Mutual de seguridad asociada")
    gratificacion_legal: str = Field(..., description="Tipo de gratificación legal")
    tasa_actividad: float = Field(..., ge=0, le=100, description="Tasa según actividad (%)")


class DireccionTrabajo(BaseModel):
    nombre_obra: str = Field(..., min_length=3, max_length=100, description="Nombre de la obra o faena")
    comuna: str = Field(..., min_length=2, max_length=50, description="Comuna de la obra")
    descripcion: Optional[str] = Field(None, max_length=200, description="Descripción de la obra")


class AccionesCapital(BaseModel):
    cantidad_acciones: int = Field(..., gt=0, description="Cantidad total de acciones")
    capital_total: float = Field(..., ge=0, description="Capital total ($)")
    capital_pagado: float = Field(..., ge=0, description="Capital pagado ($)")
    capital_por_pagar: float = Field(..., ge=0, description="Capital por pagar ($)")
    fecha_pago: Optional[date]
    socios: Optional[List[str]] = Field(default=None, description="Lista de socios")


class UsuarioAutorizado(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50, description="Nombre del usuario autorizado")
    rut: str = Field(..., min_length=9, max_length=12, description="RUT válido en formato XX.XXX.XXX-X")
    correo: EmailStr = Field(..., description="Correo electrónico válido")
    contrasena: str = Field(
        ...,
        min_length=8,
        max_length=20,
        description="Contraseña (8-20 caracteres, debe tener mayúscula, minúscula y número)"
    )
    rol: str = Field(..., description="Rol asignado (Administrador, Usuario, etc.)")

    # Validar seguridad de contraseña
    @field_validator("contrasena")
    def validar_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe tener al menos una mayúscula")
        if not any(c.islower() for c in v):
            raise ValueError("La contraseña debe tener al menos una minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe tener al menos un número")
        return v

    @field_validator("rut")
    @classmethod
    def validar_rut(cls, v):
        if v is None:
            return v
        if not validar_rut_chileno(v):
            raise ValueError("RUT inválido")
        return v


# ------------------------------
# Schema principal Empresa → Update
# ------------------------------

class EmpresaUpdateRequest(BaseModel):
    razon_social: Optional[str] = Field(None, min_length=2, max_length=60, description="Razón social de la empresa")
    nombre_fantasia: Optional[str] = Field(None, max_length=45, description="Nombre de fantasía")
    rut_empresa: Optional[str] = Field(None, min_length=9, max_length=12, description="RUT de la empresa en formato válido")
    direccion: Optional[DireccionEmpresa]
    tipo_propiedad: Optional[str] = Field(None, description="Tipo de propiedad de la empresa")
    telefono: Optional[str] = Field(None, pattern=r"^\+?\d{8,15}$", description="Teléfono de contacto")
    correo_electronico: Optional[EmailStr]

    datos_legales: Optional[DatosLegales]
    actividad_economica: Optional[ActividadEconomicaTributaria]
    seguridad_prevision: Optional[SeguridadPrevision]
    direcciones_trabajo: Optional[List[DireccionTrabajo]]
    acciones_capital: Optional[AccionesCapital]
    usuarios_autorizados: Optional[List[UsuarioAutorizado]]
    archivos_historicos: Optional[List[str]] = Field(default=None, description="Rutas o IDs de archivos históricos")

    @field_validator("rut_empresa")
    @classmethod
    def validar_rut_empresa(cls, v):
        if v is None:
            return v
        if not validar_rut_chileno(v):
            raise ValueError("RUT de empresa inválido")
        return v


# ------------------------------
# Subschemas de lectura (para Full Response)
# ------------------------------

class UsuarioRead(BaseModel):
    id_usuario: int
    nombre: str
    correo: EmailStr

    class Config:
        orm_mode = True

class EmpresaSocioRead(BaseModel):
    id: int
    nombre: str
    porcentaje: float

    class Config:
        orm_mode = True

class EmpresaParametrosRead(BaseModel):
    id: int
    parametro1: str
    parametro2: str

    class Config:
        orm_mode = True

class EmpresaRepresentanteRead(BaseModel):
    id: int
    nombre: str
    rut: str

    class Config:
        orm_mode = True

class EmpresaSeguridadRead(BaseModel):
    id: int
    mutual: str
    tasa: float

    class Config:
        orm_mode = True

class EmpresaTipoRead(BaseModel):
    id: int
    tipo: str

    class Config:
        orm_mode = True

class TerritorialRead(BaseModel):
    id_territorial: int
    region: str
    comuna: str

    class Config:
        orm_mode = True


# ------------------------------
# Empresa Full Response (para GET)
# ------------------------------

class EmpresaFullResponse(BaseModel):
    id_empresa: int
    rut_empresa: Optional[int]
    DV_rut: Optional[str]
    nombre_real: Optional[str]
    nombre_fantasia: Optional[str]
    razon_social: Optional[str]
    giro: Optional[str]
    fecha_constitucion: Optional[date]
    fecha_inicio_actividades: Optional[date]
    estado_suscripcion: int
    direccion_fisica: Optional[str]
    telefono: Optional[str]
    correo: Optional[str]

    territorial: Optional[TerritorialRead] = None
    empresa_socio: Optional[List[EmpresaSocioRead]] = None
    empresa_parametros: Optional[EmpresaParametrosRead] = None
    empresa_representante: Optional[List[EmpresaRepresentanteRead]] = None
    empresa_seguridad: Optional[EmpresaSeguridadRead] = None
    empresa_tipo: Optional[EmpresaTipoRead] = None
    usuario: Optional[List[UsuarioRead]] = None

    class Config:
        orm_mode = True
