# Gold Prediction ML

A machine-learning project that predicts the short-term **direction of gold** (long vs. no-trade) from macroeconomic and market features, wraps the model behind a REST API, and layers an LLM chat assistant on top for plain-language market commentary.

This is a personal learning project built while transitioning from **Product Manager / Business Analyst (banking, 15 years)** into an **AI Engineer** role. It's designed to hit the core skills that role requires — ML pipelines, model serving, LLMs/RAG, and cloud deployment — while staying grounded in a domain (financial markets) the author already knows well.

## What it does

1. **Pulls data** from Twelve Data (market prices/ETFs/commodities/crypto) and FRED (currencies, VIX, macro indicators).
2. **Engineers features** on top of the raw series (technical indicators, macro signals).
3. **Predicts** whether current conditions favor a long position in gold, using a LightGBM classifier trained with walk-forward validation.
4. **Serves the prediction** through a FastAPI endpoint, cached for 12h since the underlying data is daily.
5. **Explains the signal** through an LLM chat endpoint (RAG-backed with scraped market commentary) so a user can ask "why" in plain language, not just get a number.

## Architecture

```
                ┌──────────────────────┐
                │   static/index.html  │   ← chat UI (served by FastAPI)
                └─────────┬────────────┘
                          │
                          ▼
                ┌──────────────────────┐
                │     FastAPI (app.py) │
                │ GET /predict/gold    │
                │ POST /post/chat      │
                │ GET /health          │
                └─────────┬────────────┘
          ┌───────────────┼────────────────────┐
          ▼               ▼                    ▼
   DataPipeline    LGBM classifier      gold_analysis.py (LLM)
   (Twelve Data +   (models/*.pkl)       + RAG retriever
    FRED, cached)                        (ChromaDB, scraped
                                          market commentary)
```

## Project layout

```
src/
├── api/                    # FastAPI app — /predict/gold, /post/chat, /health
├── api_providers/          # Twelve Data, FRED, Stooq clients + dataframe merging
├── pipeline/               # DataPipeline orchestration (fetch → merge → feature engineer)
├── ml_work/
│   ├── feature_engineering/    # LGBM feature engineering
│   ├── lgm_classifier/         # training, walk-forward validation, MLflow logging
│   ├── financial_metrics.py    # Sharpe, CAGR, drawdown
│   └── trading_estimates.py
└── llm/
    ├── gold_analysis.py    # builds market context, calls the LLM for commentary
    ├── chat.py             # per-session chat history (Chat_history)
    └── rag/                # scraper, indexer, retriever (ChromaDB)

models/            # trained model + feature column list (joblib)
static/            # minimal HTML/JS chat frontend served by FastAPI
tests/             # pytest — feature engineering + financial metrics
streamlit_app.py   # alternative UI, not used in production (see file for why)
```

## Tech stack

- **ML**: LightGBM, scikit-learn-style pipeline, walk-forward validation, MLflow for experiment tracking
- **API**: FastAPI, Pydantic, uvicorn
- **LLM/RAG**: OpenAI/Azure OpenAI, ChromaDB, trafilatura + Playwright for scraping market commentary
- **Data sources**: Twelve Data, FRED, Stooq
- **Infra**: Docker, Azure Container Instances, GitHub Actions (build → push → deploy, plus scheduled start/stop to cut cost on idle nights/weekends)

## Running locally

```bash
# API
source venv/bin/activate
uvicorn src.api.app:app --reload --port 8000
# docs at http://localhost:8000/docs

# Chat UI (served by FastAPI itself)
# open http://localhost:8000/
```

## Model performance (walk-forward, 5 folds)

| Fold | Period | Sharpe | CAGR | Max DD |
|------|--------|--------|------|--------|
| 1 | 2016-08 – 2018-08 | -0.39 | -3.6% | -39.0% |
| 2 | 2018-08 – 2020-07 | 1.79 | 20.1% | -30.5% |
| 3 | 2020-07 – 2022-06 | -0.09 | -1.4% | -52.3% |
| 4 | 2022-06 – 2024-05 | 1.69 | 24.2% | -36.4% |
| 5 | 2024-05 – 2026-05 | 2.15 | 28.2% | -8.6% |

The model performs well in trending regimes and poorly in choppy/reversing ones — a known limitation, tracked as a possible regime-overfitting issue rather than a bug.

##  Mlflow metrics summary
| run_id                           | status   | start_time                       | end_time                         | tags.mlflow.source.type   | tags.mlflow.runName   |   metrics.classification/accuracy_score |   metrics.classification/train_accuracy |   metrics.classification/test_accuracy |   metrics.classification/log_Loss |   metrics.classification/roc_auc |   metrics.strategy/average_trade_return_pct |   metrics.strategy/pnl_long_pct |   metrics.strategy/sharpe |   metrics.strategy/sharpe_trade |   metrics.strategy/vol_annual_pct |   metrics.strategy/cagr_pct |   metrics.strategy/drawdown_from_peak_pct |   metrics.benchmark/buy_and_hold_return_pct |   metrics.benchmark/buy_and_hold_vol_annual_pct |   metrics.benchmark/buy_and_hold_cagr_pct |   metrics.benchmark/buy_and_hold_drawdown_pct |
|:---------------------------------|:---------|:---------------------------------|:---------------------------------|:--------------------------|:----------------------|----------------------------------------:|----------------------------------------:|---------------------------------------:|----------------------------------:|---------------------------------:|--------------------------------------------:|--------------------------------:|--------------------------:|--------------------------------:|----------------------------------:|----------------------------:|------------------------------------------:|--------------------------------------------:|------------------------------------------------:|------------------------------------------:|----------------------------------------------:|
| 4801fbb415114db79e792bd68575373c | FINISHED | 2026-07-09 07:58:06.952000+00:00 | 2026-07-09 07:58:09.533000+00:00 | LOCAL                     | omniscient-tern-539   |                                0.577699 |                                0.840651 |                               0.674067 |                          0.652939 |                         0.543894 |                                   0.0389265 |                        0.843549 |                  0.884243 |                         1.1375  |                          11.0936  |                     14.2622 |                                  -15.7821 |                                     124.104 |                                         14.4368 |                                   16.1176 |                                      -24.9455 |

## Status / roadmap

Actively being closed out before moving to the next learning project (a regulatory-document RAG system). Remaining scope, in order:

- [ ] Central bank gold purchase trends as narrative LLM context (not a model feature — data is too sparse/monthly to safely resample to daily without leaking across the train/test split)
- [ ] Function calling / tool use in `gold_analysis.py` (LLM calls the model instead of the prediction always being stuffed into the prompt)
- [ ] Evals for `gold_analysis.py` (scenario tests + LLM-as-judge)

See `claude_ai_engineer_checklist.md` for the full skills checklist this project is mapped against.
