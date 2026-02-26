from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
import os

router = APIRouter()

# Папка для загрузки файлов
UPLOAD_DIR = "storage"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    """
    Загружает файл на сервер и возвращает его ID
    """
    try:
        # Генерируем уникальный ID
        file_id = str(uuid.uuid4())
        
        # Определяем расширение файла
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "bin"
        
        # Формируем безопасное имя файла
        file_name = f"{file_id}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        
        # Читаем и сохраняем файл
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