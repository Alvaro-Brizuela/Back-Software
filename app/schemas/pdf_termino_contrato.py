from pydantic import BaseModel
from datetime import date


class PDFTerminoContratoRequest(BaseModel):
    rut_trabajador: str  # RUT sin DV para buscar en DB
    ciudad: str
    fecha_carta: date
    fecha_termino: date
    articulo_causal: str  # Ej: "Artículo 160 N° 3 Letra B"
    descripcion_causal: str  # Ej: "CONCLUSION DEL TRABAJO QUE DIO ORIGEN AL CONTRATO"
    fundamentacion: str  # Ej: "Lo anterior se fundamenta en el término de la obra específica..."
    lugar_pago_finiquito: str  # Ej: "Notaría LEONARDO EMANUEL MOLINA ubicado en calle TEATINOS 333 Comuna de SANTIAGO CENTRO"
    telefono_notaria: str  # Ej: "2 25423 0033"


class PDFTerminoContratoResponse(BaseModel):
    message: str
    pdf_path: str
