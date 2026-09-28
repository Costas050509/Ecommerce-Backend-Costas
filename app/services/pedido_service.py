from decimal import Decimal
from app.models import ItemPedido, Pedido, Producto
from app.schemas.pedido import PedidoCreate
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


def crear_pedido(db: Session, usuario_id: int, datos: PedidoCreate) -> Pedido:
  total_acumulado = Decimal("0.00")
  items_a_crear = []

  try:
    for item in datos.items:
      producto = (
          db.query(Producto).filter(Producto.id == item.producto_id).first()
      )

      if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El producto con id {item.producto_id} no existe",
        )

      if producto.stock < item.cantidad:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Stock insuficiente para '{producto.nombre}'. Quedan"
                f" {producto.stock} unidades."
            ),
        )

      # Descontar stock
      producto.stock -= item.cantidad

      # Guardar precio del momento
      precio_momento = Decimal(str(producto.precio))
      subtotal = precio_momento * item.cantidad
      total_acumulado += subtotal

      items_a_crear.append({
          "producto_id": producto.id,
          "cantidad": item.cantidad,
          "precio_unitario": precio_momento,
      })

    nuevo_pedido = Pedido(
        usuario_id=usuario_id, total=total_acumulado, estado="pendiente"
    )
    db.add(nuevo_pedido)
    db.flush()

    for item_dict in items_a_crear:
      item_db = ItemPedido(
          pedido_id=nuevo_pedido.id,
          producto_id=item_dict["producto_id"],
          cantidad=item_dict["cantidad"],
          precio_unitario=item_dict["precio_unitario"],
      )
      db.add(item_db)

    db.commit()
    db.refresh(nuevo_pedido)
    return nuevo_pedido

  except HTTPException as e:
    db.rollback()
    raise e
  except Exception as e:
    db.rollback()
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Error al procesar la compra: {str(e)}",
    )


def obtener_mis_pedidos(db: Session, usuario_id: int):
  return (
      db.query(Pedido)
      .filter(Pedido.usuario_id == usuario_id)
      .order_by(Pedido.id.desc())
      .all()
  )


def obtener_pedido_por_id(
    db: Session, pedido_id: int, usuario_id: int, es_admin: bool = False
):
  pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
  if not pedido or (pedido.usuario_id != usuario_id and not es_admin):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado"
    )
  return pedido