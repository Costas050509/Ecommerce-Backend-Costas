from sqlalchemy.orm import Session
from typing import Optional
from app.models import Producto
from app.schemas import ProductoCreate

def crear_producto(db: Session, producto: ProductoCreate):
    db_producto = Producto(**producto.model_dump())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto

def listar_productos(
    db: Session, 
    skip: int = 0, 
    limit: int = 10, 
    nombre: Optional[str] = None, 
    precio_max: Optional[float] = None
):
    query = db.query(Producto)
    
    if nombre:
        query = query.filter(Producto.nombre.ilike(f"%{nombre}%"))
    if precio_max is not None:
        query = query.filter(Producto.precio_final <= precio_max)
        
    return query.offset(skip).limit(limit).all()