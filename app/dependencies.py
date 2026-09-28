from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import models
from app.core.config import settings
from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.Usuario:
  credentials_exception = HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="No se pudieron validar las credenciales",
      headers={"WWW-Authenticate": "Bearer"},
  )
  try:
    payload = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    email: str = payload.get("sub")
    tipo: str = payload.get("tipo")
    if email is None or tipo != "access":
      raise credentials_exception
  except JWTError:
    raise credentials_exception

  usuario = (
      db.query(models.Usuario).filter(models.Usuario.email == email).first()
  )
  if usuario is None:
    raise credentials_exception
  return usuario


def require_admin(
    current_user: models.Usuario = Depends(get_current_user),
) -> models.Usuario:
  if current_user.rol != "admin":
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tenés permisos de administrador para realizar esta acción",
    )
  return current_user