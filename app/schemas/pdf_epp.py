from pydantic import BaseModel
from typing import List


class EppDeliveryItem(BaseModel):
    elemento_proteccion: str


class PDFEppRequest(BaseModel):
    nombre: str
    rut: str
    cargo: str
    empresa_nombre: str
    empresa_rut: str
    elementos: List[EppDeliveryItem]


class PDFEppResponse(BaseModel):
    message: str
    pdf_path: str