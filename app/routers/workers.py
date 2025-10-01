from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models.generated import DatosTrabajador, Trabajador, Cargo
from app.services.dependencies import get_current_user

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

    # Usar SQL directo para evitar problemas con herencia de tablas
    from sqlalchemy import text

    # Construir query base
    sql_query = """
        SELECT
            dt.id_trabajador,
            dt.nombre,
            dt.apellido_paterno,
            dt.apellido_materno,
            dt.rut,
            dt."DV_rut",
            c.nombre as cargo_nombre,
            c.id_cargo
        FROM datos_trabajador dt
        JOIN trabajador t ON dt.id_trabajador = t.id_trabajador
        LEFT JOIN cargo c ON t.id_cargo = c.id_cargo
        WHERE t.id_empresa = :empresa_id
    """

    params = {"empresa_id": empresa_id}

    # Aplicar filtros opcionales
    if nombre:
        sql_query += " AND dt.nombre ILIKE :nombre"
        params["nombre"] = f"%{nombre}%"

    if apellido_paterno:
        sql_query += " AND dt.apellido_paterno ILIKE :apellido_paterno"
        params["apellido_paterno"] = f"%{apellido_paterno}%"

    if apellido_materno:
        sql_query += " AND dt.apellido_materno ILIKE :apellido_materno"
        params["apellido_materno"] = f"%{apellido_materno}%"

    if cargo:
        sql_query += " AND c.nombre ILIKE :cargo"
        params["cargo"] = f"%{cargo}%"

    # Ejecutar query
    resultados = db.execute(text(sql_query), params).fetchall()

    # Formatear resultados
    trabajadores = []
    for r in resultados:
        trabajadores.append({
            "id_trabajador": r.id_trabajador,
            "nombre": r.nombre,
            "apellido_paterno": r.apellido_paterno,
            "apellido_materno": r.apellido_materno,
            "rut": f"{r.rut}-{r.DV_rut}",
            "cargo": {
                "id_cargo": r.id_cargo,
                "nombre": r.cargo_nombre
            } if r.cargo_nombre else None
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

    # Usar SQL directo
    from sqlalchemy import text

    sql_query = """
        SELECT
            dt.id_trabajador,
            dt.nombre,
            dt.apellido_paterno,
            dt.apellido_materno,
            dt.rut,
            dt."DV_rut",
            c.nombre as cargo_nombre,
            c.id_cargo
        FROM datos_trabajador dt
        JOIN trabajador t ON dt.id_trabajador = t.id_trabajador
        LEFT JOIN cargo c ON t.id_cargo = c.id_cargo
        WHERE t.id_empresa = :empresa_id
        AND dt.rut = :rut
    """

    params = {"empresa_id": empresa_id, "rut": int(rut)}

    # Ejecutar query
    resultados = db.execute(text(sql_query), params).fetchall()

    # Formatear resultados
    trabajadores = []
    for r in resultados:
        trabajadores.append({
            "id_trabajador": r.id_trabajador,
            "nombre": r.nombre,
            "apellido_paterno": r.apellido_paterno,
            "apellido_materno": r.apellido_materno,
            "rut": f"{r.rut}-{r.DV_rut}",
            "cargo": {
                "id_cargo": r.id_cargo,
                "nombre": r.cargo_nombre
            } if r.cargo_nombre else None
        })

    return {
        "total": len(trabajadores),
        "trabajadores": trabajadores
    }
