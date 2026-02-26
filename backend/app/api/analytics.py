from fastapi import APIRouter, HTTPException
import pandas as pd
import os

router = APIRouter()

# Путь к папке storage (относительно backend/)
STORAGE_DIR = os.path.join(os.path.dirname(__file__), "../../storage")

@router.post("/{file_id}")
async def analyze_file(file_id: str):
    """
    Анализирует файл и возвращает статистику
    """
    # Ищем файл по ID
    found_path = None
    if os.path.exists(STORAGE_DIR):
        for filename in os.listdir(STORAGE_DIR):
            if filename.startswith(file_id):
                found_path = os.path.join(STORAGE_DIR, filename)
                break
    
    if not found_path or not os.path.exists(found_path):
        raise HTTPException(status_code=404, detail=f"Файл не найден: {file_id}")
    
    try:
        # Определяем расширение
        ext = os.path.splitext(found_path)[1].lower()
        print(f"📁 Читаем файл: {found_path}, расширение: {ext}")
        
        # Читаем в зависимости от типа
        if ext == '.csv':
            df = pd.read_csv(found_path)
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(found_path)
        else:
            raise ValueError(f"Неподдерживаемый формат: {ext}")
        
        # Считаем статистику только по числовым колонкам
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        
        return {
            "file_id": file_id,
            "filename": os.path.basename(found_path),
            "rows": len(df),
            "columns": list(df.columns),
            "numeric_columns": numeric_cols,
            "summary": {
                col: {
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                }
                for col in numeric_cols
            },
            "preview": df.head(3).to_dict(orient="records")
        }
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Файл пустой")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Ошибка парсинга CSV")
    except Exception as e:
        print(f"❌ Ошибка: {e}")  # ← увидим в терминале
        raise HTTPException(status_code=500, detail=str(e))