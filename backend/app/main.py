from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
import os
import shutil

from app import models, database
from app.database import SessionLocal, engine

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

# Хэширование
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

# Вспомогательные функции
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Проверка токена через заголовок Authorization
    # (в реальном проекте нужно добавить middleware)
    
    try:
        file_id = str(uuid.uuid4())
        ext = file.filename.split('.')[-1]
        filename = f"{file_id}.{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        content = await file.read()
        with open(filepath, "wb") as f:
            f.write(content)
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "size": len(content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "CELMA API работает!", "status": "ok"}