from fastapi import APIRouter, HTTPException
import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LinearRegression

router = APIRouter()

STORAGE_DIR = "storage"

@router.post("/{file_id}")
async def analyze_file(file_id: str):
    """
    ГЛУБОКИЙ ML АНАЛИЗ ФАЙЛА
    Автоматически определяет разделитель (; или ,) и кодировку.
    Строит прогноз линейной регрессией.
    """
    
    # 1. Поиск файла в хранилище
    file_path = None
    if os.path.exists(STORAGE_DIR):
        for filename in os.listdir(STORAGE_DIR):
            if filename.startswith(file_id):
                file_path = os.path.join(STORAGE_DIR, filename)
                break
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден в хранилище")

    try:
        # 2. УМНОЕ ЧТЕНИЕ CSV (Исправление проблемы с разделителями)
        df = None
        # Пробуем комбинации: сначала UTF-8, потом Latin1. Внутри пробуем ',' и ';'
        encodings = ['utf-8', 'latin1', 'cp1251']
        separators = [',', ';', '\t']
        
        for enc in encodings:
            if df is not None: break
            for sep in separators:
                try:
                    temp_df = pd.read_csv(file_path, encoding=enc, sep=sep)
                    # Если колонок больше 1, значит разделитель угадан верно
                    if len(temp_df.columns) > 1:
                        df = temp_df
                        print(f"✅ Файл успешно прочитан: кодировка={enc}, разделитель='{sep}'")
                        break
                except Exception:
                    continue
        
        if df is None or len(df.columns) <= 1:
            raise HTTPException(status_code=400, detail="Не удалось разобрать CSV. Проверьте формат файла.")

        # Очистка от пустых строк
        df = df.dropna(how='all')
        
        # Преобразуем все возможные числовые колонки (убираем пробелы из чисел "1 000" -> 1000)
        for col in df.columns:
            if df[col].dtype == 'object':
                # Пробуем очистить строку от пробелов и привести к числу
                try:
                    df[col] = df[col].astype(str).str.replace(r'\s+', '', regex=True).str.replace(',', '.', regex=False)
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    pass

        # 3. Поиск числовых колонок
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_cols:
            raise HTTPException(status_code=400, detail="В файле нет числовых данных для анализа. Проверьте колонки.")

        # Выбираем главную целевую колонку (ту, где сумма максимальна - обычно это Выручка)
        target_col = max(numeric_cols, key=lambda x: df[x].sum() if pd.api.types.is_numeric_dtype(df[x]) else 0)
        
        # 4. ML: Прогнозирование тренда (Линейная регрессия)
        # X - индекс строки (время), y - значения целевой колонки
        X = np.arange(len(df)).reshape(-1, 1)
        y = df[target_col].fillna(0).values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Генерируем прогноз на следующие 5 шагов (месяцев/периодов)
        future_X = np.arange(len(df), len(df) + 5).reshape(-1, 1)
        forecast_values = model.predict(future_X)
        
        # 5. Поиск аномалий (отклонение > 2 сигмы)
        mean_val = df[target_col].mean()
        std_val = df[target_col].std()
        anomalies_count = int(((df[target_col] - mean_val).abs() > (2 * std_val)).sum())
        
        # 6. Подготовка данных для графика (последние 10 точек истории + прогноз)
        history_limit = 10
        history_df = df.tail(history_limit)
        
        # Метки для оси X (берем первую колонку как название периода, если она есть, иначе индекс)
        label_col = df.columns[0] 
        chart_labels = [str(x) for x in history_df[label_col].tolist()]
        chart_values = history_df[target_col].tolist()
        
        forecast_labels = [f"Прогноз {i+1}" for i in range(5)]
        
        # 7. Генерация умного текста отчета
        trend_direction = "роста" if model.coef_[0] > 0 else "снижения"
        confidence = round(model.score(X, y) * 100, 1) # Точность модели R^2
        
        insight_text = (
            f"Выявлен устойчивый тренд {trend_direction} по показателю '{target_col}'. "
            f"Точность модели прогноза: {confidence}%. "
        )
        if anomalies_count > 0:
            insight_text += f"⚠️ Обнаружено {anomalies_count} аномальных значений (выбросов). "
        else:
            insight_text += "Данные чистые, без резких выбросов. "
            
        if forecast_values[-1] > mean_val:
            insight_text += "💡 Прогноз благоприятный: ожидается превышение средних показателей."
        else:
            insight_text += "⚠️ Прогноз осторожный: ожидается стабилизация или снижение."

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
            # Данные для двойного графика
            "chart_history_labels": chart_labels,
            "chart_history_data": chart_values,
            "chart_forecast_labels": forecast_labels,
            "chart_forecast_data": [float(x) for x in forecast_values],
            "ai_insight": insight_text
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Критическая ошибка ML: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обработки данных: {str(e)}")