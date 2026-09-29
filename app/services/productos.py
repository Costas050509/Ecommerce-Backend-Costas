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


def obtener_producto(db: Session, producto_id: int):
  return db.query(Producto).filter(Producto.id == producto_id).first()


def actualizar_producto(db: Session, producto_id: int, producto: ProductoCreate):
  db_producto = db.query(Producto).filter(Producto.id == producto_id).first()
  if not db_producto:
    return None
  db_producto.nombre = producto.nombre
  db_producto.descripcion = producto.descripcion
  db_producto.precio = producto.precio
  db_producto.stock = producto.stock
  db.commit()
  db.refresh(db_producto)
  return db_producto


def eliminar_producto(db: Session, producto_id: int):
  db_producto = db.query(Producto).filter(Producto.id == producto_id).first()
  if not db_producto:
    return False
  db.delete(db_producto)
  db.commit()
  return True