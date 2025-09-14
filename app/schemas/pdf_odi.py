from pydantic import BaseModel
from typing import List


class OdiRow(BaseModel):
    tarea: str
    riesgo: str
    consecuencias: str
    precaucion: str


class PDFOdiRequest(BaseModel):
    nombre: str
    rut: str
    cargo: str
    empresa_nombre: str
    empresa_rut: str
    elementos: List[OdiRow]


class PDFOdiResponse(BaseModel):
    message: str
    pdf_path: str