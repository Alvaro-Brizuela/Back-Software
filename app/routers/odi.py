from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import os

from app.database import get_db
from app.models.generated import Odi, Empresa
from app.schemas.odi import OdiCreate, OdiResponse 
from app.schemas.pdf_odi import PDFOdiRequest, PDFOdiResponse
from app.services.pdf_generator import PDFOdiGenerator
from app.services.dependencies import get_current_user

router = APIRouter(prefix="/odi", tags=["ODI"])


@router.post("/create", response_model=OdiResponse, status_code=status.HTTP_201_CREATED)
def create_odi(odi_data: OdiCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):

    if current_user["rol"] not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para crear ODI"
        )

    try:
        new_odi = Odi(
            tarea=odi_data.tarea,
            riesgo=odi_data.riesgo,
            consecuencias=odi_data.consecuencias,
            precaucion=odi_data.precaucion,
        )
        
        db.add(new_odi)
        db.commit()
        db.refresh(new_odi)
        
        return new_odi 
    
    except IntegrityError as e:
        db.rollback()
        if "odi_tarea_unique" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una Tarea con este nombre"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )


@router.post("/generate-pdf")
def generate_odi_pdf(pdf_data: PDFOdiRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):

    if current_user["rol"] not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para crear ODI"
        )
    try:
        # Obtener empresa_id del usuario autenticado
        empresa_id = current_user["empresa_id"]

        # Obtener empresa
        empresa = db.query(Empresa).filter(Empresa.id_empresa == empresa_id).first()
        if not empresa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empresa no encontrada"
            )

        # Obtener los elementos ODI por IDs
        elementos = db.query(Odi).filter(
            Odi.id_odi.in_(pdf_data.elementos),
            Odi.id_empresa == empresa_id
        ).all()
        if len(elementos) != len(pdf_data.elementos):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Algunos elementos ODI no fueron encontrados"
            )
        print("HOLLAAAAAA")
        print(elementos)

        print(elementos[0].tarea)

        # Construir los datos para el PDF
        class OdiRow:
            def __init__(self, tarea: str, riesgo: str, consecuencias: str, precaucion: str):
                self.tarea = tarea
                self.riesgo =  riesgo 
                self.consecuencias = consecuencias
                self.precaucion = precaucion


        class PDFDataForGenerator:
            pass

        pdf_generator_data = PDFDataForGenerator()
        pdf_generator_data.nombre = pdf_data.nombre
        pdf_generator_data.rut = pdf_data.rut
        pdf_generator_data.cargo = pdf_data.cargo
        pdf_generator_data.empresa_nombre = empresa.nombre_fantasia
        pdf_generator_data.empresa_rut = f"{empresa.rut_empresa}-{empresa.DV_rut}"
        pdf_generator_data.elementos = [OdiRow(tarea=e.tarea, riesgo=e.riesgo, consecuencias=e.consecuencias, precaucion=e.precaucion) for e in elementos]

        # Crear instancia del generador de PDF
        pdf_generator = PDFOdiGenerator()

        # Generar el PDF
        pdf_path = pdf_generator.generate_pdf(pdf_generator_data)

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
            filename=f"entrega_odi_{pdf_data.rut}.pdf"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el PDF: {str(e)}"
        )

@router.get("/list", response_model=list[OdiResponse])
def list_odi(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["rol"] not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para listar ODI"
        )
    
    empresa_id = current_user["empresa_id"]
    odis = db.query(Odi).filter(Odi.id_empresa == empresa_id).all()
    return odis

@router.delete("/delete/{id_odi}", status_code=status.HTTP_204_NO_CONTENT)
def delete_odi(id_odi: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):

    if current_user["rol"] not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para listar ODI"
        )
 
    empresa_id = current_user["empresa_id"]

    odi = db.query(Odi).filter(Odi.id_odi == id_odi, Odi.id_empresa == empresa_id).first()
    if not odi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ODI no encontrado")

    db.delete(odi)
    db.commit()
    return None