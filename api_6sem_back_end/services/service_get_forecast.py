from api_6sem_back_end.ml.train_tendency_line import train_model
from api_6sem_back_end.utils.query_filter import Filtro, build_query_filter

def get_forecast(filtro: Filtro, role: str):
        base_filter = build_query_filter(filtro)

        if role != "Gestor":
            levels_map = {
                "N1": ["N1"],
                "N2": ["N1", "N2"],
                "N3": ["N1", "N2", "N3"]
            }
            allowed_levels = levels_map.get(role.upper(), [])
            base_filter["access_level"] = {"$in": allowed_levels}

        model, df_grouped = train_model(filtro, train_until="2025-08-31", custom_filter=base_filter)

        if model is None or df_grouped is None or df_grouped.empty:
            return None

        last_date = df_grouped['ds'].max()
        future = model.make_future_dataframe(periods=12, freq="M")
        forecast = model.predict(future)
        forecast["yhat"] = forecast["yhat"].clip(lower=0)
        forecast_next_year = forecast[forecast['ds'] > last_date].head(12)

        result_by_month = {str(i).zfill(2): 0 for i in range(1, 13)}
        for _, row in forecast_next_year.iterrows():
            month_str = str(row["ds"].month).zfill(2)
            result_by_month[month_str] = float(row["yhat"])

        return result_by_month