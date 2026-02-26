import pandas as pd
import os

def parse_file(file_path: str):
    """
    Простой парсер файлов для CSV и Excel
    """
    # Получаем расширение: '.csv' → 'csv'
    ext = os.path.splitext(file_path)[1].lower().replace('.', '')
    
    print(f"🔍 Парсим файл: {file_path}, расширение: {ext}")  # ← для отладки
    
    if ext == 'csv':
        return pd.read_csv(file_path)
    elif ext == 'xlsx' or ext == 'xls':
        return pd.read_excel(file_path)
    else:
        # Показываем, что мы видим, чтобы понять проблему
        available = os.listdir(os.path.dirname(file_path))
        raise ValueError(f"Unsupported format: '{ext}'. Files in storage: {available}")