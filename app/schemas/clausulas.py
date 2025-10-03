from pydantic import BaseModel


class ClausulaCreate(BaseModel):
    titulo: str
    clausula: str


class ClausulaResponse(BaseModel):
    id_clausula: int
    id_empresa: int
    titulo: str
    clausula: str

    class Config:
        from_attributes = True
