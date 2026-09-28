from pydantic import BaseModel, EmailStr, field_validator


class UsuarioCreate(BaseModel):
  nombre: str
  email: EmailStr
  password: str
  acepto_tratamiento: bool

  @field_validator("acepto_tratamiento")
  @classmethod
  def validar_acepto_tratamiento(cls, v: bool) -> bool:
    if not v:
      raise ValueError("Debes aceptar el tratamiento de datos personales")
    return v


class UsuarioOut(BaseModel):
  id: int
  nombre: str
  email: EmailStr
  rol: str

  class Config:
    from_attributes = True


class Token(BaseModel):
  access_token: str
  refresh_token: str
  token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
  refresh_token: str