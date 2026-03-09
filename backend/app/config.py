from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    # База данных
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./celma.db")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 дней
    
    # Тарифы
    FREE_REPORTS_LIMIT: int = 1  # Пробный доступ - 1 отчет
    PRO_REPORTS_LIMIT: int = 50  # Pro - 50 отчетов в месяц
    BUSINESS_REPORTS_LIMIT: int = 500  # Business - 500 отчетов в месяц
    
    # Redis для кэширования
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    class Config:
        env_file = ".env"

settings = Settings()