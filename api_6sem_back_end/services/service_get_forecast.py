from matplotlib import pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
from api_6sem_back_end.ml.train_tendency_line import train_model
from api_6sem_back_end.utils.query_filter import Filtro

def get_forecast(filtro: Filtro):
    model, df_grouped = train_model(filtro)

    if model is None:
        return {"error": "Sem dados para treinamento"}

    last_date = df_grouped['ds'].max()
    future = model.make_future_dataframe(periods=12, freq="M")
    forecast = model.predict(future)

    forecast_train = forecast[forecast["ds"].isin(df_grouped["ds"])]

    mae = mean_absolute_error(df_grouped["y"], forecast_train["yhat"])
    mape = mean_absolute_percentage_error(df_grouped["y"], forecast_train["yhat"]) * 100

    # Adicionar pontos reais (em vermelho)
    plt.scatter(df_grouped["ds"], df_grouped["y"], color="red", label="Real")

    # Adicionar previsão (linha azul)
    plt.plot(forecast["ds"], forecast["yhat"], color="blue", label="Previsão")

    # Ajustes visuais
    plt.title("Comparação: Real x Previsão Prophet")
    plt.xlabel("Data")
    plt.ylabel("Quantidade de Tickets")
    plt.legend()
    plt.grid(True)
    plt.show()

    print("MAE:", mae)
    print("MAPE:", mape, "%")

    forecast["yhat"] = forecast["yhat"].clip(lower=0)
    forecast["yhat_lower"] = forecast["yhat_lower"].clip(lower=0)
    forecast["yhat_upper"] = forecast["yhat_upper"].clip(lower=0)

    forecast_next_year = forecast[forecast['ds'] > last_date].head(12)

    result_by_month = {str(i).zfill(2): 0 for i in range(1, 13)}
    for _, row in forecast_next_year.iterrows():
        month_str = str(row["ds"].month).zfill(2)
        result_by_month[month_str] = float(row["yhat"])

    return result_by_month