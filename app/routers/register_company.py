from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from app.database import get_db
from app.models.generated import Empresa, EmpresaSocio, EmpresaSeguridad, EmpresaTipo, Usuario
from app.schemas.register_company import EmpresaUpdateRequest, EmpresaFullResponse
from app.services.dependencies import get_current_user
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


@router.get("/full", response_model=EmpresaFullResponse)
def obtener_empresa(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)   # 👈 empresa_id viene del token
    ):
    empresa = (
        db.query(Empresa)
        .options(
            joinedload(Empresa.territorial),
            joinedload(Empresa.empresa_socio),
            joinedload(Empresa.empresa_socio).joinedload(EmpresaSocio.pago_acciones),
            joinedload(Empresa.empresa_parametros),
            joinedload(Empresa.empresa_representante),
            joinedload(Empresa.empresa_seguridad),
            joinedload(Empresa.empresa_seguridad).joinedload(EmpresaSeguridad.caja_compensaciones),
            joinedload(Empresa.empresa_seguridad).joinedload(EmpresaSeguridad.mutual_seguridad),
            joinedload(Empresa.empresa_tipo),
            joinedload(Empresa.empresa_tipo).joinedload(EmpresaTipo.regimen_tributario),
            joinedload(Empresa.empresa_tipo).joinedload(EmpresaTipo.tipo_actividad),
            joinedload(Empresa.empresa_tipo).joinedload(EmpresaTipo.tipo_sociedad),
            joinedload(Empresa.usuario),
            joinedload(Empresa.usuario).joinedload(Usuario.territorial),
            joinedload(Empresa.usuario).joinedload(Usuario.login_usuario),
        )
        .filter(Empresa.id_empresa == user["empresa_id"])
        .first()
    )
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa