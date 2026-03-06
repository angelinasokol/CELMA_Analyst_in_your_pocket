from fastapi import APIRouter, HTTPException
import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder

router = APIRouter()

STORAGE_DIR = "storage"

@router.post("/{file_id}")
async def analyze_file(file_id: str):
    """
    ГЛУБОКИЙ АНАЛИЗ ДАННЫХ С ИСПОЛЬЗОВАНИЕМ ML
    1. Чистка данных
    2. Поиск главной числовой метрики
    3. Построение прогноза (Linear Regression)
    4. Поиск аномалий
    """
    
    # 1. Поиск файла
    file_path = None
    if os.path.exists(STORAGE_DIR):
        for filename in os.listdir(STORAGE_DIR):
            if filename.startswith(file_id):
                file_path = os.path.join(STORAGE_DIR, filename)
                break
    
    if not file_path:
        raise HTTPException(status_code=404, detail="Файл не найден")

    try:
        # 2. Чтение и очистка
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin1')
        
        df = df.dropna(how='all') # Удалить пустые строки
        
        # 3. Поиск числовых колонок
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_cols:
            raise HTTPException(status_code=400, detail="В файле нет числовых данных для анализа")

        # Выбираем главную колонку для анализа (самая дисперсивная или первая крупная)
        # Логика: берем колонку с максимальной суммой (обычно это Выручка/Продажи)
        target_col = max(numeric_cols, key=lambda x: df[x].sum() if pd.api.types.is_numeric_dtype(df[x]) else 0)
        
        # 4. ML: Прогнозирование тренда (Линейная регрессия)
        # Создаем ось X (порядковый номер строки) и Y (значения целевой колонки)
        X = np.arange(len(df)).reshape(-1, 1)
        y = df[target_col].fillna(0).values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Генерируем прогноз на следующие 5 шагов (будущее)
        future_X = np.arange(len(df), len(df) + 5).reshape(-1, 1)
        forecast_values = model.predict(future_X)
        
        # 5. Поиск аномалий (отклонение > 2 стандартных отклонений)
        mean_val = df[target_col].mean()
        std_val = df[target_col].std()
        anomalies_count = int(((df[target_col] - mean_val).abs() > (2 * std_val)).sum())
        
        # 6. Формирование данных для графика (берем последние 10 точек истории + 5 точек прогноза)
        history_limit = 10
        history_df = df.tail(history_limit)
        
        chart_labels = [str(x) for x in history_df.index.tolist()] # Или название месяца, если есть
        chart_values = history_df[target_col].tolist()
        
        # Добавляем метки для прогноза
        forecast_labels = [f"Прогноз {i+1}" for i in range(5)]
        
        # 7. Генерация умного текста
        trend_direction = "роста" if model.coef_[0] > 0 else "падения"
        confidence = round(model.score(X, y) * 100, 1) # Точность модели R^2
        
        insight_text = (
            f"Выявлен устойчивый тренд {trend_direction} по показателю '{target_col}'. "
            f"Точность модели: {confidence}%. "
        )
        if anomalies_count > 0:
            insight_text += f"⚠️ Обнаружено {anomalies_count} аномальных значений, требующих проверки. "
        else:
            insight_text += "Данные чистые, аномалий не выявлено. "
            
        if forecast_values[-1] > mean_val:
            insight_text += "💡 Прогноз благоприятный: ожидается превышение средних показателей."

        return {
            "file_id": file_id,
            "rows": len(df),
            "columns": list(df.columns),
            "target_metric": target_col,
            "summary": {
                "mean": float(mean_val),
                "max": float(df[target_col].max()),
                "min": float(df[target_col].min()),
                "trend_coefficient": float(model.coef_[0]),
                "forecast_next_month": float(forecast_values[0])
            },
            # Данные для двойного графика (История + Прогноз)
            "chart_history_labels": chart_labels,
            "chart_history_data": chart_values,
            "chart_forecast_labels": forecast_labels,
            "chart_forecast_data": forecast_values.tolist(),
            "ai_insight": insight_text
        }

    except Exception as e:
        print(f"ML Error: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка ML-анализа: {str(e)}")