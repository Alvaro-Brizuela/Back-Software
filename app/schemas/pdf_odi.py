from pydantic import BaseModel
from typing import List


class PDFOdiRequest(BaseModel):
    nombre: str
    rut: str
    cargo: str
    empresa_nombre: str
    empresa_rut: str
    elementos: List[int]


class PDFOdiResponse(BaseModel):
    message: str
    pdf_path: str