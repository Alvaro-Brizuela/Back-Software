from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional, List

from app.database import get_db
from app.models.generated import DatosTrabajador, Trabajador, Cargo, Territorial, Salud,Afp
from app.services.dependencies import get_current_user
from app.schemas.workers import TrabajadorCreate, TrabajadorResponse

router = APIRouter(prefix="/trabajadores", tags=["Trabajadores"])


@router.get("/search")
def search_trabajadores(
    nombre: Optional[str] = Query(None, description="Nombre del trabajador"),
    apellido_paterno: Optional[str] = Query(None, description="Apellido paterno del trabajador"),
    apellido_materno: Optional[str] = Query(None, description="Apellido materno del trabajador"),
    cargo: Optional[str] = Query(None, description="Nombre del cargo"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Busca trabajadores por nombre, apellidos y/o cargo.
    Puede recibir 1, 2, 3 o los 4 parametros.
    """
    # Verificar que el usuario tenga rol 1 (admin) o 2 (contador)
    if current_user["rol"] not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para buscar trabajadores"
        )

    # Obtener empresa_id del usuario autenticado
    empresa_id = current_user["empresa_id"]

    # Buscar trabajadores con ORM
    trabajadores_query = db.execute(
        select(Trabajador).where(
            Trabajador.id_empresa == empresa_id
        )
    ).scalars().all()

    trabajadores = []
    for t in trabajadores_query:
        datos = db.query(DatosTrabajador).filter(
            DatosTrabajador.id_trabajador == t.id_trabajador
        ).first()

        if datos:
            # Aplicar filtros opcionales
            if nombre and nombre.lower() not in datos.nombre.lower():
                continue
            if apellido_paterno and apellido_paterno.lower() not in datos.apellido_paterno.lower():
                continue
            if apellido_materno and apellido_materno.lower() not in datos.apellido_materno.lower():
                continue

            cargo_obj = db.query(Cargo).filter(Cargo.id_cargo == t.id_cargo).first() if t.id_cargo else None

            # Filtro de cargo
            if cargo and (not cargo_obj or cargo.lower() not in cargo_obj.nombre.lower()):
                continue

            afp = db.query(Afp).filter(Afp.id_afp == t.id_afp).first() if t.id_afp else None
            salud = db.query(Salud).filter(Salud.id_salud == t.id_salud).first() if t.id_salud else None

            trabajadores.append({
                "id_trabajador": datos.id_trabajador,
                "nombre": datos.nombre,
                "apellido_paterno": datos.apellido_paterno,
                "apellido_materno": datos.apellido_materno,
                "rut": f"{datos.rut}-{datos.DV_rut}",
                "fecha_nacimiento": datos.fecha_nacimiento,
                "nacionalidad": datos.nacionalidad,
                "direccion_real": datos.direccion_real,
                "cargo": {
                    "id_cargo": cargo_obj.id_cargo,
                    "nombre": cargo_obj.nombre
                } if cargo_obj else None,
                "afp": {
                    "id_afp": afp.id_afp,
                    "nombre": afp.nombre
                } if afp else None,
                "salud": {
                    "id_salud": salud.id_salud,
                    "nombre": salud.nombre
                } if salud else None
            })

    return {
        "total": len(trabajadores),
        "trabajadores": trabajadores
    }


@router.get("/search-by-rut")
def search_trabajadores_by_rut(
    rut: str = Query(..., description="RUT del trabajador (sin digito verificador)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Busca un trabajador por RUT.
    """
    # Verificar que el usuario tenga rol 1 (admin) o 2 (contador)
    if current_user["rol"] not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para buscar trabajadores"
        )

    # Obtener empresa_id del usuario autenticado
    empresa_id = current_user["empresa_id"]

    # Validar que el RUT sea numerico
    if not rut.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El RUT debe contener solo numeros"
        )

    # Buscar trabajador con ORM
    trabajador = db.execute(
        select(Trabajador).where(
            Trabajador.id_empresa == empresa_id
        )
    ).scalars().all()

    # Filtrar por RUT en datos_trabajador
    trabajadores = []
    for t in trabajador:
        datos = db.query(DatosTrabajador).filter(
            DatosTrabajador.id_trabajador == t.id_trabajador,
            DatosTrabajador.rut == int(rut)
        ).first()

        if datos:
            cargo = db.query(Cargo).filter(Cargo.id_cargo == t.id_cargo).first() if t.id_cargo else None
            afp = db.query(Afp).filter(Afp.id_afp == t.id_afp).first() if t.id_afp else None
            salud = db.query(Salud).filter(Salud.id_salud == t.id_salud).first() if t.id_salud else None

            trabajadores.append({
                "id_trabajador": datos.id_trabajador,
                "nombre": datos.nombre,
                "apellido_paterno": datos.apellido_paterno,
                "apellido_materno": datos.apellido_materno,
                "rut": f"{datos.rut}-{datos.DV_rut}",
                "fecha_nacimiento": datos.fecha_nacimiento,
                "nacionalidad": datos.nacionalidad,
                "direccion_real": datos.direccion_real,
                "cargo": {
                    "id_cargo": cargo.id_cargo,
                    "nombre": cargo.nombre
                } if cargo else None,
                "afp": {
                    "id_afp": afp.id_afp,
                    "nombre": afp.nombre
                } if afp else None,
                "salud": {
                    "id_salud": salud.id_salud,
                    "nombre": salud.nombre
                } if salud else None
            })

    return {
        "total": len(trabajadores),
        "trabajadores": trabajadores
    }

@router.post("/", response_model=TrabajadorResponse, status_code=status.HTTP_201_CREATED)
def create_trabajador(
    trabajador: TrabajadorCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Crea un trabajador usando nombres en lugar de IDs.
    """
    if current_user["rol"] not in [1, 2]:
        raise HTTPException(status_code=403, detail="No tienes permisos")

    empresa_id = current_user["empresa_id"]

    # ------------------------
    # Resolver IDs desde nombres
    # ------------------------
    id_cargo = None
    if trabajador.cargo:
        cargo = db.execute(select(Cargo).where(
            Cargo.id_empresa == empresa_id,
            Cargo.nombre.ilike(trabajador.cargo)
        )).scalar_one_or_none()
        if not cargo:
            raise HTTPException(404, f"Cargo '{trabajador.cargo}' no encontrado")
        id_cargo = cargo.id_cargo

    afp = db.execute(select(Afp).where(Afp.nombre.ilike(trabajador.afp))).scalar_one_or_none()
    if not afp:
        raise HTTPException(404, f"AFP '{trabajador.afp}' no encontrada")

    id_salud = None
    if trabajador.salud:
        salud = db.execute(select(Salud).where(Salud.nombre.ilike(trabajador.salud))).scalar_one_or_none()
        if not salud:
            raise HTTPException(404, f"Salud '{trabajador.salud}' no encontrada")
        id_salud = salud.id_salud

    territorial = db.execute(
    select(Territorial).where(
        Territorial.region.ilike(trabajador.region),
        Territorial.comuna.ilike(trabajador.comuna)
    )
    ).scalar_one_or_none()

    if not territorial:
        raise HTTPException(404, f"Territorial '{trabajador.region} - {trabajador.comuna}' no encontrado")


    # ------------------------
    # Insertar en tablas
    # ------------------------
    nuevo_trabajador = Trabajador(
        id_empresa=empresa_id,
        id_afp=afp.id_afp,
        id_territorial=territorial.id_territorial,
        id_cargo=id_cargo,
        id_salud=id_salud,
    )
    db.add(nuevo_trabajador)
    db.flush()

    datos = DatosTrabajador(
        id_trabajador=nuevo_trabajador.id_trabajador,
        nombre=trabajador.nombre,
        apellido_paterno=trabajador.apellido_paterno,
        apellido_materno=trabajador.apellido_materno,
        fecha_nacimiento=trabajador.fecha_nacimiento,
        rut=trabajador.rut,
        DV_rut=trabajador.DV_rut,
        nacionalidad=trabajador.nacionalidad,
        direccion_real=trabajador.direccion_real,
    )
    db.add(datos)
    db.commit()
    db.refresh(nuevo_trabajador)

    return nuevo_trabajador