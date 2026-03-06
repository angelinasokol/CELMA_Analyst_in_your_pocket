from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import upload, analytics, auth # И ai, если создавал

app = FastAPI(title="Analytics API")

# 🔥 ЭТОТ БЛОК ДОЛЖЕН БЫТЬ ПЕРЕД include_router!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем всем (для разработки ок)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(upload.router, prefix="/upload")
app.include_router(analytics.router, prefix="/analytics")
# app.include_router(auth.router, prefix="/auth") # Если есть
# app.include_router(ai.router, prefix="/ai")     # Если есть

@app.get("/")
def root():
    return {"message": "API is running 🚀"}