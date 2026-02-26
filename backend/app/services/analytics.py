def calculate_metrics(df):
    total_revenue = df["revenue"].sum()
    total_expenses = df["expenses"].sum()

    profit = total_revenue - total_expenses
    margin = (profit / total_revenue) * 100

    return {
        "total_revenue": float(total_revenue),
        "total_expenses": float(total_expenses),
        "profit": float(profit),
        "margin": round(margin, 2)
    }