from sqlalchemy.orm import Session
from app.schemas.login import UserToken
from app.schemas.register_company import (
    EmpresaCreate, 
    EmpresaRead,
    UsuarioAutorizado,
    AccionesCapital,
    DireccionEmpresa,
    DatosLegales,
    ActividadEconomicaTributaria,
    SeguridadPrevision,
    DireccionTrabajo,
    RepresentanteLegal,
    )
from app.models.generated import (
    Empresa,
    Usuario,
    EmpresaParametros,
    EmpresaRepresentante,
    EmpresaSeguridad,
    EmpresaSocio,
    EmpresaTipo,
)
