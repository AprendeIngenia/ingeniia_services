# src/core/config.py

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ISS: str
    JWT_AUD: str
    
    # Email
    EMAIL_PROVIDER: str
    SENDGRID_API_KEY: str
    FROM_EMAIL: str
    VERIFICATION_EMAIL_TEMPLATE_ID: str
    FRONTEND_URL: str = "https://www.ingeniia.co"
    
    # Captcha
    RECAPTCHA_SECRET_KEY: str
    RECAPTCHA_VERIFY_URL: str = "https://www.google.com/recaptcha/api/siteverify"
    RECAPTCHA_MIN_SCORE: float = 0.5
    
    # CORS
    CORS_ORIGINS: List[str]
    
    # App
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    EMAIL_TOKEN_EXPIRE_MINUTES: int = 120
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()