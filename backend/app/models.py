from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    
    # Тариф
    tariff = Column(String, default="free")  # free, pro, business
    tariff_expires = Column(DateTime, nullable=True)
    
    # Статистика
    reports_count = Column(Integer, default=0)
    reports_limit = Column(Integer, default=1)  # Для free - 1
    reports_reset_date = Column(DateTime, default=datetime.utcnow)
    
    # Дополнительно
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Настройки
    settings = Column(JSON, default={})
    
class Tariff(Base):
    __tablename__ = "tariffs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True)  # free, pro, business
    price_monthly = Column(Float, default=0)
    price_yearly = Column(Float, default=0)
    reports_limit = Column(Integer)
    features = Column(JSON, default={})
    is_active = Column(Boolean, default=True)

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    filename = Column(String)
    file_size = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="processing")  # processing, completed, failed
    result = Column(JSON, nullable=True)