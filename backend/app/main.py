from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import upload, analytics, auth

app = FastAPI(title="Analytics API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры с префиксами
app.include_router(upload.router, prefix="/upload")
app.include_router(analytics.router, prefix="/analytics")
app.include_router(auth.router, prefix="/auth")

# Корневой маршрут
@app.get("/")
def root():
    return {"message": "API is running 🚀"}