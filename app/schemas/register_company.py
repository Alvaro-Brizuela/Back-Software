from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from app.services.rut_validation import validar_rut_chileno

# ------------------------------
# Subschemas con validaciones (para Update)
# ------------------------------

class DireccionEmpresa(BaseModel):
    region: Optional[str] = Field(None, min_length=2, max_length=50, description="Nombre de la región")
    comuna: Optional[str] = Field(None, min_length=2, max_length=50, description="Nombre de la comuna")
    provincia: Optional[str] = Field(None, min_length=2, max_length=50, description="Nombre de la provincia")
    direccion: Optional[str] = Field(None, min_length=5, max_length=100, description="Dirección detallada")


class RepresentanteLegal(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=60, description="Nombre completo del representante")
    rut: Optional[str] = Field(None, min_length=9, max_length=12, description="RUT válido en formato XX.XXX.XXX-X")
    genero: Optional[str] = Field(None, description="Género del representante legal")


class DatosLegales(BaseModel):
    fecha_constitucion: Optional[date] = Field(None, description="Fecha de constitución de la empresa")
    fecha_inicio_actividades: Optional[date] = Field(None, description="Fecha de inicio de actividades")
    representante: Optional[RepresentanteLegal] = None
    tipo_sociedad: Optional[str] = Field(None, min_length=3, max_length=50, description="Tipo de sociedad (SpA, Ltda, etc.)")


class ActividadEconomicaTributaria(BaseModel):
    giro: Optional[str] = Field(None, min_length=3, max_length=100, description="Giro principal de la empresa")
    regimen_tributario: Optional[str] = Field(None, description="Régimen tributario aplicable")
    actividades: Optional[List[str]] = Field(default=None, max_items=7, description="Lista de actividades económicas")


class SeguridadPrevision(BaseModel):
    mutual_seguridad: Optional[str] = Field(None, description="Mutual de seguridad asociada")
    gratificacion_legal: Optional[str] = Field(None, description="Tipo de gratificación legal")
    tasa_actividad: Optional[float] = Field(None, ge=0, le=100, description="Tasa según actividad (%)")


class DireccionTrabajo(BaseModel):
    nombre_obra: Optional[str] = Field(None, min_length=3, max_length=100, description="Nombre de la obra o faena")
    comuna: Optional[str] = Field(None, min_length=2, max_length=50, description="Comuna de la obra")
    descripcion: Optional[str] = Field(None, max_length=200, description="Descripción de la obra")


class AccionesCapital(BaseModel):
    cantidad_acciones: Optional[int] = Field(None, gt=0, description="Cantidad total de acciones")
    capital_total: Optional[float] = Field(None, ge=0, description="Capital total ($)")
    capital_pagado: Optional[float] = Field(None, ge=0, description="Capital pagado ($)")
    capital_por_pagar: Optional[float] = Field(None, ge=0, description="Capital por pagar ($)")
    fecha_pago: Optional[date] = None
    socios: Optional[List[str]] = Field(default=None, description="Lista de socios")


class UsuarioAutorizado(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=50, description="Nombre del usuario autorizado")
    rut: Optional[str] = Field(None, min_length=9, max_length=12, description="RUT válido en formato XX.XXX.XXX-X")
    correo: Optional[EmailStr] = Field(None, description="Correo electrónico válido")
    contrasena: Optional[str] = Field(
        None,
        min_length=8,
        max_length=20,
        description="Contraseña (8-20 caracteres, debe tener mayúscula, minúscula y número)"
    )
    rol: Optional[str] = Field(None, description="Rol asignado (Administrador, Usuario, etc.)")

    @field_validator("contrasena")
    def validar_password(cls, v):
        if v is None:
            return v
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
    direccion: Optional[DireccionEmpresa] = None
    tipo_propiedad: Optional[str] = Field(None, description="Tipo de propiedad de la empresa")
    telefono: Optional[str] = Field(None, pattern=r"^\+?\d{8,15}$", description="Teléfono de contacto")
    correo_electronico: Optional[EmailStr] = None

    datos_legales: Optional[DatosLegales] = None
    actividad_economica: Optional[ActividadEconomicaTributaria] = None
    seguridad_prevision: Optional[SeguridadPrevision] = None
    direcciones_trabajo: Optional[List[DireccionTrabajo]] = None
    acciones_capital: Optional[AccionesCapital] = None
    usuarios_autorizados: Optional[List[UsuarioAutorizado]] = None
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
    id_usuario: Optional[int] = None
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None

    class Config:
        from_attributes = True


class EmpresaSocioRead(BaseModel):
    id: Optional[int] = None
    nombre: Optional[str] = None
    porcentaje: Optional[float] = None

    class Config:
        from_attributes = True


class EmpresaParametrosRead(BaseModel):
    id: Optional[int] = None
    parametro1: Optional[str] = None
    parametro2: Optional[str] = None

    class Config:
        from_attributes = True


class EmpresaRepresentanteRead(BaseModel):
    id: Optional[int] = None
    nombre: Optional[str] = None
    rut: Optional[str] = None

    class Config:
        from_attributes = True


class EmpresaSeguridadRead(BaseModel):
    id: Optional[int] = None
    mutual: Optional[str] = None
    tasa: Optional[float] = None

    class Config:
        from_attributes = True


class EmpresaTipoRead(BaseModel):
    id: Optional[int] = None
    tipo: Optional[str] = None

    class Config:
        from_attributes = True


class TerritorialRead(BaseModel):
    id_territorial: Optional[int] = None
    region: Optional[str] = None
    comuna: Optional[str] = None

    class Config:
        from_attributes = True


# ------------------------------
# Empresa Full Response (para GET)
# ------------------------------

class EmpresaFullResponse(BaseModel):
    id_empresa: Optional[int] = None
    rut_empresa: Optional[int] = None
    DV_rut: Optional[str] = None
    nombre_real: Optional[str] = None
    nombre_fantasia: Optional[str] = None
    razon_social: Optional[str] = None
    giro: Optional[str] = None
    fecha_constitucion: Optional[date] = None
    fecha_inicio_actividades: Optional[date] = None
    estado_suscripcion: Optional[int] = None
    direccion_fisica: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None

    territorial: Optional[TerritorialRead] = None
    empresa_socio: Optional[List[EmpresaSocioRead]] = None
    empresa_parametros: Optional[EmpresaParametrosRead] = None
    empresa_representante: Optional[List[EmpresaRepresentanteRead]] = None
    empresa_seguridad: Optional[EmpresaSeguridadRead] = None
    empresa_tipo: Optional[EmpresaTipoRead] = None
    usuario: Optional[List[UsuarioRead]] = None

    class Config:
        from_attributes = True
