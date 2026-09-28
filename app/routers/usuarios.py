import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Usuario, Pedido, SolicitudRevocacion

# Cambiamos a 'router' para que main.py lo reconozca
router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.get("/me/datos")
def obtener_mis_datos(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    pedidos = db.query(Pedido).filter(Pedido.usuario_id == current_user.id).all()
    solicitudes = db.query(SolicitudRevocacion).filter(SolicitudRevocacion.usuario_id == current_user.id).all()
    
    return {
        "usuario": {
            "id": current_user.id,
            "nombre": current_user.nombre,
            "email": current_user.email,
            "activo": current_user.activo
        },
        "pedidos": pedidos,
        "solicitudes_revocacion": solicitudes
    }

@router.get("/me/exportar")
def exportar_mis_datos(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    datos = obtener_mis_datos(current_user, db)
    contenido = json.dumps(datos, default=str, indent=2)
    
    return Response(
        content=contenido,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=mis_datos_{current_user.id}.json"}
    )

@router.delete("/me")
def dar_de_baja(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.nombre = "Usuario Anónimo"
    current_user.email = f"anonimo_{current_user.id}@borrado.local"
    current_user.hashed_password = "Baja_Anonimizada"
    current_user.activo = False
    current_user.fecha_baja = datetime.now(timezone.utc)
    
    db.commit()
    return {"message": "Cuenta dada de baja y datos anonimizados correctamente"}