# macro-fx-ml
FXPulse – Machine Learning–based USD/PLN forecasting using macroeconomic indicators

 - FX curreny rates from twelve data ( USD/EUR, USD/PLN - this I want to forecast, USD/CHF, CHF/PLN, EUR/PLN)
 - Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity, Quoted on an Investment Basis from FRED : https://fred.stlouisfed.org/series/DGS10
 - Dane historyczne: Poland 10-Year Government Bond Yield (10YPLY.B) : https://stooq.pl/q/d/?s=10yply.b&i=d&f=19900525&t=20260129 




FRED API docs : https://fred.stlouisfed.org/docs/api/fred/








                ┌──────────────────────┐
                │     Streamlit UI     │
                │ (dashboard + signal) │
                └─────────┬────────────┘
                          │
                          ▼
                ┌──────────────────────┐
                │     API (FastAPI)    │
                │ /predict /features   │
                └─────────┬────────────┘
                          │
                          ▼
                ┌──────────────────────┐
                │     pipeline.py      │  ← ORCHESTRATION
                │ run_pipeline()       │
                └─────────┬────────────┘
      ┌──────────┬────────┼────────┬──────────┐
      ▼          ▼        ▼        ▼          ▼
 data_loader  features   model   signals   evaluation





project/
│
├── main.py                # entrypoint (lokalnie / debug)
├── pipeline.py            # orchestration
│
├── api/
│   └── app.py             # FastAPI
│
├── ui/
│   └── app.py             # Streamlit
│
├── core/
│   ├── data_loader.py
│   ├── features.py
│   ├── model.py
│   ├── signals.py
│   └── evaluation.py
│
├── config/
│   └── settings.py
│
├── artifacts/
│   └── model.pkl







def run_pipeline():
    # 1. dane
    data = load_data()

    # 2. features
    X = create_features(data)

    # 3. model
    model = load_model()
    y_pred = model.predict(X.tail(1))

    # 4. decyzja
    signal = generate_signal(y_pred)

    return signal