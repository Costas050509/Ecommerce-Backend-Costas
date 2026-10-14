from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "API E-Commerce"
    DATABASE_URL: str
    SECRET_KEY: str = "dev_secret_key_123456789_change_me"
    ALGORITHM: str = "HS256"
    ACCESS_MIN: int = 30
    REFRESH_MIN: int = 10080
    CORS_ORIGINS: str = ""  # <-- NUEVA variable

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()