from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
  return pwd_context.hash(password)


def verificar_password(plain_password: str, hashed_password: str) -> bool:
  return pwd_context.verify(plain_password, hashed_password)


def crear_token(data: dict, expires_delta: timedelta) -> str:
  to_encode = data.copy()
  expiracion = datetime.now(timezone.utc) + expires_delta
  to_encode.update({"exp": expiracion})
  return jwt.encode(
      to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
  )