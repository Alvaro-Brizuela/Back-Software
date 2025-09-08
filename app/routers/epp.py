from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import os

from app.database import get_db
from app.models.generated import Epp, Empresa
from app.schemas.epp import EppCreate, EppResponse
from app.schemas.pdf_epp import PDFEppRequest, PDFEppResponse
from app.services.pdf_generator import PDFEppGenerator

router = APIRouter(prefix="/epp", tags=["EPP"])


@router.post("/create", response_model=EppResponse, status_code=status.HTTP_201_CREATED)
def create_epp(epp_data: EppCreate, db: Session = Depends(get_db)):
    # Verificar que la empresa existe
    empresa = db.query(Empresa).filter(Empresa.id_empresa == epp_data.id_empresa).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La empresa especificada no existe"
        )
    
    try:
        new_epp = Epp(
            id_empresa=epp_data.id_empresa,
            epp=epp_data.epp,
            descripcion=epp_data.descripcion
        )
        
        db.add(new_epp)
        db.commit()
        db.refresh(new_epp)
        
        return new_epp
    
    except IntegrityError as e:
        db.rollback()
        if "epp_nombre_unique" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un EPP con este nombre"
            )
        elif "epp_descripcion_unique" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un EPP con esta descripción"
            )
        elif "fk_epp_empresa" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La empresa especificada no existe"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )


@router.post("/generate-pdf")
def generate_epp_pdf(pdf_data: PDFEppRequest):
    try:
        # Crear instancia del generador de PDF
        pdf_generator = PDFEppGenerator()
        
        # Generar el PDF
        pdf_path = pdf_generator.generate_pdf(pdf_data)
        
        # Verificar que el archivo se creó correctamente
        if not os.path.exists(pdf_path):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al generar el PDF"
            )
        
        # Devolver el archivo PDF como respuesta
        return FileResponse(
            path=pdf_path,
            media_type='application/pdf',
            filename=f"entrega_epp_{pdf_data.rut}.pdf"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el PDF: {str(e)}"
        )