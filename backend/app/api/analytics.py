from fastapi import APIRouter
from app.services.file_parser import parse_file
from app.services.analytics import calculate_metrics
from app.services.forecast import linear_forecast

router = APIRouter(prefix="/analytics")

@router.post("/{file_path}")
def analyze(file_path: str):
    df = parse_file(file_path)

    metrics = calculate_metrics(df)
    forecast = linear_forecast(df)

    return {
        "metrics": metrics,
        "forecast": forecast
    }