from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Agregamos pool_pre_ping y pool_recycle para que no falle cuando Neon se duerme
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   # Prueba la conexión antes de usarla
    pool_recycle=300      # Recicla las conexiones cada 5 minutos
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()