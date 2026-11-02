import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app import models
from tests.ayudantes import registrar, token_de

# 1. Crear una base de datos en memoria
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionPrueba = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db_prueba():
    with SessionPrueba() as db:
        yield db

@pytest.fixture
def client():
    # Creamos las tablas en la base de prueba
    Base.metadata.create_all(bind=engine)
    
    # Reemplazamos la dependencia real por la de prueba
    app.dependency_overrides[get_db] = get_db_prueba
    
    with TestClient(app) as c:
        yield c
        
    # Limpiamos todo al terminar
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def cliente(client):
    """Headers de un cliente común, ya logueado."""
    return token_de(client, *registrar(client))

@pytest.fixture
def admin(client):
    """Headers de un admin. No hay endpoint para el rol: se toca la base."""
    email, password = registrar(client, email="admin@prueba.com")
    with SessionPrueba() as db:
        usuario = db.query(models.Usuario).filter_by(email=email).one()
        usuario.rol = "admin"  # Tu backend usa "admin", así que está perfecto
        db.commit()
    return token_de(client, email, password)

@pytest.fixture
def producto(client, admin):
    """Un producto con 2 unidades. Ajustá los campos a tu ProductoCreate."""
    r = client.post(
        "/productos/",
        headers=admin,
        json={
            "nombre": "Jugo de Prueba",
            "descripcion": "Jugo para los tests",
            "precio": 1500.0,
            "stock": 10,
            # Si tu modelo pide imagen_url, podés agregarla acá o dejarla en null
        },
    )
    assert r.status_code == 201, r.text
    return r.json()