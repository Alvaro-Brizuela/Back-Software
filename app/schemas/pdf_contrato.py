from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class PDFContratoRequest(BaseModel):
    ciudad_firma: str
    fecha_contrato: date
    representante_legal: str
    rut_representante: str
    domicilio_representante: str
    nombre_trabajador: str
    nacionalidad_trabajador: str
    rut_trabajador: str
    estado_civil_trabajador: str
    fecha_nacimiento_trabajador: date
    domicilio_trabajador: str
    cargo_trabajador: str
    lugar_trabajo: str
    sueldo: int
    jornada: str
    descripcion_jornada: str
    clausulas: Optional[List[str]] = []


class PDFContratoResponse(BaseModel):
    message: str
    pdf_path: str
