from pydantic import BaseModel


class NacionalidadResponse(BaseModel):
    id_nacionalidad: int
    nacionalidad: str

    class Config:
        from_attributes = True
