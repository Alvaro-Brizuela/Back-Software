from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from app.services.rut_validation import validar_rut_chileno

# ==============================================================
# Subschemas con validaciones (para Update)
# ==============================================================

class DireccionEmpresa(BaseModel):
    region: Optional[str] = Field(None, min_length=2, max_length=50)
    comuna: Optional[str] = Field(None, min_length=2, max_length=50)
    provincia: Optional[str] = Field(None, min_length=2, max_length=50)
    direccion: Optional[str] = Field(None, min_length=5, max_length=100)


class RepresentanteLegal(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=60)
    rut: Optional[str] = Field(None, min_length=9, max_length=12)
    genero: Optional[str] = None


class DatosLegales(BaseModel):
    fecha_constitucion: Optional[date] = None
    fecha_inicio_actividades: Optional[date] = None
    representante: Optional[RepresentanteLegal] = None
    tipo_sociedad: Optional[str] = Field(None, min_length=3, max_length=50)


class ActividadEconomicaTributaria(BaseModel):
    giro: Optional[str] = Field(None, min_length=3, max_length=100)
    regimen_tributario: Optional[str] = None
    actividades: Optional[List[str]] = Field(default=None, max_items=7)


class SeguridadPrevision(BaseModel):
    mutual_seguridad: Optional[str] = None
    gratificacion_legal: Optional[str] = None
    tasa_actividad: Optional[float] = Field(None, ge=0, le=100)


class DireccionTrabajo(BaseModel):
    nombre_obra: Optional[str] = Field(None, min_length=3, max_length=100)
    comuna: Optional[str] = Field(None, min_length=2, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=200)


class AccionesCapital(BaseModel):
    cantidad_acciones: Optional[int] = Field(None, gt=0)
    capital_total: Optional[float] = Field(None, ge=0)
    capital_pagado: Optional[float] = Field(None, ge=0)
    capital_por_pagar: Optional[float] = Field(None, ge=0)
    fecha_pago: Optional[date] = None
    socios: Optional[List[str]] = None


class UsuarioAutorizado(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    rut: Optional[str] = Field(None, min_length=9, max_length=12)
    correo: Optional[EmailStr] = None
    contrasena: Optional[str] = Field(
        None,
        min_length=8,
        max_length=20,
        description="Contraseña (8-20 caracteres, debe tener mayúscula, minúscula y número)"
    )
    rol: Optional[str] = None

    @field_validator("contrasena")
    def validar_password(cls, v):
        if v is None:
            return v
        if not any(c.isupper() for c in v):
            raise ValueError("Debe tener al menos una mayúscula")
        if not any(c.islower() for c in v):
            raise ValueError("Debe tener al menos una minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("Debe tener al menos un número")
        return v

    @field_validator("rut")
    @classmethod
    def validar_rut(cls, v):
        if v is None:
            return v
        if not validar_rut_chileno(v):
            raise ValueError("RUT inválido")
        return v


# ==============================================================
# Schema principal Empresa → Update
# ==============================================================

class EmpresaUpdateRequest(BaseModel):
    razon_social: Optional[str] = Field(None, min_length=2, max_length=60)
    nombre_fantasia: Optional[str] = Field(None, max_length=45)
    rut_empresa: Optional[str] = Field(None, min_length=9, max_length=12)
    direccion: Optional[DireccionEmpresa] = None
    tipo_propiedad: Optional[str] = None
    telefono: Optional[str] = Field(None, pattern=r"^\+?\d{8,15}$")
    correo_electronico: Optional[EmailStr] = None

    datos_legales: Optional[DatosLegales] = None
    actividad_economica: Optional[ActividadEconomicaTributaria] = None
    seguridad_prevision: Optional[SeguridadPrevision] = None
    direcciones_trabajo: Optional[List[DireccionTrabajo]] = None
    acciones_capital: Optional[AccionesCapital] = None
    usuarios_autorizados: Optional[List[UsuarioAutorizado]] = None
    archivos_historicos: Optional[List[str]] = None

    @field_validator("rut_empresa")
    @classmethod
    def validar_rut_empresa(cls, v):
        if v is None:
            return v
        if not validar_rut_chileno(v):
            raise ValueError("RUT inválido")
        return v


# ==============================================================
# Subschemas de lectura (para Full Response)
# ==============================================================

class PagoAccionesRead(BaseModel):
    id: Optional[int] = None
    acciones: Optional[int] = None
    capital_pagado: Optional[float] = None
    capital_por_pagar: Optional[float] = None

    class Config:
        from_attributes = True


class EmpresaSocioRead(BaseModel):
    id_socio: Optional[int] = None
    nombre_socio: Optional[str] = None
    apellido_paterno_socio: Optional[str] = None
    apellido_materno_socio: Optional[str] = None
    aporte_total: Optional[int] = None
    cantidad_acciones: Optional[int] = None
    porcentaje_participacion: Optional[int] = None

    pago_acciones: Optional[List[PagoAccionesRead]] = None

    class Config:
        from_attributes = True


class EmpresaParametrosRead(BaseModel):
    id: Optional[int] = None
    descripcion_gratifiacion: Optional[str] = None
    valor_gratificacion: Optional[float] = None

    class Config:
        from_attributes = True


class EmpresaRepresentanteRead(BaseModel):
    id: Optional[int] = None
    nombre_representante: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    rut_representante_dv: Optional[str] = None

    class Config:
        from_attributes = True


class CajaCompensacionRead(BaseModel):
    id: Optional[int] = None
    nombre: Optional[str] = None

    class Config:
        from_attributes = True


class MutualSeguridadRead(BaseModel):
    id: Optional[int] = None
    nombre: Optional[str] = None

    class Config:
        from_attributes = True


class EmpresaSeguridadRead(BaseModel):
    id: Optional[int] = None
    tasa_mutual: Optional[float] = None
    tasa_caja: Optional[float] = None

    caja_compensaciones: Optional[CajaCompensacionRead] = None
    mutual_seguridad: Optional[MutualSeguridadRead] = None

    class Config:
        from_attributes = True


class TipoSociedadRead(BaseModel):
    id: Optional[int] = None
    nombre: Optional[str] = None

    class Config:
        from_attributes = True


class TipoActividadRead(BaseModel):
    id: Optional[int] = None
    nombre: Optional[str] = None

    class Config:
        from_attributes = True


class RegimenTributarioRead(BaseModel):
    id: Optional[int] = None
    nombre: Optional[str] = None

    class Config:
        from_attributes = True


class EmpresaTipoRead(BaseModel):
    id: Optional[int] = None
    tipo_sociedad: Optional[TipoSociedadRead] = None
    tipo_actividad: Optional[TipoActividadRead] = None
    regimen_tributario: Optional[RegimenTributarioRead] = None

    class Config:
        from_attributes = True


class LoginUsuarioRead(BaseModel):
    id_login: Optional[int] = None
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    tipo_usuario: Optional[int] = None

    class Config:
        from_attributes = True


class TerritorialRead(BaseModel):
    id_territorial: Optional[int] = None
    region: Optional[str] = None
    comuna: Optional[str] = None

    class Config:
        from_attributes = True


class UsuarioRead(BaseModel):
    id_usuario: Optional[int] = None
    nombre: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None

    territorial: Optional[TerritorialRead] = None
    login_usuario: Optional[List[LoginUsuarioRead]] = None  # 👈 ahora lista

    class Config:
        from_attributes = True


# ==============================================================
# Empresa Full Response (para GET)
# ==============================================================

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
