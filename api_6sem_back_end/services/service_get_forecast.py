from fastapi import APIRouter
from prophet.diagnostics import performance_metrics, cross_validation

from api_6sem_back_end.ia.train_tendency_line import train_model
from api_6sem_back_end.utils.query_filter import Filtro

router = APIRouter(prefix="/tickets", tags=["Tickets"])

def get_forecast(filtro: Filtro):
    model, df_grouped = train_model(filtro, train_until="2025-08-31")

    if model is None:
        return {"error": "Sem dados para treinamento"}

    last_date = df_grouped['ds'].max()
    future = model.make_future_dataframe(periods=12, freq="M")
    forecast = model.predict(future)
    forecast["yhat"] = forecast["yhat"].clip(lower=0)
    forecast["yhat_lower"] = forecast["yhat_lower"].clip(lower=0)
    forecast["yhat_upper"] = forecast["yhat_upper"].clip(lower=0)

    forecast_next_year = forecast[forecast['ds'] > last_date].head(12)

    result_by_month = {str(i).zfill(2): 0 for i in range(1, 13)}
    for _, row in forecast_next_year.iterrows():
        month_str = str(row["ds"].month).zfill(2)
        result_by_month[month_str] = float(row["yhat"])

    return result_by_month
