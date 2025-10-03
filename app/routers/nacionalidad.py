from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.generated import Nacionalidad
from app.schemas.nacionalidad import NacionalidadResponse
from app.services.dependencies import get_current_user

router = APIRouter(prefix="/nacionalidad", tags=["Nacionalidad"])


@router.get("/list", response_model=list[NacionalidadResponse])
def list_nacionalidades(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    nacionalidades = db.query(Nacionalidad).all()
    return nacionalidades
