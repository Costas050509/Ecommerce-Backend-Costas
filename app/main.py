import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import Base, engine
from app.routers import auth, pedidos, productos, usuarios
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-Commerce Backend",
    description="API para gestión de usuarios, productos y pedidos",
    version="1.0.0",
)

# 2. Configurar orígenes permitidos (puerto de Vite/React)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# 3. Agregar el middleware a FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Permite peticiones de tu React
    allow_credentials=True,      # Permite envío de tokens/cookies
    allow_methods=["*"],          # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],          # Permite Authorization y otros headers
)

# Montar archivos estáticos
os.makedirs("uploads/productos", exist_ok=True)
app.mount("/static", StaticFiles(directory="uploads"), name="static")
app.mount("/demo", StaticFiles(directory="app/static/demo"), name="demo")

# 4. Incluir routers
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