from fastapi import FastAPI, Depends, HTTPException, status, Header, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
import os
import hashlib
import secrets

# Конфигурация
SECRET_KEY = "celma-super-secret-key-2026-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 часа

# Функции для работы с паролями (без bcrypt/passlib)
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

# Модели данных
class User(BaseModel):
    id: str
    email: str
    hashed_password: str
    reports_today: int = 0
    last_reset: datetime = datetime.utcnow()
    created_at: datetime = datetime.utcnow()

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Временное хранилище (в памяти)
users_db = {}

# JWT функции
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# Получение текущего пользователя
async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    token = parts[1]
    payload = decode_token(token)
    
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = payload["sub"]
    user = users_db.get(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

# Проверка лимита отчетов
def check_report_limit(user: User):
    if datetime.utcnow() - user.last_reset > timedelta(days=1):
        user.reports_today = 0
        user.last_reset = datetime.utcnow()
    
    if user.reports_today >= 10:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily report limit exceeded (10 reports per day)"
        )
    return user

# Создаем приложение
app = FastAPI(title="CELMA API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Эндпоинты аутентификации
@app.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Проверяем уникальность email
    for user in users_db.values():
        if user.email == user_data.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Создаем пользователя
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user_data.password)
    
    user = User(
        id=user_id,
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    users_db[user_id] = user
    access_token = create_access_token({"sub": user_id})
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    # Ищем пользователя
    user = None
    for u in users_db.values():
        if u.email == user_data.email:
            user = u
            break
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token({"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me")
async def get_my_profile(current_user: User = Depends(get_current_user)):
    if datetime.utcnow() - current_user.last_reset > timedelta(days=1):
        current_user.reports_today = 0
        current_user.last_reset = datetime.utcnow()
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "reports_today": current_user.reports_today,
        "reports_left": max(0, 10 - current_user.reports_today),
        "created_at": current_user.created_at.isoformat()
    }

# Папка для загрузки файлов
UPLOAD_DIR = "storage"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Эндпоинт загрузки с проверкой лимита
@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # Проверяем лимит
    check_report_limit(current_user)
    
    try:
        file_id = str(uuid.uuid4())
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "bin"
        file_name = f"{file_id}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "saved_as": file_name,
            "size": len(content)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки файла: {str(e)}")

# Эндпоинт аналитики с проверкой лимита и увеличением счетчика
@app.post("/analytics/{file_id}")
async def get_analytics(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    # Проверяем лимит
    check_report_limit(current_user)
    
    try:
        # Ищем файл
        files = os.listdir(UPLOAD_DIR)
        file_name = None
        for f in files:
            if f.startswith(file_id):
                file_name = f
                break
        
        if not file_name:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_path = os.path.join(UPLOAD_DIR, file_name)
        
        # Увеличиваем счетчик
        current_user.reports_today += 1
        
        # Базовая аналитика
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
            ],
            "reports_left": 10 - current_user.reports_today,
            "reports_today": current_user.reports_today
        }
        
        print(f"✅ Файл проанализирован: {file_name}")
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")

@app.get("/")
async def root():
    return {"message": "CELMA API is running", "status": "ok"}