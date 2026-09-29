import os
import secrets
from typing import List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db, require_admin
from app.services import productos as productos_service
from app.utils.archivos import parece_imagen

router = APIRouter(prefix="/productos", tags=["Productos"])


# --- Función Helper para eliminar el archivo físico ---
def eliminar_archivo_imagen(imagen_url: str):
    """Borra el archivo físico de la imagen si pertenece a nuestro servidor local."""
    if imagen_url and imagen_url.startswith("/static/productos/"):
        nombre_archivo = imagen_url.replace("/static/productos/", "")
        ruta_archivo = os.path.join("uploads", "productos", nombre_archivo)
        
        if os.path.exists(ruta_archivo):
            try:
                os.remove(ruta_archivo)
                print(f"🗑️ Imagen eliminada del disco: {ruta_archivo}")
            except Exception as e:
                print(f"⚠️ Error al intentar eliminar la imagen {ruta_archivo}: {e}")


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
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ProductoOut)
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
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return prod_actualizado


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    admin: models.Usuario = Depends(require_admin),
):
    # 1. Buscamos el producto primero para obtener su imagen_url
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # 2. Eliminamos la imagen física del disco ANTES de borrar de la base de datos
    eliminar_archivo_imagen(producto.imagen_url)

    # 3. ¡AQUÍ ESTÁ LA SOLUCIÓN AL ERROR DE FOREIGN KEY!
    # Borramos todos los items de pedidos que referencian a este producto.
    # ⚠️ ADVERTENCIA: Esto alterará el historial de pedidos de los usuarios.
    db.query(models.ItemPedido).filter(models.ItemPedido.producto_id == producto_id).delete()
    db.commit() # Guardamos la eliminación de los items

    # 4. Ahora sí, eliminamos el producto de la base de datos
    exito = productos_service.eliminar_producto(db=db, producto_id=producto_id)
    if not exito:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return None


@router.post("/{producto_id}/imagen", response_model=schemas.ProductoOut)
async def subir_imagen_producto(
    producto_id: int,
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: models.Usuario = Depends(require_admin),
):
    nombre_original = archivo.filename or ""
    _, ext = os.path.splitext(nombre_original)
    ext = ext.lower()

    extensiones_permitidas = {".jpg", ".jpeg", ".png", ".webp"}
    if ext not in extensiones_permitidas:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Formato de archivo no soportado. Extensiones permitidas: .jpg, .jpeg, .png, .webp",
        )

    contenido = await archivo.read()
    max_bytes = 2 * 1024 * 1024  # 2 MB
    if len(contenido) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="El archivo excede el tamaño máximo permitido de 2 MB",
        )

    if not parece_imagen(contenido):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="El contenido del archivo no corresponde a una imagen válida",
        )

    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado"
        )

    if producto.imagen_url:
        eliminar_archivo_imagen(producto.imagen_url)

    nombre_seguro = f"{producto_id}-{secrets.token_hex(8)}{ext}"
    carpeta_destino = os.path.join("uploads", "productos")
    os.makedirs(carpeta_destino, exist_ok=True)

    ruta_guardado = os.path.join(carpeta_destino, nombre_seguro)
    with open(ruta_guardado, "wb") as f:
        f.write(contenido)

    producto.imagen_url = f"/static/productos/{nombre_seguro}"
    db.commit()
    db.refresh(producto)

    return producto


@router.delete("/{producto_id}/imagen", response_model=schemas.ProductoOut)
def eliminar_imagen_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    admin: models.Usuario = Depends(require_admin),
):
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado"
        )

    if not producto.imagen_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El producto no tiene imagen para eliminar"
        )

    eliminar_archivo_imagen(producto.imagen_url)
    producto.imagen_url = None
    db.commit()
    db.refresh(producto)

    return producto