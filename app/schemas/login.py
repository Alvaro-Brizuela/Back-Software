from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    usuario_id: int
    empresa_id: int
    rol: int