from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
import os
import hashlib
import secrets

from app import models, database
from app.database import SessionLocal, engine, get_db

# Создаем таблицы
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="CELMA API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Конфигурация
SECRET_KEY = "celma-super-secret-key-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 дней

# Папка для загрузки файлов
UPLOAD_DIR = "storage"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Хэширование без passlib
def get_password_hash(password: str) -> str:
    """Простое хэширование пароля"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((salt + password).encode())
    return f"{salt}:{hash_obj.hexdigest()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    try:
        salt, hash_value = hashed_password.split(':')
        hash_obj = hashlib.sha256((salt + plain_password).encode())
        return hash_obj.hexdigest() == hash_value
    except:
        return False

# Модели Pydantic
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

# JWT функции
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# Эндпоинты
@app.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Проверяем, существует ли пользователь
    db_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    
    # Создаем нового пользователя
    user = models.User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        reports_limit=1,  # Free тариф
        reports_reset_date=datetime.utcnow()
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    access_token = create_access_token({"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "tariff": user.tariff,
            "reports_left": user.reports_limit - user.reports_count,
            "reports_limit": user.reports_limit
        }
    }

@app.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_data.email).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    
    # Обновляем last_login
    user.last_login = datetime.utcnow()
    db.commit()
    
    access_token = create_access_token({"sub": user.id})
    
    # Сброс счетчика если прошло больше месяца
    if datetime.utcnow() - user.reports_reset_date > timedelta(days=30):
        user.reports_count = 0
        user.reports_reset_date = datetime.utcnow()
        db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "tariff": user.tariff,
            "reports_left": user.reports_limit - user.reports_count,
            "reports_limit": user.reports_limit
        }
    }

@app.get("/auth/me")
async def get_me(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Невалидный токен")
    
    user = db.query(models.User).filter(models.User.id == payload["sub"]).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    
    # Сброс счетчика если прошло больше месяца
    if datetime.utcnow() - user.reports_reset_date > timedelta(days=30):
        user.reports_count = 0
        user.reports_reset_date = datetime.utcnow()
        db.commit()
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "tariff": user.tariff,
        "reports_left": user.reports_limit - user.reports_count,
        "reports_limit": user.reports_limit,
        "reports_today": user.reports_count
    }

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Невалидный токен")
    
    user = db.query(models.User).filter(models.User.id == payload["sub"]).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    
    # Проверка лимита
    if datetime.utcnow() - user.reports_reset_date > timedelta(days=30):
        user.reports_count = 0
        user.reports_reset_date = datetime.utcnow()
    
    if user.reports_count >= user.reports_limit:
        raise HTTPException(
            status_code=429, 
            detail=f"Лимит отчетов исчерпан. Ваш тариф: {user.tariff}, лимит: {user.reports_limit}"
        )
    
    # Сохраняем файл
    file_id = str(uuid.uuid4())
    ext = file.filename.split('.')[-1]
    filename = f"{file_id}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)
    
    # Увеличиваем счетчик
    user.reports_count += 1
    db.commit()
    
    return {
        "file_id": file_id,
        "filename": file.filename,
        "size": len(content),
        "reports_left": user.reports_limit - user.reports_count,
        "reports_today": user.reports_count
    }

@app.post("/analytics/{file_id}")
async def get_analytics(
    file_id: str,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Не авторизован")
    
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Невалидный токен")
    
    user = db.query(models.User).filter(models.User.id == payload["sub"]).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    
    # Проверяем существование файла
    files = os.listdir(UPLOAD_DIR)
    file_name = None
    for f in files:
        if f.startswith(file_id):
            file_name = f
            break
    
    if not file_name:
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    # Демо-данные для аналитики
    result = {
        "file_id": file_id,
        "filename": file_name,
        "rows": 100,
        "columns": ["date", "sales", "profit", "category"],
        "summary": {
            "numeric_columns": ["sales", "profit"],
            "categorical_columns": ["date", "category"],
        },
        "preview": [
            {"date": "2026-01-01", "sales": 1000, "profit": 200, "category": "A"},
            {"date": "2026-01-02", "sales": 1500, "profit": 300, "category": "B"},
        ]
    }
    
    return result

@app.get("/")
async def root():
    return {"message": "CELMA API работает!", "status": "ok", "version": "2.0"}