from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class EppElemento(BaseModel):
    id_epp: int
    cantidad: Optional[int] = None
    fecha_entrega: Optional[date] = None


class PDFEppRequest(BaseModel):
    nombre: str
    rut: str
    cargo: str
    elementos: List[EppElemento]


class PDFEppResponse(BaseModel):
    message: str
    pdf_path: str