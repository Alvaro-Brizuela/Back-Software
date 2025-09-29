from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.generated import Empresa
from app.schemas.register_company import EmpresaUpdateRequest, EmpresaRead
router = APIRouter(prefix="/empresa", tags=["empresa"])

@router.put("/{empresa_id}")
def actualizar_empresa(empresa_id: int, data: EmpresaUpdateRequest, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.id_empresa == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    # Actualizar campos
    empresa.razon_social = data.razon_social
    empresa.nombre_fantasia = data.nombre_fantasia
    empresa.rut_empresa = data.rut_empresa
    empresa.giro = data.giro
    empresa.fecha_constitucion = data.fecha_constitucion
    empresa.fecha_inicio_actividades = data.fecha_inicio_actividades
    empresa.direccion_fisica = data.direccion_fisica
    empresa.telefono = data.telefono
    empresa.correo = data.correo

    db.commit()
    db.refresh(empresa)

    return {
        "msg": "Datos de empresa actualizados correctamente",
        "empresa_id": empresa.id_empresa
    }
