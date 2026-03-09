from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app import models, database, config
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.settings.SECRET_KEY, algorithm=config.settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: str):
    return jwt.encode(
        {"sub": user_id, "type": "refresh", "exp": datetime.utcnow() + timedelta(days=90)},
        config.settings.SECRET_KEY,
        algorithm=config.settings.ALGORITHM
    )

def decode_token(token: str):
    try:
        payload = jwt.decode(token, config.settings.SECRET_KEY, algorithms=[config.settings.ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db)
):
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен"
        )
    
    user = db.query(models.User).filter(models.User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )
    
    return user

def check_report_limit(user: models.User, db: Session):
    # Сброс счетчика каждый месяц
    if datetime.utcnow() - user.reports_reset_date > timedelta(days=30):
        user.reports_count = 0
        user.reports_reset_date = datetime.utcnow()
        
        # Обновляем лимит согласно тарифу
        tariff = db.query(models.Tariff).filter(models.Tariff.name == user.tariff).first()
        if tariff:
            user.reports_limit = tariff.reports_limit
        
        db.commit()
    
    if user.reports_count >= user.reports_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Достигнут лимит отчетов",
                "limit": user.reports_limit,
                "current": user.reports_count,
                "tariff": user.tariff,
                "upgrade_url": "/#pricing"
            }
        )
    
    return user