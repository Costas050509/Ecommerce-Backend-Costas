from typing import List
from app.database import get_db
from app.dependencies import (
    get_current_user, 
)
from app.models import Usuario 
from app.schemas.pedido import PedidoCreate, PedidoOut
from app.services import pedido_service
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db         
from app.dependencies import get_current_user   
from app.models import Pedido, Producto, SolicitudRevocacion, Usuario, generar_codigo

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("/", response_model=PedidoOut, status_code=status.HTTP_201_CREATED)
def checkout(
    datos: PedidoCreate,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
  return pedido_service.crear_pedido(
      db=db, usuario_id=usuario_actual.id, datos=datos
  )


@router.get("/mios", response_model=List[PedidoOut])
def mis_pedidos(
    db: Session = Depends(get_db), usuario_actual=Depends(get_current_user)
):
  return pedido_service.obtener_mis_pedidos(
      db=db, usuario_id=usuario_actual.id
  )


@router.get("/{pedido_id}", response_model=PedidoOut)
def obtener_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    usuario_actual=Depends(get_current_user),
):
  es_admin = getattr(usuario_actual, "rol", "") == "admin"
  return pedido_service.obtener_pedido_por_id(
      db=db,
      pedido_id=pedido_id,
      usuario_id=usuario_actual.id,
      es_admin=es_admin,
  )

@router.post("/{pedido_id}/revocacion", status_code=status.HTTP_201_CREATED)
def revocar_pedido(pedido_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    # 1. Validar propiedad (404 si no existe o no es tuyo)
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id, Pedido.usuario_id == current_user.id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    # 2. Validar que no esté cancelado (409)
    if pedido.estado == "cancelado":
        raise HTTPException(status_code=409, detail="El pedido ya se encuentra cancelado")

    # 3. Validar plazo de 10 días (409) - Art 34 Ley 24.240 / Disp 954/2025
    ahora = datetime.now(timezone.utc)
    # Asegurar zona horaria en creado_en
    creado_en = pedido.creado_en if pedido.creado_en.tzinfo else pedido.creado_en.replace(tzinfo=timezone.utc)
    
    if (ahora - creado_en) > timedelta(days=10):
        raise HTTPException(status_code=409, detail="El plazo de 10 días para revocar la compra ha expirado")

    # 4. Transacción: Devolver stock, cambiar estado y registrar solicitud
    try:
        for item in pedido.items:
            producto = db.query(Producto).filter(Producto.id == item.producto_id).first()
            if producto:
                producto.stock += item.cantidad  # Devuelve el stock

        pedido.estado = "cancelado"
        codigo_solicitud = generar_codigo()
        solicitud = SolicitudRevocacion(
            codigo=codigo_solicitud,
            pedido_id=pedido.id,
            usuario_id=current_user.id
        )
        db.add(solicitud)
        db.commit()
        db.refresh(solicitud)

        return {
            "codigo": solicitud.codigo,
            "pedido_id": solicitud.pedido_id,
            "creada_en": solicitud.creada_en
        }
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al procesar la revocación")