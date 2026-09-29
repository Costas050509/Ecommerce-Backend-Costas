from datetime import datetime, timezone
import secrets
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.database import Base


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    imagen_url = Column(String, nullable=True)


# --- Modelos nuevos Paso 2 ---

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    rol = Column(String, default="cliente", nullable=False)
    activo = Column(Boolean, default=True)
    fecha_baja = Column(DateTime(timezone=True), nullable=True)
    acepto_tratamiento = Column(Boolean, nullable=False)
    fecha_consentimiento = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relación uno-a-muchos con Pedido
    pedidos = relationship("Pedido", back_populates="usuario")


class Pedido(Base):
  __tablename__ = "pedidos"

  id = Column(Integer, primary_key=True, index=True)
  usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
  total = Column(Numeric(12, 2), nullable=False, default=0.0)
  estado = Column(String, default="pendiente", nullable=False)
  creado_en = Column(DateTime, default=datetime.utcnow)

  # Relaciones
  usuario = relationship(
      "Usuario", back_populates="pedidos"
  )  # <-- ESTA LÍNEA FALTABA
  items = relationship(
      "ItemPedido", back_populates="pedido", cascade="all, delete-orphan"
  )


class ItemPedido(Base):
  __tablename__ = "items_pedidos"

  id = Column(Integer, primary_key=True, index=True)
  pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
  producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
  cantidad = Column(Integer, nullable=False)
  precio_unitario = Column(Numeric(12, 2), nullable=False)

  pedido = relationship("Pedido", back_populates="items")
  producto = relationship("Producto")



class SolicitudRevocacion(Base):
    __tablename__ = "solicitudes_revocacion"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    creada_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


def generar_codigo() -> str:
    fecha = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"ARR-{fecha}-{secrets.token_hex(3).upper()}"