from typing import Optional
from sqlalchemy.orm import Session
from app.models import Producto
from app.schemas.producto import ProductoCreate


def crear_producto(db: Session, producto: ProductoCreate):
  db_producto = Producto(
      nombre=producto.nombre,
      descripcion=producto.descripcion,
      precio=producto.precio,
      stock=producto.stock if producto.stock is not None else 0,
  )
  db.add(db_producto)
  db.commit()
  db.refresh(db_producto)
  return db_producto


def listar_productos(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    nombre: Optional[str] = None,
    precio_max: Optional[float] = None,
):
  query = db.query(Producto)

  if nombre:
    query = query.filter(Producto.nombre.ilike(f"%{nombre}%"))
  if precio_max is not None:
    query = query.filter(Producto.precio <= precio_max)

  return query.offset(skip).limit(limit).all()