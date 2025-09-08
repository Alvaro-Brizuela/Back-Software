from pydantic import BaseModel
from typing import List


class EppDeliveryItem(BaseModel):
    elemento_proteccion: str


class PDFEppRequest(BaseModel):
    rut: str
    nombre: str
    cargo: str
    elementos: List[EppDeliveryItem]


class PDFEppResponse(BaseModel):
    message: str
    pdf_path: str