import pandas as pd

def build_monthly_forecast(monthly_df, periods=12):
    """
    Dummy forecast: reuse last known value for future months.
    This avoids Prophet/stanc issues on Render while keeping the API shape.
    """
    if monthly_df.empty:
        future_list = []
        totals = {
            "next_3_months": 0.0,
            "next_6_months": 0.0,
            "next_12_months": 0.0,
        }
        return future_list, totals

    last_date = monthly_df["date"].max()
    last_value = float(monthly_df["sold"].iloc[-1])

    future_dates = pd.date_range(
        start=last_date + pd.offsets.MonthBegin(1),
        periods=periods,
        freq="MS",
    )

    future_list = [
        {"date": d.strftime("%Y-%m"), "predicted_sold": last_value}
        for d in future_dates
    ]

    next_3_total = last_value * 3
    next_6_total = last_value * 6
    next_12_total = last_value * 12

    totals = {
        "next_3_months": next_3_total,
        "next_6_months": next_6_total,
        "next_12_months": next_12_total,
    }

    return future_list, totals



