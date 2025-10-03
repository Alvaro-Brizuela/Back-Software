from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.generated import Clausulas
from app.schemas.clausulas import ClausulaCreate, ClausulaResponse
from app.services.dependencies import get_current_user

router = APIRouter(prefix="/clausulas", tags=["Clausulas"])


@router.post("/create", response_model=ClausulaResponse, status_code=status.HTTP_201_CREATED)
def create_clausula(
    clausula_data: ClausulaCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["rol"] not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear cláusulas"
        )

    try:
        # Obtener empresa_id de la sesión actual
        empresa_id = current_user["empresa_id"]

        new_clausula = Clausulas(
            id_empresa=empresa_id,
            titulo=clausula_data.titulo,
            clausula=clausula_data.clausula
        )

        db.add(new_clausula)
        db.commit()
        db.refresh(new_clausula)

        return new_clausula

    except IntegrityError as e:
        db.rollback()
        if "unique_empresa_titulo" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una cláusula con este título en tu empresa"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )


@router.get("/list", response_model=list[ClausulaResponse])
def list_clausulas(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["rol"] not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para listar cláusulas"
        )

    empresa_id = current_user["empresa_id"]
    clausulas = db.query(Clausulas).filter(Clausulas.id_empresa == empresa_id).all()
    return clausulas
