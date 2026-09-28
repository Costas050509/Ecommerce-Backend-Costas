from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import models
from app.core.config import settings
from app.core.security import crear_token, hash_password, verificar_password
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.usuario import (
    RefreshTokenRequest,
    Token,
    UsuarioCreate,
    UsuarioOut,
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/register", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED
)
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_user = (
        db.query(models.Usuario)
        .filter(models.Usuario.email == usuario.email)
        .first()
    )
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado",
        )

    nuevo_usuario = models.Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        hashed_password=hash_password(usuario.password),
        acepto_tratamiento=usuario.acepto_tratamiento,
        rol="cliente",
        activo=True,
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # Buscar usuario por email (Swagger UI manda el email en form_data.username)
    usuario = (
        db.query(models.Usuario)
        .filter(models.Usuario.email == form_data.username)
        .first()
    )

    # Validar existencia y contraseña
    if not usuario or not verificar_password(
        form_data.password, usuario.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validar que la cuenta no esté dada de baja / inactivada
    if hasattr(usuario, "activo") and not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La cuenta se encuentra desactivada o dada de baja",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generación de tokens
    access_token = crear_token(
        data={"sub": usuario.email, "rol": usuario.rol, "tipo": "access"},
        expires_delta=timedelta(minutes=int(settings.ACCESS_MIN)),
    )
    refresh_token = crear_token(
        data={"sub": usuario.email, "rol": usuario.rol, "tipo": "refresh"},
        expires_delta=timedelta(minutes=int(settings.REFRESH_MIN)), 
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UsuarioOut)
def obtener_perfil(current_user: models.Usuario = Depends(get_current_user)):
    return current_user


@router.post("/refresh", response_model=Token)
def refresh_token(
    request: RefreshTokenRequest, db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token de refresco inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            request.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        email: str = payload.get("sub")
        tipo: str = payload.get("tipo")
        if email is None or tipo != "refresh":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    usuario = (
        db.query(models.Usuario).filter(models.Usuario.email == email).first()
    )
    if not usuario or (hasattr(usuario, "activo") and not usuario.activo):
        raise credentials_exception

    new_access_token = crear_token(
        data={"sub": usuario.email, "rol": usuario.rol, "tipo": "access"},
        expires_delta=timedelta(minutes=settings.ACCESS_MIN),
    )
    new_refresh_token = crear_token(
        data={"sub": usuario.email, "rol": usuario.rol, "tipo": "refresh"},
        expires_delta=timedelta(minutes=settings.REFRESH_MIN),
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }