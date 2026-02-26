from fastapi import APIRouter, UploadFile, File
import pandas as pd
import uuid
import os

router = APIRouter(prefix="/upload")

UPLOAD_DIR = "storage"

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = f"{UPLOAD_DIR}/{file_id}_{file.filename}"

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return {"file_id": file_id}