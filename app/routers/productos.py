from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db, require_admin
from app.services import productos as productos_service

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.get("/", response_model=List[schemas.ProductoOut])
def obtener_productos(
    skip: int = 0,
    limit: int = 10,
    nombre: Optional[str] = None,
    precio_max: Optional[float] = None,
    db: Session = Depends(get_db),
):
  return productos_service.listar_productos(
      db=db, skip=skip, limit=limit, nombre=nombre, precio_max=precio_max
  )


@router.get("/{producto_id}", response_model=schemas.ProductoOut)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
  producto = productos_service.obtener_producto(
      db=db, producto_id=producto_id
  )
  if not producto:
    raise HTTPException(
        status_code=404, detail="Producto no encontrado"
    )
  return producto


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ProductoOut,
)
def crear_producto(
    producto: schemas.ProductoCreate,
    db: Session = Depends(get_db),
    admin: models.Usuario = Depends(require_admin),
):
  return productos_service.crear_producto(db=db, producto=producto)


@router.put("/{producto_id}", response_model=schemas.ProductoOut)
def actualizar_producto(
    producto_id: int,
    producto: schemas.ProductoCreate,
    db: Session = Depends(get_db),
    admin: models.Usuario = Depends(require_admin),
):
  prod_actualizado = productos_service.actualizar_producto(
      db=db, producto_id=producto_id, producto=producto
  )
  if not prod_actualizado:
    raise HTTPException(
        status_code=404, detail="Producto no encontrado"
    )
  return prod_actualizado


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    admin: models.Usuario = Depends(require_admin),
):
  exito = productos_service.eliminar_producto(db=db, producto_id=producto_id)
  if not exito:
    raise HTTPException(
        status_code=404, detail="Producto no encontrado"
    )
  return None