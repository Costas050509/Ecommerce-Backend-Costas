import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import Base, engine
from app.routers import auth, pedidos, productos, usuarios
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-Commerce Backend",
    description="API para gestión de usuarios, productos y pedidos",
    version="1.0.0",
)

# Leer orígenes desde la variable de entorno CORS_ORIGINS
# Formato esperado: "https://url1.com,https://url2.com" (separados por coma)
# Si no está definida, usa localhost por defecto
cors_env = settings.CORS_ORIGINS or "http://localhost:5173,http://127.0.0.1:5173"
origins = [o.strip() for o in cors_env.split(",") if o.strip()]

print(f"[CORS] Orígenes permitidos: {origins}")  # Para debug en los logs

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
os.makedirs("uploads/productos", exist_ok=True)
app.mount("/static", StaticFiles(directory="uploads"), name="static")
app.mount("/demo", StaticFiles(directory="app/static/demo"), name="demo")

# Incluir routers
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(pedidos.router)
app.include_router(productos.router)


@app.get("/")
def root():
    return {"mensaje": "API del E-Commerce funcionando correctamente"}

@app.get("/salud")
def salud(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"estado": "ok", "base": "ok"}
    except Exception:
        return {"estado": "ok", "base": "error"}