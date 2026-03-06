from fastapi import APIRouter, HTTPException
import os
import pandas as pd
import json

router = APIRouter()

UPLOAD_DIR = "storage"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/analytics/{file_id}")
async def get_analytics(file_id: str):
    """
    Анализирует загруженный файл
    """
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
        
        # Определяем тип файла по расширению
        ext = file_name.split(".")[-1].lower()
        
        if ext == "csv":
            df = pd.read_csv(file_path, encoding='utf-8')
        elif ext == "xlsx":
            df = pd.read_excel(file_path)
        elif ext == "xml":
            df = pd.read_xml(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Базовая аналитика
        result = {
            "file_id": file_id,
            "filename": file_name,
            "rows": len(df),
            "columns": list(df.columns),
            "summary": {
                "numeric_columns": df.select_dtypes(include=['number']).columns.tolist(),
                "categorical_columns": df.select_dtypes(include=['object']).columns.tolist(),
            },
            "preview": df.head(5).to_dict(orient='records')
        }
        
        # Добавляем статистику для числовых колонок
        numeric_stats = {}
        for col in df.select_dtypes(include=['number']).columns:
            numeric_stats[col] = {
                "mean": float(df[col].mean()) if not df[col].isna().all() else 0,
                "min": float(df[col].min()) if not df[col].isna().all() else 0,
                "max": float(df[col].max()) if not df[col].isna().all() else 0,
                "std": float(df[col].std()) if not df[col].isna().all() else 0
            }
        
        result["numeric_stats"] = numeric_stats
        
        print(f"✅ Файл успешно прочитан: {file_name}")
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")