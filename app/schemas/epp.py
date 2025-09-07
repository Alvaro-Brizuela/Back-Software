from pydantic import BaseModel


class EppCreate(BaseModel):
    id_empresa: int
    epp: str
    descripcion: str


class EppResponse(BaseModel):
    id_epp: int
    id_empresa: int
    epp: str
    descripcion: str

    class Config:
        from_attributes = True