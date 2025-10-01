from pydantic import BaseModel
from typing import List


class PDFEppRequest(BaseModel):
    nombre: str
    rut: str
    cargo: str
    elementos_ids: List[int]


class PDFEppResponse(BaseModel):
    message: str
    pdf_path: str