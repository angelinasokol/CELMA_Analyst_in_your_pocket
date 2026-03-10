from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean, JSON
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
    tariff = Column(String, default="free")
    tariff_expires = Column(DateTime, nullable=True)
    
    # Статистика
    reports_count = Column(Integer, default=0)
    reports_limit = Column(Integer, default=1)
    reports_reset_date = Column(DateTime, default=datetime.utcnow)
    
    # Дополнительно
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True)
    filename = Column(String)
    file_size = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="processing")
    result = Column(JSON, nullable=True)