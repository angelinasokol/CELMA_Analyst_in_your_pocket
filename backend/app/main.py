from fastapi import FastAPI
from app.api import upload, analytics, auth

app = FastAPI(title="Analytics API")

app.include_router(upload.router)
app.include_router(analytics.router)
app.include_router(auth.router)