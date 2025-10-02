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
from app.services.dependencies import get_current_user
from sqlalchemy import text

router = APIRouter(prefix="/epp", tags=["EPP"])


@router.get("/list", response_model=list[EppResponse])
def list_epp(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Verificar que el usuario tenga rol 1 (admin) o 2 (contador)
    if current_user["rol"] not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para listar EPP"
        )

    # Obtener empresa_id de la sesión del usuario
    empresa_id = current_user["empresa_id"]

    # Obtener todos los EPP de la empresa
    epps = db.query(Epp).filter(Epp.id_empresa == empresa_id).all()

    return epps


@router.post("/create", response_model=EppResponse, status_code=status.HTTP_201_CREATED)
def create_epp(
    epp_data: EppCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Verificar que el usuario tenga rol 1 (admin) o 2 (contador)
    if current_user["rol"] not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear EPP"
        )

    # Obtener empresa_id de la sesión del usuario
    empresa_id = current_user["empresa_id"]

    # Verificar que la empresa existe
    empresa = db.query(Empresa).filter(Empresa.id_empresa == empresa_id).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La empresa especificada no existe"
        )

    try:
        new_epp = Epp(
            id_empresa=empresa_id,
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
def generate_epp_pdf(
    pdf_data: PDFEppRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Verificar que el usuario tenga rol 1 (admin) o 2 (contador)
    if current_user["rol"] not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para generar PDF de EPP"
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

        # Validar que el RUT contenga solo números
        if not pdf_data.rut.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El RUT debe contener solo números"
            )

        # Buscar trabajador por RUT en la empresa
        sql_query = text("""
            SELECT dt.nombre, dt.apellido_paterno, dt.apellido_materno,
                   dt.rut, dt."DV_rut", c.nombre as cargo_nombre
            FROM datos_trabajador dt
            JOIN trabajador t ON dt.id_trabajador = t.id_trabajador
            LEFT JOIN cargo c ON t.id_cargo = c.id_cargo
            WHERE t.id_empresa = :empresa_id AND dt.rut = :rut
        """)

        result = db.execute(sql_query, {"empresa_id": empresa_id, "rut": int(pdf_data.rut)}).fetchone()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trabajador no encontrado en tu empresa"
            )

        # Obtener datos del trabajador
        trabajador_nombre = f"{result.nombre} {result.apellido_paterno} {result.apellido_materno}"
        trabajador_rut = f"{result.rut}-{result.DV_rut}"
        trabajador_cargo = result.cargo_nombre or ""

        # Obtener IDs de los elementos
        elementos_ids = [e.id_epp for e in pdf_data.elementos]

        # Obtener los elementos EPP por IDs
        elementos_epp = db.query(Epp).filter(
            Epp.id_epp.in_(elementos_ids),
            Epp.id_empresa == empresa_id
        ).all()

        if len(elementos_epp) != len(elementos_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Algunos elementos EPP no fueron encontrados o no pertenecen a tu empresa"
            )

        # Crear diccionario para mapear id_epp a objeto Epp
        epp_dict = {e.id_epp: e for e in elementos_epp}

        # Construir los datos para el PDF
        class EppDeliveryItem:
            def __init__(self, elemento_proteccion: str, cantidad=None, fecha_entrega=None):
                self.elemento_proteccion = elemento_proteccion
                self.cantidad = cantidad
                self.fecha_entrega = fecha_entrega

        class PDFDataForGenerator:
            pass

        pdf_generator_data = PDFDataForGenerator()
        pdf_generator_data.nombre = trabajador_nombre
        pdf_generator_data.rut = trabajador_rut
        pdf_generator_data.cargo = trabajador_cargo
        pdf_generator_data.empresa_nombre = empresa.nombre_fantasia
        pdf_generator_data.empresa_rut = f"{empresa.rut_empresa}-{empresa.DV_rut}"
        pdf_generator_data.elementos = [
            EppDeliveryItem(
                elemento_proteccion=epp_dict[e.id_epp].epp,
                cantidad=e.cantidad,
                fecha_entrega=e.fecha_entrega
            )
            for e in pdf_data.elementos
        ]

        # Crear instancia del generador de PDF
        pdf_generator = PDFEppGenerator()

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
            filename=f"entrega_epp_{pdf_data.rut}.pdf"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el PDF: {str(e)}"
        )