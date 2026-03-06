from fastapi import APIRouter, HTTPException
import pandas as pd
import os
import json

router = APIRouter()

STORAGE_DIR = "storage"

@router.post("/{file_id}")
async def analyze_file(file_id: str):
    """
    Анализирует файл по ID и возвращает РЕАЛЬНУЮ статистику
    """
    # 1. Ищем файл в хранилище
    file_path = None
    if os.path.exists(STORAGE_DIR):
        for filename in os.listdir(STORAGE_DIR):
            if filename.startswith(file_id):
                file_path = os.path.join(STORAGE_DIR, filename)
                break
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")

    try:
        # 2. Читаем файл (автоматически определяем кодировку)
        # Пробуем utf-8, если ошибка - latin1 (она читает всё)
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin1')

        # 3. Считаем РЕАЛЬНЫЕ метрики
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        # Подготовка данных для графика (берем первые 10 строк для превью)
        preview_data = []
        labels = []
        
        # Если есть числовые колонки, строим график по первой из них
        chart_column = numeric_cols[0] if numeric_cols else None
        
        for index, row in df.head(10).iterrows():
            # Метка: берем индекс или первое значение строки
            label = str(row.iloc[0]) if len(row) > 0 else f"Запись {index+1}"
            labels.append(label)
            
            # Значение: берем числовую колонку или просто индекс
            value = row[chart_column] if chart_column else index
            preview_data.append(float(value))

        # 4. Формируем ОТВЕТ с реальными данными
        return {
            "file_id": file_id,
            "rows": len(df),
            "columns": list(df.columns),
            "numeric_columns": numeric_cols,
            "summary": {
                col: {
                    "mean": float(df[col].mean()),
                    "sum": float(df[col].sum()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max())
                } for col in numeric_cols
            },
            # Данные для графика
            "chart_labels": labels,
            "chart_data": preview_data,
            "chart_label_name": chart_column or "Индекс"
        }

    except Exception as e:
        print(f"Ошибка анализа: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обработки файла: {str(e)}")