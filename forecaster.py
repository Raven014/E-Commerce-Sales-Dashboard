# # forecaster.py
# import pandas as pd
# from prophet import Prophet

# def build_monthly_forecast(monthly_df, periods=12):
#     """
#     monthly_df: DataFrame with columns ['date', 'sold'] (date is datetime)
#     periods: number of future months to forecast
#     returns: (future_list, totals_dict)
#     """
#     model_df = monthly_df.rename(columns={'date': 'ds', 'sold': 'y'})
#     model = Prophet(
#         yearly_seasonality=True,
#         weekly_seasonality=False,
#         daily_seasonality=False
#     )
#     model.fit(model_df)

#     future = model.make_future_dataframe(periods=periods, freq='MS')
#     forecast = model.predict(future)
#     future_part = forecast.tail(periods)[['ds', 'yhat']]

#     future_list = [
#         {'date': d.strftime('%Y-%m'), 'predicted_sold': float(y)}
#         for d, y in zip(future_part['ds'], future_part['yhat'])
#     ]

#     next_3_total = sum(item['predicted_sold'] for item in future_list[:3])
#     next_6_total = sum(item['predicted_sold'] for item in future_list[:6])
#     next_12_total = sum(item['predicted_sold'] for item in future_list[:12])

#     totals = {
#         'next_3_months': next_3_total,
#         'next_6_months': next_6_total,
#         'next_12_months': next_12_total,
#     }

#     return future_list, totals


# forecaster.py
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

    # generate future months
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

