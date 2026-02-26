from sklearn.linear_model import LinearRegression
import numpy as np

def linear_forecast(df):
    y = df["revenue"].values
    X = np.arange(len(y)).reshape(-1, 1)

    model = LinearRegression()
    model.fit(X, y)

    next_value = model.predict([[len(y)]])[0]

    return float(next_value)