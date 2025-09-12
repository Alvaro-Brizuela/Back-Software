from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import os

from app.database import get_db
from app.models.generated import Odi 
from app.schemas.odi import OdiCreate, OdiResponse 

router = APIRouter(prefix="/odi", tags=["ODI"])


@router.post("/create", response_model=OdiResponse, status_code=status.HTTP_201_CREATED)
def create_odi(odi_data: OdiCreate, db: Session = Depends(get_db)):
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

