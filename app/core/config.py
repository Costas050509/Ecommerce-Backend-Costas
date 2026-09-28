from pydantic_settings import BaseSettings


class Settings(BaseSettings):
  PROJECT_NAME: str = "API E-Commerce"
  DATABASE_URL: (
      str  # Se lee del .env (ej: postgresql://postgres:postgres@localhost:5432/ecommerce_db)
  )
  SECRET_KEY: str = (
      "dev_secret_key_123456789_change_me"  # Fallback seguro para que Alembic no falle
  )
  ALGORITHM: str = "HS256"
  ACCESS_MIN: int = 30
  REFRESH_MIN: int = 10080

  class Config:
    env_file = ".env"
    extra = "ignore"


settings = Settings()