from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Pedido, Producto, SolicitudRevocacion, Usuario, generar_codigo
from app.schemas.pedido import PedidoCreate, PedidoOut
from app.services import pedido_service

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

# Esquema para recibir el producto_id desde el frontend
class RevocacionRequest(BaseModel):
    producto_id: int

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
def revocar_pedido(
    pedido_id: int, 
    datos: RevocacionRequest,
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(get_current_user)
):
    # 1. Validar propiedad (Si no existe, simulamos éxito para no revelar datos)
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id, Pedido.usuario_id == current_user.id).first()
    if not pedido:
        return {
            "codigo": generar_codigo(), # Código falso
            "pedido_id": pedido_id,
            "creada_en": datetime.now(timezone.utc)
        }

    # 2. Validar que no esté cancelado (409)
    if pedido.estado == "cancelado":
        raise HTTPException(status_code=409, detail="El pedido ya se encuentra cancelado")

    # 3. Validar plazo de 10 días (409)
    ahora = datetime.now(timezone.utc)
    creado_en = pedido.creado_en if pedido.creado_en.tzinfo else pedido.creado_en.replace(tzinfo=timezone.utc)
    
    if (ahora - creado_en) > timedelta(days=10):
        raise HTTPException(status_code=409, detail="El plazo de 10 días para revocar la compra ha expirado")

    # 4. Buscar el ítem específico dentro del pedido
    item_a_revocar = next((item for item in pedido.items if item.producto_id == datos.producto_id), None)
    
    if not item_a_revocar:
        # Mismo truco de seguridad: si el producto no está en el pedido, simulamos éxito
        return {
            "codigo": generar_codigo(),
            "pedido_id": pedido_id,
            "creada_en": datetime.now(timezone.utc)
        }

    # 5. Transacción: Devolver stock y actualizar
    try:
        producto = db.query(Producto).filter(Producto.id == item_a_revocar.producto_id).first()
        if producto:
            producto.stock += item_a_revocar.cantidad

        monto_a_restar = float(item_a_revocar.precio_unitario) * item_a_revocar.cantidad

        db.delete(item_a_revocar)
        db.flush()

        db.refresh(pedido)

        if not pedido.items:
            pedido.estado = "cancelado"
            pedido.total = 0
        else:
            pedido.total = float(pedido.total) - monto_a_restar

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
    except Exception as e:
        db.rollback()
        print(f"Error en revocación: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar la revocación")