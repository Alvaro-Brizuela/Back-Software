from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.models.generated import Empresa
from app.schemas.pdf_contrato import PDFContratoRequest, PDFContratoResponse
from app.services.pdf_generator import PDFContratoGenerator
from app.services.dependencies import get_current_user

router = APIRouter(prefix="/contrato", tags=["Contrato"])


@router.post("/generate-pdf")
def generate_contrato_pdf(
    pdf_data: PDFContratoRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["rol"] not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para generar contratos"
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

        # Construir los datos para el PDF con información de la empresa
        class PDFDataForGenerator:
            pass

        pdf_generator_data = PDFDataForGenerator()
        pdf_generator_data.ciudad_firma = pdf_data.ciudad_firma
        pdf_generator_data.fecha_contrato = pdf_data.fecha_contrato
        pdf_generator_data.empresa_nombre = empresa.nombre_fantasia
        pdf_generator_data.empresa_rut = f"{empresa.rut_empresa}-{empresa.DV_rut}"
        pdf_generator_data.representante_legal = pdf_data.representante_legal
        pdf_generator_data.rut_representante = pdf_data.rut_representante
        pdf_generator_data.domicilio_representante = pdf_data.domicilio_representante
        pdf_generator_data.nombre_trabajador = pdf_data.nombre_trabajador
        pdf_generator_data.nacionalidad_trabajador = pdf_data.nacionalidad_trabajador
        pdf_generator_data.rut_trabajador = pdf_data.rut_trabajador
        pdf_generator_data.estado_civil_trabajador = pdf_data.estado_civil_trabajador
        pdf_generator_data.fecha_nacimiento_trabajador = pdf_data.fecha_nacimiento_trabajador
        pdf_generator_data.domicilio_trabajador = pdf_data.domicilio_trabajador
        pdf_generator_data.cargo_trabajador = pdf_data.cargo_trabajador
        pdf_generator_data.lugar_trabajo = pdf_data.lugar_trabajo
        pdf_generator_data.sueldo = pdf_data.sueldo
        pdf_generator_data.jornada = pdf_data.jornada
        pdf_generator_data.descripcion_jornada = pdf_data.descripcion_jornada
        pdf_generator_data.clausulas = pdf_data.clausulas

        # Crear instancia del generador de PDF
        pdf_generator = PDFContratoGenerator()

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
            filename=f"contrato_{pdf_data.rut_trabajador}.pdf"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el PDF: {str(e)}"
        )
