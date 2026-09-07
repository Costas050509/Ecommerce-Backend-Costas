from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.dependencies import get_db
from app import models, schemas

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.get("/", response_model=List[schemas.ProductoOut])
def listar_productos(
    skip: int = 0,
    limit: int = 10,
    nombre: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Producto)
    if nombre:
        query = query.filter(models.Producto.nombre.ilike(f"%{nombre}%"))
    return query.offset(skip).limit(limit).all()

@router.get("/{producto_id}", response_model=schemas.ProductoOut)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto