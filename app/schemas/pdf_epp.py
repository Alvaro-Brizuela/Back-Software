from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class EppElemento(BaseModel):
    id_epp: int
    cantidad: Optional[int] = Field(None, ge=1, description="Cantidad debe ser mayor o igual a 1")
    fecha_entrega: Optional[date] = None


class PDFEppRequest(BaseModel):
    nombre: str
    rut: str
    cargo: str
    elementos: List[EppElemento]


class PDFEppResponse(BaseModel):
    message: str
    pdf_path: str