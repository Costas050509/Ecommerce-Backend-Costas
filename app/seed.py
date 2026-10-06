"""
Script de siembra (Seeder) para la base de datos del E-Commerce.

¿Para qué sirve este archivo?
-----------------------------
Cuando desplegás tu backend en plataformas como Render, Railway o Supabase,
la base de datos PostgreSQL en la nube inicia completamente VACÍA.
Este script se encarga de:
1. Crear las tablas necesarias si aún no existen.
2. Crear un usuario Administrador por defecto (para poder gestionar el panel y productos).
3. Crear un usuario Cliente de prueba (para poder probar compras y autenticación).
4. Poblar el catálogo con productos iniciales de muestra con precios, stock y fotos.

Uso:
----
Desde la terminal en la raíz del proyecto:
    python -m app.seed
o directamente:
    python app/seed.py
"""

import sys
import os

# Asegurar que el directorio raíz esté en el path para poder importar 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app import models
from app.core.security import hash_password


def seed_usuarios(db: Session) -> dict:
    """Crea los usuarios iniciales (Admin y Cliente) si no existen."""
    print("[*] Verificando usuarios iniciales...")
    
    # 1. Usuario Administrador
    admin_email = os.getenv("SEED_ADMIN_EMAIL", "admin@ecommerce.com")
    admin_password = os.getenv("SEED_ADMIN_PASSWORD", "admin123")
    
    admin = db.query(models.Usuario).filter(models.Usuario.email == admin_email).first()
    if not admin:
        admin = models.Usuario(
            nombre="Administrador",
            email=admin_email,
            hashed_password=hash_password(admin_password),
            rol="admin",
            activo=True,
            acepto_tratamiento=True,
            fecha_consentimiento=datetime.now(timezone.utc),
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"  [+] Usuario Admin creado: {admin_email} (password: {admin_password})")
    else:
        print(f"  [i] Usuario Admin ya existe: {admin_email}")

    # 2. Usuario Cliente Demo
    cliente_email = os.getenv("SEED_CLIENTE_EMAIL", "cliente@ecommerce.com")
    cliente_password = os.getenv("SEED_CLIENTE_PASSWORD", "cliente123")
    
    cliente = db.query(models.Usuario).filter(models.Usuario.email == cliente_email).first()
    if not cliente:
        cliente = models.Usuario(
            nombre="Cliente Demo",
            email=cliente_email,
            hashed_password=hash_password(cliente_password),
            rol="cliente",
            activo=True,
            acepto_tratamiento=True,
            fecha_consentimiento=datetime.now(timezone.utc),
        )
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        print(f"  [+] Usuario Cliente creado: {cliente_email} (password: {cliente_password})")
    else:
        print(f"  [i] Usuario Cliente ya existe: {cliente_email}")

    return {"admin": admin, "cliente": cliente}


def seed_productos(db: Session) -> list:
    """Crea un catálogo de productos de prueba si no existen."""
    print("[*] Verificando catalogo de productos...")
    
    productos_iniciales = [
        {
            "nombre": "Notebook Pro Max 16",
            "descripcion": "Laptop de alto rendimiento con procesador octa-core, 32GB RAM y 1TB SSD NVMe.",
            "precio": 1499.99,
            "stock": 15,
            "imagen_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop&q=60",
        },
        {
            "nombre": "Smartphone Ultra 5G",
            "descripcion": "Pantalla AMOLED de 120Hz, camara de 108MP y bateria para 2 dias de uso continuo.",
            "precio": 899.50,
            "stock": 30,
            "imagen_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&auto=format&fit=crop&q=60",
        },
        {
            "nombre": "Auriculares Wireless Noise Cancelling",
            "descripcion": "Cancelacion activa de ruido premium, audio espacial y hasta 40 horas de autonomia.",
            "precio": 199.99,
            "stock": 50,
            "imagen_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=60",
        },
        {
            "nombre": "Teclado Mecanico RGB Custom",
            "descripcion": "Switches mecanicos lubricados, retroiluminacion RGB configurable y conexion inalambrica 2.4GHz.",
            "precio": 129.00,
            "stock": 25,
            "imagen_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&auto=format&fit=crop&q=60",
        },
        {
            "nombre": "Mouse Gamer Ergonomico 16000 DPI",
            "descripcion": "Sensor optico de alta precision, peso ultraligero y switches opticos de rapida respuesta.",
            "precio": 59.99,
            "stock": 40,
            "imagen_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800&auto=format&fit=crop&q=60",
        },
        {
            "nombre": "Monitor Curvo 27\" 165Hz QHD",
            "descripcion": "Resolucion 2560x1440, panel IPS con tiempo de respuesta de 1ms y compatibilidad FreeSync/G-Sync.",
            "precio": 349.00,
            "stock": 12,
            "imagen_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&auto=format&fit=crop&q=60",
        },
        {
            "nombre": "Smartwatch Deportivo Pro",
            "descripcion": "Sensor de ritmo cardiaco, oximetro SpO2, GPS integrado y sumergible hasta 50 metros.",
            "precio": 179.99,
            "stock": 20,
            "imagen_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&auto=format&fit=crop&q=60",
        },
        {
            "nombre": "Webcam 4K Ultra HD con Microfono",
            "descripcion": "Enfoque automatico, correccion de poca luz y microfonos estereo con reduccion de ruido.",
            "precio": 89.90,
            "stock": 35,
            "imagen_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800&auto=format&fit=crop&q=60",
        },
    ]

    productos_creados = []
    for item in productos_iniciales:
        prod = db.query(models.Producto).filter(models.Producto.nombre == item["nombre"]).first()
        if not prod:
            prod = models.Producto(
                nombre=item["nombre"],
                descripcion=item["descripcion"],
                precio=item["precio"],
                stock=item["stock"],
                imagen_url=item["imagen_url"],
            )
            db.add(prod)
            db.commit()
            db.refresh(prod)
            print(f"  [+] Producto creado: {prod.nombre} - ${prod.precio}")
        else:
            print(f"  [i] Producto ya existe: {prod.nombre}")
        productos_creados.append(prod)

    return productos_creados


def seed_pedidos(db: Session, cliente: models.Usuario, productos: list):
    """Crea un pedido inicial de muestra asociado al cliente demo si no tiene pedidos."""
    print("[*] Verificando pedidos de muestra...")
    if not cliente or not productos:
        return

    pedido_existente = db.query(models.Pedido).filter(models.Pedido.usuario_id == cliente.id).first()
    if not pedido_existente and len(productos) >= 2:
        prod1 = productos[0]
        prod2 = productos[2]

        subtotal1 = Decimal(str(prod1.precio)) * 1
        subtotal2 = Decimal(str(prod2.precio)) * 2
        total = subtotal1 + subtotal2

        nuevo_pedido = models.Pedido(
            usuario_id=cliente.id,
            total=total,
            estado="pagado",
            creado_en=datetime.now(timezone.utc),
        )
        db.add(nuevo_pedido)
        db.commit()
        db.refresh(nuevo_pedido)

        item1 = models.ItemPedido(
            pedido_id=nuevo_pedido.id,
            producto_id=prod1.id,
            cantidad=1,
            precio_unitario=Decimal(str(prod1.precio)),
        )
        item2 = models.ItemPedido(
            pedido_id=nuevo_pedido.id,
            producto_id=prod2.id,
            cantidad=2,
            precio_unitario=Decimal(str(prod2.precio)),
        )
        db.add_all([item1, item2])
        db.commit()
        print(f"  [+] Pedido de muestra creado (ID: {nuevo_pedido.id}) por un total de ${total}")
    else:
        print("  [i] Pedidos de muestra ya existentes o no requeridos.")


def seed_all():
    """Ejecuta todas las tareas de siembra de la base de datos."""
    print("=" * 60)
    print(">>> INICIANDO PROCESO DE SEEDING DE BASE DE DATOS <<<")
    print("=" * 60)

    # 1. Asegurar que las tablas existan en la base de datos
    print("[*] Creando tablas en la base de datos si no existen...")
    Base.metadata.create_all(bind=engine)
    print("  [OK] Tablas verificadas/creadas.")

    # 2. Iniciar sesion e insertar los registros iniciales
    db = SessionLocal()
    try:
        usuarios = seed_usuarios(db)
        productos = seed_productos(db)
        seed_pedidos(db, usuarios.get("cliente"), productos)
        print("=" * 60)
        print(">>> SEEDING COMPLETADO EXITOSAMENTE <<<")
        print("=" * 60)
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error durante el proceso de seeding: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
