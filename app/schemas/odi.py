from pydantic import BaseModel

class OdiCreate(BaseModel):
    tarea: str
    riesgo: str
    consecuencias: str
    precaucion: str

class OdiResponse(BaseModel):
    id_odi: int
    id_empresa: int
    tarea: str
    riesgo: str
    consecuencias: str
    precaucion: str

    class Config:
        from_attributes: True