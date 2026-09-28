from typing import Optional
from pydantic import BaseModel


class ProductoBase(BaseModel):
  nombre: str
  descripcion: Optional[str] = None
  precio: float
  stock: int = 0  # <-- Si no envían el stock, asigna 0 por defecto


class ProductoCreate(ProductoBase):
  pass


class ProductoOut(ProductoBase):
  id: int

  class Config:
    from_attributes = True