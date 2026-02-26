import pandas as pd

def parse_file(path: str):
    if path.endswith(".csv"):
        return pd.read_csv(path)

    if path.endswith(".xlsx") or path.endswith(".xls"):
        return pd.read_excel(path)

    if path.endswith(".json"):
        return pd.read_json(path)

    raise ValueError("Unsupported format")